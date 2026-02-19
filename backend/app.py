from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

SECRET_KEY = "BBBDAP_SECRET_KEY"

# ==========================
# Database Connection
# ==========================
def get_db():
    conn = sqlite3.connect("bbdap.db")
    conn.row_factory = sqlite3.Row
    return conn

# ==========================
# JWT Decorator
# ==========================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token missing"}), 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({"message": "Invalid Token"}), 401
        return f(*args, **kwargs)
    return decorated

# ==========================
# LOGIN
# ==========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == "owner" and password == "1234":
        token = jwt.encode({
            "user": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401

# ==========================
# DASHBOARD KPI
# ==========================
@app.route("/dashboard")
@token_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(total_amount) as total_sales FROM orders")
    total_sales = cursor.fetchone()["total_sales"] or 0

    cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
    total_orders = cursor.fetchone()["total_orders"]

    avg_order = total_sales / total_orders if total_orders > 0 else 0

    conn.close()

    return jsonify({
        "total_sales": total_sales,
        "total_orders": total_orders,
        "average_order": round(avg_order, 2)
    })

# ==========================
# SALES TREND
# ==========================
@app.route("/sales")
@token_required
def sales():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT order_date, SUM(total_amount) as daily_sales
        FROM orders
        GROUP BY order_date
        ORDER BY order_date
    """)

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "date": row["order_date"],
            "sales": row["daily_sales"]
        })

    return jsonify(result)

# ==========================
# FORECAST (7-day Moving Average)
# ==========================
@app.route("/forecast")
@token_required
def forecast():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(total_amount) as total
        FROM orders
        WHERE order_date >= date('now','-7 day')
    """)

    total = cursor.fetchone()["total"] or 0
    conn.close()

    forecast_value = total / 7

    return jsonify({
        "forecast_next_day": round(forecast_value, 2)
    })

# ==========================
# STOCK ALERT
# ==========================
@app.route("/stock-alert")
@token_required
def stock_alert():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name, quantity_in_stock FROM products")
    products = cursor.fetchall()

    alerts = []
    for product in products:
        if product["quantity_in_stock"] < 20:
            alerts.append({
                "product": product["name"],
                "status": "LOW STOCK"
            })

    conn.close()
    return jsonify(alerts)

# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
