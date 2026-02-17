# Kimi Claw AI 开发 Nanodesk 指导

> 本文档记录 Kimi Claw AI（Nado）在开发 Nanodesk 时的最佳实践、常见模式和注意事项。
> 
> 创建时间：2026-02-17
> 最后更新：2026-02-17

---

## 项目结构理解

### 核心目录

```
Nanodesk/
├── nanodesk/              # 主代码目录
│   ├── desktop/           # Windows 桌面应用
│   ├── channels/          # 通讯频道扩展
│   ├── tools/             # 工具扩展
│   ├── skills/            # 技能扩展
│   ├── providers/         # LLM 提供商适配
│   ├── patches/           # 核心补丁
│   └── scripts/           # 辅助脚本
│       ├── build/         # 构建脚本
│       ├── dev/           # 开发脚本
│       ├── git/           # Git 操作脚本
│       └── release/       # 发布脚本
├── tests/                 # 测试文件
├── docs/                  # 文档
│   ├── design/            # 设计文档
│   ├── setup/             # 配置指南
│   └── discussion/        # 讨论记录
└── pyproject.toml         # 项目配置
```

### 关键文件

| 文件 | 用途 |
|------|------|
| `nanodesk/bootstrap.py` | 启动注入逻辑，注册自定义工具和频道 |
| `nanodesk/patches/` | 修改 nanobot 核心行为的补丁 |
| `nanodesk/desktop/main.py` | Windows 桌面应用入口 |

---

## 开发工作流

### 1. 分支策略

```
feature/xxx  →  develop  →  nanodesk(main)
     ↑              ↑
   新功能         集成测试
```

**当前工作分支：** `nanodesk`

### 2. 常用命令

```bash
# 安装开发环境
pip install -e .

# 启动 Gateway
nanodesk gateway --verbose

# 启动桌面应用（开发模式）
python -m nanodesk.desktop.main

# 运行测试
python tests/test_adapter_integration.py

# 同步上游
./nanodesk/scripts/git/sync-upstream.ps1
```

---

## 配置管理

### Nanodesk 配置位置

```
Linux/Mac: ~/.nanobot/config.json
Windows:   C:\Users\<用户名>\.nanobot\config.json
```

### 配置 Kimi Coding Adapter

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

### Adapter 配置位置

```
~/.openclaw/kimi-adapter.json
```

```json
{
  "api_key": "ndsk-kimi-adapter-7a3f9e2d",
  "port": 8000,
  "host": "127.0.0.1"
}
```

---

## 开发模式

### 模式一：命令行开发（推荐用于后端开发）

```bash
# 启动 Gateway，通过飞书/Telegram 交互
nanodesk gateway --verbose
```

### 模式二：桌面应用开发（推荐用于 UI 开发）

```bash
# 启动桌面应用
python -m nanodesk.desktop.main
```

### 模式三：直接测试（推荐用于功能验证）

```bash
# 运行特定测试
python tests/test_adapter_integration.py
```

---

## 添加自定义工具

### 步骤

1. **创建工具文件** `nanodesk/tools/my_tool.py`:

```python
from nanobot.agent.tools.base import Tool

class MyTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "描述工具功能"
    
    async def execute(self, **kwargs) -> str:
        # 实现逻辑
        return "结果"
```

2. **注册工具** 在 `nanodesk/bootstrap.py`:

```python
from nanodesk.tools.my_tool import MyTool
from nanobot.agent.tools.registry import ToolRegistry

ToolRegistry.register(MyTool())
```

---

## 测试规范

### 测试文件位置

- 通用测试：`tests/test_*.py`
- 桌面应用测试：`nanodesk/desktop/test_desktop.py`
- 电源管理测试：`nanodesk/scripts/dev/test_power_management.py`

### 测试模板

```python
#!/usr/bin/env python3
"""测试描述"""

import json
import urllib.request
import sys

def test_feature():
    """测试功能"""
    try:
        # 测试逻辑
        assert condition, "错误信息"
        print("✅ 测试通过")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    tests = [
        ("测试名称", test_feature),
    ]
    
    results = [(name, func()) for name, func in tests]
    
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{len(results)} passed")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 常见任务

### 任务 1：验证 Adapter 连接

```bash
cd tests
python test_adapter_integration.py
```

### 任务 2：启动 Adapter 服务

```bash
cd ~/NadoMemory/bridge/kimi_coding_adapter
./adapter.sh start
./adapter.sh status
./adapter.sh test
```

### 任务 3：查看日志

```bash
# Adapter 日志
tail -f /tmp/adapter.log

# Nanodesk Gateway 日志
# 在桌面应用日志窗口查看
```

### 任务 4：构建桌面版

```powershell
# Windows
.\nanodesk\scripts\build\build_all.ps1 -Clean
```

---

## 注意事项

### 1. 路径处理

- 使用 `pathlib.Path` 而非字符串拼接
- 配置文件路径：`Path.home() / ".nanobot" / "config.json"`

### 2. 异步代码

- 工具 `execute` 方法是 async
- 使用 `await` 调用异步操作

### 3. 错误处理

- 使用 try/except 捕获具体异常
- 提供清晰的错误信息

### 4. 配置读取

- 优先从标准位置读取配置
- 提供合理的默认值
- 敏感信息（API Key）使用 DPAPI 加密（桌面版）

---

## 待办事项跟踪

查看 `docs/TODO.md` 获取最新开发计划。

**高优先级任务：**
- [ ] 本地知识检索
- [ ] 工具执行即时反馈
- [ ] Windows 截图工具

**当前状态：**
- ✅ Kimi Coding Adapter 集成完成
- ✅ Adapter 权限管理完成
- ✅ 测试脚本完成

---

## 参考链接

- [Nanodesk README](./README.md)
- [TODO 列表](./docs/TODO.md)
- [配置指南](./docs/setup/CONFIGURATION.md)
- [架构设计](./docs/ARCHITECTURE.md)

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
```
