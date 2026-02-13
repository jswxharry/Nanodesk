# 工具执行反馈改进设计

> 解决"工具执行后 AI 不主动回复"的 UX 问题

**提案状态**: 📝 设计阶段  
**优先级**: 高  
**影响范围**: `nanobot/agent/loop.py`, `nanobot/agent/tools/`

---

## 问题描述

### 当前行为（问题）

```
用户: "查看本机 IP"
AI:   "我来执行命令..."                    ← 只说了要做什么
      [执行 ipconfig，耗时 2 秒]           ← 用户完全不知道发生了什么
      [等待 LLM 生成回复]                  ← 用户觉得"卡住了"
AI:   "IP 是 192.168.1.5"                 ← 5秒后才回复

用户: "执行好了吗?"  ← 用户焦虑，主动追问
```

### 根本原因

当前代码流程（`loop.py` 247-249 行）：

```python
result = await self.tools.execute(tool_call.name, tool_call.arguments)
messages = self.context.add_tool_result(messages, tool_call.id, tool_call.name, result)
# 继续循环，等 LLM 决定下一步说什么
```

**问题**：
1. 工具执行是"静默"的，用户看不到进度
2. 执行结果直接塞进 context，没有即时反馈给用户
3. 长时任务（如 `pip install`）会让用户觉得 AI 挂了

---

## 目标用户体验

```
用户: "查看本机 IP"
AI:   "我来执行命令查看 IP 地址..."        ← 立即响应
      [2秒后]
AI:   "✅ 执行完成，IP 地址是 192.168.1.5"  ← 即时反馈结果
```

对于长时间任务：
```
用户: "安装 numpy"
AI:   "⏳ 正在执行 pip install numpy，预计需要 10-30 秒..."
      [10秒后]
AI:   "⏳ 仍在安装中..."
      [完成后]
AI:   "✅ 安装完成，numpy 2.1.0 已可用"
```

---

## 设计方案

### 方案 A: 即时状态推送（推荐）

修改 `AgentLoop._process_message`，在工具执行前后添加状态消息：

```python
# nanobot/agent/loop.py

async def _execute_tool_with_feedback(self, tool_call, channel, chat_id):
    """执行工具并发送状态反馈"""
    
    # 1. 发送"正在执行"通知
    tool_name = tool_call.name
    await self.bus.publish_outbound(OutboundMessage(
        channel=channel,
        chat_id=chat_id,
        content=f"⏳ 正在执行 `{tool_name}`...",
        reply_to_message_id=None
    ))
    
    # 2. 执行工具
    start_time = asyncio.get_event_loop().time()
    result = await self.tools.execute(tool_call.name, tool_call.arguments)
    elapsed = asyncio.get_event_loop().time() - start_time
    
    # 3. 发送执行结果摘要
    result_summary = self._summarize_result(tool_call.name, result, elapsed)
    await self.bus.publish_outbound(OutboundMessage(
        channel=channel,
        chat_id=chat_id,
        content=result_summary,
        reply_to_message_id=None
    ))
    
    return result


def _summarize_result(self, tool_name: str, result: str, elapsed: float) -> str:
    """生成执行结果摘要"""
    
    # 截断过长的结果
    max_len = 500
    if len(result) > max_len:
        display = result[:max_len] + f"\n... (还有 {len(result) - max_len} 字符)"
    else:
        display = result
    
    # 检查是否有错误
    if "error" in result.lower() or "失败" in result:
        status = "❌"
    else:
        status = "✅"
    
    return f"{status} `{tool_name}` 执行完成 ({elapsed:.1f}s):\n```\n{display}\n```"
```

**优点**:
- 用户立即知道发生了什么
- 执行结果即时可见
- 实现简单，改动小

**缺点**:
- 多轮工具调用时消息较多
- 需要控制消息频率

---

### 方案 B: 流式进度更新（长时任务）

对于 `exec` 等可能长时间运行的工具，添加进度回调：

```python
# nanobot/agent/tools/shell.py

class ExecTool(Tool):
    async def execute(
        self, 
        command: str, 
        timeout: int = 60,
        progress_callback: Callable[[str], None] | None = None
    ) -> str:
        """
        执行 shell 命令，支持进度回调
        
        progress_callback: 定期发送进度消息
        """
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.workspace
        )
        
        # 定期报告进度
        last_progress = asyncio.get_event_loop().time()
        while True:
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=5.0  # 每5秒检查一次
                )
                break
            except asyncio.TimeoutError:
                elapsed = asyncio.get_event_loop().time() - last_progress
                if elapsed > 10 and progress_callback:  # 10秒报告一次
                    progress_callback(f"⏳ 仍在执行中... ({int(elapsed)}s)")
                    last_progress = asyncio.get_event_loop().time()
        
        # ... 处理结果
```

