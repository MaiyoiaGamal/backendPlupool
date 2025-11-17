# Plupool Backend API

RESTful API backend for the Plupool application built with FastAPI, PostgreSQL, and SQLAlchemy.

## Features

- User authentication with JWT tokens
- Role-based access control (Pool Owner, Technician, Company)
- **Services Management (Maintenance Services)**
- **Pool Types Management (Construction)**
- **Maintenance Packages (Monthly, Quarterly, Yearly)**
- **Booking System with Custom Pool Dimensions**
- **Automated Maintenance Reminders**
- Arabic validation messages
- Password hashing with bcrypt
- PostgreSQL database
- Interactive API documentation (Swagger UI)

## Tech Stack

- **Framework**: FastAPI 0.118.0
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt 4.2.1
- **Python**: 3.13+

## Project Structure
```
backendPlupool/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Authentication endpoints
│   │       │   ├── users.py         # User management endpoints
│   │       │   ├── services.py      # Services, Pool Types, Packages endpoints
│   │       │   ├── bookings.py      # Bookings endpoints
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
│   │   ├── user.py                  # User model
│   │   ├── service.py               # Service model
│   │   ├── pool_type.py             # Pool Type model
│   │   ├── maintenance_package.py   # Maintenance Package model
│   │   └── booking.py               # Booking model
│   ├── schemas/
│   │   ├── user.py                  # User schemas
│   │   ├── auth.py                  # Auth schemas
│   │   ├── token.py                 # Token schemas
│   │   ├── service.py               # Service schemas
│   │   ├── pool_type.py             # Pool Type schemas
│   │   ├── maintenance_package.py   # Package schemas
│   │   └── booking.py               # Booking schemas
│   └── main.py                      # Application entry point
├── tests/
├── venv/
├── create_tables.py                 # Database tables creation script
├── seed_data.py                     # Sample data seeding script
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.13+
- PostgreSQL 14+
- pip

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/MaiyoiaGamal/backendPlupool.git
cd backendPlupool
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure PostgreSQL**
```bash
# Start PostgreSQL
brew services start postgresql@14  # macOS with Homebrew

# Create database and user
psql postgres
```

In PostgreSQL shell:
```sql
CREATE DATABASE plupool_db;
CREATE USER plupool_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE plupool_db TO plupool_user;
\c plupool_db
GRANT ALL ON SCHEMA public TO plupool_user;
\q
```

5. **Configure environment variables**

Create `.env` file in the project root:
```env
# Application
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
```

6. **Seed sample data (optional but recommended)**
```bash
python seed_data.py
```
The script creates any missing tables and inserts demo content so the API,
dashboards, store, and technician flows have something to render:
- Core catalog: curated services, pool types, and maintenance packages
- Store data: categories, featured products, and promotional offers
- Sample activity: seeded users, bookings, testimonials, notifications, contact messages
- Technician experience: tasks, pool profiles, and recent water-quality readings

7. **Run the application**
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API Endpoints

### 📁 Plupool API Structure
```
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
├── 📁 Services (Protected) 🆕
│   ├── Get All Services (GET /api/v1/services/services)
│   ├── Get Service by ID (GET /api/v1/services/services/{id})
│   ├── Create Service - Admin (POST /api/v1/services/services)
│   ├── Update Service - Admin (PUT /api/v1/services/services/{id})
│   └── Delete Service - Admin (DELETE /api/v1/services/services/{id})
│
├── 📁 Pool Types (Protected) 🆕
│   ├── Get All Pool Types (GET /api/v1/services/pool-types)
│   ├── Get Pool Type by ID (GET /api/v1/services/pool-types/{id})
│   ├── Create Pool Type - Admin (POST /api/v1/services/pool-types)
│   ├── Update Pool Type - Admin (PUT /api/v1/services/pool-types/{id})
│   └── Delete Pool Type - Admin (DELETE /api/v1/services/pool-types/{id})
│
├── 📁 Maintenance Packages (Protected) 🆕
│   ├── Get All Packages (GET /api/v1/services/maintenance-packages)
│   ├── Get Package by ID (GET /api/v1/services/maintenance-packages/{id})
│   ├── Create Package - Admin (POST /api/v1/services/maintenance-packages)
│   ├── Update Package - Admin (PUT /api/v1/services/maintenance-packages/{id})
│   └── Delete Package - Admin (DELETE /api/v1/services/maintenance-packages/{id})
│
├── 📁 Bookings - User (Protected) 🆕
│   ├── Create Booking (POST /api/v1/bookings/bookings)
│   ├── Get My Bookings (GET /api/v1/bookings/bookings/my-bookings)
│   ├── Get My Booking Detail (GET /api/v1/bookings/bookings/my-bookings/{id})
│   └── Get My Maintenance Reminders (GET /api/v1/bookings/bookings/my-reminders)
│
├── 📁 Bookings - Admin (Protected) 🆕
│   ├── Get All Bookings (GET /api/v1/bookings/admin/bookings)
│   ├── Get Pending Bookings (GET /api/v1/bookings/admin/bookings/pending)
│   ├── Update Booking Status (PUT /api/v1/bookings/admin/bookings/{id})
│   └── Delete Booking (DELETE /api/v1/bookings/admin/bookings/{id})
│
└── 📁 Validation Tests
    ├── Invalid Phone
    ├── Invalid Name
    └── Invalid OTP
