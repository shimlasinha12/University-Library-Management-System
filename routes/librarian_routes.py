from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from middleware.auth_middleware import role_required
from utils.helpers import validate_required, validate_positive_int, paginate
import models.user_model as user_model
import models.book_model as book_model
import models.borrow_model as borrow_model
import models.report_model as report_model

librarian_bp = Blueprint("librarian", __name__)


# ------------------------------------------------------------------ Dashboard
@librarian_bp.route("/")
@role_required("librarian")
def dashboard():
    stats = report_model.get_dashboard_stats()
    recent = report_model.get_recent_borrow_records(limit=8)
    return render_template("librarian/dashboard.html", stats=stats, recent=recent)


# ------------------------------------------------------------------ Book catalog (read-only)
@librarian_bp.route("/books")
@role_required("librarian")
def books():
    query = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    if query:
        all_books = book_model.search_books(query)
    else:
        all_books = book_model.get_all_books()
    paged, total_pages = paginate(all_books, page)
    return render_template("librarian/books.html", books=paged, page=page,
                           total_pages=total_pages, query=query)


# ------------------------------------------------------------------ Issue book
@librarian_bp.route("/issue", methods=["GET", "POST"])
@role_required("librarian")
def issue_book():
    students = user_model.get_all_users_by_role("student")
    all_books = book_model.get_all_books()
    available_books = [b for b in all_books if b["available_copies"] > 0]

    if request.method == "POST":
        book_id = request.form.get("book_id", "").strip()
        user_id = request.form.get("user_id", "").strip()

        errors = validate_required({"Book": book_id, "Student": user_id})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("librarian/issue_book.html",
                                   students=students, books=available_books)

        book = book_model.get_book_by_id(int(book_id))
        if book is None or book["available_copies"] < 1:
            flash("Book is not available for issue.", "danger")
            return render_template("librarian/issue_book.html",
                                   students=students, books=available_books)

        # Prevent duplicate active borrow for same book/user
        current = borrow_model.get_current_borrowed_by_user(int(user_id))
        if any(r["book_id"] == int(book_id) for r in current):
            flash("This student already has an active borrow for this book.", "warning")
            return render_template("librarian/issue_book.html",
                                   students=students, books=available_books)

        borrow_model.issue_book(int(book_id), int(user_id))
        flash("Book issued successfully.", "success")
        return redirect(url_for("librarian.borrow_records"))

    return render_template("librarian/issue_book.html",
                           students=students, books=available_books)


# ------------------------------------------------------------------ Return book
@librarian_bp.route("/return", methods=["GET", "POST"])
@role_required("librarian")
def return_book():
    issued_records = [r for r in borrow_model.get_all_borrow_records()
                      if r["status"] == "issued"]

    if request.method == "POST":
        record_id = request.form.get("record_id", "").strip()
        if not record_id:
            flash("Please select a borrow record.", "danger")
            return render_template("librarian/return_book.html", records=issued_records)

        record = borrow_model.return_book(int(record_id))
        if record is None:
            flash("Borrow record not found.", "danger")
        else:
            fine = borrow_model.calculate_fine(record["due_date"], __import__("datetime").date.today())
            if fine > 0:
                flash(f"Book returned. Fine charged: Rs. {fine:.2f}", "warning")
            else:
                flash("Book returned successfully. No fine.", "success")
        return redirect(url_for("librarian.borrow_records"))

    return render_template("librarian/return_book.html", records=issued_records)


# ------------------------------------------------------------------ Borrow Records
@librarian_bp.route("/borrows")
@role_required("librarian")
def borrow_records():
    query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "")
    page = int(request.args.get("page", 1))

    records = borrow_model.get_all_borrow_records()

    if query:
        records = [r for r in records
                   if query.lower() in r["book_title"].lower()
                   or query.lower() in r["user_name"].lower()
                   or query.lower() in r["username"].lower()]
    if status_filter in ("issued", "returned"):
        records = [r for r in records if r["status"] == status_filter]

    paged, total_pages = paginate(records, page)
    return render_template("librarian/borrow_records.html", records=paged,
                           page=page, total_pages=total_pages,
                           query=query, status_filter=status_filter)


# ------------------------------------------------------------------ Fines
@librarian_bp.route("/fines")
@role_required("librarian")
def fines():
    fine_records = borrow_model.get_all_fines()
    return render_template("librarian/fines.html", fines=fine_records)


# ------------------------------------------------------------------ Students list (view only)
@librarian_bp.route("/students")
@role_required("librarian")
def students():
    students_list = user_model.get_all_users_by_role("student")
    return render_template("librarian/students.html", students=students_list)


@librarian_bp.route("/students/view/<int:user_id>")
@role_required("librarian")
def view_student(user_id):
    student_user = user_model.get_user_by_id(user_id)
    if student_user is None or student_user["role"] != "student":
        flash("Student not found.", "danger")
        return redirect(url_for("librarian.students"))
    profile = user_model.get_student_by_user_id(user_id)
    borrows = borrow_model.get_borrow_records_by_user(user_id)
    return render_template("librarian/student_view.html",
                           student=student_user, profile=profile, borrows=borrows)


# ------------------------------------------------------------------ Profile
@librarian_bp.route("/profile", methods=["GET", "POST"])
@role_required("librarian")
def profile():
    user_id = session["user_id"]
    user = user_model.get_user_by_id(user_id)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = validate_required({"Full Name": full_name, "Email": email})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("librarian/profile.html", user=user)

        if new_password:
            if new_password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("librarian/profile.html", user=user)
            user_model.update_user_password(user_id, generate_password_hash(new_password))

        user_model.update_user(user_id, full_name, email, user["status"])
        session["full_name"] = full_name
        flash("Profile updated successfully.", "success")
        return redirect(url_for("librarian.profile"))

    return render_template("librarian/profile.html", user=user)
