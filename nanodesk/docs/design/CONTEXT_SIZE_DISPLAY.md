# 上下文大小显示功能设计

> 让用户实时查看对话上下文（token 数量），便于管理长对话

**提案状态**: 📝 设计阶段  
**优先级**: 低-中  
**影响范围**: `nanobot/agent/loop.py`, `nanobot/agent/context.py`

---

## 需求描述

### 用户场景

```
用户: /context on                    ← 开启上下文显示
Agent: ✅ 已开启上下文大小显示

用户: 帮我分析这个代码文件
Agent: [分析结果]
      📊 上下文: 2,847 tokens / 约 11.4 KB

用户: 继续分析另一个文件...
Agent: [分析结果]
      📊 上下文: 8,932 tokens / 约 35.7 KB  ← 用户意识到接近上限

用户: /context off                   ← 关闭显示
Agent: ✅ 已关闭上下文大小显示
```

### 核心需求

| 功能 | 说明 |
|------|------|
| 开关控制 | 默认关闭，通过命令 `/context on/off` 切换 |
| 持久化 | 开启后在同一会话中持续显示 |
| 显示位置 | 每条回复末尾附加 token 信息 |
| 显示格式 | 简洁，不干扰主要内容 |

---

## 技术方案

### Token 计算方式

```python
# 方案 1: tiktoken (OpenAI 官方，准确)
import tiktoken

def count_tokens(messages: list[dict], model: str = "gpt-4") -> int:
    """计算消息列表的 token 数量"""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # 默认编码
    
    total = 0
    for msg in messages:
        # 每条消息的格式开销
        total += 4  # <|im_start|>{role}\n{content}<|im_end|>\n
        
        if isinstance(msg["content"], str):
            total += len(encoding.encode(msg["content"]))
        elif isinstance(msg["content"], list):
            # 多模态内容（图片等）
            for item in msg["content"]:
                if item.get("type") == "text":
                    total += len(encoding.encode(item["text"]))
                elif item.get("type") == "image_url":
                    total += 1000  # 图片估算值
    
    return total
```

```python
# 方案 2: 简单估算 (无需额外依赖)
def estimate_tokens(messages: list[dict]) -> int:
    """
    简单估算 token 数量
    英文约 1 token/字，中文约 2 tokens/字
    """
    total_chars = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total_chars += len(content)
        elif isinstance(content, list):
            for item in content:
                if item.get("type") == "text":
                    total_chars += len(item["text"])
    
    # 粗略估算：字符数 / 2.5
    return int(total_chars / 2.5)
```

**推荐**: 方案 1 (tiktoken) 更准确，可以添加为可选依赖

---

### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     AgentLoop                           │
│  ┌─────────────────┐         ┌──────────────────────┐  │
│  │  process_message│         │   ContextMonitor     │  │
│  │                 │         │  ┌────────────────┐  │  │
│  │  ┌───────────┐  │         │  │ count_tokens() │  │  │
│  │  │ build_ctx │──┼────────>│  └────────────────┘  │  │
│  │  └───────────┘  │         │           │          │  │
│  │         │       │         │  ┌────────▼─────────┐│  │
│  │  ┌──────▼──────┐│         │  │ format_display() ││  │
│  │  │ send_resp   ││<────────│  └──────────────────┘│  │
│  │  └─────────────┘│         └──────────────────────┘  │
│  └─────────────────┘                                    │
└─────────────────────────────────────────────────────────┘
```

### 数据流

```python
# 1. 用户开启显示
user_message = "/context on"
→ session_manager.set_flag("show_context_size", True)
→ reply: "✅ 已开启上下文大小显示"

# 2. 正常对话（已开启）
user_message = "帮我分析代码"
→ messages = context.build_messages(history, user_message)
→ token_count = count_tokens(messages)
→ response = llm.generate(messages)
→ response += f"\n\n📊 上下文: {token_count:,} tokens"
→ send_reply(response)

