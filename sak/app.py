from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
app.secret_key = "S3cR3t@123"  # Change this to a strong secret key

# Login Page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Any email can log in (no fixed email/password)
        session["user"] = email
        return redirect(url_for("dashboard"))

    return render_template("login.html")

# Dashboard Page
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files["file"]
        subject = request.form["subject"]
        message = request.form["message"]
        sender_email = request.form["sender_email"]
        sender_password = request.form["sender_password"]

        if file and file.filename.endswith(".xlsx"):
            file_path = os.path.join("uploads", file.filename)
            file.save(file_path)

            # Read Excel file
            df = pd.read_excel(file_path)
            emails = df["Email"].tolist()

            # Send emails
            success, error = send_bulk_emails(sender_email, sender_password, emails, subject, message)
            if success:
                flash("Emails sent successfully!", "success")
            else:
                flash(f"Error: {error}", "danger")
        else:
            flash("Invalid file format. Please upload an Excel file.", "danger")

    return render_template("dashboard.html")

# Function to Send Emails
def send_bulk_emails(sender_email, sender_password, recipients, subject, message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        for email in recipients:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = email
            msg["Subject"] = subject

            msg.attach(MIMEText(message, "plain"))
            server.sendmail(sender_email, email, msg.as_string())

        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)

# Logout Route
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# Run the App
if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
