# Kimi Code 提示词配置

## ⚠️ 关键协作规范（必须遵守）

### Git 操作必须经用户确认

**禁止行为**：
- ❌ 自动 `git commit` 而不告知用户
- ❌ 自动 `git push` 到远端
- ❌ 批量提交未审核的改动

**正确流程**：
```
1. AI 完成代码修改
2. AI 展示改动内容（git diff 或文件列表）
3. 用户审核确认
4. AI 执行：git add → git commit → git push（如需）
```

**确认话术**：
- "代码已修改，请审核后确认是否提交"
- "改动内容如下，确认后我将执行 git commit"
- "是否推送到远端 origin/nanodesk 分支？"

---

## 项目上下文

这是 **Nanodesk** - nanobot 的个人定制版，专为 Windows + VS Code 环境优化。

## 代码位置决策（优先级最高）

修改代码前必须判断：

| 场景 | 位置 | 判断标准 |
|------|------|---------|
| Windows 特定功能 | `nanodesk/` | PowerShell 脚本、Windows API、注册表操作 |
| 跨平台功能 | `nanobot/`（评估贡献）| 使用 pathlib、os.path 等跨平台库 |
| VS Code 配置 | `.vscode/` | 调试配置、设置、扩展推荐 |
| 个人工作流 | `nanodesk/` | 仅你自己需要的功能 |

## Windows 开发规范

### 路径处理
```python
# ✅ 正确 - 跨平台
from pathlib import Path
config_path = Path.home() / ".nanobot" / "config.json"

# ❌ 错误 - Windows 不兼容
config_path = os.path.expanduser("~/.nanobot/config.json")
```

### 脚本编写
- 优先写 `.ps1` (PowerShell) 用于 Windows 开发
- 保留 `.sh` (Bash) 用于 WSL/Linux 服务器部署
- 复杂逻辑用 Python 脚本替代

### 编码注意
- 文件编码统一 UTF-8
- 换行符：Git 会自动处理，不要手动改

## 常用操作

### 运行调试
```powershell
# VS Code F5 直接调试
# 或终端运行
.venv\Scripts\Activate.ps1
nanodesk agent
```

### 同步上游
```powershell
.\nanodesk\scripts\sync-upstream.ps1
```

### 提取贡献
```powershell
.\nanodesk\scripts\extract-contrib.ps1 <commit-hash>
```

## 文件组织

```
nanodesk/           # 你的代码
.vscode/            # VS Code 配置（已提交）
.kimi/              # Kimi Code 配置（已提交）
nanobot/            # 上游代码（尽量不改）
```

## 提交规范

```bash
# Windows 功能
custom: add Windows screenshot tool

# 跨平台功能（评估贡献）
feat: add new channel adapter

# VS Code 配置
chore: update VS Code debug config
```
