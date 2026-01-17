# CLAUDE.md

Instructions for Claude Code when working on this repository.

## Required Reading

Before making any changes, read and understand:
- **[AGENTS.md](./AGENTS.md)** - Project architecture, patterns, and development guidelines

## Rules for All Changes

When making changes to this codebase, you MUST follow these rules:

### 1. Integration Tests

**Always add or update integration tests when:**
- Adding new functionality (metrics, CLI options, features)
- Modifying existing behavior
- Fixing bugs (add a test that would have caught the bug)
- Changing API interactions or data processing logic

Tests are located in `tests/` and use pytest. See existing tests for patterns:
- `tests/test_auth.py` - Authentication tests
- `tests/test_cli.py` - CLI entry point tests
- `tests/test_metrics.py` - Metric collector tests

Run tests before committing: `pytest tests/ -v`

### 2. AGENTS.md Updates

**Update AGENTS.md when:**
- Adding new files or modules
- Changing the project architecture
- Adding new patterns or conventions
- Modifying the metrics system
- Adding new dependencies
- Changing development workflows

### 3. README.md Updates

**Update README.md when:**
- Adding user-facing features or CLI options
- Changing installation or setup steps
- Modifying usage examples
- Adding new environment variables or configuration
- Changing output format or display

## Pre-Commit Checklist

Before completing any task, verify:

- [ ] Integration tests added/updated (if code changed)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] AGENTS.md updated (if architecture/patterns changed)
- [ ] README.md updated (if user-facing changes)
- [ ] Lint passes (`ruff check github_stats/ tests/`)

## CI/CD Awareness

This repo uses GitHub Actions (`.github/workflows/ci.yml`):
- Tests run on Python 3.9, 3.10, 3.11, 3.12
- Lint (Ruff) and Security checks are required
- Pushes to `develop` auto-merge to `main` if all checks pass

See `REPO_SETUP_SPEC.md` for branch protection details.

## Quick Reference

| Action | Files to Consider |
|--------|-------------------|
| New metric | `metrics/*.py`, `cli.py`, `tests/test_metrics.py`, `AGENTS.md` |
| New CLI option | `cli.py`, `tests/test_cli.py`, `README.md` |
| Auth changes | `auth.py`, `tests/test_auth.py`, `AGENTS.md` |
| Display changes | `display.py`, `output.py`, `README.md` |
| New dependency | `pyproject.toml`, `requirements.txt`, `AGENTS.md` |
