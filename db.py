# db.py

import sqlite3


def init_db():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reserved_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        """)
        conn.commit()


def get_random_topic():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.execute(
            "SELECT content FROM topics ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else None


def get_random_topic_id_and_content():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.execute(
            "SELECT id, content FROM topics ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        return row if row else (None, None)


def set_latest_thread_id(thread_id):
    with sqlite3.connect("topics.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS latest_thread (id INTEGER PRIMARY KEY, thread_id INTEGER)"
        )
        cur.execute("DELETE FROM latest_thread")
        cur.execute("INSERT INTO latest_thread (id, thread_id) VALUES (?, ?)",
                    (1, thread_id))
        conn.commit()


def get_latest_thread_id():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.execute("SELECT thread_id FROM latest_thread WHERE id = 1")
        row = cur.fetchone()
        return row[0] if row else None


# 🎯 新規：指定されたお題が存在するかチェック
def find_topic_id_by_content(content):
    with sqlite3.connect("topics.db") as conn:
        cur = conn.execute("SELECT id FROM topics WHERE content = ?",
                           (content, ))
        row = cur.fetchone()
        return row[0] if row else None


# 🎯 新規：予約を追加
def add_reserved_topic(topic_id):
    with sqlite3.connect("topics.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO reserved_topics (topic_id) VALUES (?)",
                    (topic_id, ))
        conn.commit()


# 🎯 新規：予約を一番先頭から取得して消費
def pop_reserved_topic_content():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT reserved_topics.id, topics.content
            FROM reserved_topics
            JOIN topics ON reserved_topics.topic_id = topics.id
            ORDER BY reserved_topics.id ASC
            LIMIT 1
        """)
        row = cur.fetchone()
        if row:
            reserved_id, content = row
            cur.execute("DELETE FROM reserved_topics WHERE id = ?",
                        (reserved_id, ))
            conn.commit()
            return content
        else:
            return None


# （おまけ）予約リスト全取得（必要ならあとで追加可能）
