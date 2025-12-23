"""Base metric class for all GitHub statistics collectors."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from github import Github


class BaseMetric(ABC):
    """
    Abstract base class for GitHub metrics.

    All metric classes should inherit from this and implement
    the required abstract methods.
    """

    def __init__(self, github_client: Github, username: str):
        """
        Initialize the metric.

        Args:
            github_client: Authenticated PyGithub client
            username: GitHub username to analyze
        """
        self.github_client = github_client
        self.username = username
        self.data: Any = None

    @abstractmethod
    def fetch(self) -> None:
        """
        Fetch data from GitHub API.

        This method should retrieve all necessary data from the GitHub API
        and store it in self.data for processing.
        """
        pass

    @abstractmethod
    def process(self) -> None:
        """
        Process the fetched data.

        This method should transform the raw API data into a format
        suitable for display.
        """
        pass

    @abstractmethod
    def get_summary(self) -> str:
        """
        Get a brief one-line summary of the metric.

        Returns:
            Brief summary string for overview display
        """
        pass

    @abstractmethod
    def get_detailed(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of the metric.

        Returns:
            Dictionary containing detailed metric information
        """
        pass

    #---------------------------------------------------------
    # Main execution
    #---------------------------------------------------------

    def collect(self) -> None:
        """
        Collect and process the metric data.

        This is a convenience method that calls fetch() and process()
        in sequence.
        """
        self.fetch()
        self.process()
