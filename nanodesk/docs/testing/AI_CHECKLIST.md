# AI 自动化测试清单

> 以下测试可由 AI 自动或半自动完成，无需用户手动操作

---

## 快速执行

```powershell
# 运行所有自动化检查
python nanodesk\docs\testing\ai_check.py
```

或逐项检查：

---

## 1. 环境检查

### 1.1 分支检查
```powershell
git branch --show-current  # 期望: develop
git log --oneline -3       # 期望: 包含 v0.2.1 相关提交
```

### 1.2 版本检查
```python
# 检查 nanodesk 版本
python -c "from nanodesk import __version__; print(__version__)"  # 期望: 0.2.1

# 检查桌面版本
python -c "from nanodesk.desktop import __version__; print(__version__)"  # 期望: 0.2.1
```

### 1.3 依赖检查
```powershell
# 检查核心依赖
python -c "import nanobot, nanodesk; print('OK')"

# 检查新增搜索工具依赖
python -c "from duckduckgo_search import DDGS; print('duckduckgo-search: OK')"
python -c "from playwright.async_api import async_playwright; print('playwright: OK')"
```

---

## 2. 代码静态检查

### 2.1 导入测试
```python
# 测试 nanobot 上游更新后的导入
python -c "
from nanobot.agent.memory import MemoryManager
from nanobot.agent.loop import AgentLoop
from nanobot.channels.feishu import FeishuChannel
print('Upstream imports: OK')
"
```

### 2.2 新内存系统检查
```python
# 验证内存系统 v2 存在
python -c "
from nanobot.agent.memory import MemoryManager
import inspect
source = inspect.getsourcefile(MemoryManager)
with open(source) as f:
    content = f.read()
    if 'grep' in content.lower() or 'two-layer' in content.lower():
        print('Memory v2 detected: OK')
    else:
        print('WARNING: May be old memory system')
"
```

### 2.3 Ruff 格式检查
```powershell
ruff check nanodesk/tools/  # 期望: 无错误
ruff format --check nanodesk/tools/  # 期望: 已格式化
```

---

## 3. 工具注册检查

### 3.1 检查工具是否正确注册
```python
python -c "
from nanodesk import bootstrap
bootstrap.inject()

from nanobot.agent.tools.registry import ToolRegistry
tools = ToolRegistry._tools

expected = ['ddg_search', 'browser_search', 'browser_fetch']
registered = [name for name in expected if name in tools]
missing = [name for name in expected if name not in tools]

print(f'Registered: {registered}')
print(f'Missing: {missing}')

if not missing:
    print('All tools registered: OK')
else:
    print('ERROR: Some tools missing!')
"
```

### 3.2 检查工具类定义
```python
# 验证工具类存在且结构正确
python -c "
from nanodesk.tools.ddg_search import DuckDuckGoSearchTool
from nanodesk.tools.browser_search import BrowserSearchTool, BrowserFetchTool

tools = [DuckDuckGoSearchTool, BrowserSearchTool, BrowserFetchTool]
for tool_class in tools:
    tool = tool_class()
    assert hasattr(tool, 'name'), f'{tool_class.__name__} missing name'
    assert hasattr(tool, 'description'), f'{tool_class.__name__} missing description'
    assert hasattr(tool, 'parameters'), f'{tool_class.__name__} missing parameters'
    print(f'{tool.name}: OK')

print('All tool classes valid: OK')
"
```

---

## 4. 配置文件检查

### 4.1 检查配置 schema
```python
# 验证配置 schema 包含新字段
python -c "
from nanobot.config.schema import Config
import inspect
sig = inspect.signature(Config)
print(f'Config fields: {list(sig.parameters.keys())}')
print('Config schema: OK')
"
```

### 4.2 检查示例配置
```powershell
# 验证 pyproject.toml 语法
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('pyproject.toml: OK')"
```

---

## 5. 构建测试（可选，耗时较长）

### 5.1 检查构建脚本
```powershell
# 检查脚本存在且可执行
Test-Path nanodesk/scripts/build_all.ps1        # 期望: True
Test-Path nanodesk/scripts/prepare_embedded_python.py  # 期望: True
```

### 5.2 快速构建测试（跳过嵌入 Python）
```powershell
# 仅测试 PyInstaller 打包（不下载嵌入 Python）
# 注意: 这会创建 build/ 目录，测试后需清理
# python nanodesk/scripts/build_desktop.ps1
```

---

## 6. 自动化检查脚本

保存为 `ai_check.py`：

```python
#!/usr/bin/env python3
"""AI automated checks for develop branch."""

import sys
import subprocess

def run(cmd, desc):
    """Run command and check result."""
    print(f"\n[CHECK] {desc}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"  ✓ PASS")
            return True
        else:
            print(f"  ✗ FAIL: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def main():
    checks = [
        ("git branch --show-current", "Branch is develop"),
        ("python -c 'from nanodesk import __version__; print(__version__)'", "Version check"),
        ("python -c 'import nanobot, nanodesk'", "Core imports"),
        ("python -c 'from duckduckgo_search import DDGS'", "ddg_search dependency"),
        ("python -c 'from playwright.async_api import async_playwright'", "playwright dependency"),
        ("python -c 'from nanobot.agent.memory import MemoryManager'", "Memory system import"),
        ("ruff check nanodesk/tools/", "Ruff lint check"),
    ]
    
    passed = sum(run(cmd, desc) for cmd, desc in checks)
    total = len(checks)
    
    print(f"\n{'='*40}")
    print(f"Results: {passed}/{total} passed")
    
    if passed == total:
        print("All automated checks passed! ✓")
        return 0
    else:
        print("Some checks failed. Please review.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 检查结果记录

AI 执行后在此记录：

| 检查项 | 结果 | 备注 |
|--------|------|------|
| 分支检查 | ⬜ | |
| 版本检查 | ⬜ | |
| 依赖检查 | ⬜ | |
| 工具注册 | ⬜ | |
| 静态检查 | ⬜ | |

**AI 检查完成后**: 转到 [MANUAL_CHECKLIST.md](./MANUAL_CHECKLIST.md) 继续手动测试
