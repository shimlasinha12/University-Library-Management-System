from database.db_config import get_connection


def get_all_authors():
    """Return all authors ordered by id ascending."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM authors ORDER BY id ASC")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_author_by_id(author_id):
    """Return a single author dict, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM authors WHERE id = %s", (author_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def create_author(name, description):
    """Insert a new author and return the new id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO authors (name, description) VALUES (%s, %s)",
            (name, description),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_author(author_id, name, description):
    """Update author fields."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE authors SET name = %s, description = %s WHERE id = %s",
            (name, description, author_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_author(author_id):
    """Delete an author by id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM authors WHERE id = %s", (author_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def count_authors():
    """Return total number of authors."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM authors")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()
