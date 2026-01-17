"""Pytest fixtures for github-stats-cli integration tests."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


@pytest.fixture
def mock_user():
    """Create a mock GitHub user."""
    user = Mock()
    user.login = "testuser"
    user.followers = 100
    user.following = 50
    return user


@pytest.fixture
def mock_repo():
    """Create a mock GitHub repository."""
    repo = Mock()
    repo.name = "test-repo"
    repo.stargazers_count = 25

    # Mock commits
    mock_commits = [Mock() for _ in range(5)]
    repo.get_commits = Mock(return_value=iter(mock_commits))

    return repo


@pytest.fixture
def mock_repos(mock_repo):
    """Create a list of mock repositories."""
    repos = []
    for i, name in enumerate(["repo-1", "repo-2", "repo-3"]):
        repo = Mock()
        repo.name = name
        repo.stargazers_count = (i + 1) * 10
        commits = [Mock() for _ in range(i + 1)]
        repo.get_commits = Mock(return_value=iter(commits))
        repos.append(repo)
    return repos


@pytest.fixture
def mock_github_client(mock_user, mock_repos):
    """Create a mock GitHub client with common responses."""
    client = Mock()

    # Mock user retrieval
    client.get_user = Mock(return_value=mock_user)
    mock_user.get_repos = Mock(return_value=iter(mock_repos))

    # Mock rate limit
    rate_limit = Mock()
    rate_limit.core = Mock()
    rate_limit.core.remaining = 4500
    rate_limit.core.limit = 5000
    rate_limit.core.reset = datetime.now()
    client.get_rate_limit = Mock(return_value=rate_limit)

    # Mock search for PRs and issues
    mock_pr_results = Mock()
    mock_pr_results.totalCount = 10
    mock_pr_results.__iter__ = Mock(return_value=iter([
        Mock(state='open', pull_request=True),
        Mock(state='closed', pull_request=True),
        Mock(state='closed', pull_request=True),
    ]))

    mock_issue_results = Mock()
    mock_issue_results.totalCount = 5
    mock_issue_results.__iter__ = Mock(return_value=iter([
        Mock(state='open'),
        Mock(state='closed'),
        Mock(state='closed'),
    ]))

    def search_issues_side_effect(query):
        if 'type:pr' in query:
            return mock_pr_results
        elif 'type:issue' in query:
            return mock_issue_results
        return Mock(totalCount=0, __iter__=Mock(return_value=iter([])))

    client.search_issues = Mock(side_effect=search_issues_side_effect)

    return client


@pytest.fixture
def mock_env_token(monkeypatch):
    """Set up mock environment with GitHub token."""
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token_12345")


@pytest.fixture
def mock_no_token(monkeypatch):
    """Remove GitHub token from environment."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_PAT", raising=False)
