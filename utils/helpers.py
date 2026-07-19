from datetime import date


def format_date(d):
    """Return a date formatted as DD-Mon-YYYY, or '-' for None."""
    if d is None:
        return "-"
    if isinstance(d, str):
        return d
    return d.strftime("%d %b %Y")


def days_overdue(due_date):
    """Return positive integer of overdue days, or 0 if not overdue."""
    if due_date is None:
        return 0
    today = date.today()
    if isinstance(due_date, str):
        from datetime import datetime
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    delta = (today - due_date).days
    return max(delta, 0)


def is_overdue(due_date):
    """Return True if the due date has passed and the book is not yet returned."""
    return days_overdue(due_date) > 0


def paginate(items, page, per_page=10):
    """Slice a list into a single page. Returns (page_items, total_pages)."""
    total = len(items)
    total_pages = max((total + per_page - 1) // per_page, 1)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total_pages


def flash_form_errors(form_errors):
    """Flash each validation error message. form_errors is a list of strings."""
    from flask import flash
    for error in form_errors:
        flash(error, "danger")


def validate_required(fields):
    """
    Check that every field value in the dict is non-empty.
    Returns a list of error message strings (empty list = all valid).
    """
    errors = []
    for label, value in fields.items():
        if not value or (isinstance(value, str) and not value.strip()):
            errors.append(f"{label} is required.")
    return errors


def validate_positive_int(label, value):
    """Return an error string if value is not a positive integer, else None."""
    try:
        v = int(value)
        if v < 1:
            return f"{label} must be a positive number."
    except (TypeError, ValueError):
        return f"{label} must be a valid number."
    return None
