import sqlite3
import random

DB_NAME = "/data/topics.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_topic(content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO topics (content) VALUES (?)", (content, ))
    conn.commit()
    conn.close()


def get_all_topics():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT content FROM topics ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_latest_topics(n=5):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT content FROM topics ORDER BY id DESC LIMIT ?", (n, ))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]


def topic_exists(content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM topics WHERE content = ?", (content, ))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def reserve_topic(content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key = 'reserved'")
    current = c.fetchone()
    if current and current[0] == content:
        conn.close()
        return False
    c.execute("REPLACE INTO config (key, value) VALUES ('reserved', ?)",
              (content, ))
    conn.commit()
    conn.close()
    return True


def get_reserved_theme():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key = 'reserved'")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def pop_reserved_topic():
    topic = get_reserved_theme()
    if not topic:
        return None
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM config WHERE key = 'reserved'")
    conn.commit()
    conn.close()
    return topic


def get_random_topic():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT content FROM topics ORDER BY RANDOM() LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def set_latest_thread_id(thread_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "REPLACE INTO config (key, value) VALUES ('latest_thread_id', ?)",
        (str(thread_id), ))
    conn.commit()
    conn.close()


def get_latest_thread_id():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key = 'latest_thread_id'")
    row = c.fetchone()
    conn.close()
    return int(row[0]) if row else None
