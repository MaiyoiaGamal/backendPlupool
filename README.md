Plupool Backend API
RESTful API backend for the Plupool application built with FastAPI, PostgreSQL, and SQLAlchemy.
Features

User authentication with JWT tokens
Role-based access control (Pool Owner, Technician, Company)
Arabic validation messages
Password hashing with bcrypt
PostgreSQL database
Interactive API documentation (Swagger UI)

Tech Stack

Framework: FastAPI 0.118.0
Database: PostgreSQL 14+
ORM: SQLAlchemy 2.0
Authentication: JWT (python-jose)
Password Hashing: bcrypt 4.2.1
Python: 3.13+

Project Structure
backendPlupool/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Authentication endpoints
│   │       │   ├── users.py         # User management endpoints
│   │       │   └── health.py        # Health check endpoint
│   │       └── api.py               # API router
│   ├── core/
│   │   ├── config.py                # Application settings
│   │   ├── security.py              # Password & JWT functions
│   │   ├── dependencies.py          # Auth dependencies
│   │   └── validators.py            # Input validators
│   ├── db/
│   │   ├── database.py              # Database connection
│   │   └── base.py                  # Base model imports
│   ├── models/
│   │   └── user.py                  # User model
│   ├── schemas/
│   │   ├── user.py                  # User schemas
│   │   ├── auth.py                  # Auth schemas
│   │   └── token.py                 # Token schemas
│   └── main.py                      # Application entry point
├── tests/
├── venv/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
Installation
Prerequisites

Python 3.13+
PostgreSQL 14+
pip

Setup

Clone the repository

bash   git clone https://github.com/yourusername/plupool-backend.git
   cd plupool-backend

Create virtual environment

bash   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies

bash   pip install -r requirements.txt

Configure PostgreSQL

bash   # Start PostgreSQL
   brew services start postgresql@14  # macOS with Homebrew
   
   # Create database and user
   psql postgres
In PostgreSQL shell:
sql   CREATE DATABASE plupool_db;
   CREATE USER plupool_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE plupool_db TO plupool_user;
   \c plupool_db
   GRANT ALL ON SCHEMA public TO plupool_user;
   \q

Configure environment variables

1. Copy the example file and edit the values you need:

   ```bash
   cp .env.example .env
   ```

2. Make sure `DATABASE_URL` matches how you plan to run PostgreSQL (see the next section for a Docker-based option).

Run PostgreSQL locally (Docker)

If you do not have PostgreSQL installed natively, the repository ships with a ready-made Compose file:

```bash
docker compose up -d db
```

This will start a PostgreSQL 16 instance listening on `localhost:5432` and keep the data in the `postgres_data` volume. Update `.env` if you change the username, password, or database name. To verify the service is healthy, run `docker compose ps` or `docker compose logs db`.

Run the application

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000

Troubleshooting: connection refused

- Ensure the PostgreSQL service is running (`brew services list`, `docker compose ps`, or `sudo service postgresql status`).
- Confirm you can connect manually: `psql postgresql://user:password@localhost:5432/plupool_db`.
- Double-check `DATABASE_URL` in `.env` matches the running host and port. When using Docker Compose from this repo the host should stay `localhost`; when running the API inside another container the host must be `db`.
- Restart the API server after changing the database connection information so SQLAlchemy picks up the new value.
API Documentation
Once the server is running, access the interactive API documentation:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
