from utils.helpers import format_date, is_overdue, days_overdue


def register_template_utils(app):
    """Register helper functions as Jinja2 globals so templates can use them."""
    app.jinja_env.globals["format_date"] = format_date
    app.jinja_env.globals["is_overdue"] = is_overdue
    app.jinja_env.globals["days_overdue"] = days_overdue
