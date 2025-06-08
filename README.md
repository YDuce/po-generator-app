# PO Generator App

A Flask application for managing purchase orders across multiple channels, with a focus on Woot integration.

## Project Structure

```
app/
├─ core/                 # Channel-agnostic domain code
│   ├─ models/          # Base models
│   ├─ interfaces.py    # Base interfaces
│   ├─ services/        # Generic services (Drive, Sheets)
│   └─ __init__.py
│
├─ channels/            # Channel-specific implementations
│   ├─ base.py         # Base channel interface
│   └─ woot/           # Woot channel implementation
│       ├─ models.py   # Woot-specific models
│       ├─ service.py  # Woot service implementation
│       └─ routes.py   # Woot API routes
│
├─ config/             # Configuration
├─ tests/              # Test suite
└─ main.py            # Application factory
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

## Development

1. Run the development server:
   ```bash
   flask run
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Format code:
   ```bash
   black .
   ```

4. Type checking:
   ```bash
   mypy .
   ```

## API Endpoints

### Woot Channel

- `GET /api/woot/orders` - List orders
- `POST /api/woot/orders` - Create order
- `GET /api/woot/orders/<order_id>` - Get order
- `PUT /api/woot/orders/<order_id>` - Update order
- `GET /api/woot/orders/<order_id>/status` - Get order status
- `POST /api/woot/export/sheets` - Export to Google Sheets

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

MIT 