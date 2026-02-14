This project is still underdevelopment
---

# UniPay 💳

*A Secure Authentication-Based Web Application*

UniPay is a Python-based web application built using **Flask** that focuses on **secure user authentication**, including **OTP-based verification**. The project demonstrates clean backend structuring, modular authentication logic, and template-based UI rendering.

This project is suitable for **academic submission**, **backend practice**, and **entry-level interview discussions**.

---

## 🚀 Features

* 🔐 User Registration & Login System
* 📩 OTP-based Authentication Flow
* 🔄 Secure Logout Handling
* 🧩 Modular Flask Blueprint Structure
* 🗄️ Database Integration (via `db.py`)
* 🎨 HTML Templates for UI Rendering

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML (Jinja Templates)
* **Database:** SQLite / Custom DB logic (via `db.py`)
* **Authentication:** OTP-based verification
* **Project Structure:** Modular & Scalable

---

## 📂 Project Structure

```
UniPay/
│
├── app.py                  # Main Flask app entry point
├── db.py                   # Database connection & operations
│
├── auth/                   # Authentication module
│   ├── login.py             # Login logic
│   ├── register.py          # Registration logic
│   ├── otp.py               # OTP generation & verification
│   ├── logout.py            # Logout handling
│   └── __init__.py
│
├── main/
│   ├── home.py              # Home/dashboard routes
│   └── __init__.py
│
├── utils/
│   └── auth_logger.py       # Authentication logging utilities
│
├── templates/               # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── otp.html
│   ├── login_otp.html
│   └── home.html
│
├── static/                  # Static assets (CSS/JS if added later)
│
└── __pycache__/             # Python cache files
```

---

## 🔐 Authentication Flow

1. **User registers** with required credentials
2. **OTP is generated** and sent (logic handled in `otp.py`)
3. User **verifies OTP** to complete authentication
4. Successful login redirects to **Home Dashboard**
5. Session is securely cleared on logout

---

## ▶️ How to Run the Project

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/UniPay.git
cd UniPay
```

### 2️⃣ Install Dependencies

```bash
pip install flask
```

*(Add more if you later include them)*

### 3️⃣ Run the Application

```bash
python app.py
```

### 4️⃣ Open in Browser

```
http://127.0.0.1:5000/
```

---

## 📌 Purpose of the Project

* Practice **Flask backend development**
* Understand **authentication workflows**
* Learn **modular code organization**
* Build a **resume-ready mini project**

---

## 🧠 Future Improvements

* 🔑 Password hashing (bcrypt)
* 📧 Email/SMS-based real OTP delivery
* 🛡️ Role-based access control
* 🎨 Improved frontend styling
* 🧪 Unit & integration tests

---

## 👤 Author

**Devansh Kolhe**
Computer Science Student
Backend & System Design Enthusiast

---

## 📄 License

This project is for **educational purposes**.


