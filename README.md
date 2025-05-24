# Inventory Manager

API-first Flask app to centralize inventory and generate purchase orders.

## Features
- Import products/orders from Excel & ShipStation  
- Configurable allocation rules & batch PO recommendations  
- AJAX-driven progress UI (HTMX) & dashboard (Chart.js)  
- Extensible connectors for Amazon, eBay, etc.  
- Export POs as Excel/CSV  

## Quickstart

1. Clone repo  
   ```bash
   git clone git@github.com:your-org/inventory-manager.git
   cd inventory-manager
Create virtualenv & install

bash
Copy
Edit
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Configure

bash
Copy
Edit
cp .env.example .env
# edit DATABASE_URL, API keys, etc.
Initialize database

bash
Copy
Edit
alembic upgrade head
Run server

bash
Copy
Edit
flask run
Run tests

bash
Copy
Edit
pytest