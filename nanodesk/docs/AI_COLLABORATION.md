# AI 协作指南

> 本文档面向 AI 编程助手，指导如何与 Nanodesk 项目协作。

---

## 一、核心原则

### 1.1 Git 操作必须经用户确认 ⚠️

**禁止**：
- ❌ 自动 `git commit` 而不告知用户
- ❌ 自动 `git push` 到远端
- ❌ 批量提交未审核的改动

**正确流程**：
1. AI 完成代码修改
2. AI 展示改动内容
3. 用户审核确认
4. AI 执行：git add → git commit → git push

### 1.2 代码位置决策

> **"这段代码对原库的其他用户也有用吗？"**

| 答案 | 位置 | 后续操作 |
|------|------|---------|
| **是** | `nanobot/` | 用 `feat:`/`fix:` 提交，考虑提 PR |
| **否** | `nanodesk/` | 用 `custom:` 提交 |

**快速判断**：
- ✅ `nanobot/` - Bug 修复、通用功能、性能优化
- ✅ `nanodesk/` - Windows 特定功能、个人工作流、实验性代码

详细判断标准参见 [CODE_LOCATION.md](./CODE_LOCATION.md)。

---

## 二、提交规范

**详见**：[COMMIT_RULES.md](./COMMIT_RULES.md)

**常用前缀**：
| 前缀 | 用途 | 示例 |
|------|------|------|
| `custom:` | 个人定制（`nanodesk/`） | `custom: add screenshot tool` |
| `feat:` | 通用功能（`nanobot/`） | `feat: add Discord channel` |
| `fix:` | Bug 修复 | `fix: handle timeout` |
| `docs:` | 文档改进 | `docs: update README` |
| `sync:` | 同步上游 | `sync: merge upstream` |

---

## 三、Git 工作流

**分支策略详见**：[BRANCHING.md](./BRANCHING.md)

**同步上游**：
```bash
# 使用脚本（推荐）
.\nanodesk\scripts\sync-upstream.ps1
```

**提取贡献**：
```bash
.\nanodesk\scripts\extract-contrib.ps1 <commit-hash>
```

---

## 四、项目结构

```
Nanodesk/
├── nanobot/                 # 📦 原库代码（跟踪上游）
├── nanodesk/                # 🔥 你的定制
│   ├── channels/            # 自定义频道
│   ├── tools/               # 自定义工具
│   ├── skills/              # 自定义技能
│   └── docs/                # 本文档
├── .vscode/                 # VS Code 配置
└── .kimi/                   # Kimi Code 配置
```

---

## 五、开发规范

### 5.1 路径处理（跨平台）

```python
# ✅ 正确
from pathlib import Path
config_path = Path.home() / ".nanobot" / "config.json"

# ❌ 错误
config_path = "~/.nanobot/config.json"
```

### 5.2 类型注解

```python
# Python 3.11+ 语法
def process(text: str | None) -> list[str]:
    ...
```

---

## 六、注意事项

**禁止**：
- ❌ 硬编码个人敏感信息
- ❌ 未经用户确认执行 Git 操作

**推荐**：
- ✅ 使用配置而非硬编码
- ✅ 不确定时优先放 `nanodesk/`
- ✅ 定期同步上游

---

## 参考

- [BRANCHING.md](./BRANCHING.md) - Git 分支管理
- [COMMIT_RULES.md](./COMMIT_RULES.md) - 提交规范
- [CODE_LOCATION.md](./CODE_LOCATION.md) - 代码归属判断
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 项目架构
