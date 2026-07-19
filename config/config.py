import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "library_management")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")

    # Fine per day for overdue books (in currency units)
    FINE_PER_DAY = 10

    # Default borrowing period in days
    BORROW_DAYS = 14
