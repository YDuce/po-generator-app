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

# Prerequisites

- Python 3.11.8 (see `.python-version` for the exact version pin)
- For Windows users: Download Python 3.11.8 from [python.org](https://www.python.org/downloads/release/python-3118/)
- For Unix/Mac users: Use [pyenv](https://github.com/pyenv/pyenv) to manage Python versions

## Setting up your environment

### Windows
1. Install Python 3.11.8 from [python.org](https://www.python.org/downloads/release/python-3118/)
2. Run the setup script:
   ```powershell
   .\scripts\setup_test_env.ps1
   ```

### Unix/Mac
1. Install Python 3.11 (e.g., `pyenv install 3.11.8`)
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

The `.python-version` file is used by `pyenv` to automatically select the correct Python version.

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