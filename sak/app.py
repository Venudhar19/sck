from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.secret_key = "your_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)

# Dummy User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Dictionary to store user credentials (for demo purposes)
users = {"admin@example.com": "password123"}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email] == password:
            user = User(email)
            login_user(user)
            session["user_email"] = email
            return redirect(url_for("send_email"))
        else:
            return "Invalid credentials. Try again."

    return render_template("login.html")

@app.route("/send_email", methods=["GET", "POST"])
@login_required
def send_email():
    if request.method == "POST":
        file = request.files["file"]
        message = request.form["message"]

        if file:
            df = pd.read_excel(file)
            send_bulk_emails(df, message, session["user_email"])
            return "Emails sent successfully!"

    return render_template("send_email.html")

def send_bulk_emails(df, message, sender_email):
    smtp_server = "smtp.example.com"  # Replace with your SMTP server (e.g., smtp.gmail.com)
    smtp_port = 587
    smtp_username = sender_email
    smtp_password = "your_email_password"

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    for index, row in df.iterrows():
        recipient = row["Email"]
        subject = row["Subject"]
        
        email_msg = MIMEText(message)
        email_msg["From"] = sender_email
        email_msg["To"] = recipient
        email_msg["Subject"] = subject

        server.sendmail(sender_email, recipient, email_msg.as_string())

    server.quit()

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)