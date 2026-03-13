# 金融分析智能体 - 软件设计文档

## 一、项目概述

### 1.1 项目定位

个人本地私有化部署的金融分析智能体工具，无需依赖云端服务核心运行能力。通过多维度智能体协作，为个人投资者提供专业、可解释、可定制的金融分析能力。

### 1.2 核心约束

| 约束项 | 值 |
|--------|-----|
| 部署环境 | 个人PC（资源有限） |
| 数据规模 | 1-10GB中等规模 |
| 用户数 | 单用户 |
| 并发任务 | 无需并发 |
| 开发方式 | TDD（分阶段） |
| 交付方式 | 6个Phase分阶段交付 |

---

## 二、架构设计

### 2.1 整体架构拓扑

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级1: 独立展现层 UI Layer                           │
│  ┌──────────────────────────────┐     ┌─────────────────────────────────┐ │
│  │     WEB UI (nano banana)     │     │    TUI (Rich库)                │ │
│  │  - 任务提交/结果展示/流式输出 │     │  - LLM配置/监控/调试/系统配置 │ │
│  └──────────────────────────────┘     └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    HTTP + SSE 流式推送
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级2: 网关与接入层 API Gateway                      │
│  ┌────────────────┐      ┌─────────────────────────────────────────────┐  │
│  │ Nginx Alpine   │─────▶│       FastAPI Backend (RESTful + SSE)        │  │
│  └────────────────┘      └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    带 Trace_ID 的任务指令
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                    层级3: 核心调度层 Core Orchestration                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    轻量化主编排智能体 (Main Agent)                   │  │
│  │  [DAG任务拆解] → [5态状态机] → [Trace_ID追踪] → [异常重试兜底]     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    JSON-RPC 2.0 / Redis Streams 异步通信
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                      层级4: 垂直分智能体执行层 Sub-Agents                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ [1]数据采集 │ [2]行业持仓 │ [3]基本面分析 │ [4]多模型估值            │  │
│  │ [5]舆情分析 │ [6]催化剂   │ [7]综合思维   │ [8]报告生成             │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    向下调用原子能力
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                    层级5: 技能与模型适配层 Skills & LLM                     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │   分层Skills: 原子级 → 组合级 → 业务级 (插件化配置驱动)             │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────┐     ┌─────────────────────────────────────┐  │
│  │   LLM Adapter 层       │     │   FastEmbed (本地量化向量化)        │  │
│  │  - OpenAI兼容接口      │     │  - CPU异步处理                      │  │
│  │  - 熔断降级/重试超时   │     │  - 严格资源隔离                     │  │
│  └────────────────────────┘     └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    并发控制: Agent只读查询，写操作入Redis队列
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                      层级6: 本地数据与中间件层 Data & Middleware             │
│  ┌──────────┐  ┌──────────────────┐  ┌─────────┐  ┌──────────┐             │
│  │Redis     │  │   DuckDB         │  │LanceDB  │  │SQLite    │             │
│  │(消息队列)│  │ (单文件分析数据库)│  │(内嵌向量)│  │(轻量日志)│             │
│  └──────────┘  └──────────────────┘  └─────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心设计原则

| 原则 | 描述 |
|------|------|
| 计算与解释分离 | 所有数值计算在Python/DuckDB，LLM仅负责基于硬事实的填空式渲染 |
| 主编排器轻量化 | 只做DAG拆解、状态机、重试、追踪 |
| 单线程写DuckDB | DataWriterWorker串行消费写指令，避免锁冲突 |
| Agent只读查询 | 写入一律入Redis Stream队列 |
| 插件化Skills | 配置驱动加载，无需修改核心代码 |
| TUI与WEB解耦 | TUI负责配置运维，WEB负责业务交互 |

---

## 三、模块详细设计

### 3.1 主编排智能体 (Main Orchestrator)

#### 3.1.1 核心职责

- 任务拆解与分发
- 分智能体生命周期管理
- 跨智能体结果聚合
- 异常兜底与重试（3次机制）
- Skills调用权限/优先级管控
- 用户指令意图解析
- 智能体间通信调度

#### 3.1.2 状态机设计

```
任务状态流转：
pending → running → completed / failed / partial_success
```

| 状态 | 描述 |
|------|------|
| pending | 任务已创建，等待调度 |
| running | 任务正在执行中 |
| completed | 任务成功完成 |
| failed | 任务执行失败 |
| partial_success | 部分成功（部分子任务失败） |

