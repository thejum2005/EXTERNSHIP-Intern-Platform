# EXTERNSHIP INTERN PLATFORM

ERP-style intern management platform built with Flask + SQLite.

## Features
- Admin + Intern roles (session-based authentication)
- Attendance (prevent duplicate per day)
- Leave requests (approve/reject + rejection reason)
- Projects and Tasks (assign + mark completed)
- Weekly feedback
- Intern Friday topic assignment

## Requirements
- Python 3.10+

## Run locally (Windows / PowerShell)

From the `spi_edge_intern_platform` folder:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python run.py
```

Then open `http://localhost:5000`.

## Default login
- **Admin**: `admin@spi-edge.local` / `admin123`

You can create a test intern from the login page (“Create a test intern”) or as Admin via **Interns**.

## Database
- SQLite file is created at `database/database.db`
- To switch to PostgreSQL, set:
  - `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname`