```
Role Dashboards
---------------

Role specific homepage APIs are exposed under `/api/v1/dashboard` and require a valid bearer token with the matching user role:

| Endpoint | Method | Role | Description |
| --- | --- | --- | --- |
| `/api/v1/dashboard/pool-owner/home` | GET | Pool Owner | Returns quick actions, featured offers, store highlights, testimonials, projects, and personalized account metrics for pool owners. |
| `/api/v1/dashboard/company/home` | GET | Company | Delivers the shared homepage sections plus a company-focused account summary (team size, active projects, pending requests, average rating). |
| `/api/v1/dashboard/technician/home` | GET | Technician | Provides technician stats (rating, weekly workload, completed tasks), a weekly planner, store highlights, projects, and recent feedback cards. |

Each response bundles navigation metadata (user info, contact channels, notification counts) and a standardized bottom navigation structure to align with the shared mobile designs.

---

## 🆕 Booking System Features

### 📋 Booking Types

1. **Maintenance Single** - One-time maintenance service
2. **Maintenance Package** - Recurring maintenance (Monthly/Quarterly/Yearly) with automated reminders
3. **Construction** - Pool construction with custom dimensions

### 🏊 Pool Construction Booking

When booking pool construction, you can specify custom dimensions:
```json
{
  "booking_type": "construction",
  "pool_type_id": 1,
  "booking_date": "2025-11-01",
  "booking_time": "10:00:00",
  "custom_length": 7.0,
  "custom_width": 4.0,
  "custom_depth": 2.0,
  "notes": "I want the pool in the backyard"
}
```

### 📦 Maintenance Packages

- **Monthly Package**: 4 visits/month, 1,200 EGP
- **Quarterly Package**: 16 visits/4 months, 4,500 EGP
- **Yearly Package**: 48 visits/year, 12,000 EGP

### 🔔 Automated Reminders

For maintenance packages, the system automatically:
- Calculates next maintenance date
- Sends reminders 3 days before the scheduled date
- Updates maintenance schedule after completion

---

## Testing Flow

### **1. Test Basic Endpoints**
```
✅ Root
✅ Health Check
✅ Guest Mode
```

### **2. Sign Up Flow (Pool Owner Example)**
```
1. Send OTP → Check terminal for code
2. Sign Up - Pool Owner → Use OTP from terminal
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
```

### **5. Test Services 🆕**
```
✅ Get All Services (needs token)
✅ Get All Pool Types (needs token)
✅ Get All Maintenance Packages (needs token)
```

### **6. Test Bookings 🆕**
```
✅ Create Maintenance Booking (needs token)
✅ Create Package Booking (needs token)
✅ Create Construction Booking with dimensions (needs token)
✅ Get My Bookings (needs token)
✅ Get Maintenance Reminders (needs token)
```

### **7. Test Admin Features (Admin token required) 🆕**
```
✅ Create Service/Pool Type/Package
✅ View All Bookings
✅ View Pending Bookings
✅ Confirm/Cancel Bookings
```
---

## Example Requests

### Create Maintenance Single Booking
```bash
POST http://127.0.0.1:8000/api/v1/bookings/bookings
Authorization: Bearer {token}
Content-Type: application/json

{
  "booking_type": "maintenance_single",
  "service_id": 1,
  "booking_date": "2025-10-30",
  "booking_time": "12:00:00",
  "notes": "Full pool cleaning needed"
}
```

### Create Maintenance Package Booking
```bash
POST http://127.0.0.1:8000/api/v1/bookings/bookings
Authorization: Bearer {token}
Content-Type: application/json

{
  "booking_type": "maintenance_package",
  "package_id": 1,
  "booking_date": "2025-10-30",
  "booking_time": "12:00:00",
  "notes": "Monthly maintenance package"
}
```

### Create Pool Construction Booking
```bash
POST http://127.0.0.1:8000/api/v1/bookings/bookings
Authorization: Bearer {token}
Content-Type: application/json

{
  "booking_type": "construction",
  "pool_type_id": 1,
  "booking_date": "2025-11-01",
  "booking_time": "10:00:00",
  "custom_length": 7.0,
  "custom_width": 4.0,
  "custom_depth": 2.0,
  "notes": "Build plunge pool in backyard"
}
```

---

## Database Schema

### New Tables 🆕

- **services** - Maintenance services
- **pool_types** - Pool construction types
- **maintenance_packages** - Subscription packages
- **bookings** - All booking records with custom dimensions

### Booking Status Flow
```
pending → confirmed → in_progress → completed
                   ↘ cancelled
```

---

## Additional Documentation

For detailed documentation, see:
- `SERVICES_SETUP.md` - Complete setup guide for services
- `SYSTEM_FLOW.md` - Detailed system flow and UI components
- `POSTMAN_EXAMPLES.md` - Ready-to-use Postman examples
- `QUICK_START.md` - Quick start guide

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

## Contact

For questions or support, please contact the development team.

**Made with ❤️ for Plupool** 🏊‍♂️