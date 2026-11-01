"""
Kamau Nails — Flask backend
----------------------------
Run with:  python app.py
Then open: http://127.0.0.1:5000

This file wires up every page, the SQLite database, the booking
system, the payment-proof upload flow, and a password-protected
admin dashboard. See README.md for full setup instructions.
"""

import os
import sqlite3
from datetime import datetime, date
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, g, send_from_directory
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kamau_nails.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "kamau-nails-dev-secret-change-me")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB uploads

# Business contact info — edit these to change them site-wide.
SALON_PHONE = "0740729339"
SALON_EMAIL = "jacktonecharles@gmail.com"
PAYMENT_NUMBER = "0740729339"

# Default admin login (change the password immediately — see README).
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "KamauNails2026!"


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables (if they don't exist yet) and seed starter content."""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            duration_minutes INTEGER,
            price INTEGER,
            icon TEXT DEFAULT 'sparkle'
        );

        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT,
            years_experience INTEGER,
            specialties TEXT,
            rating REAL DEFAULT 5.0,
            initials TEXT
        );

        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            service_id INTEGER,
            technician_id INTEGER,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            special_requests TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_id) REFERENCES services (id),
            FOREIGN KEY (technician_id) REFERENCES technicians (id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service_name TEXT,
            amount_paid TEXT,
            transaction_code TEXT,
            screenshot_filename TEXT,
            status TEXT DEFAULT 'Awaiting Verification',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings (id)
        );

        CREATE TABLE IF NOT EXISTS testimonials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            quote TEXT NOT NULL,
            rating INTEGER DEFAULT 5,
            approved INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            subject TEXT,
            message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS newsletter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    db.commit()

    # Seed admin account.
    cur = db.execute("SELECT COUNT(*) AS c FROM admins")
    if cur.fetchone()["c"] == 0:
        db.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            (DEFAULT_ADMIN_USERNAME, generate_password_hash(DEFAULT_ADMIN_PASSWORD)),
        )

    # Seed services.
    cur = db.execute("SELECT COUNT(*) AS c FROM services")
    if cur.fetchone()["c"] == 0:
        starter_services = [
            ("Manicure", "Classic Manicure", "Shape, cuticle care, hand massage and polish.", 40, 800, "hand"),
            ("Manicure", "Luxury Manicure", "Exfoliation, paraffin dip, extended massage and premium polish.", 60, 1500, "hand"),
            ("Manicure", "Gel Manicure", "Long-wear gel polish with a glass-like, chip-free finish.", 50, 1800, "hand"),
            ("Pedicure", "Classic Pedicure", "Soak, shape, cuticle care and polish for happy feet.", 45, 1000, "foot"),
            ("Pedicure", "Spa Pedicure", "Sea-salt soak, callus treatment, mask and massage.", 60, 1800, "foot"),
            ("Pedicure", "Luxury Pedicure", "Our signature soak, hot-stone massage and premium polish.", 75, 2500, "foot"),
            ("Extensions", "Acrylic Nails", "Durable, sculpted extensions in any length or shape.", 90, 2500, "sparkle"),
            ("Extensions", "Gel Nails", "Lightweight, natural-looking gel overlay or extension.", 90, 2800, "sparkle"),
            ("Nail Art", "Custom Nail Art", "Hand-painted designs, from minimal to fully custom.", 30, 500, "brush"),
            ("Nail Art", "Ombre Nails", "Seamless gradient blends in your choice of colours.", 30, 700, "brush"),
            ("Nail Art", "French Tips", "The timeless classic, done crisp and precise.", 30, 600, "brush"),
            ("Repairs", "Nail Repair", "Fix a chip, crack or lifted tip fast.", 20, 300, "wrench"),
            ("Special", "Bridal Package", "Trial + wedding-day mani-pedi for the bride.", 120, 4500, "ring"),
            ("Special", "Kids Nail Service", "Gentle polish for our youngest guests (12 & under).", 30, 500, "star"),
            ("Add-on", "Paraffin Wax Treatment", "Deeply moisturising heated-wax hand treatment.", 15, 400, "sparkle"),
        ]
        db.executemany(
            "INSERT INTO services (category, name, description, duration_minutes, price, icon) VALUES (?,?,?,?,?,?)",
            starter_services,
        )

    # Seed technicians.
    cur = db.execute("SELECT COUNT(*) AS c FROM technicians")
    if cur.fetchone()["c"] == 0:
        starter_techs = [
            ("Amina Wanjiru", "Senior Nail Artist", 8, "Nail art, ombre, bridal", 5.0, "AW"),
            ("Grace Njeri", "Gel & Extensions Specialist", 6, "Acrylics, gel extensions", 4.9, "GN"),
            ("Faith Achieng", "Spa Pedicure Expert", 5, "Spa pedicures, reflexology touch", 4.8, "FA"),
            ("Brenda Moraa", "Nail Technician", 3, "Classic mani/pedi, French tips", 4.9, "BM"),
        ]
        db.executemany(
            "INSERT INTO technicians (name, position, years_experience, specialties, rating, initials) VALUES (?,?,?,?,?,?)",
            starter_techs,
        )

    # Seed testimonials.
    cur = db.execute("SELECT COUNT(*) AS c FROM testimonials")
    if cur.fetchone()["c"] == 0:
        starter_testimonials = [
            ("Wambui K.", "My nails have never looked this good. The attention to detail is unmatched!", 5),
            ("Naliaka M.", "Booked online in two minutes and the salon was exactly as beautiful as the photos.", 5),
            ("Cynthia A.", "Amina did my bridal set and I got compliments all night. Worth every shilling.", 5),
        ]
        db.executemany(
            "INSERT INTO testimonials (customer_name, quote, rating) VALUES (?, ?, ?)",
            starter_testimonials,
        )

    db.commit()
    db.close()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_globals():
    return {
        "salon_phone": SALON_PHONE,
        "salon_email": SALON_EMAIL,
        "current_year": datetime.now().year,
    }


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    db = get_db()
    featured = db.execute(
        "SELECT * FROM services GROUP BY category ORDER BY id LIMIT 6"
    ).fetchall()
    testimonials = db.execute(
        "SELECT * FROM testimonials WHERE approved = 1 ORDER BY id DESC LIMIT 6"
    ).fetchall()
    techs = db.execute("SELECT * FROM technicians LIMIT 3").fetchall()
    return render_template("index.html", featured=featured, testimonials=testimonials, techs=techs)


