# Patches

存放必须修改 nanobot 核心代码时的补丁记录。

## 原则

**尽量避免直接修改 `nanobot/` 目录的文件！**

优先使用以下方式：
1. Monkey patch（运行时动态替换）
2. 继承扩展（继承原类添加功能）
3. 配置覆盖（通过配置文件修改行为）

## 如果必须修改核心代码

1. 在 `nanodesk` 分支修改 `nanobot/` 下的文件
2. 生成 patch 文件保存到这里：
   ```bash
   git diff nanobot/xxx.py > nanodesk/patches/001-description.patch
   ```
3. 提交 patch 文件到 git
4. 恢复 `nanobot/` 原文件，保持干净

## 应用补丁（可选）

如果需要在特定环境应用补丁，可以：

```python
# 在 bootstrap.py 中
import subprocess
from pathlib import Path

patches_dir = Path(__file__).parent / "patches"
for patch in patches_dir.glob("*.patch"):
    subprocess.run(["git", "apply", str(patch)], cwd=patches_dir.parent.parent)
```

## 更好的选择：提 PR

如果修改具有通用性，建议提取出来给原库提 PR，而不是用 patch。
