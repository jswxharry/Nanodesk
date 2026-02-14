# 测试工作流程

## 角色分工

| 角色 | 职责 |
|------|------|
| 🤖 **AI** | 执行自动化脚本、分析改动挑选测试用例、生成测试报告初稿、基于人类填写补足文档 |
| 👤 **人类** | 执行手动测试步骤、审核 AI 生成的报告、确认最终结论 |

---

## 测试流程

```
┌──────────────────────────────┐
│ 1. AI 执行自动化测试          │ ← AI 运行测试脚本
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ 2. AI 生成测试报告            │ ← AI 分析改动，挑选相关测试用例
│    复制 test-report-template.md│    生成报告到 reports/
│    到 reports/，填写自动化部分  │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ 3. 人类审核并补充手动测试      │ ← 人类查看 reports/ 里的报告
│    执行需要人工测试的步骤      │    确认哪些测试已通过/需人工验证
│    填写手动测试结果            │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ 4. AI 补足文档                │ ← AI 基于人类的填写
│    完善报告内容               │    完善问题描述、结论等
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ 5. 人类确认结论               │ ← 人类做最终决策
│    做最终决策                 │    合并/修复/暂缓
└──────────────────────────────┘
```

---

## 详细步骤

### Step 1: AI 执行自动化测试

AI 根据功能改动，执行对应的自动化测试脚本：

```powershell
# 电源管理自动化测试
python nanodesk/scripts/dev/test_power_management.py

# 桌面应用自动化测试
.\nanodesk\scripts\dev\run_tests.ps1

# 其他脚本...
```

**AI 产出**: 自动化测试原始结果

---

### Step 2: AI 生成测试报告

#### 2.1 分析改动，挑选测试用例

AI 根据代码改动判断涉及的功能，挑选对应测试用例：

| 改动文件/模块 | 涉及功能 | 挑选测试用例 |
|--------------|---------|-------------|
| `nanodesk/desktop/core/power_manager.py` | 电源管理 | `power-management-test.md` |
| `nanodesk/bootstrap.py` | 启动流程、电源管理 | `power-management-test.md` |
| `nanodesk/desktop/windows/*.py` | 桌面应用 | `desktop-app-test.md` |
| `nanodesk/tools/*search*.py` | 搜索工具 | `search-tools-test.md` |
| `nanobot/channels/feishu.py` | 飞书集成 | `feishu-integration-test.md` |
| `nanobot/agent/loop.py` | 核心 Agent | 全部测试用例 |

**多改动场景**：如涉及多个功能，创建综合测试报告

#### 2.2 命名测试报告

命名模板：
```
test-report-{日期}-{版本}-{功能描述}.md
```

示例：
```
test-report-20260215-v0.2.2-power-management.md
test-report-20260215-v0.2.2-desktop-app.md
test-report-20260215-v0.2.2-all.md  # 综合测试
```

#### 2.3 生成报告

```bash
# AI 复制模板创建新报告（按命名规范）
cp nanodesk/docs/testing/test-report-template.md \
   nanodesk/docs/testing/reports/test-report-20260215-v0.2.2-power-management.md
```

**AI 填写内容**:
- 基本信息（分支、Commit、版本等）
- 自动化测试结果
- 需要人工测试的项目列表（从相关 `*-test.md` 提取）

**报告结构示例**:
```markdown
# 测试报告：电源管理功能

## 改动范围
- files: `nanodesk/desktop/core/power_manager.py`, `nanodesk/bootstrap.py`
- 功能: Windows 电源管理（插电阻止睡眠，电池允许睡眠）

## 自动化测试
✅ 通过 10/10

## 需要人工验证（来自 power-management-test.md）
- [ ] 插电功能测试
- [ ] 电池功能测试（需笔记本）
- [ ] 电源切换测试（需笔记本）
- [ ] 单实例锁测试
```

---

### Step 3: 人类审核并补充

人类查看 `reports/` 中的报告：

1. **查看 AI 已填写的自动化结果**
2. **判断哪些测试需要人工执行**
3. **按测试用例执行手动测试**
4. **填写手动测试结果**

**人类填写内容**:
- 手动测试勾选（通过/失败）
- 测试备注/问题描述
- 发现的问题列表

---

### Step 4: AI 补足文档

AI 基于人类的填写，完善报告：

- 补充问题描述的技术细节
- 生成已修复问题列表（从 git log 提取）
- 撰写 AI 总结和建议

**AI 填写内容**:
- 已修复的问题
- AI 总结
- 合并建议

---

### Step 5: 人类确认结论

人类查看完整报告，做最终决策：

```markdown
## 结论
AI 建议: 立即合并
理由: 1. ... 2. ...

人类确认: ✅ 同意 / ❌ 需修改
最终决策: ⬜ 合并  ⬜ 修复后合并  ⬜ 暂缓
```

**人类填写内容**:
- 审核确认
- 签字
- 最终决策

---

## 文件说明

| 文件 | 用途 | 谁用 |
|------|------|------|
| `TEST-WORKFLOW.md` | 本流程文档 | AI + 人 |
| `test-report-template.md` | 报告模板（结构） | AI |
| `*-test.md` | 测试用例步骤 | 人（查看并执行） |
| `reports/test-report-*.md` | 具体测试报告 | AI 生成初稿，人补充 |

---

## 快速开始

```powershell
# AI 第1-2步：执行自动化 + 生成报告
python nanodesk/scripts/dev/test_power_management.py
# AI 复制模板到 reports/，填写自动化结果

# 人类第3步：审核报告，执行手动测试
notepad nanodesk/docs/testing/reports/test-report-20260215.md
# 人类执行 power-management-test.md 中的步骤

# AI 第4步：基于人类填写补足文档
# AI 补充问题描述、生成总结

# 人类第5步：确认结论
# 人类查看报告，签字确认
```