---

### 方案 C: 统一状态管理（高级）

添加 `ToolExecutionState` 管理工具执行状态：

```python
# nanobot/agent/tools/state.py

from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class ToolState(Enum):
    PENDING = "pending"
    RUNNING = "running"  
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class ToolExecution:
    id: str
    name: str
    arguments: dict
    state: ToolState
    start_time: datetime
    end_time: datetime | None = None
    result: str | None = None
    progress_message_id: str | None = None  # 用于更新状态消息

class ToolExecutionManager:
    """管理正在执行的工具任务"""
    
    def __init__(self, bus: MessageBus):
        self.executions: dict[str, ToolExecution] = {}
        self.bus = bus
    
    async def start_execution(
        self, 
        tool_name: str, 
        arguments: dict,
        channel: str,
        chat_id: str
    ) -> ToolExecution:
        """开始执行，发送状态消息"""
        exec_id = str(uuid.uuid4())
        execution = ToolExecution(
            id=exec_id,
            name=tool_name,
            arguments=arguments,
            state=ToolState.RUNNING,
            start_time=datetime.now()
        )
        
        # 发送"正在执行"消息
        msg = await self.bus.publish_outbound(OutboundMessage(
            channel=channel,
            chat_id=chat_id,
            content=f"⏳ 正在执行 `{tool_name}`...",
        ))
        execution.progress_message_id = msg.message_id
        
        self.executions[exec_id] = execution
        return execution
    
    async def complete_execution(
        self, 
        exec_id: str, 
        result: str,
        success: bool = True
    ):
        """完成执行，更新状态"""
        execution = self.executions[exec_id]
        execution.end_time = datetime.now()
        execution.result = result
        execution.state = ToolState.COMPLETED if success else ToolState.FAILED
        
        # 编辑原消息或发送新消息
        elapsed = (execution.end_time - execution.start_time).total_seconds()
        status = "✅" if success else "❌"
        content = f"{status} `{execution.name}` 完成 ({elapsed:.1f}s)"
        
        await self.bus.edit_message(  # 需要频道支持编辑消息
            channel=execution.channel,
            message_id=execution.progress_message_id,
            content=content
        )
```

---

## 推荐实施路径

### Phase 1: 即时反馈（1-2 天）

实现方案 A 的核心功能：

1. **修改 `AgentLoop._process_message`**:
   - 工具执行前发送"正在执行"消息
   - 工具执行后发送结果摘要

2. **添加结果截断和格式化**:
   - 避免过长结果刷屏
   - 添加成功/失败状态 emoji

3. **配置开关**:
   - 添加 `tools.show_execution_feedback: bool` 配置
   - 默认开启，可关闭

### Phase 2: 长时任务优化（1 周）

1. **为 ExecTool 添加超时回调**
2. **实现定期心跳消息**（每 10 秒）
3. **支持消息编辑**（飞书/Discord 支持编辑原消息）

### Phase 3: 状态管理（可选）

1. 实现完整的 `ToolExecutionManager`
2. 支持工具执行历史查询
3. 支持取消正在执行的工具

---

## 相关代码位置

| 文件 | 相关代码 | 修改点 |
|------|----------|--------|
| `nanobot/agent/loop.py` | 243-249 行 | 添加执行前后反馈 |
| `nanobot/agent/tools/shell.py` | `execute()` 方法 | 添加进度回调 |
| `nanobot/config/schema.py` | `ToolsConfig` | 添加反馈配置项 |
| `nanobot/bus/events.py` | `OutboundMessage` | 可能需要编辑消息支持 |

---

## 验收标准

- [ ] 执行工具前，用户收到"正在执行..."通知
- [ ] 执行完成后，用户立即看到结果（不等待 LLM 回复）
- [ ] 长时间任务（>10s）定期报告进度
- [ ] 结果消息包含执行时间和状态
- [ ] 可通过配置关闭反馈功能

---

## 参考截图

![用户反馈截图](../assets/tool_feedback_issue.png)

用户抱怨："为啥你每次要我主动问百回答"

---

## 下一步行动

1. **确认方案**: 选择方案 A/B/C 或组合
2. **快速验证**: 实现 Phase 1，在桌面端测试
3. **收集反馈**: 观察是否解决用户焦虑问题
