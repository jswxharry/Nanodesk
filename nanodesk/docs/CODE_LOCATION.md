# 代码归属判断指南

决定代码应该放在 `nanobot/` 还是 `nanodesk/` 的详细标准。

## 一、必须放在 nanodesk/ 的情况（个人定制）

以下情况**绝对不要**放到原库：

### 1. 个人环境相关
- 本地文件路径（如 `/Users/yourname/Documents`）
- 个人电脑特定的配置
- 仅在你的机器上能运行的代码

### 2. 私有业务逻辑
- 公司内部工作流
- 个人账号相关逻辑
- 特定组织的集成代码

### 3. 实验/临时功能
- 快速原型验证
- 尚未测试稳定的功能
- 仅供个人学习尝试的代码

### 4. 特定工具依赖
- 只有你的电脑安装的软件
- 非通用 API（如公司内部接口）
- 本地服务依赖

## 二、适合 nanobot/ 的情况（通用贡献）

以下情况**适合**贡献给原库：

### 1. Bug 修复
- 修复崩溃、错误行为
- 改进错误处理
- 修复边界情况

### 2. 通用功能
- 新的 Channel（Discord、Slack 等主流平台）
- 通用工具（网页搜索、文件操作等）
- 配置项扩展

### 3. 性能优化
- 不改动行为的速度提升
- 内存使用优化
- 资源管理改进

### 4. 文档改进
- 修正错误说明
- 补充缺失文档
- 示例代码

## 三、灰色地带（需要判断）

以下情况需要具体分析：

| 场景 | 建议位置 | 理由 |
|------|---------|------|
| 新的 LLM Provider | nanobot/ | 通用功能 |
| 特定厂商的 API 适配 | nanodesk/ | 太具体 |
| 改进的日志格式 | nanobot/ | 通用改进 |
| 个人偏好的输出样式 | nanodesk/ | 主观偏好 |
| 新的配置选项 | nanobot/ | 通用扩展 |
| 硬编码的默认值修改 | nanodesk/ | 个人偏好 |

## 四、快速决策流程

```
开始修改代码
    │
    ▼
是否修复 Bug？
    │
    ├─ 是 → nanobot/（如果确定是 Bug）
    │
    └─ 否 → 是否通用功能？
              │
              ├─ 是 → 其他人需要吗？
              │         │
              │         ├─ 是 → nanobot/（贡献）
              │         │
              │         └─ 否 → nanodesk/
              │
              └─ 否 → nanodesk/（定制）
```

## 五、不确定时的处理

如果 10 秒内无法判断：

1. **优先放在 `nanodesk/`**
2. 在代码注释中标记：`# TODO: 评估是否适合上游`
3. 提交信息标记：`git commit -m "xxx - TODO: evaluate for upstream"`
4. 后续讨论决定

## 六、示例判断

### ✅ 好的 nanodesk/ 代码

```python
# nanodesk/tools/local_screenshot.py
# 只在 macOS 上工作，依赖个人安装的截图工具
class LocalScreenshotTool(Tool):
    async def execute(self):
        # 硬编码的个人快捷键
        os.system("screencapture -i ~/Desktop/shot.png")
```

### ✅ 好的 nanobot/ 代码

```python
# nanobot/channels/mattermost.py
# 新的通用频道，任何人可用
class MattermostChannel(BaseChannel):
    ...
```

### ⚠️ 需要重构的代码

```python
# 坏例子：硬编码个人路径在 nanobot/ 文件中
# nanobot/agent/tools/filesystem.py
WORKSPACE = "/Users/myname/mybot"  # ❌ 必须移到配置
```

应该改为：
```python
# 从配置读取
WORKSPACE = config.workspace_path  # ✅ 通用
```
