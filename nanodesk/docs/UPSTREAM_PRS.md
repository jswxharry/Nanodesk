# Nanobot 上游 PR 跟踪与评估

> 跟踪 HKUDS/nanobot 原库的重要 PR，评估对 Nanodesk 的价值和合并优先级
> 
> 最后更新：2026-02-12

---

## 已同步更新 ✅

### 2026-02-12 同步批次

本次同步合并了 upstream/main 的 6 个新提交：

| PR | 功能 | 影响文件 | 状态 |
|----|------|---------|------|
| #538 | 交织链式思考 (Interleaved CoT) | `agent/loop.py` | ✅ 已同步 |
| #533 | Cron 一次性定时任务 (`at` 参数) | `agent/tools/cron.py`, `skills/cron/SKILL.md` | ✅ 已同步 |
| #543 | 子代理增强 (edit_file + 时间上下文) | `agent/subagent.py`, `agent/context.py` | ✅ 已同步 |

**详细变更**：
1. **交织链式思考**: 每次工具调用后添加反思提示 `"Reflect on the results and decide next steps."`，提升 Agent 推理能力
2. **Cron 一次性任务**: 新增 `at` 参数支持 ISO 格式时间（如 `2026-02-12T10:30:00`），执行后自动删除
3. **子代理增强**: 
   - 添加 `EditFileTool` 到子代理工具集
   - 系统提示增加当前时间和时区信息
   - 提示技能目录位置 `workspace/skills/`

---

## 高价值 PR ⭐⭐⭐（推荐优先关注）

### PR #257 - Token Usage Tracking & Budget Monitoring
| 属性 | 内容 |
|------|------|
| **链接** | https://github.com/HKUDS/nanobot/pull/257 |
| **状态** | Open |
| **功能** | 全面的 Token 使用量追踪和预算监控 |

**包含功能**：
- ✅ `UsageTracker` - 记录 LLM API 消耗（每日 JSON 存储）
- ✅ `UsageMonitor` - 月度预算和告警阈值
- ✅ `nanobot usage` CLI 命令 - 日/周/月统计
- ✅ `UsageTool` - Agent 自我感知 token 消耗
- ✅ Ollama Provider 支持（本地 LLM）
- ✅ NVIDIA Provider 支持
- ✅ Shell 安全加固（命令黑名单、目录限制）
- ✅ Alarm 工具（定时提醒）

**对 Nanodesk 价值**：⭐⭐⭐⭐⭐
- 解决了我们之前想自行实现的功能
- 包含 Ollama 本地模型支持（隐私+省钱）
- Shell 安全加固提升生产环境安全性

**跟进策略**：等待合并，合并后立即同步

---

### PR #171 - MCP (Model Context Protocol) Support
| 属性 | 内容 |
|------|------|
| **链接** | https://github.com/HKUDS/nanobot/pull/171 |
| **状态** | Open |
| **功能** | MCP 客户端完整实现 |

**包含功能**：
- ✅ Stdio Transport（本地 MCP 服务器）
- ✅ SSE Transport（远程 HTTP MCP 服务器）
- ✅ 自动工具发现和注册
- ✅ 工具名前缀（`mcp_`）避免冲突
- ✅ 安全加固（命令白名单、SSRF 防护、路径遍历防护）
- ✅ `nanobot mcp test` CLI 命令

**对 Nanodesk 价值**：⭐⭐⭐⭐⭐
- MCP 是 AI 工具生态的标准协议
- 可连接大量现成的 MCP 工具（文件系统、搜索、数据库等）
- 比自行开发工具更高效

**跟进策略**：高优先级，合并后评估是否需要调整自定义工具

---

### PR #272 - Custom Provider (OpenAI-compatible)
| 属性 | 内容 |
|------|------|
| **链接** | https://github.com/HKUDS/nanobot/pull/272 |
| **状态** | Open |
| **功能** | 自定义 OpenAI 兼容 Provider |

**包含功能**：
- ✅ 支持任意自定义 Provider ID
- ✅ 配置 apiKey + apiBase
- ✅ 模型名格式：`{provider_id}/{model_name}`
- ✅ 绕过复杂的 LiteLLM 前缀逻辑

**适用场景**：
- NanoGPT
- NVIDIA API
- Z.ai Coding Plan
- 其他 OpenAI 兼容服务

**对 Nanodesk 价值**：⭐⭐⭐⭐
- 我们已有智谱 AI 配置，此 PR 可能更通用
- 需要评估是否替换现有方案

**跟进策略**：合并后测试是否可替代现有自定义配置

---

## 中等价值 PR ⭐⭐（值得关注）

### PR #339 - Window Protocol Channel
| 属性 | 内容 |
|------|------|
| **链接** | https://github.com/HKUDS/nanobot/pull/339 |
| **状态** | Open |
| **功能** | HTTP + WebSocket 服务器 + iOS 客户端 |

