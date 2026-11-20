## What changed
<!-- One or two sentences. Link the issue if there is one. -->

## Why
<!-- The problem this solves, or the acceptance criterion it meets. -->

## How to verify
<!-- Exact commands a reviewer should run. -->

## Checklist (author)
- [ ] Tests pass locally (`python -m pytest tests/ -v`)
- [ ] Lint clean (`python -m ruff check src tests`)
- [ ] I explained every line I added and can defend it in review
- [ ] I added a test for any new behaviour
- [ ] Raw data in `data/raw/` unchanged
- [ ] Cleaned data / figures / reports regenerated (if applicable)
- [ ] No secrets committed (API keys, tokens, passwords)
- [ ] README / docs updated if behaviour changed

## Checklist (reviewer)
- [ ] I understand every line of the diff
- [ ] Tests cover the new behaviour and would fail without it
- [ ] Error paths are handled, not silently swallowed
- [ ] No leakage / no data copied from `data/raw/` into features
- [ ] CI is green
