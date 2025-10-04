
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
