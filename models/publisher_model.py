from database.db_config import get_connection


def get_all_publishers():
    """Return all publishers ordered by id ascending."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM publishers ORDER BY id ASC")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_publisher_by_id(publisher_id):
    """Return a single publisher dict, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM publishers WHERE id = %s", (publisher_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def create_publisher(name, address, contact):
    """Insert a new publisher and return the new id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO publishers (name, address, contact) VALUES (%s, %s, %s)",
            (name, address, contact),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_publisher(publisher_id, name, address, contact):
    """Update publisher fields."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE publishers SET name = %s, address = %s, contact = %s WHERE id = %s",
            (name, address, contact, publisher_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_publisher(publisher_id):
    """Delete a publisher by id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM publishers WHERE id = %s", (publisher_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def count_publishers():
    """Return total number of publishers."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM publishers")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()
