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

Postman urls

📁 Plupool API
│
├── 📁 Health & Root
│   ├── Root (GET /)
│   └── Health Check (GET /api/v1/health)
│
├── 📁 Authentication
│   ├── Guest Mode (POST /api/v1/auth/guest)
│   ├── Send OTP (POST /api/v1/auth/send-otp)
│   └── Verify OTP (Login) (POST /api/v1/auth/verify-otp)
│
├── 📁 Sign Up
│   ├── Sign Up - Technician (POST /api/v1/auth/signup/technician)
│   ├── Sign Up - Pool Owner (POST /api/v1/auth/signup/pool-owner)
│   └── Sign Up - Company (POST /api/v1/auth/signup/company)
│
├── 📁 Users (Protected)
│   ├── Get Current User (GET /api/v1/users/me)
│   ├── Get All Users (GET /api/v1/users/)
│   └── Get User by ID (GET /api/v1/users/{id})
│
└── 📁 Validation Tests
    ├── Invalid Phone
    ├── Invalid Name
    └── Invalid OTP
```

---

## **Testing Flow:**

### **1. Test Basic Endpoints**
```
✅ Root
✅ Health Check
✅ Guest Mode
```

### **2. Sign Up Flow (Technician Example)**
```
1. Send OTP → Check terminal for code
2. Sign Up - Technician → Use OTP from terminal
3. Verify response
```

### **3. Login Flow**
```
1. Send OTP → Get code from terminal
2. Verify OTP → Token auto-saved in environment
3. Get Current User → Uses saved token
```

### **4. Test Protected Endpoints**
```
✅ Get Current User (needs token)
✅ Get All Users (needs token)
✅ Get User by ID (needs token)