# 3. 用户关闭显示
user_message = "/context off"
→ session_manager.set_flag("show_context_size", False)
→ reply: "✅ 已关闭上下文大小显示"
```

---

## 详细实现

### 1. Token 计数模块

```python
# nanobot/agent/token_counter.py
"""Token 计数工具，支持多种模型"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)

# 是否可用 tiktoken
TIKTOKEN_AVAILABLE = False
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    logger.debug("tiktoken not available, using estimation")


def count_tokens(messages: list[dict], model: Optional[str] = None) -> dict:
    """
    计算消息列表的 token 数量
    
    Returns:
        {
            "total": 总 token 数,
            "system": 系统消息 tokens,
            "history": 历史消息 tokens,
            "current": 当前消息 tokens,
            "method": "tiktoken" or "estimate"
        }
    """
    if TIKTOKEN_AVAILABLE:
        return _count_with_tiktoken(messages, model)
    else:
        return _count_with_estimate(messages)


def _count_with_tiktoken(messages: list[dict], model: Optional[str]) -> dict:
    """使用 tiktoken 精确计算"""
    try:
        encoding = tiktoken.encoding_for_model(model or "gpt-4")
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    result = {"total": 0, "system": 0, "history": 0, "current": 0, "method": "tiktoken"}
    
    for i, msg in enumerate(messages):
        tokens = _encode_message(msg, encoding)
        result["total"] += tokens
        
        # 分类统计
        if msg.get("role") == "system":
            result["system"] += tokens
        elif i == len(messages) - 1 and msg.get("role") == "user":
            result["current"] += tokens
        else:
            result["history"] += tokens
    
    return result


def _count_with_estimate(messages: list[dict]) -> dict:
    """简单估算（无需 tiktoken）"""
    result = {"total": 0, "system": 0, "history": 0, "current": 0, "method": "estimate"}
    
    for i, msg in enumerate(messages):
        content = msg.get("content", "")
        if isinstance(content, str):
            # 英文约 0.25 tokens/char，中文约 0.5 tokens/char
            # 粗略平均：chars / 2.5
            tokens = max(1, int(len(content) / 2.5))
        elif isinstance(content, list):
            tokens = 0
            for item in content:
                if item.get("type") == "text":
                    tokens += max(1, int(len(item.get("text", "")) / 2.5))
                elif item.get("type") == "image_url":
                    tokens += 1000  # 图片估算
        else:
            tokens = 0
        
        result["total"] += tokens
        
        if msg.get("role") == "system":
            result["system"] += tokens
        elif i == len(messages) - 1 and msg.get("role") == "user":
            result["current"] += tokens
        else:
            result["history"] += tokens
    
    return result


def _encode_message(msg: dict, encoding) -> int:
    """编码单条消息"""
    tokens = 4  # 消息格式开销 <|im_start|>role\n
    
    content = msg.get("content", "")
    if isinstance(content, str):
        tokens += len(encoding.encode(content))
    elif isinstance(content, list):
        for item in content:
            if item.get("type") == "text":
                tokens += len(encoding.encode(item["text"]))
            elif item.get("type") == "image_url":
                # 图片 token 计算复杂，估算 1000
                tokens += 1000
    
    tokens += 2  # <|im_end|>\n
    return tokens


def format_display(token_info: dict) -> str:
    """格式化显示 token 信息"""
    total = token_info["total"]
    method = token_info["method"]
    
    # 估算 KB（约 4 bytes/token）
    kb = total * 4 / 1024
    
    # 不同模型的上下文上限提示
    if total > 120000:
        warning = " ⚠️接近上限"
    elif total > 80000:
        warning = " 🟡注意"
    else:
        warning = ""
    
    method_note = "~" if method == "estimate" else ""
    
    return f"📊 上下文: {method_note}{total:,} tokens / {method_note}{kb:.1f} KB{warning}"
```

### 2. 命令处理

```python
# nanobot/agent/loop.py

async def _process_message(self, msg: InboundMessage) -> OutboundMessage | None:
    # ... 现有代码 ...
    
    # 处理 /context 命令
    if msg.content.strip() == "/context on":
        self.session_manager.set_session_flag(
            msg.channel, msg.chat_id, "show_context_size", True
        )
        return OutboundMessage(
            channel=msg.channel,
            chat_id=msg.chat_id,
            content="✅ 已开启上下文大小显示\n\n"
                   "💡 提示：每条回复末尾将显示当前对话的 token 数量\n"
                   "   发送 `/context off` 关闭显示"
        )
    
    if msg.content.strip() == "/context off":
        self.session_manager.set_session_flag(
            msg.channel, msg.chat_id, "show_context_size", False
        )
        return OutboundMessage(
            channel=msg.channel,
            chat_id=msg.chat_id,
            content="✅ 已关闭上下文大小显示"
        )
    
    # ... 正常处理流程 ...
```

### 3. 回复附加 token 信息

```python
# nanobot/agent/loop.py

async def _generate_response(self, messages: list[dict], msg: InboundMessage) -> str:
    """生成回复，可能附加 token 信息"""
    
    # 调用 LLM 生成回复
    response = await self.provider.generate(messages)
    
    # 检查是否需要显示上下文大小
    show_context = self.session_manager.get_session_flag(
        msg.channel, msg.chat_id, "show_context_size", default=False
    )
    
    if show_context:
        from nanobot.agent.token_counter import count_tokens, format_display
        
        token_info = count_tokens(messages, model=self.model)
        display = format_display(token_info)
        
        # 附加到回复末尾
        response += f"\n\n{display}"
    
    return response
```

---

## 配置选项

```python
# nanobot/config/schema.py

class AgentConfig(BaseModel):
    """Agent 配置"""
    
    # ... 现有配置 ...
    
    enable_context_size_display: bool = True
    """是否启用 /context 命令功能"""
    
    context_size_warning_threshold: int = 80000
    """token 数量警告阈值（黄色提醒）"""
    
    context_size_critical_threshold: int = 120000
    """token 数量危险阈值（红色警告）"""
```

---

## 用户界面

### 命令格式

```
/context on       # 开启显示
/context off      # 关闭显示  
/context status   # 查看当前状态
```

### 显示样式

**正常状态**:
```
📊 上下文: 2,847 tokens / 11.1 KB
```

**接近上限** (黄色):
```
🟡 上下文: 85,432 tokens / 333.7 KB
```

**接近上限** (红色，使用估算):
```
⚠️ 上下文: ~125,600 tokens / ~490.6 KB
```

---

## 依赖管理

```toml
# pyproject.toml
[project.optional-dependencies]
tiktoken = ["tiktoken>=0.5.0"]
all = ["tiktoken>=0.5.0", ...]
```

```python
# 安装时提示
"""
tiktoken not available, using estimation.
For accurate token counting, install with:
    pip install tiktoken
