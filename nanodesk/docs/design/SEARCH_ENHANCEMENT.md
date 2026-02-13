# 搜索能力强化设计

> 无需 API Key 的搜索解决方案评估与设计

**提案状态**: 📝 设计阶段  
**优先级**: 低-中  
**核心约束**: ❌ 无需 API Key  

---

## 现状分析

### 现有搜索工具

| 工具 | 实现 | 状态 | 优点 | 缺点 |
|------|------|------|------|------|
| `ddg_search` | DuckDuckGo (ddgs 包) | ✅ 可用 | 无需 API Key、隐私友好 | 偶尔 Rate Limit、结果质量一般 |
| `browser_search` | Playwright + Google/Bing | ⚠️ 需 Playwright | 结果真实、无需 API | 需手动安装 Playwright、慢、CAPTCHA |
| `browser_fetch` | Playwright 页面抓取 | ⚠️ 需 Playwright | 可获取 JS 渲染内容 | 同上 |

### 现有问题

1. **ddg_search Rate Limiting**
   ```
   频繁查询时返回: "202 Ratelimit"
   需要等待冷却或重试
   ```

2. **结果质量不稳定**
   - DDG 搜索结果有时不如 Google 全面
   - 无高级搜索语法支持（site:, filetype: 等）

3. **无本地缓存**
   - 重复查询浪费请求
   - 离线时完全不可用

4. **无多源聚合**
   - 单一来源，失败即完全失败
   - 无法对比多个引擎结果

---

## 目标

### 核心需求

| 需求 | 优先级 | 说明 |
|------|--------|------|
| 无需 API Key | 必须 | 个人使用，不想管理 Key |
| 稳定可靠 | 高 | 减少 Rate Limit，提高可用性 |
| 结果质量 | 中 | 比现有 DDG 更好或至少持平 |
| 响应速度 | 中 | 不显著慢于现有方案 |
| 隐私可控 | 低 | 可选，不强制 |

### 用户体验目标

```
用户: "搜索 Python 3.12 新特性"
     ↓
Agent: 自动选择最佳搜索源
     ↓
结果: 快速返回，无需用户关心背后实现
```

---

## 方案评估

### 方案 1: 多源聚合 + 智能切换（推荐）

**架构**

```
用户查询
   ↓
[搜索调度器]
   ↓         ↓         ↓
DDG      SearXNG    本地缓存
(默认)   (备用)     (加速)
   ↓         ↓         ↓
[结果聚合]
   ↓
[去重排序]
   ↓
返回结果
```

**组件**

```python
# nanodesk/tools/search_enhanced.py

class EnhancedSearchTool(Tool):
    """
    多源聚合搜索，无需 API Key
    自动切换、缓存、重试
    """
    
    SOURCES = [
        ("ddg", DDGSource(), priority=1),      # 默认
        ("searxng", SearXNGSource(), priority=2),  # 备用
        ("wikipedia", WikipediaSource(), priority=3),  # 知识查询
    ]
    
    async def execute(
        self, 
        query: str,
        source: str | None = None,  # 指定源，None=自动
        use_cache: bool = True,
        max_results: int = 10
    ) -> str:
        
        # 1. 检查缓存
        if use_cache:
            cached = await self._get_cache(query)
            if cached:
                return cached
        
        # 2. 按优先级尝试源
        for name, source_impl, _ in self.SOURCES:
            if source and name != source:
                continue
                
            try:
                results = await source_impl.search(query, max_results)
                if results:
                    # 缓存并返回
                    if use_cache:
                        await self._set_cache(query, results)
                    return results
            except RateLimitError:
                logger.warning(f"{name} rate limited, trying next")
                continue
            except Exception as e:
                logger.error(f"{name} error: {e}")
                continue
        
        return "Error: All search sources exhausted"
```

**搜索源实现**

| 源 | 无需 API Key | 部署需求 | 质量 | 可靠性 |
|---|------------|---------|------|--------|
| **DuckDuckGo** | ✅ | 无 | 中 | 中（Rate Limit） |
| **SearXNG** | ✅ | 自托管 | 高 | 高（可控） |
| **Wikipedia** | ✅ | 无 | 高（知识） | 高 |
| **GitHub** | ✅ | 无 | 高（代码） | 高（60/hour） |
| **ArXiv** | ✅ | 无 | 高（学术） | 高 |

**SearXNG 自托管选项**

```yaml
# docker-compose.yml 示例
version: '3'
services:
  searxng:
    image: searxng/searxng
    ports:
      - "8080:8080"
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080
    volumes:
      - ./searxng:/etc/searxng
```

**成本对比**

| 方案 | 月度成本 | 维护成本 | 效果 |
|------|---------|---------|------|
| DDG 单源 | 免费 | 低 | 中 |
| SearXNG (本地) | 免费 | 中 | 高 |
| SearXNG (VPS) | $3-5/月 | 低 | 高 |
| Brave API | 免费 (2k/月) | 低 | 高 |

**优点**
- 多源冗余，单点失败自动切换
- 可配置本地缓存，减少重复请求
- 扩展性好，新增源只需实现接口

**缺点**
- SearXNG 需要自托管（可选）
- 代码复杂度比单源高

---

### 方案 2: DDG 优化增强（轻量）

