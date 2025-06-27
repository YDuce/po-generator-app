# AGENTS.md

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

## ✅ **Final Sanity Check (Why this works simply):**

* **Clarity**: Clear separation (core vs. channel).
* **Simplicity**: Minimal required components, simple real-time updates.
* **Extensible**: Channels fully optional and independent.
* **No forced complexity**: Channels choose when/how to add complexity.