# PO Generator App

A Flask-based application for generating Purchase Orders (POs) with Google Drive integration and multi-channel support.

## Overview

The PO Generator App streamlines the process of creating and managing Purchase Orders across multiple channels. It integrates with Google Drive for document storage and Google Sheets for PO templates, with a current focus on Woot channel integration.

For detailed documentation, please refer to the [docs](./docs) directory:
- [API Documentation](./docs/api.md)
- [Authentication System](./docs/authentication.md)
- [Database Models and Migrations](./docs/database.md)
- [Improvement Plan](./docs/plan.md)

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

## Prerequisites

- Python 3.11.8 (see `.python-version` for the exact version pin)
- PostgreSQL database
- Google Cloud Project with OAuth credentials

## Quick Start

### Windows
1. Install Python 3.11.8 from [python.org](https://www.python.org/downloads/release/python-3118/)
2. Run the setup script:
   ```powershell
   .\scripts\setup_test_env.ps1
   ```

### Unix/Mac
1. Install Python 3.11.8 (e.g., `pyenv install 3.11.8`)
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Set up environment variables:
   ```bash
   cp .env .env
   # Edit .env with your configuration
   ```

2. Initialize the database:
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

3. Code quality tools:
   ```bash
   # Format code
   black .

   # Type checking
   mypy .

   # Linting
   flake8

   # Run pre-commit hooks
   pre-commit run --all-files
   ```

## API Endpoints

For a complete list of API endpoints and their documentation, see [API Documentation](./docs/api.md).

### Key Endpoints

- **Authentication**: `/api/auth/google`, `/api/auth/refresh`
- **User Management**: `/api/auth/me`, `/api/auth/check`
- **Organisation Management**: `/api/organisations/{id}`
- **Purchase Order Management**: `/api/purchase-orders`
- **Woot Channel**: `/api/woot/orders`, `/api/woot/export/sheets`

## Branch Information

This repository follows the Git workflow described in [AGENTS.md](./AGENTS.md). The current branch structure:

- `main`: Production-ready code
- `pycharm`: Development branch with latest features and improvements

## Contributing

1. Review the [AGENTS.md](./AGENTS.md) file for development conventions
2. Create a feature branch following the naming convention `feat/<ticket>`
3. Make your changes following the project's coding standards
4. Run tests and linting to ensure code quality
5. Submit a pull request to the appropriate branch

## License

MIT
