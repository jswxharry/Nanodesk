# Nanodesk 待办事项

> 记录进行中的任务和待办功能
> 
> 最后更新：2026-02-13
> 
> 📜 **历史记录**: [CHANGELOG.md](./CHANGELOG.md)

---

## 待办功能 📋

| 优先级 | 功能 | 状态 | 备注 |
|--------|------|------|------|
| ⭐⭐ | Windows 截图工具 | 📋 待开发 | 飞书指令截图 |
| ⭐ | 本地文件管理 | 📋 待开发 | 读取本地文件 |
| ⭐ | 钉钉通道 | 📋 评估中 | 备选通道 |
| ⭐ | Discord | ❌ 搁置 | 需代理 |
| ⭐ | 飞书语音 | 🔄 回滚待审 | 需开通 `im:resource` 权限 |

---

## 测试任务 🧪

- [ ] **搜索工具测试** - ddg_search, browser_search, browser_fetch
- [ ] **上游 v0.1.3.post7 测试** - 内存系统 v2、`/new` 命令、飞书修复
- [ ] 确认无误后合并 `develop` → `nanodesk`

---

## 上游跟踪 🔗

详见 [UPSTREAM_PRS.md](./UPSTREAM_PRS.md)

| PR | 功能 | 优先级 |
|----|------|--------|
| #257 | Token Usage Tracking | 🔴 高 |
| #171 | MCP Support | 🔴 高 |
| #272 | Custom Provider | 🟡 中 |

---

## 快速参考

```powershell
# 运行测试
.\nanodesk\scripts\run_tests.ps1          # 完整测试
.\nanodesk\scripts\run_tests_quick.ps1    # 快速测试

# 启动桌面应用（开发模式）
.\nanodesk\scripts\run_desktop.ps1

# 启动 Gateway
nanodesk gateway --verbose

# 同步上游
.\nanodesk\scripts\sync-upstream.ps1
```

---

## 文档索引

- [README.md](./README.md) - 文档总索引
- [CHANGELOG.md](./CHANGELOG.md) - 版本历史
- [BRANCHING.md](./BRANCHING.md) - Git 分支管理
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 开发者指南
- [UPSTREAM_PRS.md](./UPSTREAM_PRS.md) - 上游 PR 跟踪
- [BUILD.md](./BUILD.md) - 构建指南
- [testing/](./testing/) - 测试文档
