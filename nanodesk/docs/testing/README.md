# 测试文档目录

> Nanodesk 测试计划、自动化脚本和测试报告

---

## 文档列表

| 文档 | 说明 |
|------|------|
| [TEST_PLAN.md](./TEST_PLAN.md) | 完整的测试计划（AI自动 + 手动）|
| [AI_CHECKLIST.md](./AI_CHECKLIST.md) | AI可完成的测试检查清单 |
| [MANUAL_CHECKLIST.md](./MANUAL_CHECKLIST.md) | 需用户手动完成的测试 |
| [test-report-template.md](./test-report-template.md) | 测试报告模板 |

---

## 测试分工

### 🤖 AI 可完成（自动化/半自动化）

- 代码静态检查
- 依赖安装验证
- 工具注册检查
- 配置文件格式验证
- 构建测试

### 👤 用户手动完成

- GUI 界面测试
- 飞书集成测试
- 对话质量评估
- 端到端场景测试

---

## 快速开始

```powershell
# 1. AI 先执行自动化检查
python nanodesk\docs\testing\ai_check.py

# 2. 用户根据 MANUAL_CHECKLIST.md 进行手动测试

# 3. 填写测试报告
copy nanodesk\docs\testing\test-report-template.md test-report-20260213.md
```