#### 3.1.3 Redis Key设计

```
任务状态: task:{trace_id}:status → 状态值
任务进度: task:{trace_id}:progress → JSON进度信息
任务结果: task:{trace_id}:result → JSON结果
子任务列表: task:{trace_id}:subtasks → JSON数组
```

#### 3.1.4 Trace_ID链路追踪

每个用户请求生成唯一Trace_ID，格式：`{timestamp}_{random_8char}`

追踪信息存储在Redis Hash中：
```
trace:{trace_id} → {
  "user_input": "...",
  "created_at": "...",
  "status": "...",
  "agents_involved": ["agent1", "agent2"],
  "skills_called": ["skill1", "skill2"],
  "errors": []
}
```

### 3.2 分智能体体系

#### 3.2.1 Agent列表

| 编号 | Agent名称 | 核心功能 |
|------|-----------|----------|
| 1 | 数据采集Agent | 多源数据抓取、清洗、标准化 |
| 2 | 行业持仓分析Agent | 行业分类、轮动分析、持仓性价比 |
| 3 | 基本面分析Agent | 财务分析、杜邦拆解、造假检测 |
| 4 | 多模型估值Agent | DCF/PE/PB/PS/PEG/DDM估值 |
| 5 | 舆情分析Agent | 情感分析、风险预警、事件聚类 |
| 6 | 催化剂分析Agent | 催化剂事件识别、时间节点分析 |
| 7 | 综合思维Agent | 多模型融合、非线性分析 |
| 8 | 报告生成Agent | 结构化报告、流式输出 |

**注：共8个垂直分智能体 + 1个主编排智能体 = 9个Agent**

#### 3.2.2 Agent进程模型

每个Agent作为独立进程运行，通过Redis Streams通信：

```python
# Agent基类架构
class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.stream_key = f"agent:{name}"
        self.consumer_group = f"group:{name}"
        
    async def start(self):
        # 创建消费者组
        await self.redis.xgroup_create(
            self.stream_key, 
            self.consumer_group, 
            id='0', 
            mkstream=True
        )
        # 消费消息
        await self.consume()
        
    async def consume(self):
        while True:
            messages = await self.redis.xreadgroup(
                groupname=self.consumer_group,
                consumername=os.getenv('HOSTNAME', 'worker'),
                streams={self.stream_key: '>'},
                count=1,
                block=5000
            )
            for msg in messages:
                result = await self.process(msg)
                await self.redis.xack(self.stream_key, self.consumer_group, msg.id)
                # 发布结果到结果队列
                await self.publish_result(msg.trace_id, result)
```

### 3.3 Skills分层设计

#### 3.3.1 分层规范

| 层级 | 描述 | 示例 |
|------|------|------|
| 原子级 | 最小不可拆分功能单元 | PE计算、单条舆情情感打分 |
| 组合级 | 多个原子级Skill组合 | 财务健康度=五大比率+造假检测 |
| 业务级 | 面向用户场景的端到端功能 | 贵州茅台基本面全维度分析 |

#### 3.3.2 Skill接口规范

```python
# 原子级Skill模板
class AtomicSkill(ABC):
    name: str  # Skill名称
    version: str  # 版本号
    input_schema: dict  # 输入JSON Schema
    output_schema: dict  # 输出JSON Schema
    
    @abstractmethod
    def execute(self, params: dict) -> dict:
        """执行Skill，返回结果"""
        pass
    
    @abstractmethod
    def validate_input(self, params: dict) -> bool:
        """验证输入参数"""
        pass
```

#### 3.3.3 Skills注册机制

```yaml
# skills_config.yaml
skills:
  - name: "pe_calculator"
    module: "skills.atomic.financial.pe_calculator"
    class: "PECalculator"
    level: "atomic"
    enabled: true
    config:
      max_pe_threshold: 100
      
  - name: "financial_health_score"
    module: "skills.composite.financial.health_score"
    class: "FinancialHealthScore"
    level: "composite"
    enabled: true
    depends_on:
      - "pe_calculator"
      - "pb_calculator"
      - "fraud_detector"
```

### 3.4 数据中心设计

#### 3.4.1 DuckDB表结构