"""
```

---

## 实施步骤

```
Phase 1: 核心功能 (1 天)
├── 创建 token_counter.py 模块
│   └── 支持 tiktoken 和估算两种模式
├── 实现 /context on/off 命令
└── 在回复末尾附加 token 信息

Phase 2: 优化 (0.5 天)
├── 分类统计 (system/history/current)
├── 阈值警告颜色
└── 添加 tiktoken 为可选依赖

Phase 3: 完善 (0.5 天)
├── 持久化开关状态
├── /context status 命令
└── 文档和示例
```

---

## 验收标准

- [ ] `/context on` 开启后，每条回复显示 token 数量
- [ ] `/context off` 关闭显示
- [ ] 未安装 tiktoken 时使用估算模式，显示 "~"
- [ ] 超过阈值时显示警告颜色
- [ ] 开关状态在同一会话中持久化
- [ ] 不影响正常对话性能（计数 < 10ms）

---

## 注意事项

1. **性能**: token 计数不应显著影响响应时间（目标 < 10ms）
2. **隐私**: token 计数本地完成，不发送额外请求
3. **兼容性**: 支持文本和多模态消息
4. **可选依赖**: tiktoken 作为可选，无依赖时降级估算

---

**下一步**: 确认需求细节后，可从 Phase 1 开始实现
