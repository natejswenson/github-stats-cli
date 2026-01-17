# GitHub Stats CLI

A beautiful command-line interface for displaying GitHub profile statistics. Get insights into commits, followers, stars, pull requests, and issues with a visually appealing terminal interface.

## Features

- **Commit Statistics**: Total commits and most active repositories
- **Follower Metrics**: Follower and following counts
- **Star Analytics**: Total stars received across all repositories
- **Pull Request Tracking**: PR count and close rate
- **Issue Management**: Issue count and resolution rate
- **Beautiful UI**: Rich terminal formatting with tables and colors
- **Rate Limit Aware**: Monitors GitHub API usage

## Installation

### Prerequisites

- Python 3.8 or higher
- A GitHub Personal Access Token (see setup instructions below)

### Install Dependencies

1. Clone or download this repository
2. Install required packages:

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## GitHub Personal Access Token Setup

To use this CLI, you need a GitHub Personal Access Token:

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Give it a descriptive name (e.g., "GitHub Stats CLI")
4. Select the following scopes:
   - `read:user` - Read user profile data
   - `repo` - (Optional) Access private repository data
5. Click **"Generate token"**
6. Copy the token (you won't be able to see it again!)

### Setting Up Your Token

#### Option 1: Environment Variable (Recommended)

```bash
export GITHUB_TOKEN=your_token_here
```

To make it permanent, add to your `~/.bashrc`, `~/.zshrc`, or equivalent:

```bash
echo 'export GITHUB_TOKEN=your_token_here' >> ~/.bashrc
source ~/.bashrc
```

#### Option 2: .env File

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your token:
   ```
   GITHUB_TOKEN=your_token_here
   ```

## Usage

### Basic Usage

```bash
# Using the installed command
github-stats username

# Or run as a Python module
python -m github_stats username
```

### Examples

```bash
# View stats for a specific user
github-stats octocat

# View stats for Linus Torvalds
github-stats torvalds

# Override token from command line
github-stats username --token ghp_your_token_here
```

### Sample Output

```
╭─────────────────────────────────────────╮
│   GitHub Stats for: octocat            │
╰─────────────────────────────────────────╯

┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Metric       ┃ Value   ┃ Details            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Commits      │ 1,234   │ Most: repo-name    │
│ Followers    │ 567     │ Following: 123     │
│ Stars        │ 890     │ Top: repo-name     │
│ Pull Requests│ 45      │ 89% closed         │
│ Issues       │ 23      │ 78% closed         │
└──────────────┴─────────┴────────────────────┘

Rate Limit: 4,950/5,000 remaining
```

## Project Structure

```
github_stats/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point for python -m
├── cli.py               # Main CLI interface
├── auth.py              # GitHub authentication
├── display.py           # Rich display utilities
└── metrics/             # Metric modules
    ├── __init__.py
    ├── base.py          # Base metric class
    ├── commits.py       # Commit statistics
    ├── followers.py     # Follower statistics
    ├── stars.py         # Star statistics
    ├── pull_requests.py # PR statistics
    └── issues.py        # Issue statistics
```

## How It Works

1. **Authentication**: Connects to GitHub API using your Personal Access Token
2. **Rate Limit Check**: Verifies sufficient API quota before fetching
3. **Data Collection**: Gathers statistics from each metric module
4. **Processing**: Calculates totals, averages, and identifies top items
5. **Display**: Presents data in a beautiful terminal table

## API Rate Limits

- **Authenticated**: 5,000 requests/hour
- **This app typically uses**: 20-75 requests per run

The app monitors your rate limit and warns you if it's running low.

## Troubleshooting

### "GitHub token not found or invalid"

- Make sure you've set the `GITHUB_TOKEN` environment variable
- Verify your token hasn't expired
- Check that your token has the required scopes

### "User 'username' not found"

- Double-check the username spelling
- Ensure the user profile is public

### Low rate limit warning

- Wait for your rate limit to reset (shown in the output)
- Authenticated requests have higher limits than unauthenticated

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .

# Run tests (when implemented)
pytest
```