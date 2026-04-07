# FAMILY BUDGET TRACKER - BACKEND API

Backend for a family budget tracker that supports users, categories, transactions, and dashboard analytics. Built with FastAPI and PostgreSQL.

Role-based access control is enforced consistently across all endpoints using JWT authentication and a reusable `require_roles(...)` dependency.

---

## What This Backend Does

- Handles **authentication and authorization** using JWT Bearer tokens.
- Enforces **role-based access control** (`admin`, `analyst`, `viewer`).
- Provides CRUD-style APIs for:
  - Users
  - Categories
  - Transactions
- Exposes dashboard analytics endpoints:
  - Monthly summary
  - Category totals
  - Recent activity

---


##  Tech Stack

| Layer      | Technology                 |
| ---------- | -------------------------- |
| Backend    | FastAPI                    |
| Database  | PostgreSQL |
| Authentication  | JWT |
| Backend and database Deployment  | Render |

---

## Setup

1. Clone repo
2. Create python vitual environment
   - `py -m venv .venv`
3. Activate venv (for windows)
   - `.venv\Scripts\Activate`
4. Create `.env` from `.env.example`
5. Install dependencies:
   - `pip install -r requirements.txt`
6. Start server:
   - `uvicorn main:app --reload`

After the server starts, visit Swagger docs:

- http://localhost:8000/docs

---

## Project Structure
```text
backend/
├─ core/
│  ├─ access_control.py      # Role guard dependency
│  └─ security.py            # JWT create/decode
├─ models/
│  ├─ auth.py                # User model + UserRole enum
│  ├─ category.py            # Category model + CashflowType enum
│  └─ transaction.py         # Transaction model
├─ routes/
│  ├─ auth.py
│  ├─ users.py
│  ├─ categories.py
│  ├─ transactions.py
│  └─ dashboard.py
├─ schemas/                  # Request/response validation
├─ services/                 # Business logic layer
├─ database.py               # Async engine/session + Base
├─ dependencies.py           # Current user auth dependency
├─ main.py                   # App entrypoint and router registration
└─ requirements.txt
```
---

## API Endpoints

Authentication: all routes require a valid `Authorization: Bearer <token>` header except the register/login endpoints.

| Method | Path                             | Auth Required | Role Restriction                  |
| ------ | -------------------------------- | ------------- | --------------------------------- |
| POST   | `/api/auth/register`             | No            | Public (creates first admin only) |
| POST   | `/api/auth/login`                | No            | Public                            |
| GET    | `/api/auth/me`                   | Yes           | `admin`, `analyst`, `viewer`      |
| POST   | `/api/users`                     | Yes           | `admin`                           |
| GET    | `/api/users`                     | Yes           | `admin`                           |
| GET    | `/api/users/{id}`                | Yes           | `admin`                           |
| PATCH  | `/api/users/{id}`                | Yes           | `admin`                           |
| DELETE | `/api/users/{id}`                | Yes           | `admin` (cannot deactivate self)  |
| POST   | `/api/categories`                | Yes           | `admin`                           |
| GET    | `/api/categories`                | Yes           | `admin`, `analyst`     |
| POST   | `/api/transactions`              | Yes           | `admin`                           |
| GET    | `/api/transactions`              | Yes           | `admin` , `analyst`      |
| GET  | `/api/transactions/{id}`         | Yes           | `admin` , `analyst`                           |
| PATCH  | `/api/transactions/{id}`         | Yes           | `admin`                           |
| DELETE | `/api/transactions/{id}`         | Yes           | `admin`                           |
| GET    | `/api/dashboard/monthly-summary`         | Yes           | `admin`, `analyst`, `viewer`      |
| GET    | `/api/dashboard/category-totals` | Yes           | `admin`, `analyst`, `viewer`      |
| GET    | `/api/dashboard/recent-activity` | Yes           | `admin`, `analyst`, `viewer`      |

---

### Transactions Filtering (GET `/api/transactions`)

- `type`: `income` or `expense`
- `category_id`: UUID
- `start_date`: `YYYY-MM-DD`
- `end_date`: `YYYY-MM-DD`
- `search`: case-insensitive match against `notes` (ILIKE)
- `skip`, `limit`: pagination

---

## Core Validation & Business Rules

- Only **one admin account** is allowed.
- Admin **cannot deactivate or delete themselves**.
- Admin **cannot be demoted or deleted** through normal user operations.
- Category names must be **unique**.
- Transaction amount must be **greater than 0**.
- Transaction date **cannot be in the future**.
- Transaction `type` must match the selected category `type`.
- Deleted transactions are **soft-deleted** (`is_deleted = true`) and excluded from normal reads.

  ---
## Test APIs Live here
https://family-budget-tracker-tziy.onrender.com/docs

---
## ScreenShots
<img width="1918" height="1013" alt="image" src="https://github.com/user-attachments/assets/648bc6ca-ba52-4b12-8014-7d7e87a77b70" />
<img width="1837" height="881" alt="image" src="https://github.com/user-attachments/assets/882cf8ce-7cfa-4ce3-b3a5-436cda38a29a" />
<img width="1876" height="702" alt="image" src="https://github.com/user-attachments/assets/7bbe216a-3569-4337-9258-fa6be194b5d2" />