```sql
-- 股票基础信息
CREATE TABLE stock_info (
    ticker VARCHAR PRIMARY KEY,
    name VARCHAR,
    industry VARCHAR,
    list_date DATE,
    market_type VARCHAR
);

-- 行情数据
CREATE TABLE price_daily (
    ticker VARCHAR,
    trade_date DATE,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    amount DECIMAL(20,2),
    PRIMARY KEY (ticker, trade_date)
);

-- 财务报表（带版本）
CREATE TABLE financial_statements (
    ticker VARCHAR,
    report_date DATE,
    report_type VARCHAR,
    version INTEGER DEFAULT 1,
    revenue DECIMAL(20,2),
    net_profit DECIMAL(20,2),
    total_assets DECIMAL(20,2),
    total_liabilities DECIMAL(20,2),
    equity DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ticker, report_date, report_type, version)
);

-- 财务指标
CREATE TABLE financial_metrics (
    ticker VARCHAR,
    report_date DATE,
    report_type VARCHAR,
    roe DECIMAL(10,4),
    roa DECIMAL(10,4),
    gross_margin DECIMAL(10,4),
    net_margin DECIMAL(10,4),
    current_ratio DECIMAL(10,4),
    debt_ratio DECIMAL(10,4),
    eps DECIMAL(10,4),
    bps DECIMAL(10,4),
    PRIMARY KEY (ticker, report_date, report_type)
);

-- 估值数据
CREATE TABLE valuations (
    ticker VARCHAR,
    valuation_date DATE,
    pe DECIMAL(10,2),
    pb DECIMAL(10,2),
    ps DECIMAL(10,2),
    peg DECIMAL(10,2),
    dcf_value DECIMAL(20,2),
    ddm_value DECIMAL(20,2),
    fair_value_low DECIMAL(20,2),
    fair_value_mid DECIMAL(20,2),
    fair_value_high DECIMAL(20,2),
    PRIMARY KEY (ticker, valuation_date)
);

-- 舆情数据
CREATE TABLE news_sentiment (
    id VARCHAR PRIMARY KEY,
    ticker VARCHAR,
    title TEXT,
    content TEXT,
    publish_date TIMESTAMP,
    sentiment_score DECIMAL(5,4),
    sentiment_label VARCHAR,
    source VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 催化剂事件
CREATE TABLE catalyst_events (
    id VARCHAR PRIMARY KEY,
    ticker VARCHAR,
    event_type VARCHAR,
    event_date DATE,
    title TEXT,
    description TEXT,
    impact_score DECIMAL(5,2),
    impact_direction VARCHAR,
    source VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 任务执行记录
CREATE TABLE task_history (
    trace_id VARCHAR PRIMARY KEY,
    user_input TEXT,
    status VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP,
    result JSON,
    error_message TEXT
);
```

#### 3.4.2 数据版本管理

```python
# 财务数据版本控制
class VersionedDataManager:
    def write_financial_data(self, ticker: str, report_date: str, 
                            report_type: str, data: dict):
        # 查询最新版本号
        current_version = self.get_current_version(ticker, report_date, report_type)
        
        # 写入新版本
        self.db.execute("""
            INSERT INTO financial_statements 
            (ticker, report_date, report_type, version, ...)
            VALUES (?, ?, ?, ?, ...)
        """, [ticker, report_date, report_type, current_version + 1, ...])
        
    def get_latest_data(self, ticker: str, report_date: str, 
                        report_type: str) -> dict:
        # 只返回最新版本
        return self.db.execute("""
            SELECT * FROM financial_statements
            WHERE ticker = ? AND report_date = ? AND report_type = ?
            ORDER BY version DESC LIMIT 1
        """, [ticker, report_date, report_type]).fetchone()
```

#### 3.4.3 并发控制机制

```python
# DataWriter单线程消费者
class DataWriterWorker:
    """串行消费写指令，避免DuckDB锁冲突"""
    
    def __init__(self):
        self.redis = RedisClient()
        self.queue_key = "data:write:queue"
        self.db = duckdb.connect(DUCKDB_PATH)
        
    async def run(self):
        while True:
            # 阻塞读取写指令
            result = self.redis.blpop(self.queue_key)
            if result:
                task = json.loads(result[1])
                await self.execute_write(task)
                
    async def execute_write(self, task: dict):
        # 根据task类型执行不同写操作
        if task['type'] == 'financial_statement':
            await self.write_financial(task)
        elif task['type'] == 'price_daily':
            await self.write_price(task)
        # ...
```

### 3.5 LLM适配器设计

#### 3.5.1 统一接口

