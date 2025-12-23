#---------------------------------------------------------
# GitHub Authentication Module
#---------------------------------------------------------

import os
import sys
from typing import Optional
from github import Github, GithubException
from github_stats.output import print_auth_error, print_auth_failed


#---------------------------------------------------------
# Main authentication functions
#---------------------------------------------------------

def get_github_client(token: Optional[str] = None) -> Github:
    # Priority: CLI argument > environment variable
    auth_token = token or _load_token_from_env()

    if not auth_token:
        print_auth_error()
        sys.exit(1)

    try:
        client = Github(auth_token)
        _validate_token(client)
        return client
    except GithubException as e:
        print_auth_failed(e.data.get('message', str(e)))
        sys.exit(1)


def check_rate_limit(client: Github) -> dict:
    rate_limit = client.get_rate_limit()
    core = rate_limit.core

    return {
        'remaining': core.remaining,
        'limit': core.limit,
        'reset_time': core.reset,
        'percentage': (core.remaining / core.limit * 100) if core.limit > 0 else 0
    }


#---------------------------------------------------------
# Helper functions
#---------------------------------------------------------

def _load_token_from_env() -> Optional[str]:
    return os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PAT')


def _validate_token(client: Github) -> None:
    client.get_user().login
