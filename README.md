# GitHub Stats CLI

[![CI Pipeline](https://github.com/natejswenson/github-stats-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/natejswenson/github-stats-cli/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A beautiful command-line interface for displaying GitHub profile statistics.

## Features

- Commit, follower, star, PR, and issue statistics
- Rich terminal formatting with tables and colors
- Rate limit aware

## Installation

```bash
# Clone the repository
git clone https://github.com/natejswenson/github-stats-cli.git
cd github-stats-cli

# Install
pip install -e .
```

## Usage

```bash
# Set your GitHub token
export GITHUB_TOKEN=your_token_here

# Run
github-stats <username>
```

### Example

```bash
$ github-stats octocat

╭──────────────────────────────────────────────────────────────────────────────╮
│ GitHub Stats for: octocat                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

╭───────────────┬───────┬────────────────────────────────╮
│ Metric        │ Value │ Details                        │
├───────────────┼───────┼────────────────────────────────┤
│ Commits       │    16 │ Most: git-consortium (6)       │
│ Followers     │    21 │ 533, Following: 9              │
│ Stars         │    20 │ 774, Top: Spoon-Knife (13,547) │
│ Pull Requests │     8 │ 37% closed                     │
│ Issues        │     5 │ 20% closed                     │
╰───────────────┴───────┴────────────────────────────────╯
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check github_stats/ tests/
```

## Project Structure

```
github_stats/
├── cli.py           # Entry point and orchestration
├── auth.py          # GitHub authentication
├── display.py       # Rich display utilities
├── output.py        # Print utilities
└── metrics/         # Metric collectors
    ├── base.py
    ├── commits.py
    ├── followers.py
    ├── stars.py
    ├── pull_requests.py
    └── issues.py
```

## License

MIT
