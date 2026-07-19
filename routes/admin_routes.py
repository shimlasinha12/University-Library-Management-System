from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from middleware.auth_middleware import login_required, role_required
from utils.helpers import validate_required, validate_positive_int, paginate
import models.user_model as user_model
import models.book_model as book_model
import models.category_model as category_model
import models.author_model as author_model
import models.publisher_model as publisher_model
import models.borrow_model as borrow_model
import models.report_model as report_model

admin_bp = Blueprint("admin", __name__)

# ------------------------------------------------------------------ Dashboard
@admin_bp.route("/")
@role_required("admin")
def dashboard():
    stats = report_model.get_dashboard_stats()
    recent = report_model.get_recent_borrow_records(limit=8)
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


# ------------------------------------------------------------------ Librarian Management
@admin_bp.route("/librarians")
@role_required("admin")
def librarians():
    librarians_list = user_model.get_all_users_by_role("librarian")
    return render_template("admin/librarians.html", librarians=librarians_list)


@admin_bp.route("/librarians/add", methods=["GET", "POST"])
@role_required("admin")
def add_librarian():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        status = request.form.get("status", "active")

        errors = validate_required({"Username": username, "Full Name": full_name,
                                    "Email": email, "Password": password})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/librarian_form.html", action="Add",
                                   form=request.form)

        if user_model.get_user_by_username(username):
            flash("Username already exists.", "danger")
            return render_template("admin/librarian_form.html", action="Add",
                                   form=request.form)

        if user_model.get_user_by_email(email):
            flash("Email already exists.", "danger")
            return render_template("admin/librarian_form.html", action="Add",
                                   form=request.form)

        user_model.create_user(username, generate_password_hash(password),
                               full_name, email, "librarian", status)
        flash("Librarian added successfully.", "success")
        return redirect(url_for("admin.librarians"))

    return render_template("admin/librarian_form.html", action="Add", form={})


