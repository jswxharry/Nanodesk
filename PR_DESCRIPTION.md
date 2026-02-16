## Summary

Merge `develop` into `nanodesk`: Add Ollama Provider support and documentation reorganization.

## Changes

### ✨ New Features

#### 1. Ollama Provider Support
- **New**: `nanodesk/providers/ollama_provider.py` - Dedicated Ollama provider for local LLM
- **New**: Support `provider: "ollama"` configuration
- **Improved**: Bypass LiteLLM model name matching issues
- **Optimized**: Support `OLLAMA_NUM_THREAD` and `OLLAMA_CONTEXT_LENGTH` environment variables

**Recommended Model**: `qwen2.5:3b`
- Response time: 15-40s (with 12-thread optimization)
- Chinese capability: Excellent
- Memory usage: ~3GB

#### 2. Documentation Reorganization
- **New**: `docs/setup/` directory for configuration guides
- **New**: `docs/setup/README.md` - Configuration navigation hub
- **New**: `docs/setup/OLLAMA.md` - Complete Ollama configuration guide with performance data
- **New**: `docs/setup/OLLAMA_INSTALL.md` - Windows installation guide (moved from docs root)
- **New**: `docs/setup/FEISHU.md` - Feishu bot configuration (moved from FEISHU_SETUP.md)
- **New**: `docs/setup/CONFIGURATION.md` - General configuration reference

#### 3. Performance Optimizations Documented
- `OLLAMA_NUM_THREAD=12` (75% of CPU cores for 16-core CPU)
- `OLLAMA_CONTEXT_LENGTH=2048`
- `memoryWindow: 10`
- Clear old session cache

### 🔧 Technical Changes

- `nanodesk/bootstrap.py` - Register Ollama provider and patch schema
- `nanobot/cli/commands.py` - Support Ollama provider selection
- `nanodesk/desktop/core/gateway_service.py` - Gateway Ollama initialization
- `nanodesk/desktop/gateway_runner.py` - Startup optimization
- `nanodesk/launcher.py` - Import order optimization

### 📚 Documentation Updates

- `docs/README.md` - Add setup/ directory navigation
- `docs/CHANGELOG.md` - Update version history
- `docs/TODO.md` - Mark Ollama support as completed
- `docs/UPSTREAM_PRS.md` - Add Ollama tracking for PR #257

### 📦 Version

- Bump version: `0.1.3.post7` → `0.2.3`

## Testing

- **Test Report**: `nanodesk/docs/testing/reports/test-report-20260216-v0.2.3-ollama-provider.md`
- **Manual Testing Required**:
  1. Ollama conversation functionality
  2. Performance optimization verification (response time < 40s)
  3. Documentation link validation

## Migration Notes

For users upgrading from previous versions:

1. Update `config.json` to use `provider: "ollama"`:
```json
{
  "agents": {
    "defaults": {
      "model": "qwen2.5:3b",
      "provider": "ollama",
      "memoryWindow": 10
    }
  },
  "providers": {
    "ollama": {
      "apiKey": "not-needed",
      "apiBase": "http://localhost:11434"
    },
    "dashscope": {
      "apiKey": ""  // Must be empty to avoid conflicts
    }
  }
}
```

2. Set environment variables:
```powershell
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREAD", "12", "Machine")
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "2048", "Machine")
```

## Related

- **Upstream PR #257**: Contains official Ollama support (not yet merged to main)
- **Nanodesk Implementation**: Temporary solution until upstream PR #257 is merged
- **Future Plan**: Evaluate switching to upstream implementation when PR #257 is merged

## Checklist

- [x] Code follows project style guidelines
- [x] Documentation updated
- [x] Test report created
- [ ] Manual testing completed (pending)
- [ ] Version bumped
