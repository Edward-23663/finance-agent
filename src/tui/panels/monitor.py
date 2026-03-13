from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, ProgressBar
from textual.widget import Widget
from rich.console import Console

console = Console()


class MonitorPanel(Widget):
    """监控面板"""

    def compose(self) -> ComposeResult:
        with Vertical(id="monitor"):
            yield Static("系统监控", classes="panel-title")
            yield Static("Agent状态:", id="agent_status")
            yield ProgressBar(total=100, show_eta=False)

    async def update_status(self):
        """更新监控状态"""
        try:
            import redis.asyncio as redis

            r = redis.Redis(host="localhost", port=6379, db=0)
            await r.ping()
            console.print("Redis连接: 正常")
            await r.close()
        except Exception as e:
            console.print(f"Redis连接: 失败 - {e}")
