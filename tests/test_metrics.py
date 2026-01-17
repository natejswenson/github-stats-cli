"""Integration tests for GitHub metrics modules."""

import pytest
from unittest.mock import Mock, MagicMock
from github import GithubException

from github_stats.metrics.commits import CommitMetric
from github_stats.metrics.followers import FollowerMetric
from github_stats.metrics.stars import StarMetric
from github_stats.metrics.pull_requests import PullRequestMetric
from github_stats.metrics.issues import IssueMetric


class TestCommitMetric:
    """Integration tests for commit statistics."""

    def test_fetch_counts_commits_per_repo(self, mock_github_client):
        """Should count commits for each repository."""
        metric = CommitMetric(mock_github_client, "testuser")

        metric.fetch()

        assert metric.data is not None
        assert isinstance(metric.data, dict)

    def test_process_calculates_total_commits(self, mock_github_client):
        """Should calculate total commits across all repos."""
        metric = CommitMetric(mock_github_client, "testuser")

        metric.collect()

        assert metric.total_commits >= 0

    def test_process_identifies_top_repo(self, mock_github_client):
        """Should identify repository with most commits."""
        metric = CommitMetric(mock_github_client, "testuser")

        metric.collect()

        if metric.total_commits > 0:
            assert metric.top_repo is not None
            assert len(metric.top_repo) == 2  # (name, count) tuple

    def test_get_summary_format(self, mock_github_client):
        """Should return properly formatted summary string."""
        metric = CommitMetric(mock_github_client, "testuser")
        metric.collect()

        summary = metric.get_summary()

        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_get_detailed_returns_dict(self, mock_github_client):
        """Should return detailed breakdown as dictionary."""
        metric = CommitMetric(mock_github_client, "testuser")
        metric.collect()

        detailed = metric.get_detailed()

        assert 'total_commits' in detailed
        assert 'repositories' in detailed
        assert 'top_repositories' in detailed

    def test_handles_empty_repos(self):
        """Should handle user with no repositories."""
        mock_client = Mock()
        mock_user = Mock()
        mock_user.get_repos.return_value = iter([])
        mock_client.get_user.return_value = mock_user

        metric = CommitMetric(mock_client, "testuser")
        metric.collect()

        assert metric.total_commits == 0
        assert metric.get_summary() == "0, No commits found"

    def test_handles_api_errors(self):
        """Should handle API errors gracefully."""
        mock_client = Mock()
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.get_commits.side_effect = GithubException(403, {"message": "Forbidden"}, None)
        mock_user.get_repos.return_value = iter([mock_repo])
        mock_client.get_user.return_value = mock_user

        metric = CommitMetric(mock_client, "testuser")
        metric.collect()  # Should not raise

        assert metric.total_commits == 0


class TestFollowerMetric:
    """Integration tests for follower statistics."""

    def test_fetch_gets_follower_counts(self, mock_github_client):
        """Should fetch follower and following counts."""
        metric = FollowerMetric(mock_github_client, "testuser")

        metric.fetch()

        assert metric.followers_count == 100
        assert metric.following_count == 50

    def test_process_calculates_ratio(self, mock_github_client):
        """Should calculate follower/following ratio."""
        metric = FollowerMetric(mock_github_client, "testuser")

        metric.collect()

        assert hasattr(metric, 'ratio')
        assert metric.ratio == 2.0  # 100/50

    def test_handles_zero_following(self):
        """Should handle zero following count."""
        mock_client = Mock()
        mock_user = Mock()
        mock_user.followers = 100
        mock_user.following = 0
        mock_client.get_user.return_value = mock_user

        metric = FollowerMetric(mock_client, "testuser")
        metric.collect()

        assert metric.ratio == float('inf')

    def test_get_summary_format(self, mock_github_client):
        """Should return formatted summary."""
        metric = FollowerMetric(mock_github_client, "testuser")
        metric.collect()

        summary = metric.get_summary()

        assert "100" in summary
        assert "Following" in summary
        assert "50" in summary

    def test_get_detailed_returns_dict(self, mock_github_client):
        """Should return detailed breakdown."""
        metric = FollowerMetric(mock_github_client, "testuser")
        metric.collect()

        detailed = metric.get_detailed()

        assert detailed['followers'] == 100
        assert detailed['following'] == 50
        assert 'ratio' in detailed


class TestStarMetric:
    """Integration tests for star statistics."""

    def test_fetch_counts_stars_per_repo(self, mock_github_client):
        """Should count stars for each repository."""
        metric = StarMetric(mock_github_client, "testuser")

        metric.fetch()

        assert metric.data is not None
        assert isinstance(metric.data, dict)

    def test_process_calculates_total_stars(self, mock_github_client):
        """Should calculate total stars across all repos."""
        metric = StarMetric(mock_github_client, "testuser")

        metric.collect()

        assert metric.total_stars >= 0

    def test_process_identifies_top_repo(self, mock_github_client):
        """Should identify most starred repository."""
        metric = StarMetric(mock_github_client, "testuser")

        metric.collect()

        if metric.total_stars > 0:
            assert metric.top_repo is not None

    def test_get_summary_includes_top_repo(self, mock_github_client):
        """Should include top repo in summary."""
        metric = StarMetric(mock_github_client, "testuser")
        metric.collect()

        summary = metric.get_summary()

        if metric.total_stars > 0:
            assert "Top:" in summary

    def test_handles_repos_without_stars(self):
        """Should handle repos with zero stars."""
        mock_client = Mock()
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.name = "no-stars-repo"
        mock_repo.stargazers_count = 0
        mock_user.get_repos.return_value = iter([mock_repo])
        mock_client.get_user.return_value = mock_user

        metric = StarMetric(mock_client, "testuser")
        metric.collect()

        assert metric.total_stars == 0
        assert metric.get_summary() == "0, No stars"


