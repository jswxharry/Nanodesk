# Nanodesk 配置指南

运行 Nanodesk 前需要完成基本配置。

## 快速开始

```powershell
# 1. 安装项目
pip install -e .

# 2. 初始化配置（交互式向导）
nanodesk onboard

# 3. 启动
nanodesk agent
```

## 配置文件位置

```
Windows: C:\Users\<用户名>\.nanobot\config.json
Linux/Mac: ~/.nanobot/config.json
```

## 必需配置

### 1. LLM API 密钥（必须）

至少需要一个 LLM 提供商的 API 密钥：

```json
{
  "providers": {
    "openai": {
      "api_key": "sk-xxxxxxxx"
    },
    "anthropic": {
      "api_key": "sk-ant-xxxxxxxx"
    },
    "deepseek": {
      "api_key": "sk-xxxxxxxx"
    }
  }
}
```

支持的提供商：OpenAI, Anthropic, DeepSeek, Groq, OpenRouter, Moonshot, Gemini, 通义千问, etc.

**获取 API Key:**
- [OpenAI](https://platform.openai.com/api-keys)
- [Anthropic](https://console.anthropic.com/)
- [DeepSeek](https://platform.deepseek.com/)
- [Moonshot](https://platform.moonshot.cn/)

### 2. 默认模型（可选）

```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "max_tokens": 8192,
      "temperature": 0.7
    }
  }
}
```

模型名称格式：`提供商/模型名`，如：
- `anthropic/claude-opus-4-5`
- `openai/gpt-4o`
- `deepseek/deepseek-chat`
- `moonshot/kimi-latest`

## 可选配置

### 频道配置（如需接收消息）

#### Telegram（最简单）

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    }
  }
}
```

获取 Token：[@BotFather](https://t.me/botfather)

#### 飞书

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "app_id": "cli_xxxxxxxx",
      "app_secret": "xxxxxxxx"
    }
  }
}
```

#### Discord

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "MTIxxxxxxxxxxxxxxxx.xxxxxx.xxxxxx"
    }
  }
}
```

### 工具配置

#### 网页搜索（Brave）

```json
{
  "tools": {
    "web": {
      "search": {
        "api_key": "BSxxxxxxxx",
        "max_results": 5
      }
    }
  }
}
```

获取：[Brave Search API](https://brave.com/search/api/)

#### 安全设置

```json
{
  "tools": {
    "exec": {
      "timeout": 60
    },
    "restrict_to_workspace": true
  }
}
```

- `restrict_to_workspace`: 限制文件操作在工作目录内

### 工作空间路径

```json
{
  "agents": {
    "defaults": {
      "workspace": "D:/Nanodesk/workspace"
    }
  }
}
```

## 完整配置示例

```json
{
  "agents": {
    "defaults": {
      "workspace": "D:/Nanodesk/workspace",
      "model": "deepseek/deepseek-chat",
      "max_tokens": 8192,
      "temperature": 0.7
    }
  },
  "providers": {
    "deepseek": {
      "api_key": "sk-xxxxxxxxxxxxxxxx"
    }
  },
  "channels": {
    "telegram": {
      "enabled": false,
      "token": ""
    }
  },
  "tools": {
    "web": {
      "search": {
        "api_key": "",
        "max_results": 5
      }
    },
    "exec": {
      "timeout": 60
    },
    "restrict_to_workspace": true
  }
}
```

## 环境变量方式

也可以用环境变量配置（优先级高于配置文件）：

```powershell
# PowerShell
$env:NANOBOT_PROVIDERS__DEEPSEEK__API_KEY = "sk-xxxxxxxx"
$env:NANOBOT_AGENTS__DEFAULTS__MODEL = "deepseek/deepseek-chat"

nanodesk agent
```

## 验证配置

```powershell
# 查看配置状态
nanodesk status

# 测试模型连接
nanodesk agent
# 输入: 你好
```

## 常见问题

**Q: 报错 "No API key provided"**
- 检查 `config.json` 中对应提供商的 `api_key`
- 或设置环境变量

**Q: 报错 "Model not found"**
- 检查模型名称格式：`提供商/模型名`
- 确认提供商配置正确

**Q: 配置文件在哪？**
```powershell
# 查看路径
python -c "from pathlib import Path; print(Path.home() / '.nanobot' / 'config.json')"
```
