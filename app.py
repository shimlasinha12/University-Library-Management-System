from flask import Flask, render_template, session, redirect, url_for, request
from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Register Blueprints (imported here so app.py is the single entry point)
from utils import register_template_utils
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.librarian_routes import librarian_bp
from routes.student_routes import student_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(librarian_bp, url_prefix="/librarian")
app.register_blueprint(student_bp, url_prefix="/student")

register_template_utils(app)


@app.route("/")
def index():
    """Root route — redirect to login or the user's dashboard."""
    if "user_id" in session:
        role = session.get("role")
        if role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif role == "librarian":
            return redirect(url_for("librarian.dashboard"))
        elif role == "student":
            return redirect(url_for("student.dashboard"))
    return redirect(url_for("auth.login"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("errors/500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
