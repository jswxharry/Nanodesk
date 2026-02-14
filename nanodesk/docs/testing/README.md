# 测试文档

## 工作流程

```
1. AI 执行自动化测试 → 运行脚本
         ↓
2. AI 生成测试报告 → 分析改动，挑选用例
                      → 按命名规范创建报告
                      → 填写自动化部分
         ↓
3. 人审核并补充 → 查看 reports/test-report-日期-版本-功能.md
                → 执行手动测试，填手动部分
         ↓
4. AI 补足文档 → 基于人类填写，完善报告
         ↓
5. 人确认结论 → 审核报告，做最终决策
```

**详细流程**: [TEST-WORKFLOW.md](./TEST-WORKFLOW.md)

---

## 文件说明

| 文件类型 | 说明 | 谁用 |
|----------|------|------|
| `TEST-WORKFLOW.md` | 完整流程说明 | AI + 人 |
| `test-report-template.md` | 报告模板（结构） | AI 复制到 reports/ |
| `*-test.md` | 测试用例步骤 | 人（查看并执行） |
| `reports/test-report-*.md` | 具体测试报告 | AI 生成初稿，人补充确认 |

---

## 测试用例列表

| 功能 | 自动化脚本 | 测试用例步骤 |
|------|-----------|-------------|
| 电源管理 | `test_power_management.py` | [power-management-test.md](./power-management-test.md) |
| 桌面应用 | `run_tests.ps1` | [desktop-app-test.md](./desktop-app-test.md) |
| 搜索工具 | - | [search-tools-test.md](./search-tools-test.md) |
| 飞书集成 | - | [feishu-integration-test.md](./feishu-integration-test.md) |

---

## 快速开始

```powershell
# Step 1-2: AI 执行自动化 + 生成报告
python nanodesk/scripts/dev/test_power_management.py
# AI 分析改动，挑选测试用例
# AI 复制模板: reports/test-report-{日期}-{版本}-{功能}.md
# 示例: test-report-20260215-v0.2.2-power-management.md
# AI 填写自动化结果

# Step 3: 人查看报告，执行手动测试
notepad nanodesk/docs/testing/reports/test-report-20260215-v0.2.2-power-management.md
cat nanodesk/docs/testing/power-management-test.md  # 查看测试步骤

# Step 4: AI 基于人类填写补足文档

# Step 5: 人确认最终结论
```
