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
Create .env file in the project root:

env   # Application
   APP_NAME=Plupool API
   APP_VERSION=1.0.0
   DEBUG=True
   
   # Database
   DATABASE_URL=postgresql://plupool_user:your_secure_password@localhost:5432/plupool_db
   
   # Security
   SECRET_KEY=your-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # CORS
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

Run the application

bash   python -m uvicorn app.main:app --reload
The API will be available at http://127.0.0.1:8000
API Documentation
Once the server is running, access the interactive API documentation:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

Misc (Generate a Word file from question photos)

- Put your images anywhere in the repo (e.g. in a folder called `inputs/`)
- Run:

  bash   python3 scripts/make_questions_doc.py --out "اسئلة.docx" inputs/ورقة1.jpg inputs/ورقة2.jpg

- Output:
  - `اسئلة.docx` will be created in the current directory (or the path you pass to `--out`)
