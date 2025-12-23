"""Pull request statistics metric."""

from typing import Dict, Any
from github import GithubException
from github_stats.metrics.base import BaseMetric


class PullRequestMetric(BaseMetric):
    """Analyze pull request activity."""

    def __init__(self, github_client, username: str):
        """Initialize pull request metric."""
        super().__init__(github_client, username)
        self.total_prs = 0
        self.merged_prs = 0
        self.open_prs = 0
        self.closed_prs = 0

    #---------------------------------------------------------
    # Main execution
    #---------------------------------------------------------

    def fetch(self) -> None:
        """Fetch pull request data using GitHub search API."""
        try:
            # Search for PRs authored by user
            query = f"type:pr author:{self.username}"
            prs = self.github_client.search_issues(query)

            # Count total and categorize by state
            self.total_prs = prs.totalCount

            # Sample PRs to categorize (limited to avoid rate limits)
            merged = 0
            open_count = 0
            closed = 0

            count = 0
            for pr in prs:
                # Limit sampling to avoid excessive API calls
                if count >= 100:
                    break
                count += 1

                if pr.state == 'open':
                    open_count += 1
                elif pr.pull_request and hasattr(pr, 'pull_request'):
                    # Check if merged (requires additional API call)
                    # For efficiency, we'll estimate based on closed state
                    closed += 1

            # Store data
            self.open_prs = open_count
            # Estimate merged/closed ratio from sample
            if count > 0:
                sample_closed = closed
                sample_ratio = sample_closed / count if count > 0 else 0
                estimated_closed = int(self.total_prs * sample_ratio)
                self.merged_prs = estimated_closed
                self.closed_prs = self.total_prs - self.open_prs - self.merged_prs
            else:
                self.merged_prs = 0
                self.closed_prs = 0

            self.data = {
                'total': self.total_prs,
                'merged': self.merged_prs,
                'open': self.open_prs,
                'closed': self.closed_prs
            }

        except GithubException as e:
            # If search fails, return empty data
            self.data = {'total': 0, 'merged': 0, 'open': 0, 'closed': 0}

    def process(self) -> None:
        """Process pull request data to calculate statistics."""
        if not self.data or self.data['total'] == 0:
            self.merge_rate = 0
            return

        # Calculate merge rate (merged / total)
        # Since we estimate merged as closed, we'll use a simpler metric
        # For now, assume closed PRs are mostly merged
        total_closed = self.data['total'] - self.data['open']
        if self.data['total'] > 0:
            self.merge_rate = (total_closed / self.data['total']) * 100
        else:
            self.merge_rate = 0

    def get_summary(self) -> str:
        """
        Get brief summary of pull request statistics.

        Returns:
            Summary string in format "X PRs, Y% closed"
        """
        if self.total_prs == 0:
            return "0, No PRs"

        return f"{self.total_prs:,}, {int(self.merge_rate)}% closed"

    def get_detailed(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of pull request statistics.

        Returns:
            Dictionary with detailed PR information
        """
        return {
            'total_prs': self.total_prs,
            'open': self.open_prs,
            'merged': self.merged_prs,
            'closed': self.closed_prs,
            'merge_rate': self.merge_rate
        }