```python
class LLMAdapter(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], 
                   temperature: float = 0.7,
                   max_tokens: int = 2000) -> str:
        """发送聊天请求"""
        pass
    
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[np.ndarray]:
        """生成文本嵌入"""
        pass

class OpenAIAdapter(LLMAdapter):
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        
class AnthropicAdapter(LLMAdapter):
    # Anthropic Claude适配器
    
class LocalAdapter(LLMAdapter):
    # 本地模型适配器（ Ollama / LM Studio ）
```

#### 3.5.2 熔断降级机制

```python
class LLMCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "closed"  # closed / open / half_open
        
    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            # 返回降级结果
            return {"error": "circuit_open", "fallback": True}
            
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
```

### 3.6 FastEmbed本地向量化

```python
class EmbeddingService:
    """本地向量化服务，CPU资源隔离"""
    
    def __init__(self, max_workers: int = 2):
        self.model = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            max_workers=max_workers  # 限制CPU使用
        )
        
    async def embed_async(self, texts: list[str]) -> list[np.ndarray]:
        """异步向量化，避免阻塞"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: list(self.model.embed(texts))
        )
        
    def chunk_and_embed(self, text: str, 
                        chunk_size: int = 512,
                        overlap: int = 50) -> list[np.ndarray]:
        """长文本分块向量化"""
        chunks = self.split_text(text, chunk_size, overlap)
        return list(self.model.embed(chunks))
```

---

## 四、API接口设计

### 4.1 FastAPI后端接口

#### 4.1.1 任务管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/tasks | 创建分析任务 |
| GET | /api/v1/tasks/{trace_id} | 查询任务状态 |
| GET | /api/v1/tasks/{trace_id}/result | 获取任务结果 |
| DELETE | /api/v1/tasks/{trace_id} | 取消任务 |

#### 4.1.2 SSE流式

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/stream/{trace_id} | SSE流式输出 |

#### 4.1.3 数据查询

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/stocks/{ticker} | 股票基本信息 |
| GET | /api/v1/stocks/{ticker}/price | 行情数据 |
| GET | /api/v1/stocks/{ticker}/financial | 财务数据 |
| GET | /api/v1/stocks/{ticker}/valuation | 估值数据 |
| GET | /api/v1/stocks/{ticker}/news | 舆情数据 |

#### 4.1.4 配置管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/config/llm | 获取LLM配置 |
| PUT | /api/v1/config/llm | 更新LLM配置 |
| GET | /api/v1/config/agents | 获取Agent状态 |
| PUT | /api/v1/config/agents | 更新Agent配置 |

#### 4.1.5 系统

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/health | 健康检查 |
| GET | /api/v1/metrics | 系统指标 |

### 4.2 请求/响应格式

```json
// POST /api/v1/tasks 请求
{
  "user_input": "分析贵州茅台的基本面和估值",
  "ticker": "600519",
  "analysis_types": ["fundamental", "valuation"],
  "options": {
    "report_format": "markdown",
    "include_charts": true
  }
}

// 响应
{
  "trace_id": "20240313_abc12345",
  "status": "pending",
  "created_at": "2024-03-13T10:00:00Z",
  "estimated_time": 120
}
```

---

## 五、TUI设计

### 5.1 功能模块

```
┌────────────────────────────────────────────┐
│     金融分析智能体 - TUI 控制台             │
├────────────────────────────────────────────┤
│ [1] LLM配置                                │
│   - API密钥管理 (加密存储)                 │
│   - 模型选择 (GPT-4o/Claude/通义/文心...) │
│   - 调用参数 (temperature, max_tokens)    │
│                                            │
│ [2] 后台监控                               │
│   - Agent运行状态 ●●●○○                    │
│   - Skills调用统计                         │
│   - LLM API成功率/耗时                     │
│   - 容器/进程状态                         │
│                                            │
│ [3] 调试工具                               │
│   - Agent单步调试                         │
│   - Skills独立测试                         │
│   - LLM API测试                           │
│   - 日志实时查看                          │
│                                            │
│ [4] 系统配置                               │
│   - 缓存策略                              │
│   - 重试参数                              │
│   - Agent启用/禁用                        │
│   - 数据源配置                            │
│                                            │
│ [Q] 退出                                   │
└────────────────────────────────────────────┘
```

### 5.2 实现技术

- **Rich库**: 表格、进度条、颜色输出
- **Textual库**: 交互式TUI框架
- **SQLite**: 日志存储

---

## 六、Docker部署设计

