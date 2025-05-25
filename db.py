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
    c.execute('''
        CREATE TABLE IF NOT EXISTS reserved_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def add_topic(content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO topics (content) VALUES (?)", (content,))
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
    c.execute("SELECT content FROM topics ORDER BY id DESC LIMIT ?", (n,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]


def topic_exists(content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM topics WHERE content = ?", (content,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def reserve_topic(content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO reserved_topics (content) VALUES (?)", (content,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success


def get_reserved_themes():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT content FROM reserved_topics ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]


def pop_reserved_topic():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, content FROM reserved_topics ORDER BY id ASC LIMIT 1")
    row = c.fetchone()
    if row:
        c.execute("DELETE FROM reserved_topics WHERE id = ?", (row[0],))
        conn.commit()
        topic = row[1]
    else:
        topic = None
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
    c.execute("REPLACE INTO config (key, value) VALUES ('latest_thread_id', ?)", (str(thread_id),))
    conn.commit()
    conn.close()


def get_latest_thread_id():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key = 'latest_thread_id'")
    row = c.fetchone()
    conn.close()
    return int(row[0]) if row else None


def set_day_n_topic(n, content):
    assert 1 <= n <= 3, "n must be 1, 2, or 3"
    key = f"day_{n}"
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO config (key, value) VALUES (?, ?)", (key, content))
    conn.commit()
    conn.close()


def get_recent_topics():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    result = {}
    for n in [1, 2, 3]:
        key = f"day_{n}"
        c.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = c.fetchone()
        result[n] = row[0] if row else None
    conn.close()
    return result