不增加新源，优化现有 DDG 实现：

```python
class DDGSearchEnhanced(Tool):
    """
    增强版 DuckDuckGo 搜索
    缓存 + 重试 + 结果优化
    """
    
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=3600)  # 1小时缓存
        self.rate_limiter = AsyncLimiter(max_rate=1, time_period=2)  # 2秒1次
    
    async def execute(self, query: str, **kwargs) -> str:
        # 1. 检查缓存
        if query in self.cache:
            return self.cache[query]
        
        # 2. 速率限制
        async with self.rate_limiter:
            # 3. 指数退避重试
            for attempt in range(3):
                try:
                    results = await self._search(query)
                    self.cache[query] = results
                    return results
                except RateLimitError:
                    wait = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait}s")
                    await asyncio.sleep(wait)
            
            return "Error: Rate limit exceeded, please try later"
    
    async def _search(self, query: str) -> str:
        # 添加随机延迟，模拟人类行为
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # 使用多个 DDG 区域（轮换）
        regions = ["wt-wt", "us-en", "uk-en"]
        region = random.choice(regions)
        
        return await ddgs.AsyncDDGS().text(query, region=region)
```

**优化点**

| 优化 | 效果 | 实现难度 |
|------|------|---------|
| 本地缓存 | 减少 50%+ 请求 | 低 |
| 速率限制 | 避免 Rate Limit | 低 |
| 指数退避 | 提高成功率 | 低 |
| 多区域轮换 | 分散请求压力 | 低 |
| 随机延迟 | 模拟人类行为 | 低 |

**优点**
- 无需额外部署
- 改动小，风险低

**缺点**
- 本质仍是单一源
- 无法突破 DDG 本身限制

---

### 方案 3: 混合模式（特定场景）

针对不同查询类型，自动选择最佳源：

```python
class HybridSearchTool(Tool):
    """
    基于查询类型选择最佳搜索源
    """
    
    # 查询类型识别规则
    RULES = [
        (r"^(what is|how to|why does|definition of)", "wikipedia"),
        (r"(github\.com|code|library|package)", "github"),
        (r"(paper|arxiv|research|study)", "arxiv"),
        (r"(latest news|today|current)", "ddg"),  # 实时性
        (r".*", "ddg"),  # 默认
    ]
    
    async def execute(self, query: str) -> str:
        source = self._detect_source(query)
        
        sources = {
            "wikipedia": WikipediaSearch(),
            "github": GitHubSearch(),
            "arxiv": ArXivSearch(),
            "ddg": DDGSearch(),
        }
        
        return await sources[source].search(query)
```

**场景匹配**

| 查询示例 | 推荐源 | 原因 |
|---------|--------|------|
| "Python 是什么" | Wikipedia | 知识准确、结构化 |
| "pandas github" | GitHub | 直接访问仓库 |
| "attention is all you need" | ArXiv | 学术论文 |
| "今日科技新闻" | DDG | 实时性 |
| "Python 教程" | DDG | 泛化查询 |

**优点**
- 针对性强，结果质量高
- 各源优势互补

**缺点**
- 需要维护识别规则
- 误判时效果反而差

---

## 推荐方案

### 短期（立即实施）：方案 2 + 方案 3 轻量版

```
改进现有 ddg_search:
├── 添加本地缓存 (TTLCache)
├── 添加速率限制 (AsyncLimiter)
├── 添加重试机制
└── 简单查询分类 (Wikipedia/GitHub/ArXiv)

不增加部署负担，提升现有体验
```

### 长期（可选）：方案 1 完整版

```
如果短期方案仍不满足:
└── 部署 SearXNG (Docker)
    ├── 获得 Google/Bing 质量结果
    ├── 无 Rate Limit
    └── 完全可控
```

---

## 实施路线图

```
Phase 1: DDG 增强 (1-2 天)
├── 添加缓存层 (diskcache/TTLCache)
├── 添加速率限制和重试
├── 优化错误提示
└── 添加使用统计

Phase 2: 多源扩展 (2-3 天)
├── 实现 WikipediaSource
├── 实现 GitHubSource
├── 实现查询分类器
└── 添加源切换命令 /search source <name>

Phase 3: SearXNG 集成 (可选，1 天)
├── SearXNGSource 实现
├── Docker Compose 配置
└── 文档和部署指南
```

---

## 决策点

| 问题 | 选项 A | 选项 B |
|------|--------|--------|
| 是否部署 SearXNG? | 否（保持简单） | 是（获得最佳体验） |
| 是否添加 Wikipedia/GitHub? | 是（轻量增强） | 否（只用 DDG） |
| 缓存存储位置? | 内存 (TTLCache) | 磁盘 (diskcache) |

**建议决策**:
- 先实现 Phase 1（DDG 增强），评估效果
- 如果仍不满足，再考虑 SearXNG 自托管

---

## 参考资源

- [SearXNG 文档](https://docs.searxng.org/)
- [DuckDuckGo 速率限制说明](https://duckduckgo.com/duckduckgo-help-pages/results/rate-limiting/)
- [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page)
- [GitHub Search API](https://docs.github.com/en/rest/search)

---

**下一步**: 确认方案后，从 Phase 1 开始实现
