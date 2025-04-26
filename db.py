# db.py

import sqlite3

DB_PATH = "/data/topics.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS topics (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS reservation (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)"
        )


def add_topic(content):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO topics (content) VALUES (?)", (content, ))
        conn.commit()


def get_random_topic():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT content FROM topics ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else None


def set_latest_thread_id(thread_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS latest_thread (id INTEGER)")
        conn.execute("DELETE FROM latest_thread")
        conn.execute("INSERT INTO latest_thread (id) VALUES (?)",
                     (thread_id, ))
        conn.commit()


def get_latest_thread_id():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT id FROM latest_thread")
        row = cur.fetchone()
        return row[0] if row else None


def reserve_topic(content):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO reservation (content) VALUES (?)",
                     (content, ))
        conn.commit()


def pop_reserved_topic():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT id, content FROM reservation ORDER BY id LIMIT 1")
        row = cur.fetchone()
        if row:
            conn.execute("DELETE FROM reservation WHERE id = ?", (row[0], ))
            conn.commit()
            return row[1]
        return None


def is_topic_exists(content):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT 1 FROM topics WHERE content = ?",
                           (content, ))
        return cur.fetchone() is not None


def get_all_topics():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT content FROM topics ORDER BY id")
        return [row[0] for row in cur.fetchall()]
