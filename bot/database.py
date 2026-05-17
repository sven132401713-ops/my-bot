import sqlite3
from datetime import datetime


DB_NAME = "orders.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            source TEXT,
            order_text TEXT,
            client_username TEXT,
            client_id TEXT,
            client_name TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def save_order(source, order_text, client_username, client_id, client_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO orders (
            created_at,
            source,
            order_text,
            client_username,
            client_id,
            client_name
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            source,
            order_text,
            client_username,
            str(client_id),
            client_name
        )
    )

    conn.commit()
    conn.close()
def get_all_orders():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, created_at, source, order_text,
               client_username, client_id, client_name
        FROM orders
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows