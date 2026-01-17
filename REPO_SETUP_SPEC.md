# Repository Setup Specification

## Overview

This document specifies the required configuration for the `github-stats-cli` repository to ensure proper branch protection, CI/CD workflow, and development practices.

## Current State

| Item | Status |
|------|--------|
| Default branch | `main` |
| Branches | `main`, `develop` |
| Branch protection (main) | **Not configured** |
| Branch protection (develop) | **Not configured** |
| CI Workflow | Active (`ci.yml`) |
| Repository secrets | `PAT_TOKEN` required for automerge |

## Required Configuration

### 1. Repository Secrets

Add the following secrets in **Settings > Secrets and variables > Actions**:

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `PAT_TOKEN` | Personal Access Token with `repo` scope for automerge | Yes |

### 2. Branch Protection Rules

#### 2.1 Main Branch (`main`)

Navigate to **Settings > Branches > Add branch protection rule**

| Setting | Value |
|---------|-------|
| Branch name pattern | `main` |
| Require a pull request before merging | **Disabled** |
| Require status checks to pass before merging | **Enabled** |
| - Require branches to be up to date before merging | Disabled |
| - Required status checks: | See below |
| Allow force pushes | **Disabled** |
| Allow deletions | **Disabled** |

**Required Status Checks for `main`:**
- `Tests (3.9)`
- `Tests (3.10)`
- `Tests (3.11)`
- `Tests (3.12)`
- `Lint`
- `Security`

> **Note:** PR reviews are disabled to allow GitHub Actions automerge (via `PAT_TOKEN` owned by `natejswenson`) to push from `develop`. Status checks still protect the branch.

#### 2.2 Develop Branch (`develop`)

Navigate to **Settings > Branches > Add branch protection rule**

| Setting | Value |
|---------|-------|
| Branch name pattern | `develop` |
| Require a pull request before merging | **Disabled** |
| Require status checks to pass before merging | **Enabled** |
| - Required status checks: | See below |
| Allow force pushes | **Disabled** |
| Allow deletions | **Disabled** |

**Required Status Checks for `develop`:**
- `Tests (3.9)`
- `Tests (3.10)`
- `Tests (3.11)`
- `Tests (3.12)`
- `Lint`
- `Security`

> **Note:** `natejswenson` can push directly to `develop`. CI runs after push; if checks fail, automerge to `main` is blocked.

### 3. Workflow Behavior

The CI pipeline (`.github/workflows/ci.yml`) is configured as follows:

```
Trigger: Push to main/develop, PRs to main/develop, manual dispatch

Jobs:
┌─────────────────────────────────────────────────────────────┐
│  Tests (3.9, 3.10, 3.11, 3.12)  │  Lint  │  Security       │
│         (parallel)               │        │                 │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │     CI Summary      │
                └─────────────────────┘
                           │
                           ▼ (only on develop push + all pass)
                ┌─────────────────────┐
                │  Auto-merge to main │
                └─────────────────────┘
```

**Automerge conditions:**
- Branch is `develop`
- Event is `push`
- `Tests` job succeeded
- `Lint` job succeeded
- `Security` job succeeded

### 4. Development Workflow

```
                    ┌─────────────────────────────────────┐
                    │  natejswenson pushes directly       │
                    └─────────────────────────────────────┘
                                    │
                                    ▼
Feature Branch ──PR──> develop ──auto-merge──> main
                          │                      │
                          ▼                      ▼
                    CI runs here           CI runs here
                    (must pass for         (protected)
                     automerge)
```

**For `natejswenson` (direct push to develop):**
1. Push changes directly to `develop`
2. CI runs automatically
3. If Tests + Lint + Security pass → auto-merge to `main`
4. If any check fails → automerge blocked, fix and push again

**For other contributors (PR workflow):**
1. Create feature branch from `develop`
2. Make changes and push
3. Open PR to `develop`
4. CI runs, requires: Tests + Lint + Security to pass
5. Get PR approval
6. Merge to `develop`
7. CI runs on `develop`, if all pass → auto-merge to `main`

### 5. Setup Commands

#### Apply Branch Protection via GitHub CLI

```bash
# Protect main branch
gh api repos/natejswenson/github-stats-cli/branches/main/protection \
  --method PUT \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["Tests (3.9)", "Tests (3.10)", "Tests (3.11)", "Tests (3.12)", "Lint", "Security"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

# Protect develop branch
gh api repos/natejswenson/github-stats-cli/branches/develop/protection \
  --method PUT \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["Tests (3.9)", "Tests (3.10)", "Tests (3.11)", "Tests (3.12)", "Lint", "Security"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

> **Note:** User/team push restrictions are only available for organization repositories. Personal repos rely on status checks for protection.

### 6. Verification Checklist

- [ ] `PAT_TOKEN` secret is configured
- [ ] Main branch protection is enabled
- [ ] Main branch requires status checks (Tests, Lint, Security)
- [ ] Main branch requires PR reviews
- [ ] Main branch disallows force push
- [ ] Develop branch protection is enabled
- [ ] Develop branch requires status checks (Tests, Lint, Security)
- [ ] Automerge works when pushing to develop (all checks pass)
- [ ] PRs to main/develop trigger CI
- [ ] Direct pushes to main are blocked

## Notes

- The automerge feature requires `PAT_TOKEN` because `GITHUB_TOKEN` lacks push permissions
- Status check names must match exactly as they appear in the workflow
- Branch protection rules require a GitHub Pro/Team/Enterprise plan for private repos (free for public repos)
