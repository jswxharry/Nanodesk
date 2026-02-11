# 语言策略设计（方案 D）

> 当前状态：已确定采用方案 D（中文为主 + 关键英文）
> 更新时间：2026-02-12
> 下次评审：当有国际用户提出需求时

## 策略概述

Nanodesk 采用**中文为主、关键英文**的混合策略，平衡个人使用舒适度与潜在国际化需求。

## 文件语言规范

### 中文文档（无需翻译）

| 目录/文件 | 说明 |
|----------|------|
| `nanodesk/docs/*.md` | 所有设计文档、开发指南、AI 提示词 |
| `nanodesk/README.md` | 项目说明（可添加顶部英文简介） |
| `nanodesk/scripts/*.ps1` | PowerShell 脚本注释（Windows 中文环境） |
| `nanodesk/scripts/*.sh` | Bash 脚本注释（保持英文，服务器通用） |
| `nanodesk/patches/README.md` | 补丁说明 |

### 必须英文（国际化惯例）

| 类型 | 说明 |
|------|------|
| **代码注释** | 所有 Python 代码的 docstring 和注释 |
| **变量/函数/类名** | 本来就是英文 |
| **Commit message** | 遵循 `feat:`, `fix:`, `docs:` 等英文惯例 |
| **配置文件** | `pyproject.toml`, `.json`, `.yaml` 等 |
| **API 接口** | 如果有对外暴露的接口 |

### 保持原样（上游文件）

| 文件 | 说明 |
|------|------|
| `README.md` (根目录) | nanobot 原库的英文 README，最小侵入 |
| `nanobot/` 下所有文件 | 上游代码，跟随上游语言 |
| `tests/` | 上游测试代码 |

## 代码注释示例

### ✅ 推荐（方案 D）

```python
# nanodesk/tools/my_tool.py

class MyTool(Tool):
    """Personal screenshot tool for Windows desktop.
    
    This tool captures screenshots using Windows-specific APIs.
    For cross-platform screenshot, consider using PIL or mss.
    
    Note: This is a personal customization, not intended for upstream.
    """
    
    @property
    def name(self) -> str:
        return "windows_screenshot"
    
    async def execute(self, **kwargs) -> str:
        # Windows-specific implementation
        # Uses PowerShell for better compatibility
        pass
```

### ❌ 避免

```python
class MyTool(Tool):
    """个人截图工具
    
    这个工具使用 Windows 特有的 API 截图。
    """
    # 这样写如果提 PR 给上游需要重写注释
```

## 未来国际化路线图

### 触发条件（满足任一即启动）

1. 有非中文母语用户提交 Issue 或 PR
2. GitHub 上收到 "Please add English docs" 请求
3. 准备向更广泛的国际社区推广
4. 项目 Star 数超过 500（自然增长带来的国际关注）

### 实施方案（届时讨论）

方案 A：双语并排
```
nanodesk/docs/
├── AI_GUIDELINES.zh.md
├── AI_GUIDELINES.en.md
└── README.md  # 导航页
```

方案 B：英文为主，中文辅助
- 将主要文档翻译为英文
- 中文文档移至 `docs/zh/`

方案 C：AI 翻译 + 人工校对
- 使用 Claude/GPT 自动翻译
- 人工校对关键术语

## 当前例外情况

以下情况可暂时打破规范：

1. **快速原型**：实验性功能先用中文注释，稳定后改写英文
2. **个人笔记**：`TODO:`, `FIXME:` 等提醒自己可用中文
3. **复杂逻辑**：非明显逻辑的中文解释可保留，同时加英文摘要

## 检查清单

提交代码前自检：

- [ ] 新代码的 docstring 是英文
- [ ] 复杂逻辑有英文注释说明
- [ ] 个人定制用 `custom:` 前缀标明
- [ ] 考虑贡献给上游的代码注释更详细

## 参考

- [Python PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- 其他个人 fork 项目（如 oh-my-zsh 的定制主题）

---

**决策记录**:
- 2026-02-12: 确定采用方案 D（中文为主 + 关键英文）
- 下次评审: 当有国际用户提出需求时
