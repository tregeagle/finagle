# Finagle

Sort your finances **like a ninja**!

Personal finance app for tracking stock transactions and calculating Australian Capital Gains Tax (CGT).

**Get In:** Accounts are simply created with a name and no other identifying information. Import your trading histories using CSV's from Sharesight, Pearler and Finagle. 

**Get Out:** Once done you can export the whole thing as a CSV and delete your account. 

It will be as if you have never been here....

## Features

- **User Management** — Create, retrieve, and delete user accounts with isolated data per user
- **Stock Transaction Tracking** — Record buy/sell transactions with date, time, ticker, quantity, price, value, fees, and optional contract notes
- **Australian CGT Calculation**
  - FIFO (First-In-First-Out) lot matching
  - 50% CGT discount for assets held >12 months
  - Capital loss offsetting per ATO guideline 18A
  - Reports grouped by Australian financial year (July–June)
- **Multi-format Import** — Bulk-import transactions from Finagle CSV, Sharesight (.xlsx), or Pearler (.csv) exports with auto-detection and row-level validation; downloadable CSV template provided
- **Data Export** — Export user data and transactions in JSON or CSV format
- **Filtering** — Query transactions by ticker symbol, action type (buy/sell), or financial year

## Tech Stack

### Backend
- **FastAPI** + **Uvicorn** (Python 3.12+)
- **SQLAlchemy 2.0** + **SQLite** (configurable)
- **Alembic** for database migrations
- **Pydantic** for data validation
- **pytest** for testing

### Frontend
- **React 19** + **TypeScript** (via Vite)
- **Tailwind CSS v4** for styling
- **React Router** for client-side routing

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
uv sync
```

### Configuration

| Variable | Description | Default |
|---|---|---|
| `FINAGLE_DATABASE_URL` | Database connection string | `sqlite:///finagle.db` |
| `FINAGLE_API_KEY` | API key for authentication (empty = auth disabled) | _(empty)_ |
| `FINAGLE_ENVIRONMENT` | `dev` or `production` (hides docs in production) | `dev` |
| `FINAGLE_MAX_UPLOAD_MB` | Maximum upload file size in MB | `10` |
| `FINAGLE_CORS_ORIGINS` | Comma-separated allowed CORS origins | `http://localhost:5173` |
| `VITE_API_URL` | API base URL (frontend `.env`) | `http://localhost:8000/api/v1` |
| `VITE_API_KEY` | API key sent by the frontend (must match `FINAGLE_API_KEY`) | _(empty)_ |

### Running

```bash
# Apply database migrations
uv run alembic upgrade head

# Start the API server
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server runs at `http://localhost:5173` and proxies API calls to the backend.

To build for production:

```bash
npm run build
```

This produces static files in `frontend/dist/` that can be deployed to any static hosting (Netlify, Vercel, S3, etc.) independently of the backend. Set `VITE_API_URL` in a `.env` file to point to the production API.

### Testing

```bash
uv run pytest
```

Tests use an in-memory SQLite database with transaction rollback between tests.

## API Reference

Base URL: `/api/v1`

### Users (`/users`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/users` | Create or get-or-create a user |
| GET | `/users/{user_id}` | Retrieve user details |
| DELETE | `/users/{user_id}` | Delete user and all associated transactions |
| GET | `/users/{user_id}/export` | Export user data (JSON or CSV) |

### Transactions (`/users/{user_id}/transactions`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/users/{user_id}/transactions` | Create a transaction |
| GET | `/users/{user_id}/transactions` | List transactions (filterable by ticker, action, financial year) |
| GET | `/users/{user_id}/transactions/{txn_id}` | Retrieve a transaction |
| DELETE | `/users/{user_id}/transactions/{txn_id}` | Delete a transaction |

### Import (`/import`)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/import/template` | Download CSV import template |
| POST | `/users/{user_id}/import` | Bulk-import transactions (CSV or XLSX; auto-detects Finagle, Sharesight, Pearler formats) |

### CGT Reports (`/users/{user_id}/reports`)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/{user_id}/reports/cgt` | CGT overview for all financial years |
| GET | `/users/{user_id}/reports/cgt/{fy}` | Detailed CGT report for a financial year (e.g. `2023-24`) |

## Deploying to Railway

Railway runs the app as a single Docker service — backend and frontend on the same origin.

### Setup

1. Create a new Railway project and link this repo
2. Add a **Volume** mounted at `/data` (for SQLite persistence)
3. Set the following **service variables**:

| Variable | Value |
|---|---|
| `FINAGLE_DATABASE_URL` | `sqlite:////data/finagle.db` |
| `FINAGLE_API_KEY` | _(generate a secret token)_ |
| `FINAGLE_ENVIRONMENT` | `production` |
| `FINAGLE_CORS_ORIGINS` | `https://<your-app>.up.railway.app` |

4. Set the following **build variables** (used as Docker build args):

| Variable | Value |
|---|---|
| `VITE_API_KEY` | _(same token as `FINAGLE_API_KEY`)_ |
| `VITE_API_URL` | `/api/v1` |

5. Deploy — Railway will build the Dockerfile, run Alembic migrations on start, and serve the app on port 8000

### Local Docker test

```bash
docker build --build-arg VITE_API_KEY=test --build-arg VITE_API_URL=/api/v1 -t finagle .
docker run -p 8000:8000 -e FINAGLE_API_KEY=test finagle
```

## Project Structure

```
finagle/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── api/v1/                  # API routers
│   │   └── routers/
│   │       ├── users.py
│   │       ├── transactions.py
│   │       ├── imports.py
│   │       └── reports.py
│   ├── core/                    # Config & database setup
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic validation schemas
│   └── services/                # Business logic
│       ├── user_service.py
│       ├── transaction_service.py
│       ├── cgt_service.py
│       ├── import_service.py
│       └── parsers/             # Import format parsers
│           ├── native.py        # Finagle CSV format
│           ├── sharesight.py    # Sharesight AllTradesReport.xlsx
│           └── pearler.py       # Pearler order-statement.csv
├── frontend/                    # React SPA (independently deployable)
│   ├── src/
│   │   ├── api/client.ts        # Typed API client
│   │   ├── pages/               # Route-level components
│   │   └── components/          # Shared UI components
│   ├── package.json
│   └── vite.config.ts
├── tests/                       # Test suite
├── alembic/                     # Database migrations
├── templates/                   # CSV import template
└── pyproject.toml
```
