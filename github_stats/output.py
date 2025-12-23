#---------------------------------------------------------
# Centralized output helper functions for console printing
#---------------------------------------------------------

from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


#---------------------------------------------------------
# Basic print functions
#---------------------------------------------------------

def print_newline() -> None:
    console.print()


def print_text(text: str) -> None:
    console.print(text)


def print_table(table: Table) -> None:
    console.print(table)


#---------------------------------------------------------
# Styled message functions
#---------------------------------------------------------

def print_error(message: str) -> None:
    console.print(f"[red]Error:[/red] {message}")


def print_warning(message: str) -> None:
    console.print(f"[yellow]Warning:[/yellow] {message}")


def print_info(message: str) -> None:
    console.print(f"[dim]{message}[/dim]")


def print_success(message: str) -> None:
    console.print(f"[green]{message}[/green]")


#---------------------------------------------------------
# Panel and header functions
#---------------------------------------------------------

def print_panel(text: str, box_style: box.Box = box.ROUNDED, border_style: str = "cyan") -> None:
    console.print(Panel(text, box=box_style, border_style=border_style))


def print_header(text: str, box_style: box.Box = box.ROUNDED, border_style: str = "cyan") -> None:
    print_newline()
    print_panel(text, box_style, border_style)
    print_newline()


#---------------------------------------------------------
# Specific use-case functions
#---------------------------------------------------------

def print_rate_limit(remaining: int, limit: int) -> None:
    percentage = (remaining / limit * 100) if limit > 0 else 0

    # Choose color based on remaining percentage
    if percentage > 50:
        color = "green"
    elif percentage > 20:
        color = "yellow"
    else:
        color = "red"

    print_newline()
    console.print(f"[dim]Rate Limit: [{color}]{remaining:,}[/{color}]/{limit:,} remaining[/dim]")
    print_newline()


def print_low_rate_limit_warning(remaining: int) -> None:
    console.print(f"[yellow]Warning: Low API rate limit ({remaining} remaining)[/yellow]")
    print_info("The app may not be able to fetch all metrics.\n")


def print_auth_error() -> None:
    print_error("GitHub token not found.")
    print_newline()
    print_text("To use this CLI, you need a GitHub Personal Access Token.")
    print_text("1. Create a token at: https://github.com/settings/tokens")
    print_text("2. Set it as an environment variable:")
    print_text("   export GITHUB_TOKEN=your_token_here")
    print_newline()
    print_text("Or copy .env.example to .env and add your token there.")


def print_auth_failed(error_message: str) -> None:
    console.print(f"[red]Error: Authentication failed - {error_message}[/red]")
    print_newline()
    print_text("Please check that your token is valid and has the required scopes.")
