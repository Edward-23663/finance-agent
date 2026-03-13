from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container
from rich.console import Console

console = Console()


class FinanceAgentTUI(App):
    """金融分析智能体 TUI"""

    CSS = """
    Screen {
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("金融分析智能体 - TUI 控制台", classes="title"),
        )
        yield Footer()

    def on_mount(self) -> None:
        console.print("[bold green]金融分析智能体 TUI 启动成功[/bold green]")


if __name__ == "__main__":
    app = FinanceAgentTUI()
    app.run()
