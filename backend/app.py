import os
import jwt
import datetime
from functools import wraps
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================
# App Setup
# ==========================
app = Flask(__name__)
CORS(app)
Swagger(app)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "BBBDAP_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================
# Models
# ==========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

# ==========================
# JWT Decorator
# ==========================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"message": "Token missing"}), 401

        try:
            token = auth_header.split(" ")[1]  # Bearer <token>
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({"message": "Invalid or Expired Token"}), 401

        return f(*args, **kwargs)

    return decorated

# ==========================
# Home
# ==========================

@app.route("/")
def home():
    return "BB-BDAP Backend Running 🚀"

# ==========================
# Register
# ==========================

@app.route("/register", methods=["POST"])
def register():
    """
    Register User
    ---
    tags:
      - Auth
    requestBody:
      required: true
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# ==========================
# Login
# ==========================

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = jwt.encode({
        "user_id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({"token": token})

# ==========================
# Dashboard KPI
# ==========================

@app.route("/dashboard")
@token_required
def dashboard():
    total_sales = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    total_orders = db.session.query(db.func.count(Order.id)).scalar() or 0

    avg_order = total_sales / total_orders if total_orders > 0 else 0

    return jsonify({
        "total_sales": total_sales,
        "total_orders": total_orders,
        "average_order": round(avg_order, 2)
    })

# ==========================
# Sales Trend
# ==========================

@app.route("/sales")
@token_required
def sales():
    results = db.session.query(
        Order.order_date,
        db.func.sum(Order.total_amount)
    ).group_by(Order.order_date).order_by(Order.order_date).all()

    return jsonify([
        {
            "date": str(r[0]),
            "sales": r[1]
        }
        for r in results
    ])

# ==========================
# Forecast
# ==========================

@app.route("/forecast")
@token_required
def forecast():
    seven_days_ago = datetime.date.today() - datetime.timedelta(days=7)

    total = db.session.query(
        db.func.sum(Order.total_amount)
    ).filter(Order.order_date >= seven_days_ago).scalar() or 0

    forecast_value = total / 7

    return jsonify({
        "forecast_next_day": round(forecast_value, 2)
    })

# ==========================
# Stock Alert
# ==========================

@app.route("/stock-alert")
@token_required
def stock_alert():
    products = Product.query.all()

    alerts = [
        {
            "product": p.name,
            "status": "LOW STOCK"
        }
        for p in products
        if p.quantity_in_stock < 20
    ]

    return jsonify(alerts)

# ==========================
# Task CRUD
# ==========================

@app.route("/tasks", methods=["POST"])
@token_required
def create_task():
    data = request.get_json()
    new_task = Task(title=data["title"])
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created"}), 201

@app.route("/tasks", methods=["GET"])
@token_required
def get_tasks():
    tasks = Task.query.all()
    return jsonify([
        {"id": t.id, "title": t.title}
        for t in tasks
    ])

@app.route("/tasks/<int:id>", methods=["PUT"])
@token_required
def update_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.get_json()
    task.title = data["title"]
    db.session.commit()
    return jsonify({"message": "Task updated"})

@app.route("/tasks/<int:id>", methods=["DELETE"])
@token_required
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})

# ==========================
# Create Tables
# ==========================

with app.app_context():
    db.create_all()

# ==========================
# Run (Local Only)
# ==========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
