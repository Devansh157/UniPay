from flask import Blueprint, render_template, session, redirect, url_for

home_bp = Blueprint("home", __name__)

@home_bp.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login.login"))

    return render_template(
        "home.html",
        username=session["user"]
    )