@admin_bp.route("/librarians/edit/<int:user_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_librarian(user_id):
    librarian = user_model.get_user_by_id(user_id)
    if librarian is None or librarian["role"] != "librarian":
        flash("Librarian not found.", "danger")
        return redirect(url_for("admin.librarians"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        status = request.form.get("status", "active")
        new_password = request.form.get("new_password", "")

        errors = validate_required({"Full Name": full_name, "Email": email})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/librarian_form.html", action="Edit",
                                   form=request.form, librarian=librarian)

        existing = user_model.get_user_by_email(email)
        if existing and existing["id"] != user_id:
            flash("Email already in use by another account.", "danger")
            return render_template("admin/librarian_form.html", action="Edit",
                                   form=request.form, librarian=librarian)

        user_model.update_user(user_id, full_name, email, status)
        if new_password:
            user_model.update_user_password(user_id, generate_password_hash(new_password))

        flash("Librarian updated successfully.", "success")
        return redirect(url_for("admin.librarians"))

    return render_template("admin/librarian_form.html", action="Edit",
                           form=librarian, librarian=librarian)


@admin_bp.route("/librarians/delete/<int:user_id>", methods=["POST"])
@role_required("admin")
def delete_librarian(user_id):
    librarian = user_model.get_user_by_id(user_id)
    if librarian and librarian["role"] == "librarian":
        user_model.delete_user(user_id)
        flash("Librarian deleted successfully.", "success")
    else:
        flash("Librarian not found.", "danger")
    return redirect(url_for("admin.librarians"))


# ------------------------------------------------------------------ Student Management (admin view)
@admin_bp.route("/students")
@role_required("admin")
def students():
    students_list = user_model.get_all_users_by_role("student")
    return render_template("admin/students.html", students=students_list)


@admin_bp.route("/students/view/<int:user_id>")
@role_required("admin")
def view_student(user_id):
    student_user = user_model.get_user_by_id(user_id)
    if student_user is None or student_user["role"] != "student":
        flash("Student not found.", "danger")
        return redirect(url_for("admin.students"))
    profile = user_model.get_student_by_user_id(user_id)
    borrows = borrow_model.get_borrow_records_by_user(user_id)
    return render_template("admin/student_view.html",
                           student=student_user, profile=profile, borrows=borrows)


@admin_bp.route("/students/delete/<int:user_id>", methods=["POST"])
@role_required("admin")
def delete_student(user_id):
    student = user_model.get_user_by_id(user_id)
    if student and student["role"] == "student":
        user_model.delete_user(user_id)
        flash("Student deleted successfully.", "success")
    else:
        flash("Student not found.", "danger")
    return redirect(url_for("admin.students"))


# ------------------------------------------------------------------ Books
@admin_bp.route("/books")
@role_required("admin")
def books():
    query = request.args.get("q", "").strip()
    page = int(request.args.get("page", 1))
    if query:
        all_books = book_model.search_books(query)
    else:
        all_books = book_model.get_all_books()
    paged, total_pages = paginate(all_books, page)
    return render_template("admin/books.html", books=paged, page=page,
                           total_pages=total_pages, query=query)


@admin_bp.route("/books/add", methods=["GET", "POST"])
@role_required("admin")
def add_book():
    categories = category_model.get_all_categories()
    authors = author_model.get_all_authors()
    publishers = publisher_model.get_all_publishers()

    if request.method == "POST":
        isbn = request.form.get("isbn", "").strip()
        title = request.form.get("title", "").strip()
        category_id = request.form.get("category_id") or None
        author_id = request.form.get("author_id") or None
        publisher_id = request.form.get("publisher_id") or None
        quantity = request.form.get("quantity", "").strip()

        errors = validate_required({"ISBN": isbn, "Title": title, "Quantity": quantity})
        qty_err = validate_positive_int("Quantity", quantity)
        if qty_err:
            errors.append(qty_err)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/book_form.html", action="Add", form=request.form,
                                   categories=categories, authors=authors, publishers=publishers)

        if book_model.get_book_by_isbn(isbn):
            flash("A book with this ISBN already exists.", "danger")
            return render_template("admin/book_form.html", action="Add", form=request.form,
                                   categories=categories, authors=authors, publishers=publishers)

        book_model.create_book(isbn, title, category_id, author_id, publisher_id, int(quantity))
        flash("Book added successfully.", "success")
        return redirect(url_for("admin.books"))

    return render_template("admin/book_form.html", action="Add", form={},
                           categories=categories, authors=authors, publishers=publishers)


@admin_bp.route("/books/edit/<int:book_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_book(book_id):
    book = book_model.get_book_by_id(book_id)
    if book is None:
        flash("Book not found.", "danger")
        return redirect(url_for("admin.books"))

    categories = category_model.get_all_categories()
    authors = author_model.get_all_authors()
    publishers = publisher_model.get_all_publishers()

    if request.method == "POST":
        isbn = request.form.get("isbn", "").strip()
        title = request.form.get("title", "").strip()
        category_id = request.form.get("category_id") or None
        author_id = request.form.get("author_id") or None
        publisher_id = request.form.get("publisher_id") or None
        quantity = request.form.get("quantity", "").strip()

        errors = validate_required({"ISBN": isbn, "Title": title, "Quantity": quantity})
        qty_err = validate_positive_int("Quantity", quantity)
        if qty_err:
            errors.append(qty_err)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/book_form.html", action="Edit", form=request.form,
                                   book=book, categories=categories, authors=authors,
                                   publishers=publishers)

        existing = book_model.get_book_by_isbn(isbn)
        if existing and existing["id"] != book_id:
            flash("Another book with this ISBN already exists.", "danger")
            return render_template("admin/book_form.html", action="Edit", form=request.form,
                                   book=book, categories=categories, authors=authors,
                                   publishers=publishers)

        book_model.update_book(book_id, isbn, title, category_id, author_id,
                               publisher_id, int(quantity))
        flash("Book updated successfully.", "success")
        return redirect(url_for("admin.books"))

    return render_template("admin/book_form.html", action="Edit", form=book, book=book,
                           categories=categories, authors=authors, publishers=publishers)


@admin_bp.route("/books/delete/<int:book_id>", methods=["POST"])
@role_required("admin")
def delete_book(book_id):
    deleted = book_model.delete_book(book_id)
    if deleted:
        flash("Book deleted successfully.", "success")
    else:
        flash("This book cannot be deleted because it has existing borrow records.", "danger")
    return redirect(url_for("admin.books"))


# ------------------------------------------------------------------ Categories
@admin_bp.route("/categories")
@role_required("admin")
def categories():
    cats = category_model.get_all_categories()
    return render_template("admin/categories.html", categories=cats)


@admin_bp.route("/categories/add", methods=["GET", "POST"])
@role_required("admin")
def add_category():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        errors = validate_required({"Name": name})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/category_form.html", action="Add", form=request.form)
        if category_model.get_category_by_name(name):
            flash("Category already exists.", "danger")
            return render_template("admin/category_form.html", action="Add", form=request.form)
        category_model.create_category(name, description)
        flash("Category added.", "success")
        return redirect(url_for("admin.categories"))
    return render_template("admin/category_form.html", action="Add", form={})


@admin_bp.route("/categories/edit/<int:category_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_category(category_id):
    cat = category_model.get_category_by_id(category_id)
    if cat is None:
        flash("Category not found.", "danger")
        return redirect(url_for("admin.categories"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        errors = validate_required({"Name": name})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/category_form.html", action="Edit",
                                   form=request.form, category=cat)
        existing = category_model.get_category_by_name(name)
        if existing and existing["id"] != category_id:
            flash("Another category with this name exists.", "danger")
            return render_template("admin/category_form.html", action="Edit",
                                   form=request.form, category=cat)
        category_model.update_category(category_id, name, description)
        flash("Category updated.", "success")
        return redirect(url_for("admin.categories"))
    return render_template("admin/category_form.html", action="Edit", form=cat, category=cat)


@admin_bp.route("/categories/delete/<int:category_id>", methods=["POST"])
@role_required("admin")
def delete_category(category_id):
    category_model.delete_category(category_id)
    flash("Category deleted.", "success")
    return redirect(url_for("admin.categories"))


# ------------------------------------------------------------------ Authors
@admin_bp.route("/authors")
@role_required("admin")
def authors():
    all_authors = author_model.get_all_authors()
    return render_template("admin/authors.html", authors=all_authors)


@admin_bp.route("/authors/add", methods=["GET", "POST"])
@role_required("admin")
def add_author():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        errors = validate_required({"Name": name})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/author_form.html", action="Add", form=request.form)
        author_model.create_author(name, description)
        flash("Author added.", "success")
        return redirect(url_for("admin.authors"))
    return render_template("admin/author_form.html", action="Add", form={})


@admin_bp.route("/authors/edit/<int:author_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_author(author_id):
    author = author_model.get_author_by_id(author_id)
    if author is None:
        flash("Author not found.", "danger")
        return redirect(url_for("admin.authors"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        errors = validate_required({"Name": name})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/author_form.html", action="Edit",
                                   form=request.form, author=author)
        author_model.update_author(author_id, name, description)
        flash("Author updated.", "success")
        return redirect(url_for("admin.authors"))
    return render_template("admin/author_form.html", action="Edit", form=author, author=author)


@admin_bp.route("/authors/delete/<int:author_id>", methods=["POST"])
@role_required("admin")
def delete_author(author_id):
    author_model.delete_author(author_id)
    flash("Author deleted.", "success")
    return redirect(url_for("admin.authors"))


# ------------------------------------------------------------------ Publishers
@admin_bp.route("/publishers")
@role_required("admin")
def publishers():
    all_publishers = publisher_model.get_all_publishers()
    return render_template("admin/publishers.html", publishers=all_publishers)


@admin_bp.route("/publishers/add", methods=["GET", "POST"])
@role_required("admin")
def add_publisher():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()
        contact = request.form.get("contact", "").strip()
        errors = validate_required({"Name": name})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/publisher_form.html", action="Add", form=request.form)
        publisher_model.create_publisher(name, address, contact)
        flash("Publisher added.", "success")
        return redirect(url_for("admin.publishers"))
    return render_template("admin/publisher_form.html", action="Add", form={})


@admin_bp.route("/publishers/edit/<int:publisher_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_publisher(publisher_id):
    pub = publisher_model.get_publisher_by_id(publisher_id)
    if pub is None:
        flash("Publisher not found.", "danger")
        return redirect(url_for("admin.publishers"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()
        contact = request.form.get("contact", "").strip()
        errors = validate_required({"Name": name})
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/publisher_form.html", action="Edit",
                                   form=request.form, publisher=pub)
        publisher_model.update_publisher(publisher_id, name, address, contact)
        flash("Publisher updated.", "success")
        return redirect(url_for("admin.publishers"))
    return render_template("admin/publisher_form.html", action="Edit", form=pub, publisher=pub)


@admin_bp.route("/publishers/delete/<int:publisher_id>", methods=["POST"])
@role_required("admin")
def delete_publisher(publisher_id):
    publisher_model.delete_publisher(publisher_id)
    flash("Publisher deleted.", "success")
    return redirect(url_for("admin.publishers"))


# ------------------------------------------------------------------ Reports
@admin_bp.route("/reports/books")
@role_required("admin")
def report_books():
    books = report_model.get_book_report()
    return render_template("admin/report_books.html", books=books)


@admin_bp.route("/reports/borrows")
@role_required("admin")
def report_borrows():
    records = report_model.get_borrow_history_report()
    return render_template("admin/report_borrows.html", records=records)


@admin_bp.route("/reports/fines")
@role_required("admin")
def report_fines():
    fines = report_model.get_fine_report()
    return render_template("admin/report_fines.html", fines=fines)


# ------------------------------------------------------------------ Profile
@admin_bp.route("/profile", methods=["GET", "POST"])
@role_required("admin")
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
            return render_template("admin/profile.html", user=user)

        if new_password:
            if new_password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("admin/profile.html", user=user)
            user_model.update_user_password(user_id, generate_password_hash(new_password))

        user_model.update_user(user_id, full_name, email, user["status"])
        session["full_name"] = full_name
        flash("Profile updated successfully.", "success")
        return redirect(url_for("admin.profile"))

    return render_template("admin/profile.html", user=user)
