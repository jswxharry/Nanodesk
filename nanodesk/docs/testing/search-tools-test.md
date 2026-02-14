# 搜索工具测试用例

## 测试内容

DuckDuckGo 搜索、浏览器搜索、浏览器抓取

---

## 测试步骤

### 1. DDG 搜索测试

```powershell
# 步骤
1. 启动 Gateway
2. 向 Agent 发送："搜索 Python 教程"
3. 观察是否调用 ddg_search 工具
4. 观察返回结果
```

**预期结果**：返回搜索结果列表

---

### 2. 浏览器搜索测试

```powershell
# 前置：确保已安装 Playwright（可选）
# pip install playwright
# playwright install

# 步骤
1. 向 Agent 发送："用浏览器搜索最新 Python 版本"
2. 观察提示（应提示安装 Playwright 或执行搜索）
```

**预期结果**：未安装时提示手动安装，已安装时执行搜索

---

### 3. 浏览器抓取测试

```powershell
# 步骤
1. 向 Agent 发送："抓取 https://example.com 的内容"
2. 观察是否调用 browser_fetch 工具
3. 观察返回的页面内容
```

**预期结果**：返回页面文本内容

---

### 4. /new 命令测试

```powershell
# 步骤
1. 与 Agent 对话几轮
2. 发送 "/new"
3. 观察是否新建会话
4. 观察历史消息是否被整合到 MEMORY.md
```

**预期结果**：新建会话，上下文清空，历史保存

---

## 测试结果填哪

复制 `test-report-template.md` 到 `reports/test-report-日期.md` 填写
