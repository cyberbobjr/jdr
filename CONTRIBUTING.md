# Contributing to the Middle‑earth RPG (JdR)

Thanks for your interest in improving the project! This one‑page guide summarizes how to propose changes effectively.

## 1. Core Principles
- Single Responsibility: every service/file has one clear concern.
- Separation of Concerns: Routers = HTTP only, Services = business logic, Managers = YAML data loading, Agents/Tools = LLM orchestration, Storage = persistence.
- Type Safety Everywhere: Python with full type hints + Pydantic models.
- English Only: code, comments, docs, data.
- No Hardcoded Game Data: always use managers under `back/models/domain/*_manager.py`.

## 2. Getting Started
```bash
# Backend
cd back
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
API docs: http://localhost:8000/docs. Frontend will be recreated later.

## 3. Branching & Commits
- Branch naming: `feat/<short-description>`, `fix/<issue-id-or-desc>`, `docs/...`, `refactor/...`, `test/...`.
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `perf:`, `chore:`.
- Keep commits focused; prefer several small logical commits over one large mixed commit.

## 4. Backend Code Standards
- Pydantic V2 models with validators and explicit error messages.
- Docstrings (Google style) for every public function/method; include Args / Returns / Raises.
- Services: no file or network I/O (delegate to persistence/storage classes).
- Avoid circular dependencies—prefer dependency injection passing services explicitly.
- Logging: use JSON logger (`back/utils/logger.py`); never `print()`.
- Exceptions: raise custom ones from `utils/exceptions.py`.
- Async: use `async` for I/O (file, network, CPU-bound stays sync unless justified).

<!-- Frontend code standards not applicable: frontend removed for now -->

## 6. Testing
```bash
# Backend tests
cd back && pytest tests/ -v
```
- Mirror source structure: add tests under matching folder (e.g. `back/tests/routers/`).
- New service or model == new test module.
- Avoid mocking managers unless necessary; prefer real YAML fixtures.
- Keep tests deterministic (no real LLM calls—mock or isolate tool logic).

## 7. Pull Request Guidelines
Include: purpose, high‑level approach, any schema changes, migration steps. PR Checklist:
- [ ] Follows SRP & layering rules
- [ ] Added/updated tests (and they pass)
- [ ] Updated docs/README if behavior or endpoints changed
- [ ] No hardcoded game data
- [ ] Logging & exceptions consistent
- [ ] Type hints & docstrings added
<!-- Frontend build step omitted: frontend removed for now -->

## 8. Issues & Feature Requests
- Search existing issues before opening new ones.
- Provide reproduction steps, expected vs actual behavior, environment details.
- Label appropriately: `bug`, `enhancement`, `docs`, `question`.

## 9. Security & Sensitive Data
- Do not commit API keys or secrets; use environment variables.
- Validate all external input; never trust raw request data.
- Report vulnerabilities privately first (open a minimal placeholder issue if needed).

## 10. LLM / Agent Changes
- Keep system prompt modifications minimal and documented.
- Persist history only through `PydanticJsonlStore`; never duplicate system prompts in storage.
- When adding tools: include clear docstring, deterministic return shape, and tests for tool edge cases.

## 11. Performance
- Avoid N+1 file or YAML loads—reuse manager instances.
- Defer heavy computation; prefer caching if needed (submit separate performance PR if large change).

## 12. Style & Hygiene
- Run minimal linting/formatting (e.g., black/ruff if configured; otherwise maintain existing style).
- Remove dead code & commented blocks before review.

---
By submitting a contribution you agree to follow these guidelines. Thank you for helping build the Middle‑earth RPG!
