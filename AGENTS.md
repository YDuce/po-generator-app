===============================================================================
SECTION 1 — GLOBAL AI AGENT PROTOCOL
===============================================================================
1. Roles  
   • **Human Architect**: sets vision, features, quality bar.  
   • **Codex** (ChatGPT Projects): cross-file reasoning, large refactors, new
     features, test scaffolding.  
   • **Cursor**: local debugging, lint fixes, line-level refactors, test writing.

2. Workflow Loop  
   1. Architect issues a precise prompt (intent + scope + constraints).  
   2. Codex implements across the codebase.  
   3. Cursor pulls, tests, refines, commits.  
   4. Repeat.

3. Prompt Standards  
   • Every prompt **must** declare intent, affected paths, and constraints.  
   • If context is missing, Codex **must** ask; never hallucinate structure.  
   • Output: only the artefacts requested (commit hash, test summary, etc.).

===============================================================================
SECTION 2 — PROJECT BLUEPRINT : WOOT-MVP v2.5
===============================================================================
A. Purpose  
   Automate the entire warehouse-to-sale workflow for the Woot marketplace while
   remaining extensible to future channels (Amazon, eBay).

B. Primary Goals  
   1. Ingest warehouse scans, Woot PORFs, and PO PDFs.  
   2. Maintain authoritative JSONB tables (products, PORFs, POs,
      inventory records).  
   3. Auto-roll leftovers into new PORFs at PO expiry (7 months).  
   4. Real-time inventory deltas via ShipStation webhooks.  
   5. Spreadsheet-driven UX via Smartsheet (Google Sheets fallback).  
   6. AI helper for category and price suggestions (HF Falcon-7B-Instruct or
      local LLM).

C. Authoritative Tech Stack  
   | Layer               | Choice / Version        |
   |---------------------|-------------------------|
   | API server          | Flask 2 (app factory)   |
   | ORM / Migrations    | SQLAlchemy 2 / Alembic  |
   | DB                  | PostgreSQL 15 (prod) / SQLite (tests) |
   | Background work     | Celery 5 + Redis        |
   | Auth                | Google OAuth2 + JWT     |
   | Spreadsheets        | Smartsheet API (primary)|
   | AI helper           | Hugging Face API        |
   | Tests               | pytest + coverage       |
   | Linters / Types     | black, flake8-bugbear, mypy --strict |

D. Target Directory Layout (after this refactor)

```
app/
├── api/
│   ├── __init__.py        # BP factory – no circular imports
│   ├── auth.py            # Google OAuth, JWT
│   ├── catalog.py         # /api/catalog
│   ├── porf.py            # /api/porf
│   ├── export.py          # /api/export/{channel}/{template}
│   └── webhooks/
│       ├── smartsheet.py  # POST /webhooks/smartsheet/scan
│       └── shipstation.py # POST /webhooks/shipstation
├── channels/
│   ├── base.py
│   └── woot/
│       ├── connector.py
│       └── models.py
├── config/
│   └── settings.py        # Pydantic BaseSettings
├── logic/
│   ├── catalog_ingest.py
│   ├── porf_builder.py
│   ├── inventory_sync.py
│   ├── exporter.py
│   └── ai_helper.py
├── models/
│   ├── base.py
│   ├── master_product.py
│   ├── woot_porf.py
│   ├── woot_porf_line.py
│   ├── woot_po.py
│   ├── woot_po_line.py
│   └── inventory_record.py
├── services/
│   ├── smartsheet.py
│   ├── shipstation.py
│   └── huggingface.py
├── tasks/
│   ├── celery_app.py      # Celery factory
│   └── jobs.py            # po_expiry_sweep, email_dropbox_poll, shipstation_sync
├── tests/                 # must reach ≥ 90 % cov for logic/, services/, api/webhooks/
└── utils/                 # shared helpers
```

E. Quality Gates (non-negotiable)  
   ```
   black .
   flake8 . --max-line-length 120
   mypy app/ services/ logic/ -p app --strict
   pytest -q -x
   alembic upgrade head
   ```

F. Coding Rules  
   • snake_case everywhere; no names that collide with SQL keywords.  
   • One function == one responsibility; Google-style docstrings required.  
   • All tasks idempotent; Celery defaults: acks_late=True, autoretry_for=(Exception,).

G. Security / Secrets (.env.sample additions)  
   ```
   SMARTSHEET_TOKEN=
   SMARTSHEET_WEBHOOK_SECRET=
   CELERY_BROKER_URL=redis://localhost:6379/0
   REDIS_URL=redis://localhost:6379/0
   ```

