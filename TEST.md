# Backend Test Guide

This document explains in a concise, reproducible way how to run the backend (FastAPI + PydanticAI) test suite located in `back/tests/`.

## 1. Prerequisites

- Python 3.11+
- Bash shell (Linux/macOS). For Windows, use WSL or adapt PowerShell examples.
- Optional: A virtual environment manager (`python -m venv` is sufficient).

## 2. Initial Environment Setup

```bash
cd back
python3.11 -m venv venv
source venv/bin/activate  # On Windows (PowerShell): venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you plan to run coverage or additional tooling later, ensure any extra dev dependencies are also installed (none required at the moment beyond `pytest` and packages already listed in `requirements.txt`).

## 3. Basic Test Execution

Run all backend tests:
```bash
cd back
pytest tests/ -v
```

### Faster Iteration (Fail Fast)
```bash
pytest tests/ -x -k "character" -v
```
Explanation:
- `-x` stops at first failure.
- `-k "character"` runs only tests whose node id matches the substring "character".

### Single Test File
```bash
pytest tests/routers/test_characters_refactored.py -v
```

### Single Test Function
You can append `::TestClass::test_function_name`:
```bash
pytest tests/routers/test_characters_refactored.py::test_get_all_characters -v
```

## 4. Coverage Reporting

Generate terminal and HTML coverage reports:
```bash
pytest tests/ --cov=back --cov-report=term --cov-report=html -v
```
Result:
- Console summary.
- HTML output in `htmlcov/` (open `htmlcov/index.html` in a browser).

## 5. Clean Test Run Script

There is a helper script at project root: `run_tests.sh` (Linux/macOS) and `run_tests_clean.ps1` (Windows). These can be used to ensure a fresh virtual environment or clean caches depending on their implementation.

Typical usage (Linux):
```bash
./run_tests.sh
```

Review the script before use to understand if it re-creates the virtual environment or modifies data files.

## 6. Data Considerations

Backend tests may read from `data/` and `back/gamedata/` YAML. Avoid modifying these files while tests run. If a test creates temporary JSONL session history under `data/sessions/`, you can purge them between runs if needed:
```bash
rm -f data/sessions/*.jsonl
```
Only do this if you are certain the files are disposable.

## 7. Selecting / Tagging Tests

If we later adopt pytest markers (e.g. `@pytest.mark.slow`), you would run only fast tests via:
```bash
pytest tests/ -m "not slow"
```
Currently no custom markers are defined.

## 8. Logging & Debugging

Tests may emit JSON logs via `back/utils/logger.py`. To increase verbosity:
```bash
pytest tests/ -vv
```
Use `-s` to see raw print/log output (disables output capture):
```bash
pytest tests/ -s -k scenario
```

## 9. Common Pytest Flags Cheat Sheet

| Flag | Purpose |
|------|---------|
| `-v` | Verbose output |
| `-x` | Stop after first failure |
| `-k expr` | Filter tests by name substring |
| `-s` | Disable output capture (show prints) |
| `--maxfail=N` | Stop after N failures |
| `--cov=PACKAGE` | Coverage for PACKAGE |
| `--cov-report=html` | HTML coverage report |

## 10. Test Structure Overview

`back/tests/` mirrors the backend architecture:
- `agents/` – Agent dependency & tool tests.
- `routers/` – FastAPI endpoint tests.
- `services/` – Business logic unit tests.
- `storage/` – Persistence layer tests (JSONL store).
- `tools/` – PydanticAI tool behavior tests.
- `utils/` – Utility helpers (dice, logger, converters).

Add future tests under the matching folder to preserve Single Responsibility alignment.

## 11. Writing New Tests (Quick Template)

Example for a service function in `character_service.py`:
```python
import pytest
from back.services.character_service import CharacterService

def test_apply_damage():
    service = CharacterService()
    character = ...  # build or mock character instance
    updated = service.apply_damage(character, 12)
    assert updated.hp == character.hp - 12
```

Place this in `back/tests/services/test_character_service.py`.

## 12. Continuous Integration (Future)

When adding CI (e.g. GitHub Actions), replicate the environment steps above:
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
- run: |
    cd back
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pytest tests/ -v --cov=back --cov-report=xml
```
The generated `coverage.xml` can feed into code quality or PR annotations.

## 13. Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Import errors | venv not activated | Activate venv, reinstall requirements |
| Missing module `pydantic_ai` | Dependency mismatch | Re-run `pip install -r requirements.txt` |
| Tests hang | Network / external calls | Isolate by running a single test with `-k` |
| Stale data artifacts | Previous session JSONL | Remove files under `data/sessions/` |

## 14. Frontend Tests

Frontend has been removed for now; there are no frontend tests to run. This file focuses on backend only.

## 15. Quick Reference

| Action | Command |
|--------|---------|
| Full suite | `pytest tests/ -v` |
| Single file | `pytest tests/routers/test_characters_refactored.py -v` |
| Coverage | `pytest tests/ --cov=back --cov-report=term-missing` |
| Fail fast | `pytest tests/ -x` |
| Specific name | `pytest tests/ -k combat` |

---
Maintained: November 13, 2025
