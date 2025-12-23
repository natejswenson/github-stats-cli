"""Star statistics metric."""

from typing import Dict, Any
from github import GithubException
from github_stats.metrics.base import BaseMetric


class StarMetric(BaseMetric):
    """Analyze repository star statistics."""

    def __init__(self, github_client, username: str):
        """Initialize star metric."""
        super().__init__(github_client, username)
        self.total_stars = 0
        self.top_repo = None
        self.repo_stars = {}

    #---------------------------------------------------------
    # Main execution
    #---------------------------------------------------------

    def fetch(self) -> None:
        """Fetch star data from all user repositories."""
        user = self.github_client.get_user(self.username)
        repos = user.get_repos()

        self.repo_stars = {}

        for repo in repos:
            try:
                stars = repo.stargazers_count
                if stars > 0:
                    self.repo_stars[repo.name] = stars
            except GithubException:
                # Skip repos we can't access
                continue

        self.data = self.repo_stars

    def process(self) -> None:
        """Process star data to calculate statistics."""
        if not self.data:
            self.total_stars = 0
            self.top_repo = None
            return

        # Calculate total stars received
        self.total_stars = sum(self.data.values())

        # Find most starred repository
        if self.data:
            self.top_repo = max(self.data.items(), key=lambda x: x[1])

    def get_summary(self) -> str:
        """
        Get brief summary of star statistics.

        Returns:
            Summary string in format "X stars, Top: repo_name"
        """
        if self.total_stars == 0:
            return "0, No stars"

        if self.top_repo:
            repo_name, stars = self.top_repo
            return f"{self.total_stars:,}, Top: {repo_name} ({stars:,})"
        else:
            return f"{self.total_stars:,}, "

    def get_detailed(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of star statistics.

        Returns:
            Dictionary with detailed star information
        """
        # Sort repos by star count
        sorted_repos = sorted(
            self.data.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            'total_stars': self.total_stars,
            'repositories_with_stars': len(self.data),
            'top_repositories': sorted_repos[:10],  # Top 10 starred repos
            'average_per_repo': self.total_stars // len(self.data) if self.data else 0
        }