### 6.1 docker-compose.yml

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - fastapi

  fastapi:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/home/user/.finance_agent
    environment:
      - REDIS_HOST=redis
      - DUCKDB_PATH=/home/user/.finance_agent/finance.db
      - LANCEDB_PATH=/home/user/.finance_agent/vectors
    depends_on:
      redis:
        condition: service_healthy

volumes:
  redis_data:
```

### 6.2 启动顺序

```yaml
# depends_on + healthcheck确保启动顺序
depends_on:
  redis:
    condition: service_healthy
```

---

## 七、测试策略

### 7.1 测试分层

| 层级 | 测试内容 | 工具 |
|------|----------|------|
| 单元测试 | 原子级Skill计算逻辑 | pytest |
| 集成测试 | Agent间通信、数据层读写 | pytest + Mock |
| 端到端 | 完整任务流程 | pytest + Integration |
| 性能测试 | 数据量增长下的性能 | pytest-benchmark |

### 7.2 TDD开发流程

```
1. 先写测试用例（定义接口契约）
2. 运行测试（预期失败）
3. 实现功能代码
4. 运行测试（通过）
5. 重构优化
6. 提交代码
```

---

## 八、交付计划

### Phase 1: 骨架工程 (2周)
- 项目结构、目录初始化
- 主编排器核心（DAG拆解、状态机、Trace_ID）
- Redis Streams通信基础
- **交付**: 可运行的空框架

### Phase 2: 数据中心 (2周)
- DuckDB核心表结构设计
- LanceDB向量存储集成
- SQLite配置管理
- DataWriter单线程写机制
- **交付**: 本地数据湖Demo

### Phase 3: 核心Agent (3周)
- 数据采集Agent + 采集Skills
- 基本面分析Agent + 财务分析Skills
- 多模型估值Agent + 估值Skills
- 报告生成Agent + 报告Skills
- **交付**: 4个核心Agent可独立运行

### Phase 4: 后端API + TUI (2周)
- FastAPI后端完整API开发
- TUI配置/监控面板
- 与nano banana的对接适配
- API文档编写
- **交付**: 完整后端API + TUI

### Phase 5: 补充Agent + RAG (2周)
- 行业持仓分析Agent
- 舆情分析Agent + FastEmbed
- 催化剂分析Agent
- 综合思维Agent
- **交付**: 全部8个分智能体 + 1个主编排

### Phase 6: 集成测试 (2周)
- 联调压测
- Docker容器化
- 文档编写
- **交付**: 完整可部署系统

**预计总工期: 13周**

---

## 九、关键指标

| 指标 | 目标 | 落地手段 |
|------|------|----------|
| 启动时间 | ≤10秒 | 懒加载Agents + 连接池预热 |
| 任务成功率 | ≥99% | 幂等键 + 重试 + 断点续跑 |
| 内存占用 | ≤2GB | Worker进程池 + FastEmbed并发限制 |
| 稳定性 | 7x24小时 | 心跳检测 + Watchdog自动拉起 |
| 中间件内存 | ≤1GB | Redis/SQLite/LanceDB合计 |

---

## 十、待确认事项

1. **nano banana WEB UI参考代码**: 用户提供后进行适配
2. **LLM API具体供应商**: 待用户配置
3. **数据源API密钥**: 待用户提供

---

## 十一、补充设计（审查修复）

### 11.1 安全认证机制

由于是单用户本地部署，采用简化认证方案：

```python
# API Key认证
API_KEY_HEADER = "X-API-Key"

# 生成API Key
def generate_api_key() -> str:
    return secrets.token_hex(32)

# 认证依赖
async def verify_api_key(x_api_key: str = Header(...)):
    stored_key = get_config("api_key")
    if not stored_key:
        # 首次启动生成
        stored_key = generate_api_key()
        save_config("api_key", stored_key)
    if x_api_key != stored_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

# 受保护接口示例
@app.post("/api/v1/tasks", dependencies=[Depends(verify_api_key)])
async def create_task(...):
    pass
```

**TUI本地认证说明：**
- TUI作为本地客户端，启动时自动读取本地存储的API Key
- API Key存储在 `~/.finance_agent/config/api_key` 文件中
- TUI发起HTTP请求时自动在Header中携带API Key
- 用户首次启动时自动生成并展示API Key（仅显示一次，需用户保存）

### 11.2 Agent依赖关系矩阵

```
数据流向图：
用户输入
    │
    ▼
