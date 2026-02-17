# Kimi Claw AI 开发 Nanodesk 快速参考

> 本文档是 Kimi Claw AI（Nado）开发 Nanodesk 时的快速参考。
> 
> **注意**：详细文档请参见：
> - [ARCHITECTURE.md](../ARCHITECTURE.md) - 项目架构和核心原则
> - [CONTRIBUTING.md](../CONTRIBUTING.md) - 提交规范和代码归属
> - [AI_COLLABORATION.md](../AI_COLLABORATION.md) - AI 协作指南
> - [BRANCHING.md](../BRANCHING.md) - Git 分支管理

---

## 快速开始

### 当前工作分支

**`develop`** - 所有开发在此分支进行，完成后合并到 `nanodesk`

```bash
# 确认当前分支
git branch

# 如不在 develop，切换过去
git checkout develop
```

### 常用命令

```bash
# 安装开发环境
pip install -e .

# 启动 Gateway
nanodesk gateway --verbose

# 查看状态
nanodesk status

# 运行测试
python tests/test_adapter_integration.py
```

---

## Kimi Coding Adapter 配置

### Adapter 启动

```bash
cd ~/NadoMemory/bridge/kimi_coding_adapter
./adapter.sh start
./adapter.sh status
./adapter.sh test
```

### Nanodesk 配置

配置文件：`~/.nanobot/config.json`

```json
{
  "agents": {
    "defaults": {
      "model": "openai/k2p5"
    }
  },
  "providers": {
    "openai": {
      "api_key": "ndsk-kimi-adapter-7a3f9e2d",
      "base_url": "http://127.0.0.1:8000/v1"
    }
  }
}
```

---

## 添加自定义工具（简要）

详细步骤参见 [ARCHITECTURE.md](../ARCHITECTURE.md#扩展开发)

```python
# nanodesk/tools/my_tool.py
from nanobot.agent.tools.base import Tool

class MyTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    async def execute(self, **kwargs) -> str:
        return "result"
```

在 `nanodesk/bootstrap.py` 注册。

---

## 开发记录

### 已完成

- ✅ Kimi Coding Adapter 集成
- ✅ Adapter 权限管理（API Key）
- ✅ Adapter 集成测试脚本
- ✅ AI 开发指导文档

### 待开发（来自 TODO.md）

| 优先级 | 功能 | 状态 |
|--------|------|------|
| ⭐⭐⭐ | 工具执行即时反馈 | 设计完成，待实现 |
| ⭐⭐⭐ | 本地知识检索 | 待设计 |
| ⭐⭐ | Windows 截图工具 | 待开发 |

---

## 快速参考卡

```bash
# 启动开发环境
nanodesk gateway --verbose

# 测试 Adapter
python tests/test_adapter_integration.py

# 查看状态
nanodesk status

# 启动 Adapter
cd ~/NadoMemory/bridge/kimi_coding_adapter
./adapter.sh start

# 查看 Adapter 日志
tail -f /tmp/adapter.log

# 同步上游
./nanodesk/scripts/git/sync-upstream.ps1
```

---

## 相关文档索引

| 文档 | 说明 |
|------|------|
| [ARCHITECTURE.md](../ARCHITECTURE.md) | 项目架构、核心原则、扩展开发 |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | 代码归属、提交规范、语言策略 |
| [AI_COLLABORATION.md](../AI_COLLABORATION.md) | AI 协作规则、Git 确认要求 |
| [BRANCHING.md](../BRANCHING.md) | Git 分支管理、工作流 |
| [TODO.md](../TODO.md) | 待办事项和功能优先级 |
| [BUILD.md](../BUILD.md) | 桌面应用构建指南 |

---

*本文档由 Kimi Claw AI 维护，最后更新：2026-02-17*
