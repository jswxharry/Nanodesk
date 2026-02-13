# AI 自主开发与测试系统设计

> 基于业界最佳实践（Devin、Vibe Coding Iterator、Self-Healing Test）的 Nanodesk 自动化开发能力提升方案

**提案状态**: 设计阶段  
**优先级**: 中-高  
**预计投入**: Phase 1 (2-3 天) → Phase 2 (1-2 周) → Phase 3 (长期演进)

---

## 背景与目标

### 现状痛点

| 环节 | 当前状况 | 问题 |
|------|----------|------|
| UI 测试 | 完全人工 | 每次发版需手动启动验证，易遗漏 |
| 回归测试 | 无自动化 | 新增功能可能破坏现有功能，难以及时发现 |
| 代码重构 | 人工执行 | 大型重构风险高，测试覆盖不确定 |
| 故障排查 | 人工阅读日志 | 依赖开发者经验，效率低 |

### 目标愿景

```
开发者 --------------------> AI 助手
   │                            │
   │  "添加搜索功能"             │
   │ ─────────────────────────> │
   │                            │
   │ <────────────────────────  │
   │    ✅ 代码实现              │
   │    ✅ 单元测试              │
   │    ✅ 启动验证（附截图）     │
   │    ✅ 代码审查摘要          │
   │                            │
   │  "LGTM" / "调整..."        │
   │ ─────────────────────────> │
```

**核心价值**:
- 减少重复验证工作 70%+
- 缩短发布周期
- 降低回归缺陷率

---

## 设计方案

### 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI 自主开发系统                             │
├──────────────┬─────────────────┬─────────────────┬──────────────┤
│   感知层      │    决策层        │    执行层        │   验证层      │
├──────────────┼─────────────────┼─────────────────┼──────────────┤
│ • 代码变更    │ • 任务规划      │ • 代码生成      │ • 静态检查    │
│ • 日志监控    │ • 错误诊断      │ • 测试生成      │ • 单元测试    │
│ • 截图分析    │ • 修复策略      │ • 自动重试      │ • 启动验证    │
│ • 测试反馈    │                 │                 │ • 日志断言    │
└──────────────┴─────────────────┴─────────────────┴──────────────┘
```

---

## Phase 1: 基础自动化（可立即实施）

### 1.1 启动验证 + 截图测试

**功能**: 自动启动应用，截取关键界面，验证基本功能

```python
# nanodesk/scripts/dev/test_desktop_startup.py
import subprocess
import time
from PIL import ImageGrab
import pytesseract

class DesktopStartupTest:
    def test_startup(self):
        """测试桌面应用能正常启动"""
        process = subprocess.Popen([
            sys.executable, "-m", "nanodesk.desktop"
        ])
        
        time.sleep(5)  # 等待启动
        
        # 截图
        screenshot = ImageGrab.grab()
        screenshot.save("test_output/startup.png")
        
        # OCR 验证关键文字存在
        text = pytesseract.image_to_string(screenshot)
        assert "Nanodesk" in text or "准备就绪" in text
        
        process.terminate()
    
    def test_system_tray(self):
        """验证系统托盘图标出现"""
        # 通过窗口枚举或进程检查
        pass
```

**所需依赖**:
```bash
pip install pillow pytesseract
# Windows: choco install tesseract
```

**验收标准**:
- [ ] 能在 CI 中运行
- [ ] 启动失败自动截图保存
- [ ] 生成 pass/fail 报告

---

### 1.2 日志断言测试

**功能**: 解析运行日志，验证关键事件和错误

```python
# nanodesk/scripts/dev/test_logs.py
import re
import tempfile

