# Nanodesk + Ollama + Qwen2.5 本地部署指南

> 本指南帮助你在 Windows 上完全离线部署 Nanodesk，使用 Ollama 运行阿里通义千问 Qwen2.5 模型。

---

## 目录

1. [方案概述](#1-方案概述)
2. [安装 Ollama](#2-安装-ollama)
3. [下载 Qwen2.5 模型](#3-下载-qwen25-模型)
4. [配置 Nanodesk 使用本地模型](#4-配置-nanodesk-使用本地模型)
5. [完全离线使用](#5-完全离线使用)
6. [性能优化](#6-性能优化)
7. [常见问题](#7-常见问题)

---

## 1. 方案概述

### 为什么选择这个组合？

| 组件 | 作用 | 优势 |
|------|------|------|
| **Nanodesk** | AI 助手框架 | 轻量、本地优先、支持多通道 |
| **Ollama** | 本地 LLM 运行环境 | 简单易用、API 兼容 OpenAI |
| **Qwen2.5** | 阿里开源大模型 | 中文最强、开源可商用 |

### 硬件要求与模型选择

| 配置 | 推荐模型 | 响应时间 | 适用场景 |
|------|---------|---------|---------|
| 8GB 内存 | **Qwen2.5:3b** (1.9GB) | 15-40秒 | ⭐ **性价比首选** |
| 16GB 内存 | Qwen2.5:7b (4.7GB) | 60-120秒 | 质量优先 |
| 32GB 内存 | Qwen2.5:14b (9GB) | 较慢 | 接近 GPT-3.5 |

> 💡 **强烈推荐**: **Qwen2.5:3b** 是 Nanodesk + Ollama 的最佳搭配
> - 中文能力强，日常对话完全够用
> - 响应速度可接受（15-40秒）
> - 内存占用低，16GB 机器运行流畅
> 
> ⚠️ **不推荐 7B**: 虽然质量更好，但响应太慢（60-120秒），日常体验不佳

---

## 2. 安装 Ollama

> 📖 **详细安装指南**：参见 [OLLAMA_INSTALL.md](./OLLAMA_INSTALL.md) - 包含 Windows 安装、D 盘迁移、国内镜像加速等详细步骤。

### 2.1 下载安装

#### 方式一：国内镜像下载（推荐）

```powershell
# PowerShell 一键下载并安装
Invoke-WebRequest -Uri "https://cnb.cool/hex/ollama/-/releases/latest/download/OllamaSetup.exe" -OutFile "OllamaSetup.exe"
Start-Process "OllamaSetup.exe"
```

#### 方式二：官方下载

访问 https://ollama.com/download 下载 `OllamaSetup.exe`

### 2.2 安装到 D 盘（解决 C 盘空间不足）

Ollama 默认安装到 C 盘，模型也会存到 C 盘。以下步骤将其迁移到 D 盘：

**步骤 1：创建 D 盘目录**

```powershell
# 创建程序目录
mkdir D:\Programs\Ollama

# 创建模型存储目录  
mkdir D:\OllamaModels
```

**步骤 2：创建符号链接（管理员 PowerShell）**

```powershell
# 将 Harry 替换为你的 Windows 用户名
$username = "Harry"

# 创建程序目录联接
cmd /c mklink /J "C:\Users\$username\AppData\Local\Programs\Ollama" "D:\Programs\Ollama"

# 创建模型目录联接
cmd /c mklink /J "C:\Users\$username\.ollama" "D:\OllamaModels"
```

**步骤 3：运行安装程序**

现在运行 `OllamaSetup.exe`，程序会自动安装到 D 盘。

### 2.3 验证安装

```powershell
ollama --version
# 应显示版本号，如：ollama version 0.5.7
```

---

## 3. 下载 Qwen2.5 模型

### 3.1 下载 Qwen2.5 模型

Ollama 官方下载速度良好，直接使用官方命令即可：

```powershell
# 下载 Qwen2.5-7B（推荐，约 4.7GB）
ollama pull qwen2.5:7b

# 或下载 Qwen2.5-3B（轻量版，约 1.9GB，适合 8GB 内存）
ollama pull qwen2.5:3b

# 下载最新版（默认 7B）
ollama pull qwen2.5:latest
```

> 💡 **提示**：如果下载中断，重新运行命令会继续下载（支持断点续传）。

### 3.3 验证模型

```powershell
# 查看已下载的模型
ollama list

# 测试运行
ollama run qwen2.5:latest

# 输入测试问题："你好，请介绍一下自己"
# 按 Ctrl+D 或输入 /bye 退出
```

---

## 4. 配置 Nanodesk 使用本地模型

### 4.1 获取 Ollama API 地址

Ollama 默认在本地启动 API 服务：

```
http://localhost:11434
```

验证服务是否运行：

```powershell
# 查看 Ollama 进程
Get-Process ollama

# 测试 API
curl http://localhost:11434/api/tags
```

### 4.2 修改 Nanodesk 配置文件

编辑 `~/.nanobot/config.json`（即 `C:\Users\你的用户名\.nanobot\config.json`）：

#### 推荐配置（Qwen2.5:3b + 优化）

```json
{
  "agents": {
    "defaults": {
      "model": "qwen2.5:3b",
      "provider": "ollama",
      "workspace": "C:\\Users\\Harry\\nanodesk_workspace",
      "memoryWindow": 10,
      "maxTokens": 2048,
      "temperature": 0.7
    }
  },
  "providers": {
    "ollama": {
      "apiKey": "not-needed",
      "apiBase": "http://localhost:11434"
    },
    "dashscope": {
      "apiKey": ""
    }
  },
  "channels": {
    "cli": {
      "enabled": true
    }
  },
  "gateway": {
    "host": "127.0.0.1",
    "port": 18790
  },
  "tools": {
    "web": {
      "search": {
        "enabled": false
      }
    },
    "exec": {
      "timeout": 60
    }
  }
}
```

**关键配置说明**：

| 配置项 | 说明 |
|--------|------|
| `agents.defaults.model` | **推荐 `qwen2.5:3b`**（速度快，中文好） |
| `agents.defaults.provider` | 必须设置为 `"ollama"` |
| `agents.defaults.memoryWindow` | **建议设为 10**（减少历史消息，提速 30%） |
| `agents.defaults.maxTokens` | **建议 2048**（3B 模型生成 4K 很慢） |
| `providers.ollama.apiBase` | `http://localhost:11434` |
| `providers.ollama.apiKey` | 本地运行随意填写，如 `not-needed` |
| `providers.dashscope.apiKey` | **必须清空 `""`**，否则可能冲突 |

> ⚠️ **重要**：
> 1. **必须清空 `dashscope.apiKey`**，否则 `qwen` 模型名会自动匹配到 DashScope
> 2. **环境变量优化**（必须重启 Ollama 生效）：
>    ```powershell
>    [Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREAD", "12", "Machine")
>    [Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "2048", "Machine")
>    ```
> 
> 💡 **注意**：Nanodesk 已内置 Ollama provider 支持，无需再使用 `custom` provider。上游 nanobot 合并 PR #133 后，可无缝切换到上游实现。

### 4.3 启动 Nanodesk

```powershell
# 方式一：命令行交互模式
nanodesk agent

# 方式二：启动网关（支持多通道）
nanodesk gateway
```

### 4.4 验证配置

在 Nanodesk 中输入：

```
你好，请介绍一下自己
```

如果看到 Qwen2.5 的回复，说明配置成功！

---

## 5. 完全离线使用

### 5.1 断网测试

1. 断开网络连接（关闭 WiFi / 拔掉网线）
2. 确保 Ollama 正在运行
3. 启动 Nanodesk
4. 正常对话测试

### 5.2 离线场景支持的功能

| 功能 | 支持情况 | 说明 |
|------|---------|------|
| AI 对话 | ✅ 完全支持 | 基于本地 Qwen2.5 |
| 文件操作 | ✅ 完全支持 | 读写本地文件 |
| Shell 命令 | ✅ 完全支持 | 执行本地命令 |
| 代码编辑 | ✅ 完全支持 | 代码生成、修改 |
| 网络搜索 | ❌ 不可用 | 需要联网 |
| 网页获取 | ❌ 不可用 | 需要联网 |

### 5.3 创建离线工作流

```powershell
# 1. 启动 Ollama（手动或开机自启）
ollama serve

# 2. 启动 Nanodesk Gateway（支持飞书/微信等通道）
nanodesk gateway

# 3. 所有对话完全离线进行
```

---

## 6. 性能优化

### 6.1 CPU 优化配置（无独立显卡）

#### 核心优化项

```powershell
# 1. 设置 CPU 线程数（推荐设为 CPU 核心数的 75%，如 16 核设 12）
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREAD", "12", "Machine)

# 2. 减少上下文长度（日常对话 2048 够用，1024 更快）
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "2048", "Machine")

# 3. 重启 Ollama 使配置生效
Stop-Process -Name ollama -Force
ollama serve
```

#### 配置验证

```powershell
# 检查环境变量是否生效
[Environment]::GetEnvironmentVariable("OLLAMA_NUM_THREAD", "Machine")

# 测试速度
ollama run qwen2.5:3b
>>> 你好
# 观察首字响应时间（优化后应在 5-15 秒）
```

### 6.2 创建优化版模型

创建 `Modelfile` 文件：

```dockerfile
FROM qwen2.5:latest

# 系统提示词 - 设定 AI 助手角色
SYSTEM """你是一个专业的个人 AI 助手，擅长编程、写作和日常任务处理。
回答简洁实用，优先给出可操作的解决方案。"""

# 参数优化
PARAMETER num_ctx 8192        # 上下文长度
PARAMETER num_thread 8        # CPU 线程数
PARAMETER temperature 0.7     # 创造性（0-1，越低越确定）
PARAMETER top_p 0.9           # 采样多样性
PARAMETER repeat_penalty 1.1  # 重复惩罚
```

创建并运行优化模型：

```powershell
# 创建自定义模型
ollama create nanodesk-qwen -f Modelfile

# 使用优化模型
ollama run nanodesk-qwen
```

更新 Nanodesk 配置使用新模型：

```json
{
  "agents": {
    "defaults": {
      "model": "nanodesk-qwen",
      "provider": "ollama"
    }
  }
}
```

### 6.3 内存优化建议

| 内存大小 | 推荐模型 | 上下文长度 |
|---------|---------|-----------|
| 8GB | qwen2.5:3b | 4096 |
| 16GB | qwen2.5:latest (7b) | 8192 |
| 32GB | qwen2.5:14b | 16384 |

### 6.4 实测速度对比（16核CPU + 16GB内存）

| 模型 | 优化配置 | 首字响应 | 总耗时 | 质量 | 推荐度 |
|------|---------|---------|--------|------|--------|
| **Qwen2.5:3b** | 12线程 + 2K上下文 | 8-15秒 | **15-40秒** | ⭐⭐⭐ | ✅ **首选** |
| Qwen2.5:3b | 默认4线程 | 20-30秒 | 60+秒 | ⭐⭐⭐ | ❌ 慢 |
| Qwen2.5:7b | 12线程 | 30-50秒 | 60-120秒 | ⭐⭐⭐⭐⭐ | ❌ 太慢 |
| Qwen2.5:7b | 默认4线程 | 60+秒 | 120+秒 | ⭐⭐⭐⭐⭐ | ❌ 不可用 |

#### 优化效果总结

**优化前 vs 优化后**（Qwen2.5:3b）：
- 响应时间：60秒 → **40秒**（提升 33%）
- 关键优化：
  1. `OLLAMA_NUM_THREAD=12`（按CPU核心数75%设置）
  2. `memoryWindow: 10`（减少历史消息处理）
  3. 清空旧会话缓存

**7B 模型测试结论**：
- 即使 16 核 + 12 线程优化，响应仍需 60-120 秒
- 不建议日常使用，仅适合不赶时间的深度任务

---

## 7. 常见问题

### Q1: Nanodesk 无法连接到 Ollama？

**检查步骤**：

```powershell
# 1. 确认 Ollama 正在运行
Get-Process ollama

# 2. 确认 API 可访问
curl http://localhost:11434/api/tags

# 3. 检查配置文件中的 apiBase 是否正确
# 应该是 "http://localhost:11434" 不是 "https"
```

### Q2: 配置正确但仍请求发送到 Dashscope/阿里云？

**症状**：日志显示请求发送到 `dashscope.aliyuncs.com`，错误信息：
```
The model `qwen2.5:latest` does not exist or you do not have access to it.
```

**原因**：如果没有使用 Nanodesk 的 Ollama provider，nanobot 的 provider 匹配逻辑会优先检查**模型名关键字**。只要模型名包含 `qwen` 且 `dashscope.api_key` 不为空，就会强制使用 DashScope。

**解决方案**：

使用 Nanodesk 内置的 Ollama provider（推荐）：
```json
{
  "agents": {
    "defaults": {
      "model": "qwen2.5:latest",
      "provider": "ollama"
    }
  },
  "providers": {
    "ollama": {
      "apiKey": "not-needed",
      "apiBase": "http://localhost:11434"
    }
  }
}
```

或者清空 DashScope 的 API key：
```json
"dashscope": {
  "apiKey": ""
}
```

然后重启 Nanodesk Gateway：
```powershell
Stop-Process -Name nanodesk -Force
nanodesk gateway
```

### Q3: 模型响应很慢？

**解决方案**：

1. **启用多线程**：
```powershell
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREAD", "8", "Machine")
```

2. **使用更小的模型**：
```powershell
ollama pull qwen2.5:3b  # 切换到 3B 版本
```

3. **检查电源模式**：
   - 控制面板 → 电源选项 → 选择"高性能"

### Q4: 如何同时支持多个模型？

模型存储在 Ollama 中，只需修改 `model` 即可切换：

```json
{
  "agents": {
    "defaults": {
      "model": "qwen2.5:3b",
      "provider": "ollama"
    }
  },
  "providers": {
    "ollama": {
      "apiKey": "not-needed",
      "apiBase": "http://localhost:11434"
    }
  }
}
```

运行时在对话中切换：

```
/model qwen2.5:3b      # 切换到轻量版
/model deepseek-r1:7b  # 切换到 DeepSeek
/model llama3.2        # 切换到 Llama
```

> 💡 **前提**：这些模型需要先用 `ollama pull` 下载到本地。

### Q5: 模型存储位置如何更改？

如果之前没创建符号链接，可以迁移：

```powershell
# 1. 停止 Ollama
Stop-Process -Name ollama -Force

# 2. 移动模型文件
robocopy "C:\Users\$env:USERNAME\.ollama\models" "D:\OllamaModels\models" /E /MOVE

# 3. 创建符号链接
cmd /c mklink /J "C:\Users\$env:USERNAME\.ollama" "D:\OllamaModels"

# 4. 重启 Ollama
ollama serve
```

### Q6: 如何查看模型下载进度？

```powershell
# 下载时显示进度
ollama pull qwen2.5:latest

# 如果卡住，按 Ctrl+C 取消后重新运行（支持断点续传）
ollama pull qwen2.5:latest
```

### Q7: 完全卸载 Ollama

```powershell
# 1. 停止服务
Stop-Process -Name ollama -Force

# 2. 卸载程序
# 设置 → 应用 → 卸载 Ollama

# 3. 删除模型文件
Remove-Item -Path "D:\OllamaModels" -Recurse -Force

# 4. 删除符号链接（如创建了）
Remove-Item -Path "C:\Users\$env:USERNAME\.ollama" -Force
```

---

## 参考资源

- [Ollama 官方文档](https://github.com/ollama/ollama)
- [Qwen2.5 模型介绍](https://github.com/QwenLM/Qwen2.5)
- [Nanodesk 配置指南](./CONFIGURATION.md)
- [Ollama Windows 详细安装指南](./OllamaWindowsSetup.md)

---

**最后更新**：2026年2月16日

**适用版本**：
- Nanodesk ≥ 0.1.0
- Ollama ≥ 0.5.0
- Qwen2.5 (all variants)