┌─────────────────────────────────────┐
│        报告生成Agent (依赖全部)       │
└─────────────────────────────────────┘
    ▲    ▲    ▲    ▲    ▲    ▲    ▲
    │    │    │    │    │    │    │
┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐
│行 ││基 ││估 ││舆 ││催 ││综 │
│业 ││本 ││值 ││情 ││化 ││合 │
│持 ││面 ││Agent││剂 ││思 ││
│仓 ││分 ││   ││分 ││分 ││维 │
│析 ││析 ││   ││析 ││析 ││ |
└───┘└───┘└───┘└───┘└───┘└───┘
    │    │    │    │    │    │
    └────┴────┴────┴────┴────┘
                 │
    ┌────────────┴────────────┐
    │      数据采集Agent        │
    └────────────┬────────────┘
                 │
    ┌────────────┴────────────┐
    │       数据中心           │
    └─────────────────────────┘
```

| Agent | 依赖Agent | 数据输入 | 输出 |
|-------|-----------|----------|------|
| 数据采集 | - | API数据源 | 原始数据 |
| 行业持仓 | 数据采集 | 行业数据 | 持仓分析 |
| 基本面分析 | 数据采集 | 财务数据 | 健康评分 |
| 多模型估值 | 基本面分析 | 估值数据 | 估值区间 |
| 舆情分析 | 数据采集 | 新闻数据 | 情感评分 |
| 催化剂 | 数据采集 | 事件数据 | 催化剂清单 |
| 综合思维 | 基本面+估值+舆情+催化剂 | 融合数据 | 综合结论 |
| 报告生成 | 全部Agent | 全部输出 | 最终报告 |

### 11.3 数据采集方案

#### 11.3.1 数据源配置

```python
# 数据源适配器
class DataSourceAdapter(ABC):
    @abstractmethod
    def get_price(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_financial(self, ticker: str, report_type: str) -> dict:
        pass

class TushareAdapter(DataSourceAdapter):
    """Tushare数据源（主力）"""
    def __init__(self, token: str):
        self.client = Tushare(token)
        
class AkShareAdapter(DataSourceAdapter):
    """AkShare数据源（补充）"""
    pass

class YFinanceAdapter(DataSourceAdapter):
    """YFinance数据源（海外）"""
    pass
```

#### 11.3.2 采集任务调度

```python
# 数据采集调度器
class DataCollectionScheduler:
    def __init__(self):
        self.scheduler = APScheduler()
        
    def setup_jobs(self):
        # 每日收盘后更新行情
        self.scheduler.add_job(
            self.update_daily_price,
            'cron',
            hour=16,
            minute=0
        )
        
        # 财报发布后更新财务数据
        self.scheduler.add_job(
            self.update_financial,
            'cron',
            month='1,4,7,10',
            day=15,
            hour=9
        )
        
        # 实时新闻采集
        self.scheduler.add_job(
            self.update_news,
            'interval',
            minutes=30
        )
```

### 11.4 缓存策略设计

```python
# Redis缓存策略
CACHE_STRATEGY = {
    # 热点数据缓存5分钟
    "hot_stock_price": {"ttl": 300, "key": "price:{ticker}"},
    # 财务数据缓存1小时
    "financial_metrics": {"ttl": 3600, "key": "fin:{ticker}:{date}"},
    # 估值数据缓存4小时
    "valuation": {"ttl": 14400, "key": "val:{ticker}"},
    # 用户配置不缓存
    "user_config": {"ttl": 0},
}

class CacheManager:
    def get(self, category: str, key: str) -> Optional[dict]:
        full_key = f"{category}:{key}"
        cached = self.redis.get(full_key)
        return json.loads(cached) if cached else None
        
    def set(self, category: str, key: str, value: dict):
        config = CACHE_STRATEGY.get(category, {"ttl": 300})
        full_key = f"{category}:{key}"
        self.redis.setex(full_key, config["ttl"], json.dumps(value))
```

### 11.5 日志规范

```python
# 统一JSON日志格式
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

# 日志级别策略
# DEBUG: 开发调试
# INFO: 正常业务流程
# WARNING: 可恢复异常（重试成功）
# ERROR: 不可恢复异常（需人工介入）
```

### 11.6 API统一修复

原问题：`/stream/{task_id}` 与 `trace_id` 不一致

修复：统一使用 `trace_id`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/stream/{trace_id} | SSE流式输出（修正） |
