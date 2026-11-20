<!-- Syed Zohaib Shah, Roll Number: PSEB-2026-010729, Date: 2026-11-20 -->
# Code Review Checklist — Online Retail ML Project

## Correctness
- [ ] The change does what the PR description says.
- [ ] Tests exist and would fail without the change.
- [ ] Edge cases handled (empty input, missing columns, NaN, duplicates).

## Reproducibility
- [ ] New data files come from a documented source.
- [ ] No hard-coded absolute paths; use `pathlib` + project-relative paths.
- [ ] Random seeds set where randomness is used.

## Data hygiene
- [ ] `data/raw/` untouched.
- [ ] Cleaned outputs written to `data/cleaned/`.
- [ ] No leaking columns reintroduced (`order_total`, `InvoiceNo` as feature).

## Style
- [ ] Functions have docstrings and type hints.
- [ ] No dead code or commented-out blocks.
- [ ] `ruff check src tests` is clean.

## Security / secrets
- [ ] No tokens, passwords, or personal data in the diff.
- [ ] `.gitignore` covers `.venv/`, `__pycache__/`, `*.db`.

## Merge
- [ ] CI green on all required checks.
- [ ] Approving reviewer can explain the change in the demo.
