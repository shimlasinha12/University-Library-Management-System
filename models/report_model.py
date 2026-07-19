from database.db_config import get_connection
import models.user_model as user_model
import models.book_model as book_model
import models.borrow_model as borrow_model
import models.category_model as category_model
import models.author_model as author_model
import models.publisher_model as publisher_model


def get_dashboard_stats():
    """Return a dictionary of aggregate counts for the admin dashboard."""
    stats = {
        "total_books": book_model.count_total_books(),
        "total_copies": book_model.count_total_copies(),
        "issued_books": borrow_model.count_issued_books(),
        "returned_books": borrow_model.count_returned_books(),
        "total_students": user_model.count_users_by_role("student"),
        "total_librarians": user_model.count_users_by_role("librarian"),
        "total_categories": category_model.count_categories(),
        "total_authors": author_model.count_authors(),
        "total_publishers": publisher_model.count_publishers(),
        "total_fine_amount": borrow_model.get_total_fine_amount(),
    }
    return stats


def get_recent_borrow_records(limit=5):
    """Return the most recent borrow records for dashboard display."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT br.*, 
                   b.title AS book_title,
                   u.full_name AS user_name,
                   u.role AS user_role
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            JOIN users u ON br.user_id = u.id
            ORDER BY br.id DESC
            LIMIT %s
            """,
            (limit,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_fine_report():
    """Return all records with fines for the fine report."""
    return borrow_model.get_all_fines()


def get_book_report():
    """Return all books with joined category, author, publisher for the book report."""
    return book_model.get_all_books()


def get_borrow_history_report():
    """Return all borrow records for the borrow history report."""
    return borrow_model.get_all_borrow_records()
