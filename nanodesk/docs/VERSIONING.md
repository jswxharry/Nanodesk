# Nanodesk 版本管理指南

> 统一项目版本号管理规范

---

## 版本号格式

采用 [语义化版本](https://semver.org/lang/zh-CN/) 规范：**MAJOR.MINOR.PATCH**

- **MAJOR** (主版本号): 不兼容的 API 修改
- **MINOR** (次版本号): 向下兼容的功能新增
- **PATCH** (修订号): 向下兼容的问题修复

**示例**: `0.2.1` - 第 0 主版本，第 2 次功能更新，第 1 次修复

---

## 需要更新的位置

发布新版本时，需要同步更新以下文件：

### 1. Python 包版本

```python
# nanodesk/__init__.py
__version__ = "0.2.1"

# nanodesk/desktop/__init__.py  
__version__ = "0.2.1"
```

### 2. pyproject.toml（如需独立发布）

```toml
[project]
name = "nanobot-ai"
version = "0.2.1"  # 或保持与上游一致
```

> **注意**: 当前 `pyproject.toml` 版本跟随上游 nanobot，仅作为依赖安装时使用。
> Nanodesk 桌面版的版本以 `nanodesk/__init__.py` 为准。

### 3. Git 标签

```bash
# 创建标签
git tag -a v0.2.1 -m "Release version 0.2.1"

# 推送标签到远程
git push origin v0.2.1
```

### 4. GitHub Release（可选）

在 GitHub 上创建 Release，关联标签 `v0.2.1`，上传打包文件。

---

## 版本更新检查清单

发布新版本前，确认以下事项：

- [ ] 更新 `nanodesk/__init__.py` 中的 `__version__`
- [ ] 更新 `nanodesk/desktop/__init__.py` 中的 `__version__`
- [ ] 更新 `nanodesk/README.md` 中的版本记录
- [ ] 更新 `nanodesk/docs/TODO.md` 中的版本记录
- [ ] 创建 Git 标签 `vX.Y.Z`
- [ ] 推送标签到 GitHub
- [ ] （可选）创建 GitHub Release
- [ ] （可选）上传打包文件到 Release

---

## 发布脚本

可以创建自动化脚本来简化版本发布：

```powershell
# scripts/release/release.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

# 验证版本号格式
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    Write-Error "Invalid version format. Use MAJOR.MINOR.PATCH (e.g., 0.2.0)"
    exit 1
}

# 更新版本号
$files = @(
    "nanodesk/__init__.py",
    "nanodesk/desktop/__init__.py"
)

foreach ($file in $files) {
    $content = Get-Content $file -Raw
    $content = $content -replace '__version__ = "[\d\.]+"', "__version__ = `"$Version`""
    Set-Content $file $content -NoNewline
    Write-Host "Updated $file"
}

# Git 提交
git add -A
git commit -m "release: bump version to $Version"

# 创建标签
git tag -a "v$Version" -m "Release version $Version"

Write-Host "Version $Version prepared. Run 'git push origin nanodesk --tags' to publish."
```

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| 0.2.0 | 2026-02-12 | Windows 桌面应用完成，支持嵌入 Python 打包 |
| 0.2.1 | 2026-02-13 | 脚本重构、测试套件、文档整合 |
| 0.1.0 | 2026-02-10 | 飞书通道验证，基础架构搭建 |

---

## 分支策略

- `main` 分支：跟踪上游，版本号跟随 nanobot
- `nanodesk` 分支：工作分支，独立版本号管理

发布桌面版时，以 `nanodesk` 分支为准。
