# Nanodesk 待办事项

> 记录项目待办功能和上游跟踪
> 
> 最后更新：2026-02-12

---

## 待办功能 📋

| 优先级 | 功能 | 状态 | 备注 |
|--------|------|------|------|
| ⭐⭐⭐ | **Windows 桌面版** | ✅ Phase 2 完成 | GUI + 配置向导 + 系统托盘 + 日志系统 |
| ⭐ | 飞书语音 | 🔄 回滚待审 | 需开通 `im:resource` 权限 |
| ⭐⭐ | Windows 截图工具 | 📋 待开发 | 飞书指令截图 |
| ⭐ | 本地文件管理 | 📋 待开发 | 读取本地文件 |
| ⭐ | 钉钉通道 | 📋 评估中 | 备选通道 |
| ⭐ | Discord | ❌ 搁置 | 需代理 |

**平台策略**: 专注 Windows 桌面版，覆盖 80% 普通用户。Linux/macOS 用户继续使用 CLI。

**上游跟踪**: [UPSTREAM_PRS.md](./UPSTREAM_PRS.md)
- 🔴 PR #257 - Token Usage Tracking
- 🔴 PR #171 - MCP Support  
- 🟡 PR #272 - Custom Provider

---

## 已完成 ✅

- [x] Nanodesk 基础架构（目录结构、VS Code、脚本）
- [x] 飞书通道（WebSocket、消息收发、Markdown）
- [x] 阿里云百炼 LLM 配置
- [x] 开发规范文档（AI_COLLABORATION.md、COMMIT_RULES.md）
- [x] 上游 PR 跟踪文档

---

## 快速参考

```powershell
# 启动 Gateway
nanodesk gateway --verbose

# 同步上游
.\nanodesk\scripts\sync-upstream.ps1

# 飞书指令
@机器人 你好    # 群聊
直接发消息      # 私聊
```

**文档索引**: [UPSTREAM_PRS.md](./UPSTREAM_PRS.md) | [FEISHU_SETUP.md](./FEISHU_SETUP.md) | [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 更新记录

| 日期 | 内容 |
|------|------|
| 2026-02-12 | 创建待办事项文档 |
| 2026-02-12 | 添加上游 PR 跟踪文档 |
