# studentID_calculator_backend

## 1. Project Introduction

This repository is the **backend service** of the "front-end / back-end
separated calculator system". It is responsible for:

- receiving mathematical expressions from the front end and parsing and
  evaluating them **safely** (no `eval`/`exec`);
- strictly validating input (illegal characters, consecutive operators,
  parentheses matching, etc.);
- persisting every successful calculation to a SQLite database;
- exposing standard RESTful JSON endpoints that use proper HTTP status
  codes;
- providing history query, single-record deletion and clear-all.

The front-end repository handles the user interface and talks to this
backend over HTTP/HTTPS. **All core calculation logic lives in the
backend.**

## 2. Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Web framework | Flask | 3.0.3 |
| ORM | Flask-SQLAlchemy / SQLAlchemy | 3.1.1 / 2.0.31 |
| Database | SQLite | bundled with Python |
| CORS | Flask-Cors | 4.0.1 |
| Testing | pytest | 8.3.2 |
| Production server | Gunicorn (Linux) | 22.0.0 |
| Expression parsing | Python stdlib `ast` + `decimal` | built-in |

## 3. Runtime Environment

- Python 3.10 or newer (development used 3.10.0)
- pip (installed with Python)
- OS: Windows / macOS / Linux (**production deployment uses Linux**)

## 4. Installation Method

```bash
# Enter the backend repository
cd studentID_calculator_backend

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 5. Startup Method

### Development mode

```bash
python run.py
```

The backend listens on `http://0.0.0.0:5000`. After startup,
`http://localhost:5000/api/health` should return:

```json
{ "status": "ok", "message": "Calculator API is running" }
```

### Production mode (Linux server)

```bash
gunicorn --bind 0.0.0.0:5000 run:app
```

## 6. Configuration Instructions

Configuration lives in `app/config.py` and can be overridden by
environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ORIGINS` | Allowed CORS origins, `*` allows all | `*` |
| `SECRET_KEY` | Reserved session key | `calculator-dev-secret` |
| `MAX_HISTORY_RECORDS` | Maximum number of history records | `100` (constant in code) |

Copy `.env.example` to `.env` and adjust as needed. If the front end and
backend are deployed on the same domain (Nginx reverse proxy), you can
tighten `CORS_ORIGINS` to your domain.

## 7. Database Initialization Method

No manual initialization is required. On startup (`create_app`) the
application automatically:

1. creates the `data/` directory in the project root;
2. creates the SQLite file `data/calculator.db`;
3. creates the `calculation_history` table if it does not exist.

Delete `data/calculator.db` and restart the service to get a fresh empty
database.

### Table structure

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK AUTOINCREMENT | Primary key |
| expression | TEXT NOT NULL | The expression |
| result | REAL NOT NULL | Result (8 decimal places of precision) |
| is_favorite | BOOLEAN DEFAULT 0 | Favorite flag (reserved) |
| note | VARCHAR(50) | Note (reserved) |
| category | VARCHAR(50) | Category (reserved) |
| created_at | DATETIME | Calculation time |

At most **100** history records are kept; the oldest records are deleted
automatically when the limit is exceeded.

## 8. Front-end/Back-end Connection Method

The backend does not connect to the front end; it only exposes HTTP
APIs. The front end specifies the backend address through the
`VITE_API_BASE_URL` environment variable (default
`http://localhost:5000`). CORS is enabled for `/api/*`, so the front end
can call the backend across ports without an extra proxy.

## 9. Project Structure

```
studentID_calculator_backend/
├── app/
│   ├── __init__.py               # Flask application factory
│   ├── config.py                 # Configuration
│   ├── models/                   # Database models
│   │   ├── calculation.py
│   │   └── history.py
│   ├── routes/                   # Routes
│   │   ├── calculate.py          # POST /api/calculate
│   │   ├── history.py            # GET/PATCH/DELETE /api/history
│   │   └── health.py             # GET /api/health
│   ├── services/                 # Business logic
│   │   ├── calculator.py         # Core calculation (safe parsing)
│   │   └── history_service.py    # History service
│   └── utils/
│       └── validators.py         # Input validation
├── tests/
│   ├── test_calculator.py        # Calculator service unit tests
│   └── test_api.py               # API tests
├── data/                         # SQLite database (auto-generated, not committed)
├── requirements.txt
├── run.py
├── nginx.conf
├── .env.example
├── README.md
└── codestyle.md
```

## API Overview

| Method | Path | Description | Success status |
|--------|------|-------------|----------------|
| POST | `/api/calculate` | Calculate and store an expression | 200 |
| GET | `/api/history` | Query history (`limit`/`offset`/`favorite`) | 200 |
| PATCH | `/api/history/{id}/favorite` | Toggle the favorite flag | 200 |
| DELETE | `/api/history/{id}` | Delete one record | 204 |
| DELETE | `/api/history` | Clear all history | 204 |
| GET | `/api/health` | Health check | 200 |

Error status codes: `400` (bad input), `404` (resource not found),
`500` (server error).

## Testing

```bash
pytest -v
```

## Deployment

1. SSH into a Linux server and install Python 3 and pip;
2. Clone the backend repository and install dependencies:
   `pip install -r requirements.txt`;
3. Start it with Gunicorn:
   `gunicorn --bind 0.0.0.0:5000 run:app`;
4. Open the corresponding port in the firewall;
5. Optionally use Nginx to reverse-proxy `/api/` to the backend (see
   `nginx.conf`).