class LogAssertionTest:
    def test_gateway_logs(self):
        """验证 Gateway 启动日志无 ERROR"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log') as f:
            # 启动 gateway 并捕获日志
            process = subprocess.Popen(
                [sys.executable, "-m", "nanodesk", "gateway"],
                stdout=f,
                stderr=subprocess.STDOUT
            )
            time.sleep(10)
            process.terminate()
            
            # 读取日志并断言
            f.flush()
            with open(f.name) as log:
                content = log.read()
                
            assert "Gateway started" in content
            assert "ERROR" not in content
            assert re.search(r"Loaded \d+ tools", content)
```

**验收标准**:
- [ ] 覆盖 Gateway、Agent 启动
- [ ] 检查 ERROR/WARNING 模式
- [ ] 验证关键初始化步骤

---

### 1.3 基准截图对比

**功能**: 保存"正常"界面截图，后续对比检测 UI 回归

```python
# nanodesk/scripts/dev/test_ui_regression.py
from PIL import Image
import imagehash

class UIRegressionTest:
    BASELINE_DIR = "test_baseline/"
    OUTPUT_DIR = "test_output/"
    
    def capture_and_compare(self, name: str):
        """截图并与基准图对比"""
        screenshot = ImageGrab.grab()
        output_path = f"{self.OUTPUT_DIR}/{name}.png"
        screenshot.save(output_path)
        
        # 对比哈希
        baseline = Image.open(f"{self.BASELINE_DIR}/{name}.png")
        hash1 = imagehash.average_hash(baseline)
        hash2 = imagehash.average_hash(screenshot)
        
        diff = hash1 - hash2
        assert diff < 10, f"UI 差异过大 (diff={diff})"
```

**验收标准**:
- [ ] 可手动更新基准图
- [ ] 差异报告可视化（高亮不同区域）
- [ ] 阈值可配置

---

## Phase 2: 智能测试（1-2 周）

### 2.1 自修复测试 (Self-Healing)

**场景**: 测试因 UI 微调失败时，AI 自动分析并修复

```python
class SelfHealingTestRunner:
    def run_with_healing(self, test_func, max_retries=3):
        """运行测试，失败时尝试自动修复"""
        for attempt in range(max_retries):
            try:
                return test_func()
            except AssertionError as e:
                if attempt < max_retries - 1:
                    # AI 分析失败原因
                    fix = self.analyze_and_fix(e, test_func)
                    if fix:
                        self.apply_fix(fix)
                        continue
                raise
    
    def analyze_and_fix(self, error, test_func):
        """
        分析测试失败原因，返回修复建议
        例如：
        - OCR 找不到文字 → 更新断言文字
        - 元素位置变化 → 更新坐标
        - 超时 → 增加等待时间
        """
        pass
```

---

### 2.2 Vision-guided 验证

**功能**: 使用 Vision 模型（如 GPT-4V）"看懂"界面判断是否通过

```python
class VisionGuidedValidator:
    def validate_screenshot(self, image_path: str, criteria: str) -> bool:
        """
        使用 Vision 模型验证截图
        
        criteria: "界面显示正常，没有错误弹窗，系统托盘图标可见"
        """
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": f"判断以下截图是否满足：{criteria}"},
                    {"type": "image_url", "image_url": {"url": f"file://{image_path}"}}
                ]
            }]
        )
        return "通过" in response.choices[0].message.content
```

**成本考虑**:
- 仅在关键节点使用（而非每个测试）
- 可配置使用开源模型（如 Llava via Ollama）

---

### 2.3 自动测试生成

**功能**: AI 分析代码变更，自动生成对应测试

```python
class AutoTestGenerator:
    def generate_for_change(self, file_path: str, diff: str) -> str:
        """
        根据代码变更生成测试代码
        
        示例：新增 ddg_search 工具
        → 生成测试：mock DDGS 调用，验证返回格式
        """
        prompt = f"""
文件: {file_path}
变更:
{diff}

请生成 pytest 测试代码：
1. 测试正常路径
2. 测试错误处理
3. 使用 mock 避免外部依赖
"""
        return llm.generate(prompt)
```

---

## Phase 3: 自主迭代（长期演进）

### 3.1 持续开发循环

借鉴 [Vibe Coding Iterator](https://github.com/dage/vibe-coding-iterator):

```
需求描述 → AI 实现 → 自动测试 → 失败分析 → AI 修复 → 循环
                 ↓
           成功 → 人工审查 → 合并
```

### 3.2 并行任务处理

借鉴 Devin 企业案例:

- 大型重构拆分为子任务
- 多个 AI 实例并行处理
- 统一代码审查入口

---

## 实施路线图

```
2026-Q1          2026-Q2          2026-Q3          2026-Q4
   │                │                │                │
   ▼                ▼                ▼                ▼
┌──────┐        ┌──────┐        ┌──────┐        ┌──────┐
│Phase1│        │Phase2│        │Phase3│        │Phase3│
│基础   │   →    │智能  │   →    │自主  │   →    │优化  │
│自动化 │        │测试  │        │迭代  │        │生产  │
└──────┘        └──────┘        └──────┘        └──────┘
 截图测试         自修复测试       Vision-guided    企业级并行
 日志断言         自动测试生成     自主开发循环      A/B测试
```

---

## 附录: 参考资源

| 项目 | 链接 | 可借鉴点 |
|------|------|----------|
| **Devin** | https://devin.ai/ | 企业级自主开发，并行任务 |
| **Vibe Coding Iterator** | https://github.com/dage/vibe-coding-iterator | Vision-guided 迭代，开源低成本 |
| **Self-Healing Tests** | https://www.mabl.com/ | UI 变化自动适配 |
| **Agentic AI QA** | https://medium.com/@AziroTech | 根因分析，自主诊断 |

---

## 下一步行动

1. **Phase 1 实施**: 创建 `test_desktop_startup.py` 基础截图测试
2. **基础设施**: 添加 `pytesseract` 和 `imagehash` 到 dev 依赖
3. **CI 集成**: 修改 `run_tests.ps1` 包含启动验证
4. **基线建立**: 保存当前稳定版本的界面截图作为基准

**需要决策**:
- [ ] Phase 1 是否立即开始？
- [ ] Vision-guided 测试使用哪个模型（GPT-4V / 本地 Llava / 其他）？
- [ ] 是否允许 AI 自动提交修复（高风险），还是仅生成修复建议？
