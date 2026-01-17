"""Integration tests for GitHub authentication module."""

import pytest
from unittest.mock import Mock, patch
from github import GithubException

from github_stats.auth import get_github_client, check_rate_limit, _load_token_from_env


class TestLoadTokenFromEnv:
    """Tests for loading token from environment variables."""

    def test_loads_github_token(self, monkeypatch):
        """Should load token from GITHUB_TOKEN environment variable."""
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
        monkeypatch.delenv("GITHUB_PAT", raising=False)

        token = _load_token_from_env()

        assert token == "ghp_test_token"

    def test_loads_github_pat(self, monkeypatch):
        """Should load token from GITHUB_PAT if GITHUB_TOKEN not set."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.setenv("GITHUB_PAT", "ghp_pat_token")

        token = _load_token_from_env()

        assert token == "ghp_pat_token"

    def test_prefers_github_token_over_pat(self, monkeypatch):
        """Should prefer GITHUB_TOKEN over GITHUB_PAT."""
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_primary")
        monkeypatch.setenv("GITHUB_PAT", "ghp_secondary")

        token = _load_token_from_env()

        assert token == "ghp_primary"

    def test_returns_none_when_no_token(self, mock_no_token):
        """Should return None when no token is set."""
        token = _load_token_from_env()

        assert token is None


class TestGetGithubClient:
    """Tests for getting an authenticated GitHub client."""

    def test_uses_provided_token(self, monkeypatch):
        """Should use token passed as argument over environment."""
        monkeypatch.setenv("GITHUB_TOKEN", "env_token")

        with patch('github_stats.auth.Github') as MockGithub:
            mock_client = Mock()
            mock_user = Mock()
            mock_user.login = "testuser"
            mock_client.get_user.return_value = mock_user
            MockGithub.return_value = mock_client

            client = get_github_client("arg_token")

            MockGithub.assert_called_with("arg_token")

    def test_falls_back_to_env_token(self, mock_env_token):
        """Should use environment token when none provided."""
        with patch('github_stats.auth.Github') as MockGithub:
            mock_client = Mock()
            mock_user = Mock()
            mock_user.login = "testuser"
            mock_client.get_user.return_value = mock_user
            MockGithub.return_value = mock_client

            client = get_github_client(None)

            MockGithub.assert_called_with("ghp_test_token_12345")

    def test_exits_when_no_token_available(self, mock_no_token):
        """Should exit with error when no token is available."""
        with pytest.raises(SystemExit):
            get_github_client(None)

    def test_exits_on_invalid_token(self, mock_env_token):
        """Should exit when token validation fails."""
        with patch('github_stats.auth.Github') as MockGithub:
            mock_client = Mock()
            mock_client.get_user.side_effect = GithubException(
                401, {"message": "Bad credentials"}, None
            )
            MockGithub.return_value = mock_client

            with pytest.raises(SystemExit):
                get_github_client("invalid_token")


class TestCheckRateLimit:
    """Tests for rate limit checking functionality."""

    def test_returns_rate_limit_info(self):
        """Should return dictionary with rate limit information."""
        mock_client = Mock()
        mock_rate_limit = Mock()
        mock_rate_limit.core.remaining = 4500
        mock_rate_limit.core.limit = 5000
        mock_rate_limit.core.reset = Mock()
        mock_client.get_rate_limit.return_value = mock_rate_limit

        result = check_rate_limit(mock_client)

        assert result['remaining'] == 4500
        assert result['limit'] == 5000
        assert result['percentage'] == 90.0

    def test_handles_zero_limit(self):
        """Should handle zero limit gracefully."""
        mock_client = Mock()
        mock_rate_limit = Mock()
        mock_rate_limit.core.remaining = 0
        mock_rate_limit.core.limit = 0
        mock_rate_limit.core.reset = Mock()
        mock_client.get_rate_limit.return_value = mock_rate_limit

        result = check_rate_limit(mock_client)

        assert result['remaining'] == 0
        assert result['limit'] == 0
        assert result['percentage'] == 0
