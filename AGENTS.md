# AGENTS.md

Here is a structured, explicit, and detailed outline clearly laying out your core ideas, ensuring simplicity, clarity, extensibility, and minimal complexity:

---

# 🎯 **Clear, Explicit Outline: Channel-Driven Inventory Manager**

## 1. **Overview (What is it?):**

* **Inventory Management App** with Google Drive & Sheets integration.
* Channels (Woot, Amazon, eBay, etc.) each have their own Drive folders.
* Orders come exclusively from **ShipStation webhooks**.
* Centralized **core backend** provides data tracking and insights.
* Channels can implement **additional functionality** based on core data.

---

## 2. **Core Backend Responsibilities:**

### 📂 **2.1. Organisation & File Management**

* Creates **Drive folders** for organisation channels (Amazon, eBay, etc.).
* Provides structured access to **user-uploaded spreadsheets**.
* Allows each channel to have clearly defined folder structures.

### 📥 **2.2. Receiving & Processing Orders**

* Single **ShipStation webhook endpoint**:

  * Verifies webhook authenticity.
  * Parses incoming order data (Order ID, product SKU, quantities, timestamps, statuses).
* **Automatically matches** orders to channel spreadsheets based on SKU or Order IDs.
* **Real-time updates** to relevant spreadsheets via Google Sheets API.

### 📊 **2.3. Data Tracking & Insights**

* Tracks key metrics from webhook data:

  * Product movement frequency.
  * Inventory turnover rates.
  * Listing status & age (how long since listed or updated).
* Generates simple insights:

  * **Slow-moving inventory**.
  * **Out-of-stock items**.
  * **Expiring or aged listings**.
* Maintains structured lists of products needing attention for each channel:

  * "Slow movers"
  * "Out-of-stock alerts"
  * "Reallocation candidates"

### 🔗 **2.4. Inter-Channel Communication (Flexible but Simple)**

* Central "reallocation" list managed by the core backend.
* Channels can read from this list and decide on actions independently.
* Possible actions channels can take (simple integration points):

  * **Pull from reallocation list**: Accept items marked by other channels for reallocation.
  * **Push to reallocation list**: Mark slow-moving or unwanted items.

*No forced complexity*: Channels voluntarily implement these actions.

---

## 3. **Individual Channel Responsibilities (Plug-and-Play Concept):**

Channels have complete autonomy in deciding their functionalities but have structured access to core backend data.

### 🛠️ **3.1. Basic Channel Setup (Minimal):**

* Folder creation & spreadsheet setup through core backend.
* Receive real-time spreadsheet updates from core backend based on ShipStation webhook data.

### ⚡ **3.2. Optional Advanced Channel Features (Clear, Simple Examples):**

**Channels can optionally implement:**

* **Automated Actions** (optional but powerful):

  * Automatically pause, list, or delist products based on slow-moving alerts.
  * Automatically adjust product pricing or quantity based on core insights.
* **Channel-specific Export**:

  * Export or generate reports (e.g., PORFs for Woot).
  * Generate formatted listings or marketing reports (e.g., Amazon or eBay listings).
* **Inter-Channel Cooperation**:

  * Pull new products from the "reallocation candidates" list to their own inventory automatically or via manual triggers.
  * Push products onto the reallocation list to share across channels.

This plug-and-play concept makes the channel modules completely independent but capable of powerful actions if they wish.

---

## 4. **Technical Structure (Clean, Simple, Extensible):**

```
inventory-manager-app
│
├── core
│   ├── models           # DB models (Orders, Products, Channels)
│   ├── services         # Google Drive, Sheets, Organisation services
│   ├── webhooks         # ShipStation webhook handling (single source)
│   └── insights         # Inventory analysis & tracking
│
├── channels
│   ├── amazon           # Optional Amazon-specific automation/actions
│   ├── ebay             # Optional eBay-specific automation/actions
│   └── woot             # Optional Woot-specific automation/actions
│
└── api                  # Flask API routes (user/org management, auth)
```

### **Responsibilities in each module:**