class TestPullRequestMetric:
    """Integration tests for pull request statistics."""

    def test_fetch_uses_search_api(self, mock_github_client):
        """Should use GitHub search API to find PRs."""
        metric = PullRequestMetric(mock_github_client, "testuser")

        metric.fetch()

        mock_github_client.search_issues.assert_called()
        call_args = str(mock_github_client.search_issues.call_args)
        assert "type:pr" in call_args
        assert "testuser" in call_args

    def test_counts_total_prs(self, mock_github_client):
        """Should count total pull requests."""
        metric = PullRequestMetric(mock_github_client, "testuser")

        metric.collect()

        assert metric.total_prs == 10

    def test_calculates_merge_rate(self, mock_github_client):
        """Should calculate merge/close rate."""
        metric = PullRequestMetric(mock_github_client, "testuser")

        metric.collect()

        assert hasattr(metric, 'merge_rate')
        assert 0 <= metric.merge_rate <= 100

    def test_get_summary_includes_rate(self, mock_github_client):
        """Should include close rate in summary."""
        metric = PullRequestMetric(mock_github_client, "testuser")
        metric.collect()

        summary = metric.get_summary()

        assert "%" in summary
        assert "closed" in summary

    def test_handles_no_prs(self):
        """Should handle user with no PRs."""
        mock_client = Mock()
        mock_results = Mock()
        mock_results.totalCount = 0
        mock_results.__iter__ = Mock(return_value=iter([]))
        mock_client.search_issues.return_value = mock_results

        metric = PullRequestMetric(mock_client, "testuser")
        metric.collect()

        assert metric.total_prs == 0
        assert metric.get_summary() == "0, No PRs"

    def test_handles_api_errors(self):
        """Should handle search API errors."""
        mock_client = Mock()
        mock_client.search_issues.side_effect = GithubException(403, {"message": "Rate limited"}, None)

        metric = PullRequestMetric(mock_client, "testuser")
        metric.collect()  # Should not raise

        assert metric.total_prs == 0


class TestIssueMetric:
    """Integration tests for issue statistics."""

    def test_fetch_uses_search_api(self, mock_github_client):
        """Should use GitHub search API to find issues."""
        metric = IssueMetric(mock_github_client, "testuser")

        metric.fetch()

        # Verify search was called with issue query
        calls = mock_github_client.search_issues.call_args_list
        issue_call = [c for c in calls if "type:issue" in str(c)]
        assert len(issue_call) > 0

    def test_counts_total_issues(self, mock_github_client):
        """Should count total issues."""
        metric = IssueMetric(mock_github_client, "testuser")

        metric.collect()

        assert metric.total_issues == 5

    def test_calculates_close_rate(self, mock_github_client):
        """Should calculate issue close rate."""
        metric = IssueMetric(mock_github_client, "testuser")

        metric.collect()

        assert hasattr(metric, 'close_rate')
        assert 0 <= metric.close_rate <= 100

    def test_get_summary_includes_rate(self, mock_github_client):
        """Should include close rate in summary."""
        metric = IssueMetric(mock_github_client, "testuser")
        metric.collect()

        summary = metric.get_summary()

        assert "%" in summary
        assert "closed" in summary

    def test_handles_no_issues(self):
        """Should handle user with no issues."""
        mock_client = Mock()
        mock_results = Mock()
        mock_results.totalCount = 0
        mock_results.__iter__ = Mock(return_value=iter([]))
        mock_client.search_issues.return_value = mock_results

        metric = IssueMetric(mock_client, "testuser")
        metric.collect()

        assert metric.total_issues == 0
        assert metric.get_summary() == "0, No issues"

    def test_get_detailed_returns_dict(self, mock_github_client):
        """Should return detailed breakdown."""
        metric = IssueMetric(mock_github_client, "testuser")
        metric.collect()

        detailed = metric.get_detailed()

        assert 'total_issues' in detailed
        assert 'open' in detailed
        assert 'closed' in detailed
        assert 'close_rate' in detailed


class TestMetricBaseClass:
    """Tests for base metric class behavior."""

    def test_collect_calls_fetch_then_process(self, mock_github_client):
        """collect() should call fetch() then process() in order."""
        metric = FollowerMetric(mock_github_client, "testuser")

        # Track call order
        calls = []
        original_fetch = metric.fetch
        original_process = metric.process

        def tracked_fetch():
            calls.append('fetch')
            return original_fetch()

        def tracked_process():
            calls.append('process')
            return original_process()

        metric.fetch = tracked_fetch
        metric.process = tracked_process

        metric.collect()

        assert calls == ['fetch', 'process']
