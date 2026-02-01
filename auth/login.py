from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db_connection
from werkzeug.security import check_password_hash
import random, time
from datetime import datetime, timedelta
from utils.auth_logger import log_auth_event

login_bp = Blueprint("login", __name__)

LOGIN_OTP_VALIDITY = 120  # seconds
MAX_OTP_ATTEMPTS = 5


# -------------------------------
# LOGIN (USERNAME + PASSWORD)
# -------------------------------
@login_bp.route("/", methods=["GET", "POST"])
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    message = None
    lock_remaining = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template(
                "login.html",
                message="All fields are required."
            )

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        # ❌ WRONG PASSWORD / USER
        if not user or not check_password_hash(user["password"], password):
            log_auth_event(
                username,
                action="login_password",
                result="failure",
                reason="wrong_password"
            )
            message = "Invalid username or password."

        # 🚫 BANNED
        elif user["is_banned"]:
            log_auth_event(
                username,
                action="login_password",
                result="blocked",
                reason="account_banned"
            )
            message = "Your account has been temporarily banned."

        # ⏳ LOCKED
        elif user["locked_until"] and user["locked_until"] > datetime.now():
            lock_remaining = int(
                (user["locked_until"] - datetime.now()).total_seconds()
            )
            log_auth_event(
                username,
                action="login_password",
                result="blocked",
                reason="account_locked"
            )
            message = "Your account is temporarily locked."

        # 📧 EMAIL NOT VERIFIED
        elif not user["email_verified"]:
            log_auth_event(
                username,
                action="login_password",
                result="blocked",
                reason="email_not_verified"
            )
            session["email_to_verify"] = user["email"]
            return render_template(
                "login.html",
                message="Please verify your email before logging in.",
                show_verify_popup=True,
                email=user["email"]
            )

        # ✅ PASSWORD OK → SEND LOGIN OTP
        else:
            login_otp = str(random.randint(100000, 999999))

            session["login_otp"] = login_otp
            session["login_otp_time"] = time.time()
            session["login_otp_user"] = user["username"]
            session["login_otp_attempts"] = 0

            print("LOGIN OTP:", login_otp, flush=True)

            log_auth_event(
                username,
                action="login_password",
                result="success",
                reason="otp_generated"
            )

            return redirect(url_for("login.login_otp"))

    return render_template(
        "login.html",
        message=message,
        lock_remaining=lock_remaining
    )


# -------------------------------
# LOGIN OTP (2FA)
# -------------------------------
@login_bp.route("/login-otp", methods=["GET", "POST"])
def login_otp():
    if "login_otp" not in session:
        return redirect(url_for("login.login"))

    message = None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE username=%s",
        (session["login_otp_user"],)
    )
    user = cursor.fetchone()

    # 🚫 BANNED
    if user["is_banned"]:
        log_auth_event(
            user["username"],
            action="login_otp",
            result="blocked",
            reason="account_banned"
        )
        session.clear()
        cursor.close()
        conn.close()
        return redirect(url_for("login.login"))

    # ⏳ LOCKED
    if user["locked_until"] and user["locked_until"] > datetime.now():
        log_auth_event(
            user["username"],
            action="login_otp",
            result="blocked",
            reason="account_locked"
        )
        session.clear()
        cursor.close()
        conn.close()
        return redirect(url_for("login.login"))

    # ⌛ OTP EXPIRED
    if time.time() - session["login_otp_time"] > LOGIN_OTP_VALIDITY:
        log_auth_event(
            user["username"],
            action="login_otp",
            result="failure",
            reason="otp_expired"
        )
        session.clear()
        cursor.close()
        conn.close()
        return redirect(url_for("login.login"))

    # -------------------------------
    # HANDLE OTP SUBMISSION
    # -------------------------------
    if request.method == "POST":
        entered_otp = request.form.get("otp")

        # ❌ WRONG OTP
        if entered_otp != session.get("login_otp"):
            log_auth_event(
                user["username"],
                action="login_otp",
                result="failure",
                reason="wrong_otp"
            )

            session["login_otp_attempts"] += 1
            attempts = session["login_otp_attempts"]

            if attempts >= MAX_OTP_ATTEMPTS:
                new_fail_count = user["otp_fail_count"] + 1

                if new_fail_count == 1:
                    lock_time = datetime.now() + timedelta(hours=24)
                elif new_fail_count == 2:
                    lock_time = datetime.now() + timedelta(hours=48)
                else:
                    cursor.execute(
                        "UPDATE users SET is_banned=1 WHERE username=%s",
                        (user["username"],)
                    )
                    conn.commit()

                    log_auth_event(
                        user["username"],
                        action="login_otp",
                        result="blocked",
                        reason="account_banned"
                    )

                    session.clear()
                    cursor.close()
                    conn.close()
                    return redirect(url_for("login.login"))

                cursor.execute(
                    """
                    UPDATE users
                    SET otp_fail_count=%s, locked_until=%s
                    WHERE username=%s
                    """,
                    (new_fail_count, lock_time, user["username"])
                )
                conn.commit()

                log_auth_event(
                    user["username"],
                    action="login_otp",
                    result="blocked",
                    reason=f"locked_{new_fail_count}"
                )

                session.clear()
                cursor.close()
                conn.close()
                return redirect(url_for("login.login"))

            message = f"Invalid OTP. Attempts left: {MAX_OTP_ATTEMPTS - attempts}"

        # ✅ OTP CORRECT
        else:
            log_auth_event(
                user["username"],
                action="login_otp",
                result="success",
                reason="verified"
            )

            cursor.execute(
                """
                UPDATE users
                SET otp_fail_count=0,
                    locked_until=NULL
                WHERE username=%s
                """,
                (user["username"],)
            )
            conn.commit()

            session.clear()
            session["user"] = user["username"]

            cursor.close()
            conn.close()
            return redirect(url_for("home.home"))

    # -------------------------------
    # OTP TIMER
    # -------------------------------
    remaining_seconds = max(
        0,
        LOGIN_OTP_VALIDITY - int(time.time() - session["login_otp_time"])
    )

    cursor.close()
    conn.close()

    return render_template(
        "login_otp.html",
        message=message,
        remaining_seconds=remaining_seconds
    )