| Module     | Responsibility                                          |
| ---------- | ------------------------------------------------------- |
| `core`     | - Central webhook processing                            |
|            | - Drive/Sheets management                               |
|            | - Inventory insights, analysis                          |
|            | - Reallocation list management                          |
| `channels` | - Optional channel-specific automation                  |
|            | - Independent optional integration to reallocation list |
| `api`      | - User authentication & management                      |

---

## 5. **Example Simple Workflow (Concrete Scenario):**

### **Step-by-step example:**

* **Organisation creation**:

  * User creates org "MyStore"
  * Backend creates Drive folders for Amazon, eBay, Woot.

* **User uploads inventory spreadsheet**:

  * User uploads spreadsheets with product SKUs to each channel folder.
  * Backend recognizes files and structures metadata.

* **Order webhook received**:

  * ShipStation sends order webhook.
  * Backend verifies webhook, parses product SKU & order details.
  * Spreadsheet for correct SKU/channel updated instantly.

* **Insight generated by backend**:

  * Product SKU `123-XYZ` hasn't sold in 60 days.
  * Backend adds `123-XYZ` to "Slow movers" reallocation list.

* **Channel optionally acts (plug-and-play)**:

  * eBay channel reads from "slow movers" list.
  * Automatically imports `123-XYZ` into its own inventory for new listing.
  * Amazon optionally removes or pauses the slow-moving SKU via Amazon API.

---

## 6. **What Makes this Clean & Simple:**

* **Single webhook source** → real-time updates (no complex polling).
* **Clear division of responsibilities**:

  * Core backend: universal data tracking, insights.
  * Channels: optional plug-and-play automation.
* **Flexible but simple inter-channel interactions**:

  * Central lists (reallocation) allow cooperation without tight coupling.
  * Channels can opt in/out of automation entirely independently.

---

## 7. **Future Extensibility (Clear path forward):**

* Adding a new channel means just creating:

  * Drive folder via backend.
  * Optional custom actions for the channel.
* No backend refactoring needed to support new channels.
* Easily add powerful future automations incrementally.

---

## 8. **Immediate Concrete Next Steps (after confirmation):**

1. Remove polling/complex adapters completely.
2. Implement single webhook endpoint clearly and cleanly.
3. Structure clearly defined reallocation lists & insights in backend.
4. Optionally document how channels can implement plug-and-play functions.

---

## ✅ **Final Sanity Check (Why this works simply):**

* **Clarity**: Clear separation (core vs. channel).
* **Simplicity**: Minimal required components, simple real-time updates.
* **Extensible**: Channels fully optional and independent.
* **No forced complexity**: Channels choose when/how to add complexity.

### 📌 **Inventory Management Core Service (Clarification and Detailed Continuation)**

---

## 🔹 **1. Fundamental Philosophy (Reinforcement)**

* **Clean & Modular Architecture**:

  * Core service as a robust **data layer**.
  * Channels as independent **functional plugins** utilizing the core service's data.

* **Plug-and-Play Mindset**:

  * Channels independently choose functionality.
  * No forced complexity on core.

* **Single Source of Truth**:

  * ShipStation webhook drives updates.
  * Google Drive/Sheets maintain organized, accessible inventory data.

---

## 🔹 **2. Clarifying the Core Service Role**

**The Core Service is fundamentally a data hub:**

**It explicitly does:**

* **Organize data:** Manage Google Drive folders & spreadsheets.
* **Update inventory:** Handle real-time inventory updates from ShipStation webhook payloads.
* **Provide basic insights:** Product movement, inventory statuses, slow-moving, or depleted items.
* **Maintain structured data models:** Efficient and clear data structures (SQLite for simple dev, PostgreSQL potentially later for scaling).
* **Manage user & organisation data:** Keep clear data models for users, organisations, and related permissions.

**It explicitly does not:**

* Directly interact with marketplace APIs (Amazon, eBay, etc.) to alter listings or perform actions.
* Enforce any particular business logic beyond basic data categorization and notification (like marking "slow movers").
* Force complex implementations or functionalities onto channels.

---

## 🔹 **3. Refined Data Models (Clear & Essential)**

Explicitly clarify required data models:

