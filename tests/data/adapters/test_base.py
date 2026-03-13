"""数据源适配器基类测试"""
import pytest
from src.data.adapters.base import DataSourceAdapter


class TestDataSourceAdapter:
    """数据源适配器测试"""

    def test_abstract_methods(self):
        """测试抽象方法"""
        with pytest.raises(TypeError):
            DataSourceAdapter()
