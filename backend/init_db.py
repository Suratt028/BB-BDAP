import sqlite3

conn = sqlite3.connect("bbdap.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_date TEXT,
    total_amount REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    quantity_in_stock INTEGER
)
""")

# Sample Data
cursor.execute("INSERT INTO products (name, quantity_in_stock) VALUES ('Croissant', 15)")
cursor.execute("INSERT INTO products (name, quantity_in_stock) VALUES ('Chocolate Cake', 50)")

conn.commit()
conn.close()

print("Database initialized!")
