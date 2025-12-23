
# -------------------------------------------------------------
# # Display utilities using Rich for beautiful terminal output.
# -------------------------------------------------------------

from typing import Dict, List, Any
from datetime import datetime
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from github_stats.output import console, print_header as output_print_header, print_rate_limit, print_error, print_warning


#---------------------------------------------------------
# Main display functions
#---------------------------------------------------------

HEADER_STYLE = "cyan"
HEADER_BOX = box.ROUNDED


def display_header(username: str) -> None:
    text = (
        "[bold cyan]GitHub Stats for:[/bold cyan] "
        f"[bold white]{username}[/bold white]"
    )
    output_print_header(text, HEADER_BOX, HEADER_STYLE)

#---------------------------------------------------------
# Summary table display
#---------------------------------------------------------
def create_summary_table(metrics_data: Dict[str, Dict[str, Any]]) -> Table:
    table = Table(box=box.ROUNDED, border_style="cyan", show_header=True, header_style="bold cyan")

    # Add columns
    table.add_column("Metric", style="bold white", no_wrap=True)
    table.add_column("Value", style="bold green", justify="right")
    table.add_column("Details", style="dim white")

    # Add rows for each metric
    for metric_name, data in metrics_data.items():
        value = data.get('value', 'N/A')
        details = data.get('details', '')

        # Format large numbers with commas
        if isinstance(value, int):
            value = f"{value:,}"

        table.add_row(metric_name, str(value), details)

    return table

#---------------------------------------------------------
# Progress bar and rate limit display
#---------------------------------------------------------
def create_progress_bar() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    )

#---------------------------------------------------------
# Rate limit display
#---------------------------------------------------------
def display_rate_limit_warning(remaining: int, limit: int) -> None:
    print_rate_limit(remaining, limit)


#---------------------------------------------------------
# Helper functions
#---------------------------------------------------------
def format_number(num: int) -> str:
    units = [
        (1_000_000_000, "B"),
        (1_000_000, "M"),
        (1_000, "K"),
    ]

    for factor, suffix in units:
        if num >= factor:
            return f"{num / factor:.1f}{suffix}"
    return str(num)


def display_error(message: str) -> None:
    print_error(message)


def display_warning(message: str) -> None:
    print_warning(message)
