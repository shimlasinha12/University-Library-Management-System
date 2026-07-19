# University Library Management System

A complete web-based library management system built with **Flask**, **MySQL**, and server-rendered **Jinja2** templates. It supports three roles — Admin, Librarian, and Student — each with their own dashboard, sidebar navigation, and feature set.

## Features

### Admin
- Dashboard with aggregate statistics (books, copies, issued, returned, students, librarians, fines)
- Full CRUD for Books, Categories, Authors, Publishers
- Manage librarian accounts (add, edit, delete, activate/deactivate)
- View and delete student accounts
- View individual student profiles with borrow history
- Three reports: Book Report, Borrow History, Fine Report (printable)
- Edit own profile and password

### Librarian
- Dashboard with library statistics and recent activity
- Browse and search the book catalog (read-only)
- Issue books to students (with 14-day borrowing period and duplicate-borrow guard)
- Process book returns (auto-calculates overdue fines at Rs. 10/day)
- View all borrow records with search and status filter (issued/returned)
- View all fines with total
- View student list and individual student profiles
- Edit own profile and password

### Student
- Self-registration with student profile (Student ID, phone, department, year, address)
- Dashboard showing current borrows, total borrowed, and total fines
- Browse and search the library catalog (card layout with availability)
- View complete borrow history with overdue indicators
- View all fines with total outstanding
- Edit profile and password

## Default Login

| Role     | Username | Password    |
|----------|----------|-------------|
| Admin    | admin    | Admin@123   |

Librarian and student accounts are created through the admin panel or student registration page.

## Tech Stack

- **Backend:** Flask 3.0.3
- **Database:** MySQL (via mysql-connector-python)
- **Auth:** Werkzeug password hashing (generate_password_hash / check_password_hash)
- **Templates:** Jinja2 with a custom CSS design system (Inter font, Font Awesome icons)
- **Session:** Flask server-side sessions

## Project Structure

```
project/
|-- app.py                      # Flask app entry point
|-- config/config.py            # App configuration (DB, secret key, fine/borrow settings)
|-- database/db_config.py       # MySQL connection factory
|-- library_management.sql      # Database schema + default admin account
|-- middleware/auth_middleware.py  # @login_required, @role_required decorators
|-- models/                     # Data access layer (one file per entity)
|   |-- user_model.py
|   |-- book_model.py
|   |-- borrow_model.py
|   |-- category_model.py
|   |-- author_model.py
|   |-- publisher_model.py
|   |-- report_model.py
|-- routes/                     # Flask Blueprints (one per role + auth)
|   |-- auth_routes.py
|   |-- admin_routes.py
|   |-- librarian_routes.py
|   |-- student_routes.py
|-- templates/                  # Jinja2 templates
|   |-- base.html               # Master layout (sidebar, topbar, flash, modal)
|   |-- auth/login.html
|   |-- admin/                  # 19 admin templates
|   |-- librarian/              # 9 librarian templates
|   |-- student/                # 7 student templates
|   |-- errors/404.html, 500.html
|-- static/
|   |-- css/main.css            # Full design system (~900 lines)
|   |-- js/main.js              # Sidebar toggle, alerts, delete modal, password toggle
|-- utils/helpers.py            # Validation, pagination, date formatting
```

## Setup

### 1. Database

Import the schema file into MySQL:

```bash
mysql -u root -p < library_management.sql
```

This creates the `library_management` database with all tables and the default admin account.

### 2. Environment

Copy `.env.example` to `.env` and update the values:

```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=library_management
DB_USER=root
DB_PASSWORD=your_password
SECRET_KEY=your_secret_key
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application starts on `http://localhost:5000`.

## Configuration

Editable in `config/config.py`:

| Setting        | Default | Description                          |
|----------------|---------|--------------------------------------|
| FINE_PER_DAY   | 10      | Fine amount per overdue day (Rs.)    |
| BORROW_DAYS    | 14      | Default borrowing period in days     |
| SECRET_KEY     | -       | Flask session secret (from .env)     |

## Security

- Passwords stored as Werkzeug hashes (never plaintext)
- Role-based access control via `@role_required` decorator on every route
- Session-based authentication
- SQL injection prevention via parameterized queries throughout the model layer
