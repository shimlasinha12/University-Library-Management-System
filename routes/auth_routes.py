from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import models.user_model as user_model

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return _redirect_dashboard()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("auth/login.html")

        user = user_model.get_user_by_username(username)

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html")

        if user["status"] == "inactive":
            flash("Your account is inactive. Please contact the administrator.", "warning")
            return render_template("auth/login.html")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["full_name"] = user["full_name"]
        session["role"] = user["role"]

        flash(f"Welcome back, {user['full_name']}!", "success")
        return _redirect_dashboard()

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


def _redirect_dashboard():
    role = session.get("role")
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    elif role == "librarian":
        return redirect(url_for("librarian.dashboard"))
    return redirect(url_for("student.dashboard"))
