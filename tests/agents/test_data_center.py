"""数据中心Agent测试"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.data_center import DataCenterAgent
from src.agents.base import AgentConfig


class TestDataCenterAgent:
    """数据中心Agent测试类"""

    @pytest.fixture
    def config(self):
        return AgentConfig(
            name="data_center", stream_key="tasks:data_center", consumer_group="data_center_group"
        )

    @pytest.fixture
    def agent(self, config):
        with patch("src.agents.data_center.DuckDBClient"), patch(
            "src.agents.data_center.LanceDBClient"
        ), patch("src.agents.data_center.RedisClient"):
            return DataCenterAgent(config)

    @pytest.mark.asyncio
    async def test_query_price_success(self, agent):
        """测试查询行情数据成功"""
        mock_result = [
            {"ticker": "600519", "trade_date": "2024-01-02", "close": 1800.5},
            {"ticker": "600519", "trade_date": "2024-01-03", "close": 1815.2},
        ]
        agent.duckdb.execute = Mock(return_value=mock_result)
        agent.redis.get = AsyncMock(return_value=None)
        agent.redis.set = AsyncMock()

        result = await agent.execute(
            {
                "type": "query_price",
                "ticker": "600519",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            }
        )

        assert result["status"] == "success"
        assert result["count"] == 2
        assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_query_price_from_cache(self, agent):
        """测试从缓存读取行情数据"""
        cached_data = '[{"ticker": "600519", "close": 1800.5}]'
        agent.redis.get = AsyncMock(return_value=cached_data)

        result = await agent.execute(
            {
                "type": "query_price",
                "ticker": "600519",
                "start_date": "2024-01-01",
                "end_date": "2024-01-10",
            }
        )

        assert result["status"] == "success"
        assert result["source"] == "cache"

    @pytest.mark.asyncio
    async def test_query_financial(self, agent):
        """测试查询财务数据"""
        mock_result = [{"ticker": "600519", "report_date": "2024-12-31", "roe": 0.25}]
        agent.duckdb.execute = Mock(return_value=mock_result)

        result = await agent.execute({"type": "query_financial", "ticker": "600519"})

        assert result["status"] == "success"
        assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_query_stock_info(self, agent):
        """测试查询股票基本信息"""
        mock_result = [{"ticker": "600519", "name": "贵州茅台", "industry": "白酒"}]
        agent.duckdb.execute = Mock(return_value=mock_result)

        result = await agent.execute({"type": "query_stock_info", "ticker": "600519"})

        assert result["status"] == "success"
        assert result["data"]["name"] == "贵州茅台"

    @pytest.mark.asyncio
    async def test_cache_get(self, agent):
        """测试获取缓存"""
        agent.redis.get = AsyncMock(return_value="test_value")

        result = await agent.execute({"type": "cache_get", "key": "test:key"})

        assert result["status"] == "success"
        assert result["value"] == "test_value"

    @pytest.mark.asyncio
    async def test_cache_set(self, agent):
        """测试设置缓存"""
        agent.redis.set = AsyncMock()

        result = await agent.execute(
            {"type": "cache_set", "key": "test:key", "value": "test_value", "ttl": 60}
        )

        assert result["status"] == "success"
        assert result["key"] == "test:key"
        agent.redis.set.assert_called_once_with("test:key", "test_value", ttl=60)

    @pytest.mark.asyncio
    async def test_query_vector(self, agent):
        """测试向量相似度检索"""
        mock_results = [{"text": "茅台财报分析", "score": 0.95, "metadata": {"ticker": "600519"}}]
        agent.lancedb.search = Mock(return_value=mock_results)

        result = await agent.execute(
            {"type": "query_vector", "text": "贵州茅台财务报表分析", "top_k": 5}
        )

        assert result["status"] == "success"
        assert len(result["results"]) == 1

    @pytest.mark.asyncio
    async def test_data_lake_manage(self, agent):
        """测试数据湖管理"""
        agent.duckdb.execute = Mock(return_value=[{"count": 100}])

        async def fake_acquire_lock(self, resource):
            class FakeLock:
                async def __aenter__(self):
                    return None

                async def __aexit__(self, *args):
                    pass

            return FakeLock()

        agent.__class__._acquire_lock = fake_acquire_lock

        result = await agent.execute(
            {
                "type": "data_lake_manage",
                "operation": "sync",
                "tickers": ["600519"],
                "data_types": ["price", "financial"],
            }
        )

        assert result["status"] == "success"
        assert result["processed"] == 1

    @pytest.mark.asyncio
    async def test_dispatch_data_access(self, agent):
        """测试数据访问调度"""
        agent.duckdb.execute = Mock(return_value=[{"count": 50}])
        agent.redis.set = AsyncMock()

        result = await agent.execute(
            {
                "type": "dispatch_data_access",
                "agent_id": "fundamental_agent",
                "tickers": ["600519"],
                "data_types": ["price"],
                "priority": "high",
            }
        )

        assert result["status"] == "success"
        assert result["agent_id"] == "fundamental_agent"

    @pytest.mark.asyncio
    async def test_aggregate_query(self, agent):
        """测试跨源数据聚合查询"""
        mock_price = [{"ticker": "600519", "close": 1800.5}]
        mock_financial = [{"ticker": "600519", "roe": 0.25}]

        def mock_execute(query, params):
            if "price_daily" in query:
                return mock_price
            elif "financial_metrics" in query:
                return mock_financial
            return []

        agent.duckdb.execute = Mock(side_effect=mock_execute)
        agent.lancedb.search = Mock(return_value=[])

        result = await agent.execute(
            {
                "type": "aggregate_query",
                "ticker": "600519",
                "metrics": ["price", "financial", "news"],
                "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
            }
        )

        assert result["status"] == "success"
        assert "price" in result["aggregated_data"]
        assert "financial" in result["aggregated_data"]

    @pytest.mark.asyncio
    async def test_unknown_task_type(self, agent):
        """测试未知任务类型"""
        with pytest.raises(ValueError, match="Unknown task type"):
            await agent.execute({"type": "unknown_type"})
