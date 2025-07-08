# Architectural Blueprint: Channel-Driven Inventory Manager

## 1. Core Philosophy

* **Architecture:** Explicitly clean, modular, and fully extensible.
* **Data Layer:** Robust core service as the central data hub.
* **Functional Plugins:** Channels independently select functionalities, explicitly opting into core insights.
* **Single Source of Truth:** Driven solely by a single ShipStation webhook; structured, organized storage via Google Drive and Sheets.
* **Separation of Concerns:** Explicit division between Core Service (data management) and Channel Plugins (functional actions).
* **Extensibility Model:** Channels explicitly decide functionalities, eliminating forced complexity in the core.

## 2. Explicit System Components & Responsibilities

### 2.1 Core Service Responsibilities

* **Organization & File Management:**

  * Explicitly creates structured Google Drive folders per channel (Amazon, eBay, Woot).
  * Manages structured access and updates to user-uploaded spreadsheets.
* **Webhook Processing:**

  * Single ShipStation webhook endpoint explicitly validates authenticity.
  * Parses order data (Order ID, SKU, quantities, timestamps, statuses).
  * Real-time spreadsheet updates via Google Sheets API based on SKU matching.
* **Data Tracking & Insights:**

  * Tracks explicit metrics: product frequency, inventory turnover, listing age/status.
  * Generates actionable insights: slow-moving, out-of-stock, aged listings.
  * Structured insight lists for channels: "Slow movers", "Out-of-stock", "Reallocation candidates".
* **Inter-Channel Communication:**

  * Maintains central "reallocation" list explicitly.
  * Channels independently choose actions (pull from or push to reallocation lists).

### 2.2 Individual Channel Responsibilities (Plug-and-Play)

* **Basic Channel Setup:**

  * Folder creation and spreadsheet setup via core.
  * Receives real-time spreadsheet updates from core.
* **Optional Advanced Features:**

  * Explicit automated actions: pause/delist products based on insights.
  * Adjust pricing, generate reports (PORFs, listings).
  * Independently manage reallocation (pull/push).

### 2.3 Explicit Responsibility Matrix

| Responsibility                   | Core Service | Channels     |
| -------------------------------- | ------------ | ------------ |
| Database Persistence             | ✅            | ❌            |
| Google Sheets/Drive Management   | ✅            | ❌            |
| Webhook Processing & Updates     | ✅            | ❌            |
| Insights & Projections           | ✅            | ✅ (Consumes) |
| Reacting to Insights             | ❌            | ✅ (Optional) |
| External Marketplace API Calls   | ❌            | ✅ (Optional) |
| Core Database/Sheet Modification | ✅            | ❌            |
| Audit Logging (Core Actions)     | ✅            | ❌            |
| Audit Logging (Channel Actions)  | ❌            | ✅ (Optional) |

## 3. Detailed Workflow: Explicit Step-by-Step

1. **Organisation Creation:** User creates organisation; core explicitly creates Drive folders per channel.
2. **Spreadsheet Upload:** Core recognizes uploaded spreadsheets, explicitly structures metadata.
3. **Webhook Processing:** ShipStation webhook received; core validates, parses, explicitly updates relevant Sheets.
4. **Insight Generation:** Explicitly identifies products (e.g., no sales in 60 days), updates insights and reallocation lists.
5. **Channel Reaction (Optional):** Channels explicitly read core insights, independently perform marketplace actions.

## 4. Explicit Data Models & Schema

* **Database:** SQLite only for the MVP.
* **Datetime:** ISO-8601 explicitly timezone-aware.

| Model        | Fields                                                                            | Constraints & Indices       |
| ------------ | --------------------------------------------------------------------------------- | --------------------------- |
| User         | id (PK), email (unique), organisation\_id (FK), allowed\_channels (JSON)          | Email unique, FK indexed    |
| Organisation | id (PK), name, drive\_folder\_id                                                  | Drive folder unique         |
| Product      | sku (PK), name, channel, quantity, status, listed\_date (datetime+TZ)             | SKU unique, indexed         |
| OrderRecord  | order\_id (PK), channel, product\_sku (FK), quantity, ordered\_date (datetime+TZ) | Order ID unique, FK indexed |
| Insights     | id (PK), product\_sku (FK), channel, status, generated\_date (datetime+TZ)        | FK indexed, status indexed  |
| Reallocation | sku, channel\_origin, reason, added\_date (datetime+TZ)                           | Indexed on SKU              |

