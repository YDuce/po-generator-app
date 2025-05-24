# SPEC.md

## Project
**inventory-manager**: API-first Flask app for inventory & PO generation.

## Goals
1. Centralize product, order, inventory across channels.
2. Configurable allocation rules & batch PO recommendations.
3. Exportable Excel/CSV POs.
4. AJAX-driven UI for real-time progress & dashboard.
5. Extensible connectors (ShipStation, Amazon, eBay).
6. AI anomaly detection/trend allocation.

## File Tree
app.py ← Flask app entrypoint
config.py ← env config loader
database.py ← SQLAlchemy + session setup
alembic/ ← migrations
models/… ← ORM models (product, order, inventory, etc.)
logic/… ← services: parsers, allocator, PO builder, AI helper
connectors/… ← base Connector API + implementations
api/… ← Flask blueprints (upload, status, results)
templates/… ← Jinja2 templates (base.html, index.html, dashboard.html)
static/
├── main.js ← HTMX + fetch logic
└── styles.css ← minimal overrides (Tailwind via CDN)
uploads/ ← incoming files
outputs/ ← generated POs
tests/
├── unit/ ← pytest unit tests
└── integration/ ← end-to-end tests
.github/workflows/ ← CI + AI review
SPEC.md ← this file
README.md ← project overview & setup

## External Dependencies
- Python 3.11+, Flask, SQLAlchemy, Alembic  
- pandas, openpyxl, requests  
- HTMX (AJAX), Tailwind (via CDN), Chart.js (via CDN)  
- pytest, flake8  
- GitHub Actions

## Constraints
- 4-space indent, snake_case, docstrings on all public functions  
- All deployments run CI: `flake8`, `pytest`, `mypy` (optional)  
- No Node build steps—static assets via CDN  

