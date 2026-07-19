from datetime import date, timedelta
from database.db_config import get_connection
from config.config import Config
import models.book_model as book_model


def issue_book(book_id, user_id, issue_date=None, borrow_days=None):
    """Create a borrow record and decrease available copies."""
    if issue_date is None:
        issue_date = date.today()
    if borrow_days is None:
        borrow_days = Config.BORROW_DAYS
    due_date = issue_date + timedelta(days=borrow_days)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO borrow_records (book_id, user_id, issue_date, due_date, status, fine_amount) "
            "VALUES (%s, %s, %s, %s, 'issued', 0.00)",
            (book_id, user_id, issue_date, due_date),
        )
        conn.commit()
        record_id = cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

    book_model.decrease_available_copies(book_id)
    return record_id


def return_book(record_id):
    """Mark a borrow record as returned, calculate fine, and increase available copies."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM borrow_records WHERE id = %s", (record_id,))
        record = cursor.fetchone()
        if record is None:
            return None
        if record["status"] == "returned":
            return record

        return_date = date.today()
        fine = calculate_fine(record["due_date"], return_date)

        cursor.execute(
            "UPDATE borrow_records SET return_date = %s, status = 'returned', fine_amount = %s "
            "WHERE id = %s",
            (return_date, fine, record_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    book_model.increase_available_copies(record["book_id"])
    return record


def calculate_fine(due_date, return_date):
    """Calculate fine for overdue books. Returns 0 if not overdue."""
    if return_date > due_date:
        delta = (return_date - due_date).days
        return float(delta * Config.FINE_PER_DAY)
    return 0.0


def get_all_borrow_records():
    """Return all borrow records with joined book and user info."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT br.*, 
                   b.title AS book_title,
                   b.isbn AS book_isbn,
                   u.full_name AS user_name,
                   u.username AS username,
                   u.role AS user_role
            FROM borrow_records br
            JOIN books b  ON br.book_id = b.id
            JOIN users u  ON br.user_id = u.id
            ORDER BY br.id DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_borrow_records_by_user(user_id):
    """Return all borrow records for a specific user."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT br.*, 
                   b.title AS book_title,
                   b.isbn AS book_isbn
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.user_id = %s
            ORDER BY br.id DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_current_borrowed_by_user(user_id):
    """Return only currently issued (not returned) books for a user."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT br.*, 
                   b.title AS book_title,
                   b.isbn AS book_isbn
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.user_id = %s AND br.status = 'issued'
            ORDER BY br.id DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_borrow_record_by_id(record_id):
    """Return a single borrow record dict, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM borrow_records WHERE id = %s", (record_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_all_fines():
    """Return all borrow records that have a fine > 0."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT br.*, 
                   b.title AS book_title,
                   u.full_name AS user_name,
                   u.username AS username
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            JOIN users u ON br.user_id = u.id
            WHERE br.fine_amount > 0
            ORDER BY br.id DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_fines_by_user(user_id):
    """Return all borrow records with fines for a specific user."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT br.*, 
                   b.title AS book_title
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.user_id = %s AND br.fine_amount > 0
            ORDER BY br.id DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def count_issued_books():
    """Return count of currently issued (not returned) books."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE status = 'issued'")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def count_returned_books():
    """Return count of returned books."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE status = 'returned'")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def get_total_fine_amount():
    """Return the sum of all fines."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(fine_amount), 0) FROM borrow_records")
        return float(cursor.fetchone()[0])
    finally:
        cursor.close()
        conn.close()
