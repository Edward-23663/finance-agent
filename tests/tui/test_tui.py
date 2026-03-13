import pytest


class TestTUI:
    """TUI测试"""

    def test_tui_imports(self):
        """测试TUI模块导入"""
        from src.tui.main import FinanceAgentTUI

        assert FinanceAgentTUI is not None

    def test_config_panel_imports(self):
        """测试配置面板导入"""
        from src.tui.panels.config import ConfigPanel

        assert ConfigPanel is not None

    def test_monitor_panel_imports(self):
        """测试监控面板导入"""
        from src.tui.panels.monitor import MonitorPanel

        assert MonitorPanel is not None
