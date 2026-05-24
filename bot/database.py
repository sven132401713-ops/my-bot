import os
import psycopg2
from datetime import datetime


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
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
    cursor.close()
    conn.close()


def save_order(source, order_text, client_username, client_id, client_name):
    conn = get_connection()
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
        VALUES (%s, %s, %s, %s, %s, %s)
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
    cursor.close()
    conn.close()


def get_all_orders():
    conn = get_connection()
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

    cursor.close()
    conn.close()

    return rows


def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM orders")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE source='Telegram'")
    telegram = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE source='VK'")
    vk = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "total": total,
        "telegram": telegram,
        "vk": vk
    }