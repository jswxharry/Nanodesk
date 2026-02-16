# Nanodesk 配置指南

> 快速配置 Nanodesk 的完整指引

---

## 快速开始（5分钟）

### 第一步：选择部署方式

| 方式 | 特点 | 适合人群 |
|------|------|---------|
| **[Ollama 本地部署](./OLLAMA.md)** | 完全离线、数据私密 | 有本地 GPU/好 CPU、注重隐私 |
| **[云端 API](./CONFIGURATION.md)** | 速度快、免维护 | 有 API 额度、追求响应速度 |

### 第二步：配置通讯频道

| 频道 | 文档 | 特点 |
|------|------|------|
| **[飞书](./FEISHU.md)** | 国内用户首选，每月 10000 次免费额度 |
| **微信** | 待支持 |
| **Telegram** | 国际用户 |

---

## 配置清单

### 最小可用配置

```json
{
  "agents": {
    "defaults": {
      "model": "qwen2.5:3b",
      "provider": "ollama",
      "workspace": "C:\\Users\\你的用户名\\.nanobot\\workspace",
      "memoryWindow": 10
    }
  },
  "providers": {
    "ollama": {
      "apiKey": "not-needed",
      "apiBase": "http://localhost:11434"
    }
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxxxxxxx",
      "appSecret": "xxxxxxxx"
    }
  }
}
```

---

## 详细文档

| 文档 | 内容 |
|------|------|
| [OLLAMA.md](./OLLAMA.md) | Ollama 本地模型完整配置（安装、优化、故障排查） |
| [FEISHU.md](./FEISHU.md) | 飞书机器人配置（创建应用、权限、事件订阅） |
| [CONFIGURATION.md](./CONFIGURATION.md) | 通用配置说明（所有选项参考） |

---

## 常见问题速查

### 模型选择

| 需求 | 推荐模型 | 响应时间 | 说明 |
|------|---------|---------|------|
| 日常中文对话 | **qwen2.5:3b** | 15-40秒 | ⭐ 性价比首选 |
| 英文场景 | llama3.2:3b | 10-30秒 | 英文能力强 |
| 推理/编程 | deepseek-r1:1.5b | 5-15秒 | 速度快，推理强 |
| 快速响应 | dashscope/qwen-turbo | 1-3秒 | 需云端 API |

### 性能优化 checklist

- [ ] 设置 `OLLAMA_NUM_THREAD`（CPU 核心数的 75%）
- [ ] 设置 `OLLAMA_CONTEXT_LENGTH=2048`
- [ ] `memoryWindow` 设为 10
- [ ] 清空旧会话缓存

---

## 配置路径

Windows: `C:\Users\<用户名>\.nanobot\config.json`

---

**下一步**：选择上方的配置文档开始设置！