**包含功能**：
- ✅ Window Protocol 通道
- ✅ 实时任务进度卡片
- ✅ `window_task` 工具
- ✅ 实时 Token 追踪
- ✅ 配套 iOS App

**对 Nanodesk 价值**：⭐⭐⭐
- 有 iOS 客户端是亮点
- 但我们主要用飞书，需求不强烈
- 实时 token 追踪在 #257 也有

**跟进策略**：低优先级，可选功能

---

### PR #154 - Docker + MCP + Feishu
| 属性 | 内容 |
|------|------|
| **链接** | https://github.com/HKUDS/nanobot/pull/154 |
| **状态** | Open |
| **功能** | Docker 多实例 + MCP + 飞书集成 |

**包含功能**：
- ✅ Docker 多实例部署（共享 venv，节省 337MB/实例）
- ✅ MCP 客户端支持（HTTP + Stdio）
- ✅ 飞书机器人完整集成

**对 Nanodesk 价值**：⭐⭐⭐
- Docker 多实例对我们个人使用价值不大
- MCP 功能已被 #171 覆盖
- 飞书功能我们已有

**跟进策略**：关注飞书实现是否有改进，其他部分可跳过

---

## 已覆盖/低价值 PR ⭐（无需关注）

### PR #94 - Feishu + MiniMax
| 属性 | 内容 |
|------|------|
| **链接** | https://github.com/HKUDS/nanobot/pull/94 |
| **状态** | Open |
| **功能** | 飞书 WebSocket 通道 + MiniMax Provider |

**评估**：
- 飞书功能 Nanodesk 已实现 ✅
- MiniMax Provider 国内使用较少

**跟进策略**：无需跟进

---

### PR #328 - Zhipu AI (智谱)
| 属性 | 内容 |
|------|------|
| **链接** | https://github.com/HKUDS/nanobot/pull/328 |
| **状态** | Open |
| **功能** | 智谱 AI Coding Plan 支持 |

**评估**：
- 使用自定义 Provider 方式配置
- 可被 #272 通用方案替代

**跟进策略**：等待 #272，更具通用性

---

### PR #126 - Docker GitHub Actions
| 属性 | 内容 |
|------|------|
| **链接** | https://github.com/HKUDS/nanobot/pull/126 |
| **状态** | Open |
| **功能** | GitHub Actions 自动构建 Docker 镜像 |

**评估**：
- 对上游项目有用
- 对个人使用 Nanodesk 价值不大

**跟进策略**：无需关注

---

## 优先级矩阵

```
高价值 + 即将合并  →  立即关注
高价值 + 长期开放  →  定期查看
中等价值          →  合并后评估
低价值            →  忽略
```

| PR | 价值 | 状态 | 优先级 | 行动 |
|----|------|------|--------|------|
| #257 | ⭐⭐⭐⭐⭐ | Open | 🔴 高 | 等待合并，立即同步 |
| #171 | ⭐⭐⭐⭐⭐ | Open | 🔴 高 | 等待合并，评估工具迁移 |
| #272 | ⭐⭐⭐⭐ | Open | 🟡 中 | 合并后测试替代现有方案 |
| #339 | ⭐⭐⭐ | Open | 🟢 低 | 可选功能 |
| #154 | ⭐⭐⭐ | Open | 🟢 低 | 被 #171 覆盖 |
| #94 | ⭐⭐ | Open | ⚪ 无 | 已有实现 |
| #328 | ⭐⭐ | Open | ⚪ 无 | 被 #272 覆盖 |
| #126 | ⭐ | Open | ⚪ 无 | 无需关注 |

---

## 跟进流程

### 每周检查
```bash
# 查看 PR 状态更新
open https://github.com/HKUDS/nanobot/pulls

# 同步上游时检查
./nanodesk/scripts/sync-upstream.ps1
```

### 当高优先级 PR 合并时
1. 立即运行 `sync-upstream.ps1`
2. 阅读 PR 详细文档
3. 更新本地配置
4. 测试功能是否正常
5. 更新 Nanodesk 文档

### 已知冲突预案
| PR | 潜在冲突 | 解决方案 |
|----|---------|---------|
| #257 | 我们曾自行实现 api_usage | 已删除，无冲突 |
| #171 | 可能与我们自定义工具重复 | 评估后迁移到 MCP |
| #272 | 智谱配置方式可能不同 | 按新格式重新配置 |

---

## 相关资源

- **nanobot PR 列表**: https://github.com/HKUDS/nanobot/pulls
- **MCP 官方**: https://modelcontextprotocol.io
- **MCP 服务器示例**: https://github.com/modelcontextprotocol/servers