@app.route("/about")
def about():
    db = get_db()
    techs = db.execute("SELECT * FROM technicians").fetchall()
    return render_template("about.html", techs=techs)


@app.route("/services")
def services():
    db = get_db()
    rows = db.execute("SELECT * FROM services ORDER BY category, id").fetchall()
    categories = {}
    for row in rows:
        categories.setdefault(row["category"], []).append(row)
    return render_template("services.html", categories=categories)


@app.route("/team")
def team():
    db = get_db()
    techs = db.execute("SELECT * FROM technicians").fetchall()
    return render_template("team.html", techs=techs)


@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


@app.route("/booking", methods=["GET", "POST"])
def booking():
    db = get_db()
    services_list = db.execute("SELECT * FROM services ORDER BY category, name").fetchall()
    techs = db.execute("SELECT * FROM technicians").fetchall()

    if request.method == "POST":
        name = request.form.get("customer_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        service_id = request.form.get("service_id")
        technician_id = request.form.get("technician_id") or None
        booking_date = request.form.get("booking_date", "")
        booking_time = request.form.get("booking_time", "")
        notes = request.form.get("special_requests", "").strip()

        errors = []
        if not name:
            errors.append("Please tell us your name.")
        if not phone:
            errors.append("Please add a phone number so we can confirm your visit.")
        if not service_id:
            errors.append("Please choose a service.")
        if not booking_date:
            errors.append("Please choose a date.")
        if not booking_time:
            errors.append("Please choose a time.")
        else:
            try:
                if datetime.strptime(booking_date, "%Y-%m-%d").date() < date.today():
                    errors.append("Please choose a date in the future.")
            except ValueError:
                errors.append("That date doesn't look right.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "booking.html", services_list=services_list, techs=techs,
                form=request.form,
            )

        cur = db.execute(
            """INSERT INTO bookings
               (customer_name, phone, email, service_id, technician_id, booking_date, booking_time, special_requests)
               VALUES (?,?,?,?,?,?,?,?)""",
            (name, phone, email, service_id, technician_id, booking_date, booking_time, notes),
        )
        db.commit()
        booking_id = cur.lastrowid
        return redirect(url_for("booking_success", booking_id=booking_id))

    return render_template("booking.html", services_list=services_list, techs=techs, form={})


@app.route("/booking/success/<int:booking_id>")
def booking_success(booking_id):
    db = get_db()
    booking_row = db.execute(
        """SELECT b.*, s.name AS service_name, s.price, t.name AS technician_name
           FROM bookings b
           LEFT JOIN services s ON b.service_id = s.id
           LEFT JOIN technicians t ON b.technician_id = t.id
           WHERE b.id = ?""",
        (booking_id,),
    ).fetchone()
    if booking_row is None:
        return redirect(url_for("booking"))
    return render_template("booking_success.html", booking=booking_row)


@app.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "POST":
        name = request.form.get("customer_name", "").strip()
        phone = request.form.get("phone", "").strip()
        service_name = request.form.get("service_name", "").strip()
        amount = request.form.get("amount_paid", "").strip()
        code = request.form.get("transaction_code", "").strip()
        file = request.files.get("screenshot")

        errors = []
        if not name:
            errors.append("Please add your name.")
        if not phone:
            errors.append("Please add your phone number.")
        if not amount:
            errors.append("Please tell us how much you paid.")
        if not code:
            errors.append("Please add the M-Pesa transaction code.")

        filename = None
        if file and file.filename:
            if allowed_file(file.filename):
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(file.filename)}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            else:
                errors.append("Please upload a PNG, JPG or PDF file.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("payment.html", form=request.form, payment_number=PAYMENT_NUMBER)

        db = get_db()
        db.execute(
            """INSERT INTO payments (customer_name, phone, service_name, amount_paid, transaction_code, screenshot_filename)
               VALUES (?,?,?,?,?,?)""",
            (name, phone, service_name, amount, code, filename),
        )
        db.commit()
        flash("Thank you! Your payment proof was submitted and is awaiting verification.", "success")
        return redirect(url_for("payment"))

    return render_template("payment.html", form={}, payment_number=PAYMENT_NUMBER)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        # honeypot spam trap
        if request.form.get("website"):
            return redirect(url_for("contact"))

        if not name or not message:
            flash("Please add your name and a message.", "error")
            return render_template("contact.html", form=request.form)

        db = get_db()
        db.execute(
            "INSERT INTO messages (name, email, phone, subject, message) VALUES (?,?,?,?,?)",
            (name, email, phone, subject, message),
        )
        db.commit()
        flash("Message sent! We'll get back to you shortly.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", form={})


@app.route("/newsletter", methods=["POST"])
def newsletter():
    email = request.form.get("email", "").strip()
    if email:
        db = get_db()
        try:
            db.execute("INSERT INTO newsletter (email) VALUES (?)", (email,))
            db.commit()
            flash("You're on the list! Watch your inbox for offers.", "success")
        except sqlite3.IntegrityError:
            flash("You're already subscribed.", "info")
    return redirect(request.referrer or url_for("home"))


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/policies")
@app.route("/policies/<section>")
def policies(section=None):
    return render_template("policies.html", section=section)


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        admin = db.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        if admin and check_password_hash(admin["password_hash"], password):
            session["is_admin"] = True
            session["admin_username"] = username
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    db = get_db()
    bookings = db.execute(
        """SELECT b.*, s.name AS service_name, t.name AS technician_name
           FROM bookings b
           LEFT JOIN services s ON b.service_id = s.id
           LEFT JOIN technicians t ON b.technician_id = t.id
           ORDER BY b.created_at DESC"""
    ).fetchall()
    payments = db.execute("SELECT * FROM payments ORDER BY created_at DESC").fetchall()
    messages = db.execute("SELECT * FROM messages ORDER BY created_at DESC").fetchall()
    stats = {
        "total_bookings": len(bookings),
        "pending_bookings": sum(1 for b in bookings if b["status"] == "Pending"),
        "total_payments": len(payments),
        "unverified_payments": sum(1 for p in payments if p["status"] == "Awaiting Verification"),
        "messages": len(messages),
    }
    return render_template(
        "admin_dashboard.html", bookings=bookings, payments=payments,
        messages=messages, stats=stats,
    )


@app.route("/admin/booking/<int:booking_id>/status", methods=["POST"])
@admin_required
def update_booking_status(booking_id):
    new_status = request.form.get("status")
    if new_status in ("Pending", "Confirmed", "Completed", "Cancelled"):
        db = get_db()
        db.execute("UPDATE bookings SET status = ? WHERE id = ?", (new_status, booking_id))
        db.commit()
        flash("Booking updated.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/payment/<int:payment_id>/status", methods=["POST"])
@admin_required
def update_payment_status(payment_id):
    new_status = request.form.get("status")
    if new_status in ("Awaiting Verification", "Verified", "Rejected"):
        db = get_db()
        db.execute("UPDATE payments SET status = ? WHERE id = ?", (new_status, payment_id))
        db.commit()
        flash("Payment updated.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/uploads/<filename>")
@admin_required
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if __name__ == "__main__":
    init_db()  # safe to re-run: only creates tables / inserts missing seed rows
    app.run(debug=True)
