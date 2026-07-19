from database.db_config import get_connection


def get_all_categories():
    """Return all categories ordered by id ascending."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories ORDER BY id ASC")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_category_by_id(category_id):
    """Return a single category dict, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_category_by_name(name):
    """Return a single category dict by name, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories WHERE name = %s", (name,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def create_category(name, description):
    """Insert a new category and return the new id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categories (name, description) VALUES (%s, %s)",
            (name, description),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_category(category_id, name, description):
    """Update category fields."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE categories SET name = %s, description = %s WHERE id = %s",
            (name, description, category_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_category(category_id):
    """Delete a category by id.

    If this deletion empties the table, AUTO_INCREMENT is reset to 1 so the
    next category created starts fresh at ID 1. No IDs are ever hardcoded —
    this only resets MySQL's internal counter, and only when it is safe to
    do so (i.e. there are no remaining rows whose IDs could collide).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM categories")
        remaining = cursor.fetchone()[0]
        if remaining == 0:
            cursor.execute("ALTER TABLE categories AUTO_INCREMENT = 1")
            conn.commit()
    finally:
        cursor.close()
        conn.close()


def count_categories():
    """Return total number of categories."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()
