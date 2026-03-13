from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Input, Button
from textual.widget import Widget
from rich.console import Console

console = Console()


class ConfigPanel(Widget):
    """LLM配置面板"""

    def compose(self) -> ComposeResult:
        with Vertical(id="config"):
            yield Static("LLM 配置", classes="panel-title")
            yield Input(placeholder="API Key", id="api_key")
            yield Input(placeholder="Base URL", id="base_url")
            yield Input(placeholder="Model Name", id="model")
            yield Button("保存配置", id="save_config")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_config":
            console.print("[green]配置已保存[/green]")
