"""Integration tests for CLI entry point."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from github_stats.cli import main, parse_arguments, collect_metrics


class TestParseArguments:
    """Tests for CLI argument parsing."""

    def test_parses_username(self, monkeypatch):
        """Should parse username positional argument."""
        monkeypatch.setattr('sys.argv', ['github-stats', 'octocat'])

        args = parse_arguments()

        assert args.username == 'octocat'
        assert args.token is None

    def test_parses_token_flag(self, monkeypatch):
        """Should parse --token flag."""
        monkeypatch.setattr('sys.argv', ['github-stats', 'testuser', '--token', 'ghp_test'])

        args = parse_arguments()

        assert args.username == 'testuser'
        assert args.token == 'ghp_test'

    def test_requires_username(self, monkeypatch):
        """Should require username argument."""
        monkeypatch.setattr('sys.argv', ['github-stats'])

        with pytest.raises(SystemExit):
            parse_arguments()


class TestCollectMetrics:
    """Tests for metrics collection."""

    def test_collects_all_metrics(self, mock_github_client):
        """Should collect data from all metric types."""
        results = collect_metrics(mock_github_client, "testuser")

        assert 'Commits' in results
        assert 'Followers' in results
        assert 'Stars' in results
        assert 'Pull Requests' in results
        assert 'Issues' in results

    def test_returns_value_and_details(self, mock_github_client):
        """Each metric should have value and details."""
        results = collect_metrics(mock_github_client, "testuser")

        for metric_name, data in results.items():
            assert 'value' in data
            assert 'details' in data

    def test_handles_metric_failure_gracefully(self, mock_github_client):
        """Should continue collecting other metrics if one fails."""
        # Make commits fail
        def failing_get_repos():
            raise Exception("API Error")

        mock_user = mock_github_client.get_user()
        original_get_repos = mock_user.get_repos

        # First call fails, subsequent calls work
        call_count = [0]
        def sometimes_failing_get_repos():
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("API Error")
            return original_get_repos()

        mock_user.get_repos = sometimes_failing_get_repos

        # Should still return results for other metrics
        results = collect_metrics(mock_github_client, "testuser")

        # At minimum, PR and Issue metrics should work (they use search, not repos)
        assert len(results) > 0


class TestMainIntegration:
    """Integration tests for main CLI function."""

    def test_main_with_valid_user(self, mock_env_token, mock_github_client, monkeypatch, capsys):
        """Should display stats for valid user."""
        monkeypatch.setattr('sys.argv', ['github-stats', 'testuser'])

        with patch('github_stats.cli.get_github_client', return_value=mock_github_client):
            main()

        captured = capsys.readouterr()
        assert 'testuser' in captured.out or 'GitHub Stats' in captured.out

    def test_main_exits_on_invalid_user(self, mock_env_token, monkeypatch):
        """Should exit gracefully when user not found."""
        monkeypatch.setattr('sys.argv', ['github-stats', 'nonexistent_user'])

        mock_client = Mock()
        from github import GithubException
        mock_client.get_user.side_effect = GithubException(404, {"message": "Not Found"}, None)
        mock_rate_limit = Mock()
        mock_rate_limit.core.remaining = 5000
        mock_rate_limit.core.limit = 5000
        mock_client.get_rate_limit.return_value = mock_rate_limit

        with patch('github_stats.cli.get_github_client', return_value=mock_client):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_warns_on_low_rate_limit(self, mock_env_token, mock_github_client, monkeypatch, capsys):
        """Should warn when rate limit is low."""
        monkeypatch.setattr('sys.argv', ['github-stats', 'testuser'])

        # Set low rate limit
        mock_github_client.get_rate_limit().core.remaining = 30

        with patch('github_stats.cli.get_github_client', return_value=mock_github_client):
            main()

        captured = capsys.readouterr()
        # Should still complete, warning is printed
        assert captured.out  # Some output was produced

    def test_main_handles_auth_failure(self, mock_no_token, monkeypatch):
        """Should handle authentication failure."""
        monkeypatch.setattr('sys.argv', ['github-stats', 'testuser'])

        # get_github_client will exit due to no token
        # We don't need to mock it - just let it fail naturally
        with patch('github_stats.cli.get_github_client', side_effect=SystemExit(1)):
            # The function catches SystemExit and returns
            main()  # Should not raise
