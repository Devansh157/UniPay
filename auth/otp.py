from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db_connection
import random, time, smtplib
from email.message import EmailMessage

otp_bp = Blueprint("otp", __name__)

EMAIL_OTP_VALIDITY = 30  # seconds
DEBUG_EMAIL = True  # True = print OTP, False = send email


# -------------------------------
# EMAIL SENDER
# -------------------------------
def send_verification_email(to_email, otp):
    if DEBUG_EMAIL:
        print("EMAIL OTP (DEV MODE):", otp, flush=True)
        return

    msg = EmailMessage()
    msg.set_content(f"Your UniPay email verification OTP is: {otp}")
    msg["Subject"] = "Verify your UniPay Account"
    msg["From"] = "your_email@gmail.com"
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("your_email@gmail.com", "your_app_password")
        smtp.send_message(msg)


# -------------------------------
# GENERATE & SEND EMAIL OTP
# -------------------------------
def send_email_verification_otp(email):
    otp = str(random.randint(100000, 999999))

    session["email_otp"] = otp
    session["email_to_verify"] = email
    session["email_otp_time"] = time.time()

    send_verification_email(email, otp)


# -------------------------------
# VERIFY EMAIL PAGE
# -------------------------------
@otp_bp.route("/verify-email", methods=["GET", "POST"])
def verify_email():

    # Guard: direct access protection
    if "email_otp" not in session or "email_otp_time" not in session:
        return redirect(url_for("register.register"))

    message = session.pop("resend_message", None)

    # ---------- VERIFY OTP ----------
    if request.method == "POST":
        entered_otp = request.form.get("otp")

        if not entered_otp:
            message = "Please enter the OTP."

        elif time.time() - session["email_otp_time"] > EMAIL_OTP_VALIDITY:
            session.clear()
            message = "OTP expired. Please register again."

        elif entered_otp != session.get("email_otp"):
            message = "Invalid OTP."

        else:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET email_verified = 1 WHERE email = %s",
                (session["email_to_verify"],)
            )

            conn.commit()
            cursor.close()
            conn.close()

            session.clear()
            return redirect(url_for("login.login"))

    # ---------- TIMER CALCULATION ----------
    elapsed = int(time.time() - session["email_otp_time"])
    remaining_seconds = max(0, EMAIL_OTP_VALIDITY - elapsed)
    otp_expired = remaining_seconds == 0

    return render_template(
        "otp.html",
        message=message,
        remaining_seconds=remaining_seconds,
        otp_expired=otp_expired
    )


# -------------------------------
# RESEND EMAIL OTP
# -------------------------------
@otp_bp.route("/resend-email-otp", methods=["POST"])
def resend_email_otp():
    if "email_to_verify" not in session:
        return redirect(url_for("register.register"))

    send_email_verification_otp(session["email_to_verify"])
    session["resend_message"] = "A new OTP has been sent."

    return redirect(url_for("otp.verify_email"))