H. Immediate Sprint v2.5 Scope  
   1. Replace `tasks/scheduler.py` with Celery + Redis.  
   2. Implement Smartsheet service layer + HMAC-verified webhook.  
   3. Implement ShipStation webhook (idempotent on shipment ID).  
   4. Delete obsolete `batch` & `batch_line` models + tables.  
   5. Consolidate config via Pydantic settings.  
   6. Raise test coverage to ≥ 90 %.

===============================================================================
(End of codex.md) ADDENDUM — IMPLEMENTATION DETAILS
1. Smartsheet Service API (contract)
```python
# services/smartsheet.py
from typing import Any, Dict, List
import hmac, hashlib, os

class SmartsheetClient:
    """Thin wrapper over the official SDK – only the calls we use."""
    def __init__(self, token: str) -> None:
        self._token = token
        self._client = smartsheet.Smartsheet(token)  # type: ignore

    # --------------------------------------------------------------------- verify
    def verify_signature(self, raw: bytes, header: str) -> bool:
        secret = os.getenv("SMARTSHEET_WEBHOOK_SECRET", "")
        actual = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
        return hmac.compare_digest(actual, header)

    # --------------------------------------------------------------------- sheets
    def get_sheet(self, sheet_id: str) -> Dict[str, Any]:
        return self._client.Sheets.get_sheet(sheet_id).to_dict()

    def add_row(self, sheet_id: str, row: Dict[str, Any]) -> None:
        self._client.Sheets.add_rows(sheet_id, [row])
```
2. Webhook Blueprint (routes only)
```python
# api/webhooks/smartsheet.py
bp = Blueprint("smartsheet_webhook", __name__, url_prefix="/webhooks/smartsheet")

@bp.post("/scan")
def scan():
    sig = request.headers.get("X-Smartsheet-Signature", "")
    if not current_app.smartsheet.verify_signature(request.data, sig):
        abort(403)
    logic.catalog_ingest.ingest_row(request.json)  # strict schema in logic layer
    return {"status": "ok"}

# api/webhooks/shipstation.py
bp = Blueprint("shipstation_webhook", __name__, url_prefix="/webhooks/shipstation")

@bp.post("")
def shipment():
    payload = request.get_json(force=True)
    sid = payload["shipmentId"]
    if models.InventoryRecord.exists_for_source("shipstation", sid):
        return {"status": "duplicate"}, 200
    logic.inventory_sync.process_webhook(payload)
    return {"status": "ok"}
```
3. Celery factory + jobs skeleton
```python
# tasks/celery_app.py
from celery import Celery

def create_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config.get("CELERY_RESULT_BACKEND"),
    )
    celery.conf.update(app.config)
    celery.autodiscover_tasks(["tasks.jobs"])
    return celery
```
```python
# tasks/jobs.py
from tasks.celery_app import create_celery
from datetime import timedelta

celery = create_celery(current_app)  # type: ignore

@celery.task(acks_late=True, autoretry_for=(Exception,))
def po_expiry_sweep():
    ...

@celery.task
def email_dropbox_poll():
    ...

@celery.task
def shipstation_sync():
    ...
```
4. Alembic Migration stub
```python
# alembic/versions/003_remove_batch.py
def upgrade():
    op.drop_table("batch")
    op.drop_table("batch_line")

def downgrade():
    # irreversible – document in migration message
    raise RuntimeError("Recreate manually if needed")
```
5. Testing matrix (minimum)
FileCase
tests/test_smartsheet_webhook.py200 OK on valid HMAC, 403 on invalid
tests/test_shipstation_webhook.pyduplicate shipment ignored (idempotent)
tests/test_celery_tasks.pypo_expiry_sweep.delay() runs in eager mode
tests/test_services_smartsheet.py.verify_signature() truth table
tests/test_logic_catalog.pyingest_row: new SKU, zero-qty SKU, bad SKU

pytest --cov=app --cov=logic --cov=services --cov=api/webhooks -q must report ≥ 90 %.

6. Rename / Delete Checklist
delete tasks/scheduler.py

delete channels/woot/models.Batch + BatchLine

rename any class PORFLine → WootPorfLine

rename column type → item_type (if present)

ensure api/__init__.py uses create_api() factory, avoiding circular import

