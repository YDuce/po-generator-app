# AGENTS.md

*Last updated: <YYYY‑MM‑DD>*

---

## 0 · Purpose

Single source of truth for automated collaborators (Codex, Cursor, CI) in this repo.  Keep rules minimal, explicit, and easy to override via prompt.

---

## 1 · Agent Capabilities & Expectations

| Agent      | May do when instructed                                                   | Always does                                              | Must not do                               |
| ---------- | ------------------------------------------------------------------------ | -------------------------------------------------------- | ----------------------------------------- |
| **Codex**  | *Scaffold **or fully implement*** code, write tests, open PRs, edit docs | Enforce layered architecture; follow prompts exactly     | Merge to `main`/`cursor` without CI green |
| **Cursor** | Live‑code small fixes, refactor, generate tests                          | Follow conventions in this file                          | Change public APIs without PR review      |
| **CI bot** | –                                                                        | run lint, type‑check, pytest, coverage; block on failure | –                                         |

*Human override:* Any human review supersedes an agent’s decision.

---

## 2 · Layered Architecture

```
app/
 ├ core/       # vendor‑agnostic models + business logic
 ├ channels/   # one sub‑package per vendor (woot, amazon, …)
 └ api/        # HTTP controllers, zero business logic
```

Import rule: **`api → channels → core`** (no reverse imports).

---

## 3 · Coding Standards (Python 3.12)

* **Formatter** – black (line ≤100)
* **Lint**     – flake8 (≤120)
* **Types**    – mypy --strict (PEP 561 stubs in `src/typings/`)
* **Tests**    – pytest; ≥90 % module coverage
* **Docstrings** – Google style
* **Structured logging** – use module‑level `logger = logging.getLogger(__name__)`

---

## 4 · Git Workflow

1. **Branch:** `git switch -c feat/<topic>` off **`cursor`**
2. Commit + push; open PR to `cursor`.
3. CI must pass (lint, type, tests, coverage) before merge.
4. Hotfixes: `hotfix/*` off `main`; merge with PR.

---

## 5 · Secrets Handling

* `.env` ignored; `.env.example` tracked with placeholders only.

---

## 6 · Editing This Doc

* Any PR may propose edits; tag **@maintainers**.
* Remove obsolete rules instead of piling exceptions.

---

## 7 · Glossary

* **PORF** – Purchase Order Request Form (Woot)
* **PO**   – Purchase Order
* **Connector / Service** – Concrete channel implementation of `BaseChannelOrderService`

---

## Google Workspace
App owns one Drive folder per organisation (ensure_workspace).
All sheets created via core.services.drive/sheets.
Sheets remain read-only until TWO_WAY_SYNC_ENABLED is True.

## Naming Helper
`slugify(label: str, identifier: int | str) -> str` converts names into
Drive-friendly slugs. Example: `slugify("PORF", 42)` → `porf-42`.
