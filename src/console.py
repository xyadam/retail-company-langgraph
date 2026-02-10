from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()


def print_step(label: str, message: str):
    console.print(f"  [dim]{label}[/dim] {message}")


def print_sql(sql: str, label: str = None):
    title = f"[bold cyan]{label}[/bold cyan]" if label else "[bold cyan]Generated SQL[/bold cyan]"
    console.print(Panel(
        Syntax(sql, "sql", theme="monokai", word_wrap=True),
        title=title,
        border_style="cyan",
    ))


def print_error(message: str):
    console.print(f"  [bold red]Error:[/bold red] {message[:200]}")


def print_report(text: str):
    console.print(Panel(
        Markdown(text),
        title="[bold green]Report[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))
