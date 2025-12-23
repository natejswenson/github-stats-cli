"""Commit statistics metric."""

from typing import Dict, Any, List
from github import GithubException
from github_stats.metrics.base import BaseMetric


class CommitMetric(BaseMetric):
    """Analyze commit activity across all user repositories."""

    def __init__(self, github_client, username: str):
        """Initialize commit metric."""
        super().__init__(github_client, username)
        self.total_commits = 0
        self.top_repo = None
        self.repo_commits = {}

    #---------------------------------------------------------
    # Main execution
    #---------------------------------------------------------

    def fetch(self) -> None:
        """Fetch commit data from all user repositories."""
        user = self.github_client.get_user(self.username)
        repos = user.get_repos()

        self.repo_commits = {}

        for repo in repos:
            try:
                # Only count commits authored by this user
                commits = repo.get_commits(author=self.username)

                # Count commits (limited to avoid rate limit issues)
                count = 0
                try:
                    # PyGithub's totalCount can be unreliable, so we iterate
                    for _ in commits:
                        count += 1
                        # Limit to avoid excessive API calls per repo
                        if count >= 1000:
                            break
                except GithubException:
                    # If we can't access commits, skip this repo
                    continue

                if count > 0:
                    self.repo_commits[repo.name] = count

            except GithubException:
                # Skip repos we can't access (private, deleted, etc.)
                continue

        self.data = self.repo_commits

    def process(self) -> None:
        """Process commit data to calculate statistics."""
        if not self.data:
            self.total_commits = 0
            self.top_repo = None
            return

        # Calculate total commits
        self.total_commits = sum(self.data.values())

        # Find top repository by commits
        if self.data:
            self.top_repo = max(self.data.items(), key=lambda x: x[1])

    def get_summary(self) -> str:
        """
        Get brief summary of commit statistics.

        Returns:
            Summary string in format "X commits, Most: repo_name"
        """
        if self.total_commits == 0:
            return "0, No commits found"

        if self.top_repo:
            repo_name, count = self.top_repo
            return f"{self.total_commits:,}, Most: {repo_name} ({count:,})"
        else:
            return f"{self.total_commits:,}, "

    def get_detailed(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of commit statistics.

        Returns:
            Dictionary with detailed commit information
        """
        # Sort repos by commit count
        sorted_repos = sorted(
            self.data.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            'total_commits': self.total_commits,
            'repositories': len(self.data),
            'top_repositories': sorted_repos[:10],  # Top 10 repos
            'average_per_repo': self.total_commits // len(self.data) if self.data else 0
        }
