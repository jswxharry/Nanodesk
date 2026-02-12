# Nanodesk 待办事项

> 记录项目已完成事项和待开发功能，供后续参考。
> 
> 最后更新：2026-02-12

---

## 已完成 ✅

### 基础架构
- [x] 创建 `nanodesk/` 目录结构
- [x] 配置 VS Code 开发环境（`.vscode/`）
- [x] 配置 Kimi Code 提示词（`.kimi/prompts.md`）
- [x] 编写 Windows PowerShell 脚本（sync-upstream, extract-contrib, init-venv）
- [x] 完善文档体系（9个文档）

### 通讯频道
- [x] 飞书（Feishu）通道配置完成
  - [x] WebSocket 长连接
  - [x] 消息收发正常
  - [x] 支持 Markdown 卡片

### 开发规范
- [x] Git 审核流程确立（必须用户确认后提交）
- [x] 代码位置决策文档（AI_COLLABORATION.md）
- [x] 提交信息规范（COMMIT_RULES.md）

### LLM 配置
- [x] 阿里云百炼（通义千问）配置
- [x] 月度 10000 次额度够用

---

## 待办事项 📋

### 高优先级

#### 1. 飞书语音功能 ⭐
**状态**：已开发，已回滚，待重新审核后合并

**实现内容**：
- 下载飞书语音文件（opus 格式）
- 使用 DashScope Paraformer 转文字
- 需要权限：`im:resource`

**文件位置**：
- `nanobot/channels/feishu.py`（需添加 `_handle_voice_message`）
- `nanodesk/tools/voice_transcription.py`（语音转文字工具）

**操作步骤**：
1. [ ] 审核代码实现
2. [ ] 飞书开放平台开通 `im:resource` 权限
3. [ ] 重新发布应用
4. [ ] 测试语音消息

**参考**：FEISHU_SETUP.md "语音功能" 章节

---

### 中优先级

#### 2. 自定义工具开发

##### 2.1 Windows 截图工具
**需求**：通过飞书发送指令，截取电脑屏幕

**实现思路**：
```python
# nanodesk/tools/screenshot.py
class ScreenshotTool(Tool):
    name = "screenshot"
    # 使用 PIL 或 pyautogui 截图
    # 保存到工作目录，返回文件路径
```

**前置条件**：
- [ ] 安装依赖：`pip install pillow` 或 `pyautogui`
- [ ] 在 `bootstrap.py` 注册工具

##### 2.2 本地文件管理工具
**需求**：通过飞书查看、读取本地文件

**实现思路**：
```python
# nanodesk/tools/local_filesystem.py
class LocalFileTool(Tool):
    # 读取 ~/Documents/xxx 文件内容
    # 注意：遵守 restrict_to_workspace 设置
```

##### 2.3 系统信息查询
**需求**：查看电脑状态（CPU、内存、磁盘）

**实现思路**：
```python
# nanodesk/tools/system_info.py
import psutil
# 获取 CPU、内存、磁盘使用情况
```

---

### 低优先级（可选）

#### 3. 其他通讯频道

##### 3.1 钉钉（DingTalk）
**评估**：
- ✅ 国内可用，无代理问题
- ⚠️ 需要企业/组织创建应用
- ⚠️ API 限额可能比飞书宽松

**配置复杂度**：⭐⭐⭐

##### 3.2 Discord
**评估**：
- ✅ 国际通用，Bot 生态成熟
- ❌ 国内需要代理
- ✅ 完全免费，无限制

**配置复杂度**：⭐⭐

##### 3.3 微信公众号（已评估，放弃）
**结论**：个人订阅号限制太多（5秒超时、被动回复），暂不实现

---

## 问题记录 🐛

### 已解决

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 飞书机器人无法聊天 | 未添加事件订阅 | 配置 `im.message.receive_v1` 事件 |
| 订阅方式保存不了 | 权限未开通 | 先开通权限，再配置订阅方式 |

### 待观察

| 问题 | 状态 | 备注 |
|------|------|------|
| 飞书 API 限额 | 监控中 | 每月 10000 次，目前够用 |

---

## 个人使用技巧 💡

### 飞书快捷指令
```
@机器人 你好          # 群聊中触发
直接发消息            # 私聊中触发
```

### VS Code 调试
```powershell
# 快速启动调试
F5  # 选择配置后启动

# 查看日志
nanodesk gateway --verbose
```

### Git 工作流
```powershell
# 日常开发
git checkout nanodesk
# ... coding ...
git add .
git commit -m "custom: xxx"  # AI 会提示确认

# 同步上游
.\nanodesk\scripts\sync-upstream.ps1
```

---

## 参考资源 📚

| 资源 | 链接 | 说明 |
|------|------|------|
| nanobot 原库 | https://github.com/HKUDS/nanobot | 上游项目 |
| 飞书开放平台 | https://open.feishu.cn/ | 机器人配置 |
| 阿里云百炼 | https://bailian.console.aliyun.com/ | LLM API |
| DashScope 文档 | https://help.aliyun.com/dashscope | 语音/模型 API |

---

## 更新记录

| 日期 | 内容 |
|------|------|
| 2026-02-12 | 创建待办事项文档，整理已完成和待办 |
