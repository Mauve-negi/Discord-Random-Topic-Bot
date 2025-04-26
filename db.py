import sqlite3
import random

DB_PATH = "/data/topics.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS latest_thread (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                thread_id INTEGER
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reserved_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        """)
        conn.commit()


def get_random_topic():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT content FROM topics ORDER BY RANDOM() LIMIT 1")
        result = cur.fetchone()
        return result[0] if result else "（お題が登録されていません）"


def add_topic(content):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO topics (content) VALUES (?)", (content, ))
        conn.commit()


def set_latest_thread_id(thread_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO latest_thread (id, thread_id) VALUES (1, ?)",
            (thread_id, ))
        conn.commit()


def get_latest_thread_id():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT thread_id FROM latest_thread WHERE id = 1")
        result = cur.fetchone()
        return result[0] if result else None


def get_latest_topics(n=5):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT content FROM topics ORDER BY id DESC LIMIT ?", (n, ))
        return [row[0] for row in cur.fetchall()]


def get_all_topics():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT content FROM topics ORDER BY id")
        return [row[0] for row in cur.fetchall()]


def topic_exists(content):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT 1 FROM topics WHERE content = ?",
                           (content, ))
        return cur.fetchone() is not None


def add_reserved_topic(content):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO reserved_topics (content) VALUES (?)",
                     (content, ))
        conn.commit()


def pop_reserved_topic():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT id, content FROM reserved_topics ORDER BY id LIMIT 1")
        result = cur.fetchone()
        if result:
            topic_id, content = result
            conn.execute("DELETE FROM reserved_topics WHERE id = ?",
                         (topic_id, ))
            conn.commit()
            return content
        else:
            return None
