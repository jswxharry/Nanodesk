# develop 分支测试计划

> 分支: develop  
> 版本: v0.2.1  
> 目标: 验证上游同步 + 新增工具 + 桌面应用功能

---

## 测试范围

### 上游 v0.1.3.post7 更新
- [ ] 内存系统 v2（双层架构 + grep 检索）
- [ ] `/new` 命令（跨频道统一）
- [ ] 内存整合功能
- [ ] 飞书卡片修复（Markdown 标题转 div）
- [ ] WhatsApp 安全修复（localhost 绑定）

### Nanodesk 新增功能
- [ ] DuckDuckGo 搜索工具（ddg_search）
- [ ] 浏览器搜索工具（browser_search）
- [ ] 浏览器抓取工具（browser_fetch）

### 桌面应用基础
- [ ] 配置向导
- [ ] Gateway 启停
- [ ] 日志查看
- [ ] 系统托盘

---

## 测试分工

| 类型 | 测试项 | 执行者 | 文档 |
|------|--------|--------|------|
| 自动化 | 代码检查、依赖验证、工具注册 | AI | [AI_CHECKLIST.md](./AI_CHECKLIST.md) |
| 手动 | GUI测试、飞书集成、对话评估 | 用户 | [MANUAL_CHECKLIST.md](./MANUAL_CHECKLIST.md) |

---

## 通过标准

- **P0（阻塞）**: 全部通过 - Gateway 启动、基础对话、工具注册
- **P1（重要）**: 允许 1-2 个非阻塞问题
- **P2（次要）**: 可记录为已知问题

**合并标准**: P0 全部通过，且无不阻塞的 P1 问题

---

## 测试环境

```powershell
# 前置检查
git checkout develop
git pull origin develop
pip install -e .
nanodesk --version  # 期望: v0.2.1
```

---

## 时间安排（建议）

| 阶段 | 内容 | 时间 | 执行者 |
|------|------|------|--------|
| 1 | AI 自动化检查 | 10 分钟 | AI |
| 2 | 桌面应用测试 | 30 分钟 | 用户 |
| 3 | 工具功能测试 | 30 分钟 | 用户 + AI |
| 4 | 飞书集成测试 | 30 分钟 | 用户 |
| 5 | 问题修复复测 | 按需 | 视情况 |

**总计**: 约 1.5-2 小时
