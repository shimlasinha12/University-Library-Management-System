from database.db_config import get_connection


def get_user_by_username(username):
    """Return a single user dict by username, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        return user
    finally:
        cursor.close()
        conn.close()


def get_user_by_id(user_id):
    """Return a single user dict by id, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email):
    """Return a single user dict by email, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_all_users_by_role(role):
    """Return a list of users filtered by role."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE role = %s ORDER BY id DESC", (role,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_student_by_user_id(user_id):
    """Return student profile dict by user_id, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM students WHERE user_id = %s", (user_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_student_by_id(student_id):
    """Return student profile dict by students.id, or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def create_user(username, password_hash, full_name, email, role, status="active"):
    """Insert a new user and return the new user id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, email, role, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (username, password_hash, full_name, email, role, status),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def create_student_profile(
    user_id, student_id_no, phone, address, department, year
):
    """Insert a student profile row linked to users.id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (user_id, student_id_no, phone, address, department, year) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, student_id_no, phone, address, department, year),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_user(user_id, full_name, email, status):
    """Update basic user fields."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET full_name = %s, email = %s, status = %s WHERE id = %s",
            (full_name, email, status, user_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def update_user_password(user_id, password_hash):
    """Update a user's password hash."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (password_hash, user_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def update_student_profile(
    user_id, phone, address, department, year
):
    """Update student profile fields by user_id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET phone = %s, address = %s, department = %s, year = %s "
            "WHERE user_id = %s",
            (phone, address, department, year, user_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_user(user_id):
    """Delete a user by id. CASCADE removes the student profile if present."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def count_users_by_role(role):
    """Return the total count of users for a given role."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE role = %s", (role,)
        )
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()
