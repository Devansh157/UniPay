from flask import Flask
from auth.login import login_bp
from auth.register import register_bp
from auth.otp import otp_bp
from auth.logout import logout_bp
from main.home import home_bp

app = Flask(__name__)
app.secret_key = "super_secret_key"

app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(otp_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(home_bp)

if __name__ == "__main__":
    app.run(debug=True)