7. .env.sample (full)
```ini
# core
DATABASE_URL=postgresql://user:pass@localhost/woot_mvp
SECRET_KEY=
JWT_SECRET=

# background
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0

# smartsheet
SMARTSHEET_TOKEN=
SMARTSHEET_WEBHOOK_SECRET=

# shipstation
SHIPSTATION_API_KEY=
SHIPSTATION_API_SECRET=

# email dropbox
DROPBOX_IMAP_HOST=
DROPBOX_IMAP_USER=
DROPBOX_IMAP_PASS=
DROPBOX_IMAP_FOLDER=INBOX

# hugging face
HF_API_TOKEN=
```
8. Pydantic settings (example fields)
```python
# config/settings.py
class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str
    jwt_secret: str

    celery_broker_url: str
    redis_url: str

    smartsheet_token: str
    smartsheet_webhook_secret: str

    shipstation_api_key: str
    shipstation_api_secret: str

    class Config:
        env_file = ".env"
```
9. Flake8 config (add to setup.cfg or pyproject.toml)
```ini
[flake8]
max-line-length = 120
extend-select = B  # bugbear
exclude = .venv,build,dist
```
ADDENDUM-II — REMAINING FACETS & NON-CODE DIRECTION

10. Logging & Observability
ConcernDirective
Log libraryUse structlog (JSONRenderer) — single logger instance per module.
Log levelsDEBUG in dev, INFO in prod; error paths emit exc_info=True.
Correlation IDsGenerate per request (X-Request-ID header); inject into Celery tasks via headers.
MetricsExpose /metrics (Prometheus) using prometheus-flask-exporter.
Health endpoints/status/health (DB ping, Redis ping, Celery ping) returns 200/503 JSON.

11. Error Handling & Validation
Flask error handler in api/__init__.py:
```python
@app.errorhandler(HTTPException)
def http_error(exc):
    return {"error": exc.description}, exc.code
@app.errorhandler(Exception)
def internal_error(exc):
    current_app.logger.exception("Unhandled error")
    return {"error": "internal-server-error"}, 500
```
Request validation: Marshmallow schemas (strict) or Pydantic models (preferred).

API always returns JSON {data: ..., error: ...}; never raw exceptions.

12. Pagination, Filtering, Sorting (API Standard)
Query params: page, page_size, sort, filter[...].

Default page_size = 50; max 500.

Use keyset pagination on large tables (id > :cursor_id) to avoid OFFSET.

13. Security Hardening
Enable Flask SESSION_COOKIE_SECURE, SESSION_COOKIE_SAMESITE="Lax".

Rate-limit all public routes with flask-limiter (100 req/min/token).

Store OAuth tokens encrypted at rest (use Fernet w/ JWT_SECRET).

14. Environment Separation
EnvBranchSettings override
localmain.env (defaults)
stagedevelop.env.stage — separate Redis DB, test keys
prodreleasereal secrets via Docker/K8s secrets

docker-compose.yml for local dev (Postgres + Redis).

15. Git / PR Policy
Branch names: feature/<short-desc>, bugfix/<short-desc>.

One logical change per PR; include checklist:

 code

 tests

 docs

 changelog entry

Commit message style (Conventional Commits):
feat(api): add smartsheet webhook, fix(tasks): handle redis downtime.

16. CI Pipeline (GitHub Actions)
pip install ".[dev]"

black --check .

flake8 .

mypy --strict app/ logic/ services/

pytest --cov=app --cov=logic --cov=services --cov=api/webhooks

alembic upgrade head on temporary SQLite DB

Fail build on coverage < 90 %.

17. Deployment Notes
Container: single Dockerfile (multi-stage) → woot-api:latest.

K8s manifests:

deployment.yaml (replicas=2, liveness /status/health)

worker.yaml (Celery worker + beat)

redis.yaml, postgres.yaml

Migrate DB on start with alembic upgrade head.

18. AI Helper Scaffolding (Phase-2)
services/huggingface.py:
```python
def suggest_category(title: str, attrs: dict) -> str: ...
def suggest_price(cost: float, brand: str, comps: list[float]) -> float: ...
```
If HF_API_TOKEN missing ⇒ raise NotImplementedError (local model later).

Expose experimental endpoints under /api/labs/ai/* (disabled in prod).

19. Smartsheet Sheet-ID Handling
Store sheet IDs in config.settings.py:
SMARTSHEET_SHEETS = {"scan": "...", "draft_porf": "...", ...}
Load from .env as comma-separated mapping.

20. Seed / Fixture Data
Management script scripts/seed.py — creates:

default vendor

dummy product SKU TEST-SKU-001

empty draft PORF

Used by tests and local onboarding.

21. Documentation Generation
make docs target: pdoc --output-dir docs app/ logic/ services/.

Serve via GitHub Pages on docs/ branch.

22. Pre-commit Hook
```bash
pre-commit install
Runs: black, flake8, mypy (fast-mode), detect-secrets.
```
