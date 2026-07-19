from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from middleware.auth_middleware import role_required
from utils.helpers import validate_required, validate_positive_int
import models.user_model as user_model
import models.book_model as book_model
import models.borrow_model as borrow_model

student_bp = Blueprint("student", __name__)


# ------------------------------------------------------------------ Dashboard
@student_bp.route("/")
@role_required("student")
def dashboard():
    user_id = session["user_id"]
    current_borrows = borrow_model.get_current_borrowed_by_user(user_id)
    borrow_history = borrow_model.get_borrow_records_by_user(user_id)
    fines = borrow_model.get_fines_by_user(user_id)
    return render_template("student/dashboard.html",
                           current_borrows=current_borrows,
                           borrow_history=borrow_history,
                           fines=fines)


# ------------------------------------------------------------------ Book Search/Catalog
@student_bp.route("/books")
@role_required("student")
def books():
    query = request.args.get("q", "").strip()
    if query:
        all_books = book_model.search_books(query)
    else:
        all_books = book_model.get_all_books()
    return render_template("student/books.html", books=all_books, query=query)


# ------------------------------------------------------------------ My Borrows
@student_bp.route("/my-borrows")
@role_required("student")
def my_borrows():
    user_id = session["user_id"]
    records = borrow_model.get_borrow_records_by_user(user_id)
    return render_template("student/my_borrows.html", records=records)


# ------------------------------------------------------------------ My Fines
@student_bp.route("/my-fines")
@role_required("student")
def my_fines():
    user_id = session["user_id"]
    fines = borrow_model.get_fines_by_user(user_id)
    return render_template("student/my_fines.html", fines=fines)


# ------------------------------------------------------------------ Registration
@student_bp.route("/register", methods=["GET", "POST"])
def register():
    """Public registration route — does not require login."""
    if "user_id" in session:
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        student_id_no = request.form.get("student_id_no", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()

        errors = validate_required({
            "Username": username,
            "Full Name": full_name,
            "Email": email,
            "Password": password,
            "Student ID": student_id_no,
        })
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("student/register.html", form=request.form)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("student/register.html", form=request.form)

        if user_model.get_user_by_username(username):
            flash("Username already taken.", "danger")
            return render_template("student/register.html", form=request.form)

        if user_model.get_user_by_email(email):
            flash("Email already registered.", "danger")
            return render_template("student/register.html", form=request.form)

        user_id = user_model.create_user(
            username, generate_password_hash(password),
            full_name, email, "student", "active"
        )
        user_model.create_student_profile(
            user_id, student_id_no, phone, address, department, year
        )
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("student/register.html", form={})


# ------------------------------------------------------------------ Profile
@student_bp.route("/profile", methods=["GET", "POST"])
@role_required("student")
def profile():
    user_id = session["user_id"]
    user = user_model.get_user_by_id(user_id)
    student_profile = user_model.get_student_by_user_id(user_id)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = validate_required({"Full Name": full_name, "Email": email})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("student/profile.html", user=user,
                                   student=student_profile)

        if new_password:
            if new_password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("student/profile.html", user=user,
                                       student=student_profile)
            user_model.update_user_password(user_id, generate_password_hash(new_password))

        user_model.update_user(user_id, full_name, email, user["status"])
        if student_profile:
            user_model.update_student_profile(user_id, phone, address, department, year)

        session["full_name"] = full_name
        flash("Profile updated successfully.", "success")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", user=user, student=student_profile)
