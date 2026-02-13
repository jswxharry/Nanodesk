# Nanodesk Agent Guide

> This document is for AI coding assistants to understand the Nanodesk project structure and development conventions.
> **Nanodesk** is a personal customization of [nanobot](https://github.com/HKUDS/nanobot), optimized for local desktop scenarios.
> Upstream repository: https://github.com/HKUDS/nanobot

## Project Overview

**Nanodesk** is a **practical personal AI assistant** optimized for daily use, based on nanobot.

> **Core Philosophy**: Practicality first, lightweight second. Solve real daily problems without unnecessary bloat.

### Key Characteristics

- **Practical-First**: Daily-use features work out of the box (search, file ops, browser, scheduling)
- **Lightweight & Understandable**: Core code ~4,000-8,000 lines, readable and customizable
- **Long-Running**: Stays alive when screen is off (Windows power management)
- **Multi-Channel Support**: Feishu (primary), Telegram, Discord, WhatsApp, DingTalk, Slack, Email, QQ, Mochat
- **Windows Desktop App**: PySide6 GUI with system tray, embedded Python packaging
- **Local-First**: Data stored locally, no cloud dependencies, fully offline capable
- **Dreams Allowed**: Aggressive designs (AI autonomous dev, context tracking) kept for future inspiration

### What We Are NOT

- ❌ **Not a feature-bloated framework** (we skip Canvas/UI, multi-agent, mobile apps)
- ❌ **Not a black-box product** (you own and understand every line of code)
- ❌ **Not just "lightweight for lightweight's sake"** (practicality trumps line count)

### Comparison: Nanodesk vs Others

| Aspect | OpenClaw | Nanodesk |
|--------|----------|----------|
| **Positioning** | Consumer product (iPhone-like) | Practical assistant (Linux-like control)
| **Installation** | npm + complex setup | pip or single-file executable
| **Best For** | Power users wanting everything | Users wanting control + practicality
| **Unique Edge** | Most features | Best Feishu integration, fully local
| **Code Ownership** | Hard to modify | Easy to customize

### Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Tracks upstream nanobot, used for submitting PRs, no direct development |
| `nanodesk` | Main working branch, contains all personal customizations (default branch) |
| `develop` | Development branch, features merged here first before nanodesk |

### Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Tracks upstream nanobot, used for submitting PRs, no direct development |
| `nanodesk` | Main working branch, contains all personal customizations (default branch) |

## Technology Stack

### Core Dependencies

- **Python**: >=3.11 (uses modern type annotation features like `str | None`, `list[str]`)
- **CLI Framework**: Typer + Rich (Markdown rendering)
- **LLM Integration**: LiteLLM (unified multi-provider interface)
- **Configuration**: Pydantic + pydantic-settings
- **Async**: asyncio + websockets
- **Logging**: loguru
- **Desktop GUI**: PySide6 (Windows desktop application)

### Additional Tools

- **Web Scraping**: readability-lxml
- **Scheduling**: croniter
- **Interactive CLI**: prompt-toolkit (history, paste support)
- **Build System**: Hatchling (Python package), PyInstaller (desktop app)
- **Channel SDKs**:
  - python-telegram-bot (Telegram)
  - lark-oapi (Feishu)
  - dingtalk-stream (DingTalk)
  - python-socketio (Mochat)
  - slack-sdk (Slack)
  - qq-botpy (QQ)
  - discord.py (Discord)

### WhatsApp Bridge

- **Runtime**: Node.js >=20
- **Language**: TypeScript
- **Library**: @whiskeysockets/baileys
- **Build**: npm + tsc

## Project Structure

```
nanobot/                    # Core framework (upstream code)
├── agent/                  # Core agent logic
│   ├── loop.py             # Main agent loop (LLM ↔ tool execution)
│   ├── context.py          # Prompt builder (history/memory/skills)
│   ├── memory.py           # Persistent memory management
│   ├── skills.py           # Skill loader (SKILL.md files)
│   ├── subagent.py         # Background task execution
│   └── tools/              # Built-in tools
│       ├── base.py         # Tool abstract base class
│       ├── registry.py     # Tool registration and execution
│       ├── filesystem.py   # read_file, write_file, edit_file, list_dir
│       ├── shell.py        # exec (shell command execution)
│       ├── web.py          # web_search (Brave), web_fetch
│       ├── message.py      # message (send outbound messages)
│       ├── spawn.py        # spawn (background subagents)
│       └── cron.py         # cron (scheduled tasks)
├── bus/                    # Message routing
│   ├── events.py           # InboundMessage, OutboundMessage
│   └── queue.py            # MessageBus (async pub/sub)
├── channels/               # Chat channel integrations
│   ├── base.py             # Base channel interface
│   ├── manager.py          # Channel lifecycle management
│   ├── telegram.py         # Telegram Bot (polling)
│   ├── discord.py          # Discord gateway (WebSocket)
│   ├── whatsapp.py         # WhatsApp bridge client
│   ├── feishu.py           # Feishu WebSocket
│   ├── dingtalk.py         # DingTalk Stream mode
│   ├── mochat.py           # Mochat Socket.IO
│   ├── slack.py            # Slack Socket Mode
│   ├── email.py            # IMAP/SMTP email
│   └── qq.py               # QQ botpy SDK
├── config/                 # Configuration
│   ├── schema.py           # Pydantic models for all config
│   └── loader.py           # Config loading/saving
├── providers/              # LLM providers
│   ├── base.py             # LLMProvider interface
│   ├── litellm_provider.py # LiteLLM implementation
│   ├── registry.py         # ProviderSpec registry (single source of truth)
│   └── transcription.py    # Voice transcription (Groq Whisper)
├── session/                # Conversation sessions
│   └── manager.py          # Session persistence (JSONL format)
├── cron/                   # Scheduled tasks
│   ├── service.py          # Cron scheduler
│   └── types.py            # Job and schedule types
├── heartbeat/              # Proactive wake-up
│   └── service.py          # Periodic heartbeat prompts
├── cli/                    # Commands
│   └── commands.py         # Typer CLI (agent, gateway, cron, etc.)
├── skills/                 # Built-in skills (Markdown instructions)
│   ├── github/             # GitHub CLI integration
│   ├── weather/            # Weather queries
│   ├── summarize/          # URL/file/YouTube summarization
│   ├── tmux/               # tmux session control
│   ├── cron/               # Cron management
│   └── skill-creator/      # Create new skills
└── utils/                  # Utility functions
    └── helpers.py          # Common helpers

nanodesk/                   # Personal customization layer
├── __init__.py             # Module identifier
├── bootstrap.py            # Startup injection logic (loads customizations)
├── launcher.py             # CLI entry point (nanodesk command)
├── desktop/                # Windows desktop application
│   ├── main.py             # GUI entry point
│   ├── windows/            # Window components
│   │   ├── main_window.py  # Main window + system tray
│   │   └── setup_wizard.py # Configuration wizard
│   ├── core/               # Core functionality
│   │   ├── config_manager.py   # Config management (with DPAPI encryption)
│   │   ├── process_manager.py  # Gateway process management
│   │   └── log_handler.py      # Log system
│   └── resources/          # Icons and assets
├── channels/               # Custom channels
├── tools/                  # Custom tools
├── skills/                 # Custom skills
├── providers/              # Custom LLM adapters
├── patches/                # Core patches if needed
├── scripts/                # Helper scripts
│   ├── build_all.ps1           # One-click desktop build
│   ├── prepare_embedded_python.py  # Prepare embedded Python
│   ├── sync-upstream.ps1/.sh   # Sync upstream updates
│   └── extract-contrib.sh/.ps1 # Extract contribution commits
└── docs/                   # Documentation (Chinese)
    ├── ARCHITECTURE.md     # Project structure and Git workflow
    ├── BUILD.md            # Desktop build guide
    ├── DESKTOP_APP_PLAN.md # Development plan
    └── ...

bridge/                     # WhatsApp Node.js bridge
├── src/
│   ├── index.ts            # Entry point
│   ├── server.ts           # WebSocket server
│   └── whatsapp.ts         # Baileys client
├── package.json
└── tsconfig.json

tests/                      # Test suite
├── test_tool_validation.py # Tool parameter validation tests
├── test_email_channel.py   # Email channel tests
└── test_cli_input.py       # CLI input tests

workspace/                  # Default workspace (created at runtime)
```

## Architecture

### Message Flow

```
User → Channel → MessageBus → AgentLoop → LLM Provider
                                ↓
                          Tool Execution
                                ↓
MessageBus ← Channel ← Response ← AgentLoop
```

### Key Components

1. **AgentLoop** (`nanobot/agent/loop.py`): Core processing engine
   - Consumes messages from MessageBus
   - Builds context (history + memory + skills + system prompt)
   - Iterates with LLM until no tool calls (max 20 iterations)
   - Persists conversations to sessions

2. **MessageBus** (`nanobot/bus/queue.py`): Async message routing
   - Inbound queue (user → agent)
   - Outbound queue (agent → user)

3. **ToolRegistry** (`nanobot/agent/tools/registry.py`): Tool management
   - All tools inherit from `Tool` base class
   - JSON Schema parameter validation
   - Async execution with error handling

4. **Provider Registry** (`nanobot/providers/registry.py`): Single source of truth for LLM providers
   - Gateways (OpenRouter, AiHubMix) detected by key prefix or base URL
   - Standard providers matched by model name keywords
   - Local deployments (vLLM) explicitly configured

5. **Nanodesk Bootstrap** (`nanodesk/bootstrap.py`): Customization injection
   - Loads before nanobot CLI starts
   - Registers custom tools, channels, providers
   - Maintains physical isolation from upstream code

## Build and Development Commands

### Installation (Development)

```bash
# Clone and install in editable mode
git clone <your-nanodesk-repo>
cd Nanodesk
pip install -e ".[dev]"

# Or using uv
uv tool install -e .
```

### Starting Nanodesk (Command Line)

```bash
# Initialize configuration
nanodesk onboard

# Edit config to add API keys
vim ~/.nanobot/config.json

# Start interactive agent
nanodesk agent

# Start gateway (connects to enabled channels)
nanodesk gateway
```

### Windows Desktop Application

```powershell
# One-click build (includes embedded Python)
.\nanodesk\scripts\build_all.ps1 -Clean

# Output: dist/Nanodesk/ folder (portable) + dist/Nanodesk-Setup-x.x.x.exe (installer)

# Run desktop app directly (requires Python + PySide6)
python -m nanodesk.desktop.main
```

### Running Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Specific test file
pytest tests/test_tool_validation.py
```

### Linting and Formatting

```bash
# Run ruff linter (config in pyproject.toml)
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

### Line Count Verification

```bash
# Verify core agent code lines (excludes channels/, cli/, providers/)
bash core_agent_lines.sh
```

## Code Style Guidelines

### Configuration (pyproject.toml)

- **Line Length**: 100 characters
- **Target Python**: 3.11+
- **Lint Rules**: E, F, I, N, W (ignores E501 line length)

### Naming Conventions

- **Classes**: PascalCase (e.g., `AgentLoop`, `ToolRegistry`)
- **Functions/Variables**: snake_case (e.g., `process_message`)
- **Private Members**: Leading underscore (e.g., `_running`)
- **Constants**: UPPER_SNAKE_CASE

### Type Annotations

- Use Python 3.11+ union syntax: `str | None` instead of `Optional[str]`
- Use built-in generics: `list[str]` instead of `List[str]`
- Import annotations when needed: `from __future__ import annotations`

### Docstrings

- Use triple double quotes: `"""Description"""`
- Google-style docstrings for complex functions
- Inline comments for non-obvious logic

### Async Patterns

- All I/O operations are async
- Tool `execute()` methods are async
- Use `asyncio.gather()` for parallel operations

## Testing Strategy

### Test Framework

- **pytest** + **pytest-asyncio** (asyncio_mode = auto)
- Tests located in `tests/` directory

### Test Coverage

- Tool parameter validation (`test_tool_validation.py`)
- Channel functionality (`test_email_channel.py`)
- CLI input handling (`test_cli_input.py`)

### Writing Tests

```python
# Async test example
async def test_tool_execution():
    tool = MyTool()
    result = await tool.execute(param="value")
    assert "expected" in result
```

## Configuration System

### Configuration Location

- **File**: `~/.nanobot/config.json`
- **Permissions**: Set to 0600 (contains API keys)

### Configuration Structure (Pydantic Models)

```python
class Config(BaseSettings):
    agents: AgentsConfig      # Default model, workspace path
    channels: ChannelsConfig  # Telegram, Discord, WhatsApp, etc.
    providers: ProvidersConfig  # API keys for LLM services
    gateway: GatewayConfig    # Gateway host/port
    tools: ToolsConfig        # Web search, exec timeout, workspace restriction
```

### Environment Variables

- Prefix: `NANOBOT_`
- Nested delimiter: `__`
- Example: `NANOBOT_PROVIDERS__OPENAI__API_KEY=sk-...`

## Adding New Features

### Adding Custom Tools (in nanodesk)

1. **Create tool class** inheriting from `Tool`:

```python
# nanodesk/tools/my_tool.py
from nanobot.agent.tools.base import Tool

class MyTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "Describe your tool functionality"
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            },
            "required": ["param"]
        }
    
    async def execute(self, **kwargs) -> str:
        return "execution result"
```

2. **Register in bootstrap.py**:

```python
# nanodesk/bootstrap.py
from nanodesk.tools.my_tool import MyTool
from nanobot.agent.tools.registry import ToolRegistry

ToolRegistry.register(MyTool())
```

### Adding Upstream LLM Providers

1. **Add ProviderSpec** to `nanobot/providers/registry.py`:

```python
ProviderSpec(
    name="myprovider",
    keywords=("myprovider", "mymodel"),
    env_key="MYPROVIDER_API_KEY",
    display_name="My Provider",
    litellm_prefix="myprovider",
    skip_prefixes=("myprovider/",),
)
```

2. **Add field** to `ProvidersConfig` in `nanobot/config/schema.py`:

```python
myprovider: ProviderConfig = ProviderConfig()
```

Environment variables, model prefixing, config matching, and `nanobot status` will work automatically.

### Adding New Channels (Upstream)

1. **Create channel class** inheriting from `BaseChannel`
2. **Implement** `start()`, `stop()`, `send_message()`
3. **Add config** to `ChannelsConfig` in `schema.py`
4. **Register** in `ChannelManager.__init__()`

## Security Considerations

### Key Security Features

1. **Workspace Restriction** (`tools.restrictToWorkspace`)
   - When enabled, all file operations are restricted to workspace directory
   - Prevents path traversal attacks

2. **Channel Access Control** (`channels.*.allowFrom`)
   - Whitelist-based user authorization
   - Empty list = allow everyone (default for personal use)
   - Must configure for production

3. **Shell Command Safety**
   - Blocks dangerous patterns: `rm -rf /`, fork bombs, `mkfs.*`
   - Enforces timeout (default 60 seconds)
   - Output limit (10KB)

4. **API Key Management**
   - Stored in config file with 0600 permissions
   - Desktop app uses DPAPI encryption for API keys
   - Never commit keys to version control
   - Use environment variables as alternative

### Production Security Checklist

- [ ] Set `restrictToWorkspace: true`
- [ ] Configure `allowFrom` list for all channels
- [ ] Set config file permissions to 0600
- [ ] Run as non-root user
- [ ] Use API keys with spending limits
- [ ] Enable logging and monitoring

See [SECURITY.md](./SECURITY.md) for full security documentation.

## Deployment

### Docker

```bash
# Build
docker build -t nanodesk .

# Initialize config (first time)
docker run -v ~/.nanobot:/root/.nanobot --rm nanodesk onboard

# Run gateway
docker run -v ~/.nanobot:/root/.nanobot -p 18790:18790 nanodesk gateway
```

### Windows Desktop (Portable)

```powershell
# Build with embedded Python
.\nanodesk\scripts\build_all.ps1 -Clean

# Distribute dist/Nanodesk/ folder (portable, no Python required)
# Or use dist/Nanodesk-Setup-*.exe installer
```

### PyPI Distribution (Upstream)

```bash
# Build
python -m build

# Upload
twine upload dist/*
```

Package name: `nanobot-ai`

## Common Tasks

### Verify Code Lines

```bash
bash core_agent_lines.sh
```

### Debug Mode

```bash
# Enable verbose logging
nanodesk gateway --verbose

# Show logs during chat
nanodesk agent --logs
```

### Reset State

```bash
# Delete all sessions
rm -rf ~/.nanobot/sessions/

# Delete config (re-run onboard)
rm ~/.nanobot/config.json
```

### Sync Upstream Updates

```powershell
# Windows
.\nanodesk\scripts\sync-upstream.ps1

# Linux/macOS
./nanodesk/scripts/sync-upstream.sh
```

### Extract Contribution Commits

```powershell
# Windows
.\nanodesk\scripts\extract-contrib.ps1 <commit-hash>

# Linux/macOS
./nanodesk/scripts/extract-contrib.sh <commit-hash>
```

Then create PR to `HKUDS/nanobot` from the `main` branch.

## VS Code Debugging

Pre-configured launch configurations in `.vscode/launch.json`:

- **Nanodesk Agent**: Debug the interactive agent
- **Nanodesk Gateway**: Debug the gateway service
- **Nanodesk Onboard**: Debug the onboarding flow
- **Current File**: Debug the currently open file

Press `F5` to start debugging.

## Resources

- **Upstream Repository**: https://github.com/HKUDS/nanobot
- **PyPI**: https://pypi.org/project/nanobot-ai/
- **Issues**: https://github.com/HKUDS/nanobot/issues
- **Discussions**: https://github.com/HKUDS/nanobot/discussions
- **Nanodesk Docs**: See `nanodesk/docs/` for detailed documentation (Chinese)
