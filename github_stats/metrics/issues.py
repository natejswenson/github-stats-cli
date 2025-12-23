"""Issue statistics metric."""

from typing import Dict, Any
from github import GithubException
from github_stats.metrics.base import BaseMetric


class IssueMetric(BaseMetric):
    """Analyze issue creation and management activity."""

    def __init__(self, github_client, username: str):
        """Initialize issue metric."""
        super().__init__(github_client, username)
        self.total_issues = 0
        self.open_issues = 0
        self.closed_issues = 0

    #---------------------------------------------------------
    # Main execution
    #---------------------------------------------------------

    def fetch(self) -> None:
        """Fetch issue data using GitHub search API."""
        try:
            # Search for issues created by user (excluding PRs)
            query = f"type:issue author:{self.username}"
            issues = self.github_client.search_issues(query)

            # Count total issues
            self.total_issues = issues.totalCount

            # Sample to categorize by state
            open_count = 0
            closed_count = 0

            count = 0
            for issue in issues:
                # Limit sampling to avoid rate limits
                if count >= 100:
                    break
                count += 1

                if issue.state == 'open':
                    open_count += 1
                else:
                    closed_count += 1

            # Calculate estimates based on sample
            if count > 0:
                open_ratio = open_count / count
                self.open_issues = int(self.total_issues * open_ratio)
                self.closed_issues = self.total_issues - self.open_issues
            else:
                self.open_issues = 0
                self.closed_issues = 0

            self.data = {
                'total': self.total_issues,
                'open': self.open_issues,
                'closed': self.closed_issues
            }

        except GithubException:
            # If search fails, return empty data
            self.data = {'total': 0, 'open': 0, 'closed': 0}

    def process(self) -> None:
        """Process issue data to calculate statistics."""
        if not self.data or self.data['total'] == 0:
            self.close_rate = 0
            return

        # Calculate close rate
        if self.data['total'] > 0:
            self.close_rate = (self.data['closed'] / self.data['total']) * 100
        else:
            self.close_rate = 0

    def get_summary(self) -> str:
        """
        Get brief summary of issue statistics.

        Returns:
            Summary string in format "X issues, Y% closed"
        """
        if self.total_issues == 0:
            return "0, No issues"

        return f"{self.total_issues:,}, {int(self.close_rate)}% closed"

    def get_detailed(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of issue statistics.

        Returns:
            Dictionary with detailed issue information
        """
        return {
            'total_issues': self.total_issues,
            'open': self.open_issues,
            'closed': self.closed_issues,
            'close_rate': self.close_rate
        }
