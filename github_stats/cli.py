#---------------------------------------------------------
# CLI entry point for github-stats
#---------------------------------------------------------

import argparse
import sys
from typing import Dict, Any, List
from github import GithubException
from dotenv import load_dotenv

from github_stats.auth import get_github_client, check_rate_limit
from github_stats.display import (
    display_header,
    create_summary_table,
    create_progress_bar,
    display_rate_limit_warning,
    display_error
)
from github_stats.output import (
    print_low_rate_limit_warning,
    print_table,
    print_warning
)

# Load environment variables from .env file if it exists
load_dotenv()


#---------------------------------------------------------
# Main execution
#---------------------------------------------------------

def main() -> None:
    args = parse_arguments()
    try:
        github_client = get_github_client(args.token)
    except SystemExit:
        return

    # Check rate limit
    rate_info = check_rate_limit(github_client)
    if rate_info['remaining'] < 50:
        print_low_rate_limit_warning(rate_info['remaining'])

    # Verify username exists
    try:
        user = github_client.get_user(args.username)
        user.login  # Trigger API call to validate user exists
    except GithubException as e:
        display_error(f"User '{args.username}' not found or inaccessible.")
        sys.exit(1)

    # Display header
    display_header(args.username)

    # Collect metrics
    metrics_data = collect_metrics(github_client, args.username)

    # Display results
    if metrics_data:
        table = create_summary_table(metrics_data)
        print_table(table)
        display_rate_limit_warning(rate_info['remaining'], rate_info['limit'])
    else:
        display_error("No metrics could be collected.")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Display beautiful GitHub profile statistics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  github-stats octocat
  github-stats torvalds --token ghp_your_token
  python -m github_stats username
        """
    )

    parser.add_argument(
        'username',
        help='GitHub username to analyze'
    )

    parser.add_argument(
        '--token',
        help='GitHub Personal Access Token (overrides GITHUB_TOKEN env var)',
        default=None
    )

    return parser.parse_args()


def collect_metrics(github_client, username: str) -> Dict[str, Dict[str, Any]]:
    # Import metrics (these will be implemented next)
    try:
        from github_stats.metrics.commits import CommitMetric
        from github_stats.metrics.followers import FollowerMetric
        from github_stats.metrics.stars import StarMetric
        from github_stats.metrics.pull_requests import PullRequestMetric
        from github_stats.metrics.issues import IssueMetric
    except ImportError:
        # Metrics not yet implemented
        display_error("Metric modules not found. Please ensure all metrics are implemented.")
        return {}

    # Define metrics to collect
    metrics = {
        'Commits': CommitMetric(github_client, username),
        'Followers': FollowerMetric(github_client, username),
        'Stars': StarMetric(github_client, username),
        'Pull Requests': PullRequestMetric(github_client, username),
        'Issues': IssueMetric(github_client, username),
    }

    results = {}

    # Collect each metric with progress indication
    with create_progress_bar() as progress:
        for metric_name, metric in metrics.items():
            task = progress.add_task(f"Fetching {metric_name}...", total=None)

            try:
                metric.collect()
                results[metric_name] = {
                    'value': metric.get_summary().split(',')[0].strip() if ',' in metric.get_summary() else metric.get_summary(),
                    'details': metric.get_summary().split(',', 1)[1].strip() if ',' in metric.get_summary() else ''
                }
                progress.update(task, completed=True)
            except Exception as e:
                # Continue with other metrics if one fails
                print_warning(f"Failed to fetch {metric_name}: {str(e)}")
                continue

    return results


if __name__ == '__main__':
    main()
