"""Follower statistics metric."""

from typing import Dict, Any
from github_stats.metrics.base import BaseMetric


class FollowerMetric(BaseMetric):
    """Analyze follower and following statistics."""

    def __init__(self, github_client, username: str):
        """Initialize follower metric."""
        super().__init__(github_client, username)
        self.followers_count = 0
        self.following_count = 0

    #---------------------------------------------------------
    # Main execution
    #---------------------------------------------------------

    def fetch(self) -> None:
        """Fetch follower and following counts."""
        user = self.github_client.get_user(self.username)

        # Get follower and following counts
        self.followers_count = user.followers
        self.following_count = user.following

        self.data = {
            'followers': self.followers_count,
            'following': self.following_count
        }

    def process(self) -> None:
        """Process follower data to calculate statistics."""
        if not self.data:
            return

        # Calculate follower/following ratio
        if self.following_count > 0:
            self.ratio = self.followers_count / self.following_count
        else:
            self.ratio = float('inf') if self.followers_count > 0 else 0

    def get_summary(self) -> str:
        """
        Get brief summary of follower statistics.

        Returns:
            Summary string in format "X followers, Following: Y"
        """
        return f"{self.followers_count:,}, Following: {self.following_count:,}"

    def get_detailed(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of follower statistics.

        Returns:
            Dictionary with detailed follower information
        """
        return {
            'followers': self.followers_count,
            'following': self.following_count,
            'ratio': self.ratio if hasattr(self, 'ratio') else 0
        }