### Required Environment Variables

* `APP_SECRET_KEY` – secret key for JWT signing
* `APP_DATABASE_URL` – database URL (defaults to SQLite if unset)
* `APP_WEBHOOK_SECRETS` – comma-separated HMAC keys for ShipStation webhook verification
* `APP_SERVICE_ACCOUNT_FILE` – path to Google service account JSON used for Drive and Sheets access
* `APP_WEBHOOK_SECRETS_FILE` – optional path to a file containing HMAC secrets (one per line)
* `APP_REDIS_URL` – Redis connection string used for concurrency locks and rate limiting
* `APP_MAX_PAYLOAD` – maximum allowed ShipStation webhook payload size in bytes (defaults to 1024)

### Local Redis Setup

Install Redis locally (e.g., `sudo apt-get install redis-server`) and start it:

```bash
redis-server --daemonize yes
```

Set `APP_REDIS_URL=redis://localhost:6379/0` before running the application or tests.

### Getting Started

1. `cp .env.example .env`
2. Fill in any secrets in `.env`.
3. `docker-compose up` or `flask run`

## 5. Technical Specifications

### 5.1 Webhook Authentication & Handling

* Explicitly HMAC SHA256 signed; header: `X-ShipStation-Signature`.
* Secrets explicitly managed and rotated quarterly.
* Webhook idempotency and 5-minute replay window enforced.
* Payloads over 1024 bytes are rejected with HTTP 413.

### 5.2 API & Authorization

* RESTful API explicitly versioned (`/api/v1/...`).
* Explicit JWT authentication (HS256, 24-hour expiry).
* JWT payload includes `sub`, `org_id`, and `roles` claims.
* RBAC explicitly defined for organisational roles and channel permissions.

### 5.3 Concurrency & Rate Limiting

* Explicit Redis queue management for Google API concurrency.
* Webhook throttling explicitly set to 100 events/sec.

### 5.4 Error Handling

* Explicit logging for 4xx and 5xx errors; retries and DLQ handling clearly defined.

### 5.5 Insights Logic

* Explicit thresholds: slow-moving ≥30 days, out-of-stock quantity=0, aging >180 days.
* Insights explicitly reviewed/purged every 90 days.

### 5.6 Logging & Observability

* Explicit structured JSON logs with correlation IDs.
* Logging uses **structlog** with JSON output only.
* Explicit metrics: webhook latency, API call durations, errors logged.

### 5.7 Security & Compliance

* Explicit anonymized handling of PII.
* Compliance-ready (SOC2/ISO 27001).

## 6. Project File Structure

```
inventory-manager-app/
├── core/
│   ├── models/ (user.py, organisation.py, product.py, order.py, insights.py)
│   ├── services/ (drive.py, sheets.py, webhook.py, insights.py)
│   ├── webhooks/ (shipstation.py)
│   ├── utils/ (auth.py, validation.py)
│   └── config/ (settings.py)
├── channels/
│   ├── amazon/ (actions.py, tasks.py, utils.py)
│   ├── ebay/ (actions.py, tasks.py, utils.py)
│   └── woot/ (actions.py, tasks.py, utils.py)
├── api/
│   ├── routes/ (auth.py, organisation.py, webhook.py)
│   └── schemas/ (user_schema.py, order_schema.py)
├── migrations/
│   └── versions/
├── tests/ (unit/, integration/, e2e/)
├── logs/ (application.log)
├── Dockerfile
├── requirements.txt
└── README.md
```

## 7. Explicit Implementation Roadmap

1. Finalize explicit schemas.
2. Implement and validate webhook endpoint explicitly.
3. Integrate explicit Google APIs via Redis.
4. Document core APIs explicitly.
5. Explicitly remove legacy complexities.
6. Establish explicit Docker-based CI/CD.
7. Implement explicit channel registration.

## 8. CI Pipeline

The CI job runs the following checks:

```bash
scripts/ci.sh
```

This script performs an Alembic upgrade/downgrade, verifies Redis connectivity,
runs linting with ruff and flake8, mypy type checking in strict mode, and
executes the pytest suite with coverage (fail under 85%).

## 9. Running Tests Locally

Tests run exclusively on SQLite for the MVP phase.

```bash
pytest --cov
```
