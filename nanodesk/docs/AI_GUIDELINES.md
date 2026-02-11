# Nanodesk AI 助手指导

本文档帮助 AI 助手理解 Nanodesk 项目结构，做出合适的代码建议。

## 项目定位

**Nanodesk** 是 [nanobot](https://github.com/HKUDS/nanobot) 的个人定制版：
- **nanobot/**：原库代码（跟踪上游，可贡献回去）
- **nanodesk/**：个人定制代码（完全自由）

## 核心决策原则

修改代码前，先判断：

> **"这段代码对原库的其他用户也有用吗？"**

- **是** → 适合贡献给 nanobot，可放在 `nanobot/` 或后续提取
- **否** → 个人定制，必须放在 `nanodesk/`

## 详细判断标准

参见 [CODE_LOCATION.md](./CODE_LOCATION.md)

## 提交信息规范

参见 [COMMIT_RULES.md](./COMMIT_RULES.md)

## 工作流程

1. **新功能开发**：优先在 `nanodesk/` 实现
2. **提取贡献**：发现通用价值后，提取到独立分支提 PR
3. **同步上游**：定期运行 `./nanodesk/scripts/sync-upstream.sh`

## 禁止事项

- ❌ 在 `nanodesk/` 中硬编码个人敏感信息（密码、Token、私钥）
- ❌ 未经评估直接修改 `nanobot/` 核心文件
- ❌ 将个人业务逻辑伪装成通用功能

## 推荐事项

- ✅ 使用配置而非硬编码
- ✅ 写清晰的注释说明代码用途
- ✅ 不确定时优先放 `nanodesk/`

## 特殊文件保护

以下文件受 `.gitattributes` 保护，同步上游时自动保留我们的版本：
- `README.md`
- `.gitignore`
- `.gitattributes`

如果 AI 建议修改这些文件，请：
1. 确认修改必要性
2. 确保不破坏现有保护规则
3. 在提交信息中说明原因
