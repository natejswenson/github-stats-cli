# AGENTS.md

Guidance for AI coding agents working on this codebase.

## Project Overview

GitHub Stats CLI is a Python command-line tool that displays GitHub profile statistics using the PyGithub API and Rich for terminal formatting.

## Architecture

```
github_stats/
├── cli.py           # Entry point, argument parsing, orchestration
├── auth.py          # GitHub authentication and rate limit checking
├── display.py       # Rich-based display utilities (headers, tables, progress)
├── output.py        # Print utilities for warnings and tables
└── metrics/         # Modular metric collectors
    ├── base.py      # Abstract BaseMetric class
    ├── commits.py   # Commit statistics
    ├── followers.py # Follower/following counts
    ├── stars.py     # Star statistics
    ├── pull_requests.py
    └── issues.py
```

## Key Patterns

### Adding New Metrics

All metrics inherit from `BaseMetric` in `github_stats/metrics/base.py`. To add a new metric:

1. Create a new file in `github_stats/metrics/`
2. Inherit from `BaseMetric`
3. Implement required methods:
   - `fetch()` - Retrieve data from GitHub API
   - `process()` - Transform raw data
   - `get_summary()` - Return one-line summary string
   - `get_detailed()` - Return detailed dict
4. Register the metric in `cli.py:collect_metrics()`

### Code Style

- Use type hints for function signatures
- Use comment headers (`#---...`) to separate major sections
- Keep error handling graceful with user-friendly messages
- Each metric should be self-contained in its own file

## Dependencies

- **PyGithub** - GitHub API wrapper
- **Rich** - Terminal formatting (tables, progress bars, colors)
- **python-dotenv** - Environment variable loading

## Development

```bash
# Install in development mode
pip install -e .

# Run the CLI
github-stats <username>
python -m github_stats <username>

# Run tests
pytest
```

## Environment Setup

Requires `GITHUB_TOKEN` environment variable or `--token` flag. Token needs `read:user` scope (and optionally `repo` for private data).

## Common Tasks

| Task | Location |
|------|----------|
| Add CLI argument | `cli.py:parse_arguments()` |
| Add new metric | Create file in `metrics/`, register in `cli.py` |
| Modify table display | `display.py:create_summary_table()` |
| Change auth logic | `auth.py` |

## Important Notes

- API rate limits: 5,000 requests/hour authenticated
- Typical run uses 20-75 API requests
- Always check rate limits before bulk operations
- Handle `GithubException` for API errors