| **Model**            | **Core Attributes**                                                     | **Purpose**                             |
| -------------------- | ----------------------------------------------------------------------- | --------------------------------------- |
| **User**             | `id`, `email`, `organisation_id`, `allowed_channels`                    | User management & permissions.          |
| **Organisation**     | `id`, `name`, `drive_folder_id`                                         | Drive folder organisation.              |
| **Product**          | `sku`, `name`, `channel`, `quantity`, `status`, `listed_date`           | Inventory tracking.                     |
| **OrderRecord**      | `order_id`, `channel`, `product_sku`, `quantity`, `ordered_date`        | Order history & status updates.         |
| **Channel** *(enum)* | e.g., `WOOT`, `AMAZON`, `EBAY`, `SHOPIFY`                               | Folder and channel identifiers.         |
| **InsightsRecord**   | `product_sku`, `channel`, `status` *(slow, reallocate, out\_of\_stock)* | Categorizing products needing attention |

---

## 🔹 **4. Explicit Webhook Implementation (Simple & Clean)**

**One webhook entry-point for ShipStation:**

* Endpoint: `/api/webhook/shipstation`
* Clearly validates incoming payload (signature verification).
* Transforms payload into internal data models (`OrderRecord`).
* Instantly updates appropriate Google Sheets based on `sku` & `channel`.

```plaintext
Webhook ➜ Verify ➜ Parse ➜ Data Model ➜ Google Sheets Update
```

---

## 🔹 **5. Clarifying Insights & Reallocation Logic**

* Core service maintains simple, actionable lists based on tracked inventory data.
* Structured reallocation lists are maintained at core:

  * "Slow-moving"
  * "Out-of-stock"
  * "Reallocation Candidates"

**Channels independently:**

* Decide whether to read from or write to these lists.
* Implement business-specific logic based on these structured insights.

**Example workflow (clarified):**

* Core service identifies product "ABC123" as slow-moving.
* Adds "ABC123" to the central "slow movers" list.
* Amazon channel plugin independently checks this list:

  * Optionally delists or adjusts pricing for "ABC123".
* eBay channel plugin independently checks this list:

  * Optionally creates a new eBay listing based on data from the core service.

**Result:**

* Core stays simple & neutral.
* Channels use the core’s structured lists freely, easily, and independently.

---

## 🔹 **6. Modular Plugin (Channel) Architecture**

Clear separation between core and channel plugins, practically:

```
inventory-manager-app/
├── core/
│   ├── models/
│   ├── services/ (Drive, Sheets, Webhooks)
│   ├── insights/ (Centralized lists)
│   └── utils/ (Shared helpers)
│
├── channels/ *(independent, optional modules)*
│   ├── amazon/
│   │   ├── actions.py *(Uses Amazon API to alter listings, prices, etc.)*
│   │   └── tasks.py *(Pulls insights from core’s lists)*
│   │
│   ├── ebay/
│   │   └── actions.py *(eBay-specific automated actions)*
│   │
│   └── woot/
│       └── actions.py *(PORF uploads, reports generation)*
│
└── api/ *(Flask endpoints for User/Org management & auth)*
```

**Key insight**:

* Channels never complicate core; they're self-contained and can be independently developed.
* Channels **opt-in** to core insights, without enforced logic from core.

---

## 🔹 **7. Channel Implementation Guidelines (Examples)**

### 🟡 **Optional Amazon Channel Actions (Explicit):**

* Automatically pause low-performing products based on core’s insights.
* Adjust pricing dynamically based on inventory turnover.
* Auto-migrate products marked for reallocation.

### 🟢 **Optional eBay Channel Actions (Explicit):**

* Automatically create new listings from reallocation candidates.
* Remove listings marked as out-of-stock.

### 🔵 **Optional Woot Channel Actions (Explicit):**

* Automatically generate and upload PORF documents from updated sheets.
* Generate monthly sales or inventory reports from core data.

---

## 🔹 **8. Keeping the SQLite Setup Lean (Simple Development Setup)**

* SQLite for local development simplicity.
* Single database for all core data (organisations, users, insights, orders).
* Easy migration path to PostgreSQL or cloud databases if needed for scaling.

---

## 🔹 **9. Extensible Design for Future Growth**

* Clearly defined plugin entry-points:

  * Core services expose structured, documented APIs.
* Channels explicitly use core’s API/data structures to implement independent logic.
* Add new channels easily without refactoring the core.

---

