# Ollama Windows 安装与配置指南

本文介绍如何在 Windows 系统上安装 Ollama，并将模型库迁移到 D 盘自定义目录（解决 C 盘空间不足问题）。

---

## 目录

1. [Ollama 简介](#1-ollama-简介)
2. [Windows 安装步骤](#2-windows-安装步骤)
3. [将 Ollama 安装到 D 盘（程序目录）](#3-将-ollama-安装到-d-盘程序目录)
4. [修改模型下载路径（重要）](#4-修改模型下载路径重要)
5. [国内镜像加速下载模型](#5-国内镜像加速下载模型)
6. [常用命令](#6-常用命令)
7. [本地模型推荐与优化（集成显卡+32G内存）](#7-本地模型推荐与优化集成显卡32g内存)
8. [与开发工具集成](#8-与开发工具集成)
9. [常见问题](#9-常见问题)

---

## 1. Ollama 简介

Ollama 是一个用于在本地运行大语言模型（LLM）的工具，支持：

- **Llama 3**、**Mistral**、**Qwen**、**DeepSeek** 等多种开源模型
- 简单的命令行接口
- REST API 供应用程序调用
- 跨平台支持（Windows、macOS、Linux）

> ⚠️ **注意**：模型文件体积较大（通常 2GB-30GB+），默认存储在 C 盘，建议修改到空间充足的其他分区。

---

## 2. Windows 安装步骤

### 方法一：官方安装包（海外网络）

1. 访问官方下载页面：[https://ollama.com/download](https://ollama.com/download)
2. 下载 Windows 版本安装包 `OllamaSetup.exe`
3. 双击运行安装程序，按向导完成安装
4. 安装完成后，Ollama 会自动在后台运行

### 方法二：中国大陆下载方案（推荐）

#### 方案A：CNB.cool 国内镜像（第三方推荐）⭐⭐⭐⭐

> **来源说明**：该方案来自技术博客 [弹霄博科](https://www.txisfine.cn/archives/8efde3fe.html) 的推荐，由 CNB.cool 平台用户创建的同步项目。

**CNB.cool** 是国内 DevOps 平台，据博客介绍，该项目每30分钟自动从官方同步最新安装包到国内节点。

**Windows 下载链接**：
```
https://cnb.cool/hex/ollama/-/releases/latest/download/OllamaSetup.exe
```

**PowerShell 一键下载安装**：
```powershell
# 下载
Invoke-WebRequest -Uri "https://cnb.cool/hex/ollama/-/releases/latest/download/OllamaSetup.exe" -OutFile "OllamaSetup.exe"

# 运行安装
Start-Process "OllamaSetup.exe"
```

**项目特点**（据博客介绍）：
- ✅ **自动同步**：每30分钟检查官方更新
- ✅ **稳定版**：只同步官方稳定版，不含预发布
- ✅ **安全可控**：Hash值与官方发布一致
- ✅ **国内节点**：下载速度快

**⚠️ 安全提醒**：
- 这是**第三方社区项目**，非 Ollama 官方提供
- 下载后请**校验数字签名**（右键→属性→数字签名），应为 "Ollama, Inc."
- 如不放心，请使用方案B（官方+下载工具）

**历史版本**：如需特定版本，访问 https://cnb.cool/hex/ollama/-/releases

#### 方案B：使用下载工具

如果 CNB.cool 无法访问，使用 **迅雷/IDM**：
1. 从 https://github.com/ollama/ollama/releases 复制官方下载链接
2. 粘贴到迅雷/IDM 中下载（自动寻找最快源）

#### 方案C：官方直接下载（可能也行）

> 有人反馈 Ollama 官方用 Cloudflare CDN，国内直接访问可能比走代理更快。可以尝试直接访问 https://ollama.com/download 下载。

#### 方案C：网盘/论坛分享（备用）

如果以上都不行：
- **百度搜**："OllamaSetup.exe 下载"
- **CSDN**：搜索 "Ollama Windows 下载"
- **蓝奏云**：技术博客常有分享

> ⚠️ 注意：从第三方下载时注意校验文件安全性

#### 方案D：使用 Winget（需代理）

```powershell
# 通过 Windows 包管理器安装
winget install Ollama.Ollama
```

### 验证安装

打开 PowerShell 或 CMD，运行：

```powershell
ollama --version
```

显示版本号即表示安装成功。

---

## 3. 将 Ollama 安装到 D 盘（程序目录）

> ⚠️ **注意**：Ollama Windows 版默认安装到 `C:\Users\{用户名}\AppData\Local\Programs\Ollama`，**官方安装器不提供自定义路径选项**。
>
> **解决方案**：在安装前通过符号链接（Symbolic Link）将安装目录指向 D 盘。

### 安装前准备：创建符号链接

**步骤 1：创建 D 盘目标目录**

```powershell
mkdir D:\Programs\Ollama
```

**步骤 2：在 C 盘创建符号链接（需要管理员权限）**

以管理员身份打开 PowerShell，执行：

```powershell
# 注意：将 Harry 替换为你的实际用户名
$target = "D:\Programs\Ollama"
$link = "C:\Users\Harry\AppData\Local\Programs\Ollama"

# 确保父目录存在
mkdir "C:\Users\Harry\AppData\Local\Programs" -ErrorAction SilentlyContinue

# 创建目录联接（Junction）
cmd /c mklink /J "$link" "$target"
```

预期输出：
```
为 C:\Users\Harry\AppData\Local\Programs\Ollama <<===>> D:\Programs\Ollama 创建的联接
```

**步骤 3：运行安装程序**

现在运行 `OllamaSetup.exe`，程序会沿着符号链接自动安装到 `D:\Programs\Ollama`。

### 验证安装路径

```powershell
# 查看 Ollama 安装位置
Get-Command ollama | Select-Object Source

# 检查实际占用的磁盘空间（应在 D 盘）
(Get-Item "D:\Programs\Ollama").FullName
```

### 已安装后的迁移方法

如果已经安装到 C 盘，想迁移到 D 盘：

```powershell
# 1. 完全退出 Ollama
Stop-Process -Name ollama -Force

# 2. 移动已安装的文件到 D 盘
robocopy "C:\Users\Harry\AppData\Local\Programs\Ollama" "D:\Programs\Ollama" /E /MOVE

# 3. 如果原目录还存在，删除后创建符号链接
Remove-Item "C:\Users\Harry\AppData\Local\Programs\Ollama" -Recurse -Force
cmd /c mklink /J "C:\Users\Harry\AppData\Local\Programs\Ollama" "D:\Programs\Ollama"

# 4. 重启 Ollama
ollama serve
```

---

## 4. 修改模型下载路径（重要）

### 4.1 问题背景

Ollama 默认将模型存储在：
```
C:\Users\{用户名}\.ollama\models\
```

大型模型（如 Llama 3 8B 约 4.7GB，70B 约 40GB）会快速占满 C 盘空间。

### 4.2 解决方案：设置环境变量

**原理**：通过设置 `OLLAMA_MODELS` 环境变量，将模型存储路径指向 D 盘。

#### 步骤 1：创建新目录

在 D 盘创建用于存储模型的目录：

```powershell
mkdir D:\OllamaModels
```

#### 步骤 2：设置环境变量

**方式 A：通过系统设置（图形界面）**

1. 按 `Win + S` 搜索 "环境变量"，选择 **编辑系统环境变量**
2. 点击 **环境变量** 按钮
3. 在 **系统变量** 区域点击 **新建**
4. 填写：
   - 变量名：`OLLAMA_MODELS`
   - 变量值：`D:\OllamaModels`
5. 点击确定保存

**方式 B：通过 PowerShell（管理员）**

```powershell
# 设置系统环境变量（需要管理员权限）
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "D:\OllamaModels", "Machine")
```

**方式 C：通过 CMD（管理员）**

```cmd
setx OLLAMA_MODELS "D:\OllamaModels" /M
```

#### 步骤 3：重启 Ollama 服务

修改环境变量后需要重启 Ollama：

```powershell
# 停止 Ollama
Stop-Process -Name ollama -Force

# 重新启动 Ollama
ollama serve
```

或直接在系统托盘右键 Ollama 图标 → **Quit**，然后重新打开 Ollama。

#### 步骤 4：验证路径生效

```powershell
# 查看当前模型路径配置
ollama list

# 或者查看环境变量是否设置成功
[Environment]::GetEnvironmentVariable("OLLAMA_MODELS", "Machine")
```

### 4.3 迁移已有模型（如需要）

如果之前已经在 C 盘下载了模型，可以迁移到新位置：

```powershell
# 1. 停止 Ollama
Stop-Process -Name ollama -Force

# 2. 复制模型文件到新目录
robocopy C:\Users\$env:USERNAME\.ollama\models D:\OllamaModels /E /MOVE

# 3. 确认复制成功后，删除原目录（可选）
# Remove-Item -Path C:\Users\$env:USERNAME\.ollama\models -Recurse -Force

# 4. 重启 Ollama
ollama serve
```

---

## 5. 下载模型

### 方法一：官方直接下载（推荐）

Ollama 官方使用 **Cloudflare R2 CDN**，在国内直接访问速度良好，无需代理。

```bash
# 直接下载（支持断点续传）
ollama pull qwen2.5:3b

# 如果中断，重新运行会继续下载
ollama pull qwen2.5:3b
```

> 💡 **提示**：如果官方下载速度确实很慢，可以尝试下面的镜像方案。

### 方法二：ModelScope 魔搭镜像（备选）

**项目**：ModelScope2Registry  
**GitHub**：https://github.com/onllama/Onllama.ModelScope2Registry

**原理**：通过 Azure 代理，从 ModelScope（魔搭社区）加速下载 GGUF 模型。

```bash
# 格式：
ollama run modelscope2ollama-registry.azurewebsites.net/<组织>/<模型名>

# 示例 - Qwen2.5-3B：
ollama run modelscope2ollama-registry.azurewebsites.net/qwen/Qwen2.5-3B-Instruct-gguf

# 使用短名称（推荐）
ollama cp modelscope2ollama-registry.azurewebsites.net/qwen/Qwen2.5-3B-Instruct-gguf qwen2.5:3b
ollama rm modelscope2ollama-registry.azurewebsites.net/qwen/Qwen2.5-3B-Instruct-gguf
```

> ⚠️ **注意**：ModelScope2Registry 是社区项目，可能随时失效。优先使用官方下载。

### 量化类型说明

| 量化类型 | 文件大小 | 精度 | 速度 | 适用场景 |
|----------|----------|------|------|----------|
| Q4_K_M | 最小 | 较低 | 最快 | CPU运行、快速测试 |
| Q4_0 | 小 | 中等 | 快 | 日常使用 |
| Q8_0 | 大 | 高 | 慢 | 精度要求高 |

---

## 6. 常用命令

### 模型管理

```powershell
# 列出已下载的模型
ollama list

# 拉取（下载）模型
ollama pull llama3.2
ollama pull qwen2.5
ollama pull deepseek-r1:14b

# 运行模型（如果未下载会自动下载）
ollama run llama3.2

# 删除模型
ollama rm llama3.2

# 查看模型信息
ollama show llama3.2
```

### 服务管理

```powershell
# 手动启动服务（默认后台自动运行）
ollama serve

# 查看帮助
ollama --help
```

### 运行时的常用操作

在 `ollama run` 交互界面中：

- `/bye` 或 `Ctrl + D` - 退出对话
- `/clear` - 清除对话历史
- `/help` - 显示帮助

---

## 7. 本地模型推荐与优化（集成显卡+32G内存）

本章节针对 **无独立显卡、32GB内存、中高端CPU** 的 Windows 配置，提供模型选择和性能优化建议。

### 7.1 推荐模型（CPU运行）

基于你的配置（32G内存+好CPU），推荐以下模型：

#### 🥇 轻量级模型（响应快，适合日常）

| 模型 | 大小 | 内存占用 | 特点 | 下载命令 |
|------|------|----------|------|----------|
| **Qwen2.5-3B** | 1.9GB | ~3GB | 中文最强，推荐首选 | `ollama pull qwen2.5:3b` |
| **Llama 3.2-3B** | 2.0GB | ~3GB | 英文好，通用强 | `ollama pull llama3.2:3b` |
| **DeepSeek-R1-1.5B** | 1.1GB | ~2GB | 推理能力强 | `ollama pull deepseek-r1:1.5b` |

**适用场景**：代码补全、文档查询、简单问答

#### 🥈 中端模型（性能平衡）

| 模型 | 大小 | 内存占用 | 特点 | 下载命令 |
|------|------|----------|------|----------|
| **Qwen2.5-7B** | 4.7GB | ~7GB | 中文能力强，推荐 | `ollama pull qwen2.5:7b` |
| **Llama 3.1-8B** | 4.9GB | ~8GB | 英文最强开源模型 | `ollama pull llama3.1:8b` |
| **DeepSeek-R1-7B** | 4.7GB | ~7GB | 推理能力突出 | `ollama pull deepseek-r1:7b` |

**适用场景**：复杂编程任务、深度技术讨论、长文档分析

#### 🥉 大模型（你的配置极限）

| 模型 | 大小 | 内存占用 | 特点 | 下载命令 |
|------|------|----------|------|----------|
| **Qwen2.5-14B** | 9.0GB | ~14GB | 接近GPT-3.5水平 | `ollama pull qwen2.5:14b` |
| **Llama 3.1-70B（Q4_K_M量化）** | 40GB | ~40GB | ⚠️ 超出你的内存，不推荐 | - |

> 💡 **建议**：32GB内存可以同时运行 **1个7B模型 + 1个3B模型**，或 **单独运行14B模型**。

---

### 7.2 性能优化配置

#### 优化1：启用多线程（关键）

默认Ollama只使用4个线程，修改环境变量利用更多CPU核心：

```powershell
# 设置使用的CPU线程数（根据你的CPU核心数调整，建议8-16）
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREAD", "12", "Machine")

# 重启Ollama生效
Stop-Process -Name ollama -Force
ollama serve
```

**建议设置**：
- 6核CPU → 设为 6
- 8核CPU → 设为 8-10
- 12核+CPU → 设为 12-16

#### 优化2：增加上下文长度

默认上下文较短，增加可处理更长的对话和代码：

```powershell
# 设置默认上下文长度（4096、8192、16384等）
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "8192", "Machine")
```

**注意**：
- 上下文越长，内存占用越多
- 3B模型建议 4096
- 7B模型建议 4096-8192
- 确保设置后仍有足够内存

#### 优化3：Modelfile 自定义配置

创建自定义配置文件，优化模型行为：

**示例：创建 qwen2.5-optimized** 

1. 创建 `Modelfile` 文件：
```dockerfile
FROM qwen2.5:7b

# 系统提示词（可选）
SYSTEM """你是一个专业的编程助手，擅长Java和Python开发。"""

# 参数优化
PARAMETER num_ctx 8192        # 上下文长度
PARAMETER num_thread 12       # CPU线程数
PARAMETER temperature 0.7     # 创造性（0-1，越低越确定）
PARAMETER top_p 0.9           # 采样多样性
```

2. 创建自定义模型：
```bash
ollama create qwen2.5-optimized -f Modelfile
```

3. 运行自定义模型：
```bash
ollama run qwen2.5-optimized
```

#### 优化4：GPU加速（如果你的集显支持）

虽然说是集成显卡，但如果较新（如Intel Iris Xe、AMD Radeon Vega），可能有支持：

```powershell
# 检查Ollama是否检测到GPU
ollama run qwen2.5:3b
# 在模型运行时查看任务管理器 -> 性能 -> GPU
```

**常见情况**：
- **Intel Iris Xe / AMD Vega**：可能有轻微加速，但不明显
- **Apple Silicon Mac（M1/M2/M3）**：有专门优化，但你是Windows
- **纯CPU**：大多数集成显卡的情况，依赖上述CPU优化

#### 优化5：系统级优化

**Windows 电源设置**：
1. 控制面板 → 电源选项 → 高性能模式
2. 确保CPU可以全速运行

**关闭不必要的程序**：
- 运行大模型时，关闭浏览器多余标签页
- 关闭其他占用内存的应用

**虚拟内存设置**（如果内存吃紧）：
1. 系统属性 → 高级 → 性能设置
2. 高级 → 虚拟内存 → 设置为自动管理或手动增加

---

### 7.3 推荐配置组合

#### 方案A：日常开发（推荐）

```powershell
# 环境变量设置
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREAD", "12", "Machine")
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "4096", "Machine")
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "D:\OllamaModels", "Machine")
```

**使用模型**：Qwen2.5-7B（主）+ Qwen2.5-3B（备用）

#### 方案B：最大性能（复杂任务）

```powershell
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREAD", "16", "Machine")
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "8192", "Machine")
```

**使用模型**：Qwen2.5-14B（单独运行）

#### 方案C：快速响应（简单任务）

```powershell
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREAD", "8", "Machine")
[Environment]::SetEnvironmentVariable("OLLAMA_CONTEXT_LENGTH", "2048", "Machine")
```

**使用模型**：Qwen2.5-3B

---

### 7.4 性能测试

测试你的配置能跑多快：

```bash
# 运行模型并观察速度
ollama run qwen2.5:7b

# 在对话中输入："请写一个简单的Python快速排序"
# 观察生成速度（tokens/秒）
```

**参考速度**（中高端CPU）：
- 3B模型：15-25 tokens/秒（流畅）
- 7B模型：8-15 tokens/秒（可用）
- 14B模型：4-8 tokens/秒（较慢但可用）

如果速度明显低于此，检查：
1. OLLAMA_NUM_THREAD 是否设置正确
2. 电源模式是否为高性能
3. 其他程序是否占用CPU

---

## 8. 与开发工具集成

### API 调用示例

Ollama 默认在本地 `http://localhost:11434` 提供服务：

```python
import requests

response = requests.post('http://localhost:11434/api/generate', json={
    "model": "llama3.2",
    "prompt": "你好，请介绍一下自己",
    "stream": False
})

print(response.json()['response'])
```

### 与 Continue/Kimi Code 等 AI 编程工具集成

在插件设置中添加 Ollama 配置：

```json
{
  "models": [
    {
      "title": "Llama 3.2 (Local)",
      "provider": "ollama",
      "model": "llama3.2",
      "apiBase": "http://localhost:11434"
    }
  ]
}
```

---

## 8. 常见问题

### Q1: 设置环境变量后路径没有变化？

- **确认**：完全退出并重新启动 Ollama（包括托盘图标）
- **确认**：新打开的终端窗口才能读取最新环境变量
- **检查**：环境变量是否设置到 "系统变量" 而非 "用户变量"

### Q2: 模型下载速度慢？

- 尝试使用代理或镜像
- 或者在网络较好的时段下载

### Q3: 如何查看当前使用的模型路径？

```powershell
# 查看 Ollama 运行时的环境变量
Get-Process ollama | Select-Object Environment
```

### Q4: 卸载 Ollama

1. 系统设置 → 应用 → 卸载 Ollama
2. 手动删除模型目录：`D:\OllamaModels`（或原来的 C 盘路径）
3. 删除配置文件：`C:\Users\{用户名}\.ollama\`

### Q5: 镜像站都不可用怎么办？

**使用下载工具是最佳选择：**
- 迅雷：自动寻找最快源
- IDM：多线程加速
- 或者用手机流量开热点下载

---

## 参考资源

- [Ollama 官方文档](https://github.com/ollama/ollama)
- [Ollama 模型库](https://ollama.com/library)
- [Windows 环境变量设置官方文档](https://learn.microsoft.com/zh-cn/windows/win32/procthread/environment-variables)

---

**最后更新**：2026年2月16日

**更新内容**：
- 添加国内镜像加速下载模型方案（ModelScope魔搭）
- 更新目录结构  
**更新说明**：镜像站经常变动，建议优先使用下载工具（迅雷/IDM）
