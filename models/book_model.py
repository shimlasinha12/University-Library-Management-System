import mysql.connector
from database.db_config import get_connection


def get_all_books():
    """Return all books with joined category, author, and publisher names."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT b.*, 
                   c.name AS category_name,
                   a.name AS author_name,
                   p.name AS publisher_name
            FROM books b
            LEFT JOIN categories c  ON b.category_id  = c.id
            LEFT JOIN authors a     ON b.author_id    = a.id
            LEFT JOIN publishers p   ON b.publisher_id = p.id
            ORDER BY b.id ASC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_book_by_id(book_id):
    """Return a single book dict with joined names, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT b.*, 
                   c.name AS category_name,
                   a.name AS author_name,
                   p.name AS publisher_name
            FROM books b
            LEFT JOIN categories c  ON b.category_id  = c.id
            LEFT JOIN authors a     ON b.author_id    = a.id
            LEFT JOIN publishers p   ON b.publisher_id = p.id
            WHERE b.id = %s
            """,
            (book_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_book_by_isbn(isbn):
    """Return a single book dict by ISBN, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM books WHERE isbn = %s", (isbn,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def search_books(query):
    """Search books by title, ISBN, author name, or category name."""
    like = f"%{query}%"
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT b.*, 
                   c.name AS category_name,
                   a.name AS author_name,
                   p.name AS publisher_name
            FROM books b
            LEFT JOIN categories c  ON b.category_id  = c.id
            LEFT JOIN authors a     ON b.author_id    = a.id
            LEFT JOIN publishers p   ON b.publisher_id = p.id
            WHERE b.title LIKE %s OR b.isbn LIKE %s 
                  OR a.name LIKE %s OR c.name LIKE %s
            ORDER BY b.id ASC
            """,
            (like, like, like, like),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def create_book(
    isbn, title, category_id, author_id, publisher_id, quantity
):
    """Insert a new book. available_copies defaults to quantity."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (isbn, title, category_id, author_id, publisher_id, quantity, available_copies) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (isbn, title, category_id, author_id, publisher_id, quantity, quantity),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_book(
    book_id, isbn, title, category_id, author_id, publisher_id, quantity
):
    """Update book fields. Adjusts available_copies by the quantity difference."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT quantity, available_copies FROM books WHERE id = %s",
            (book_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return
        old_qty = row[0]
        available = row[1]
        diff = quantity - old_qty
        new_available = available + diff
        if new_available < 0:
            new_available = 0
        cursor.execute(
            "UPDATE books SET isbn = %s, title = %s, category_id = %s, "
            "author_id = %s, publisher_id = %s, quantity = %s, available_copies = %s "
            "WHERE id = %s",
            (isbn, title, category_id, author_id, publisher_id, quantity, new_available, book_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_book(book_id):
    """Delete a book by id.

    Returns True if the book was deleted. Returns False if the book could
    not be deleted because it is still referenced by borrow_records (the
    foreign key constraint is intentionally left in place to protect
    borrowing history — this only prevents the app from crashing on that
    constraint and reports the failure to the caller instead).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        return True
    except mysql.connector.errors.IntegrityError:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def decrease_available_copies(book_id):
    """Decrement available_copies by 1 (called on book issue)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE books SET available_copies = available_copies - 1 WHERE id = %s "
            "AND available_copies > 0",
            (book_id,),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def increase_available_copies(book_id):
    """Increment available_copies by 1 (called on book return)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE books SET available_copies = available_copies + 1 "
            "WHERE id = %s AND available_copies < quantity",
            (book_id,),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def count_total_books():
    """Return total number of book titles in catalog."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def count_total_copies():
    """Return total sum of all book quantities."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM books")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()