## 🔹 **10. Immediate Next Steps (Clear Actionable Roadmap)**

1. **Validate & finalize data models** (as outlined above).
2. **Implement and test webhook endpoint** (ShipStation payloads).
3. **Set up clean integration with Google Drive/Sheets API** for real-time sheet updates.
4. **Clearly document core service API** for potential future channels.
5. **Remove existing complexity** (adapters, polling, Celery tasks) completely.
6. **Define initial insights logic** (slow-moving, out-of-stock).

---

## ✅ **Final Sanity & Simplicity Check**

* **Simple**: One webhook, minimal core logic, independent channels.
* **Clear**: Explicitly defined roles, clearly structured data.
* **Extensible**: Independent channels, easy plug-and-play expansion.
* **No forced complexity**: Each piece only handles its responsibility clearly.

---

## 🚩 **Final Confirmation & Next Move:**

**This outline explicitly clarifies and continues your previous approval, addresses all your considerations, and refines the architecture to a clear, workable blueprint.**

**Next Steps:**

* Confirm this explicitly structured approach.
* Start immediate lean implementation steps outlined above.
* Keep clear boundaries between core service and optional channel plugins for maximum clarity and flexibility.

**This approach ensures you have a lean, flexible, and powerful foundation upon which channel-specific logic can flourish independently.**

## 📌 **CTO Architectural Continuation & Final Clarifications**

---

### 🔹 **Core Service vs. Channel Responsibilities (Clarification)**

**Core Service Responsibilities:**

* **Central Data Management**

  * Maintains a centralized, normalized set of database tables:

    * **Products**, **Orders**, **Users**, **Organisations**, **Insights**.
  * Acts as the single source of truth for all inventory and order statuses.
* **Webhook Processing (ShipStation)**

  * Validates incoming webhook requests.
  * Parses data, updates central database, logs events clearly.
* **Insights Generation**

  * Centralized insights (slow-moving, reallocation candidates, out-of-stock).
  * Channels are consumers of these insights, not the generators.
* **Drive & Sheets Management**

  * Manages organization-level Drive folders and spreadsheets structure.
  * Updates Sheets based on centralized data directly (this is core’s responsibility).

**Why Core handles updates to Sheets:**

* **Consistency & Integrity**:

  * Core ensures uniform, predictable updates. Avoids duplication, conflicts.
* **Single Source of Truth Enforcement**:

  * Channels should not have uncontrolled or conflicting access to Sheets.
* **Simplicity & Scalability**:

  * Channels don't worry about Sheet formatting or drive permissions.

---

**Individual Channel Responsibilities (Plug-and-Play):**

* **Optional Business Logic & API Integrations**:

  * Specific marketplace functionality (e.g., Amazon API calls, Woot PORF creation).
  * **Only** concerns itself with using the data provided by the core.
* **Event-based Triggers (Reactionary)**

  * Reacts to core data events or insights (e.g., slow movers, reallocation alerts).
  * Decides independently on actions to take based on provided insights.
* **Core Service Consumption** (read-only)

  * Consumes structured lists and data from core service.
  * Doesn't directly alter core database tables or Google Sheets.

**Channels Do Not:**

* Directly update Google Sheets.
* Independently handle inventory data persistence (core service does that).
* Actively poll or duplicate core data logic.

---

### 🔹 **Workflow Clarification: From Webhook to Channel Action**

Explicit, professional workflow example:

```plaintext
┌───────────────────────────────┐
│       ShipStation Webhook     │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Core Service (Webhook API)  │
│  - Validates incoming webhook │
│  - Updates central DB tables  │
│  - Updates relevant Sheets    │
│  - Logs clearly               │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Core Service (Insights)     │
│  - Analyzes new data          │
│  - Updates central insights   │
│    (slow-moving, out-of-stock)│
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│     Channels (Optional)       │
│  - Checks updated insights    │
│  - Runs independent logic     │
│    (e.g., Amazon delist slow) │
│  - Makes API calls externally │
│  - Does not alter core DB     │
│    or Sheets directly         │
└───────────────────────────────┘
```

* **Channels are fully reactive and decoupled.**
* **Core service always initiates the flow.**
* **Channels operate as optional “listeners” or “reactors” to core updates.**

