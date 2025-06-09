# Project Road‑Map & Technical Overview

*Last updated: 2025‑06‑08*

---

## 0 · Key Invariants

* **Import graph:** `api → channels → core` only.
* **Structured logging:** every public fn keeps/creates `logger = logging.getLogger(__name__)`.
* **Google Auth split:**

  * **User login / account provisioning** → **Google OAuth** (client‑side flow, scopes `profile`, `email`).
  * **Drive/Sheets API calls** → **service‑account**. Users get Viewer ACL on created sheets.
* **Workspace folder:** `Your-App-Workspace-<orgId>/` created at signup; sub‑folders per channel.
* **Channel storage layout (Woot example):**

  ```
  Your-App-Workspace-<orgId>/
    └─ woot/
        ├─ porfs/   # PORF spreadsheets only
        └─ pos/     # PO spreadsheets + PDFs
  ```

  *Flat‑by‑type strategy (Option A)* – keeps Drive fast and codepaths simple. Sheets and PDFs belonging to the same transaction are linked in DB/UI, not by folder proximity.
* **CI gates:** black –check · flake8 (≤120) · mypy --strict · pytest · alembic migrate.

## 1 · High‑Level Architecture (recap) · High‑Level Architecture (recap)

```
app/
 ├ core/          # vendor‑agnostic models + business logic
 ├ channels/      # one sub‑package per vendor (woot, …)
 └ api/           # HTTP controllers only
```

*Postgres is source of truth.*  Drive/Sheets is a read‑only mirror (v1).

---

## 2 · Implementation Snapshot (MVP branch)

| Area                       | Status                                                 | Notes                                                         |
| -------------------------- | ------------------------------------------------------ | ------------------------------------------------------------- |
| Google **OAuth login**     | ✅ complete           | via Flask-Dance, env vars configured |
| **Workspace provisioning** | ✅ complete           | folder ID stored on `organisation` table |
| **DriveService**           | ✅ ensure_workspace/subfolder                          |                                                               |
| **SheetsService**          | ✅ open/copy/append; V2 stubs declared                  |                                                               |
| **Woot PORF ingest**       | ✅ parses & writes sheet; tests failing on import path |                                                               |
| **CI workflow**            | ✅ green              | coverage ≥90%, mypy strict |

---

## 3 · Immediate Fix List

1. **Import paths** – replace `app.integrations.*` with `core.services.*`.
2. **Type stubs** – add `types-google-auth`, `types-requests` or create local stubs.
3. **Monkey‑patch Google in tests** – via `pytest` fixture.
4. **Logger sweep** – ensure no logger removed during refactor.
5. **Alembic** – auto‑include channel models.

---

## 4 · MVP Checklist (v0.1.0)

| Feature                            | Owner  | Status |
| ---------------------------------- | ------ | ------ |
| Google OAuth login + signup        | Cursor | 🔲     |
| Workspace folder on signup         | Codex  | 🔲     |
| POST `/api/woot/porf-upload` green | Cursor | ⚠️     |
| Front‑end PoC upload page          | Human  | 🔲     |
| CI green on GitHub                 | Codex  | 🔲     |

---

## 5 · Back‑log (post‑MVP)

* Two‑way sheet sync (`get_sheet_changes`, `apply_db_updates_to_sheet`).
* ShipStation webhooks → order ingest.
* Channel: Amazon connector skeleton.
* Metrics endpoint (`/health/metrics`).
* Naming strategy helper (slugify org + yyyy‑mm‑dd) for sheets/folders.
* Front‑end design system (Tailwind + DaisyUI).

---

## 6 · Developer How‑To

### Local env vars

```
FLASK_ENV=development
GOOGLE_CLIENT_ID=<id>
GOOGLE_CLIENT_SECRET=<secret>
GOOGLE_SVC_KEY=/abs/path/service-account.json
```

### Running tests

```bash
bash scripts/setup_test_env.sh
pytest -q
```

### Monkey‑patch template

```python
from unittest import mock
@mock.patch("core.services.sheets.append_rows", lambda *a, **k: None)
```

---

## 7 · Update Protocol

1. Edit `ROADMAP.md` in PR.
2. Tag **@codex-bot** for architecture review.
3. Merge when CI green.

--- · End‑to‑End Workflow Reference (v1)

1. **User hits `/login/google`** → Google OAuth consent (scopes `profile email`).
2. **Callback** → `api/auth.py` exchanges code, retrieves userinfo.
3. **Account provisioning**

   * `upsert_user()` stores user; `organisation` row created if first login.
4. **Workspace creation**

   * `DriveService.ensure_workspace(org_id)` creates `Your-App-Workspace-<orgId>`.
   * User granted Viewer access.
5. **Add Channel UI** (front‑end) – user selects "Add Woot Channel".
6. **Backend** lazily creates sub‑folders: `woot/porfs`, `woot/pos`.
7. **PORF upload**

   * POST CSV/XLSX to `/api/woot/porf-upload`.
   * `ingest_porf()` parses → DB rows → sheet copy via `SheetsService`.
   * Response `{porf_id, sheet_url}`.
8. **Read‑only sheets** – Viewer ACL until `TWO_WAY_SYNC_ENABLED = True`.
9. **Future V2** – Drive push notifications → `get_sheet_changes()`. 