---

### 🔹 **Example Channel Integration Scenario (Explicit Detail)**

**Scenario:** Amazon channel wants to pause listings with slow-moving stock.

1. **Core service:**

   * Identifies products that haven’t moved in 30 days.
   * Adds `sku: "ABC123", channel: "AMAZON", status: "slow-moving"` into insights.

2. **Amazon Channel (optional module):**

   * Periodically checks the insights endpoint provided by core:

     * Finds `ABC123` flagged as slow-moving.
   * Independently calls Amazon's Seller API:

     * Pauses or adjusts listing for `ABC123`.
     * Optionally, channel logs this action locally (not in core tables).

3. **Result:**

   * Channel reacts based on core insights without complexity or direct DB access.
   * Core stays clean, secure, and in control.

---

### 🔹 **Further Data & Interaction Clarifications**

* **Core database (SQLite for simplicity):**

  * Simplified local DB, centralized tables.
  * Easy future migration to production databases (PostgreSQL).
* **Core ↔ Channel Interaction Model:**

  * Channels communicate with core via clearly defined APIs:

    * Read-only access to insights.
    * No write access to core DB tables or Sheets.
* **Centralized Logging & Event Management:**

  * Clear logs and audit trails in core service for all webhooks & insight generation.
  * Channels can optionally log their actions separately if needed.

---

### 🔹 **Architectural & Technical Guidelines for Developers**

* **Core Service Guidelines:**

  * Maintain simplicity and clear separation of concerns.
  * Keep models and services strictly organized.
  * Use robust logging, clear documentation, and well-defined APIs.
  * Validate every webhook and payload rigorously.

* **Channel Plugin Guidelines:**

  * Fully independent development & deployment.
  * Clear documentation for how channels can integrate with core.
  * Do not duplicate core logic; use core’s APIs only.
  * React asynchronously to core updates, no active polling.
  * Clearly document each channel's capabilities and business logic.

---

### 🔹 **Future-Proofing & Flexibility:**

* **Easy Channel Expansion**:

  * Clearly documented APIs allow easy addition of future channels without refactoring core.
* **Flexible Insights & Actions:**

  * New insights can be added centrally without impacting existing channel implementations.
* **Scalable Logging & Audit Trails:**

  * Core logging structure easily extendable for future analytics or monitoring.
* **Straightforward Migration & Scaling:**

  * Initial SQLite setup easily migratable to PostgreSQL or Cloud SQL with minimal changes.

---

### 🔹 **Professional Recommendations (CTO Advisory):**

* Maintain strict adherence to single responsibility principles:

  * Core: Data-centric tasks (persistence, basic insights, sheets management).
  * Channels: Independent marketplace-specific actions.

* Clearly documented API interactions between core & channels to reduce confusion and increase scalability.

* Robust, centralized logging/auditing to enable transparency, easier debugging, and future analytics.

* Consider API versioning for core endpoints as channel features expand.

---

### 🔹 **Explicit Responsibilities Table (Final Clarity):**

| **Responsibility**                    | **Core Service** | **Channels** |
| ------------------------------------- | ---------------- | ------------ |
| Database Persistence                  | ✅                | ❌            |
| Google Sheets Management              | ✅                | ❌            |
| Inventory/Orders Updates              | ✅ (via Webhooks) | ❌            |
| Insights & Projections                | ✅                | ❌            |
| React to Insights                     | ❌                | ✅ (optional) |
| External API calls (e.g., Amazon API) | ❌                | ✅ (optional) |
| Direct DB/Sheet Modification          | ✅                | ❌            |
| Audit Logging (Core)                  | ✅                | ❌            |
| Audit Logging (Actions)               | ❌                | ✅ (optional) |

---

## ✅ **Final CTO Architectural Summary & Approval**

* **Clean & Clear Boundaries**: Responsibility definitions are explicitly clarified.
* **Simplicity & Robustness**: Clear and explicit workflow ensures no ambiguity.
* **Plug-and-Play Flexibility**: Channels independently consume core services.

**Next Actions (Development Team):**

* Confirm and implement the architecture as outlined above.
* Document APIs clearly for easy, independent channel implementations.
* Keep development focused and simple, strictly adhering to the defined responsibilities table.
