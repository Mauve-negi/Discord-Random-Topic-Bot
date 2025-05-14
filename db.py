import sqlite3
import os

DB_PATH = "topics.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # お題テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT UNIQUE NOT NULL
            )
        """)
        # 直近スレッドID記録
        cur.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # 予約お題テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE NOT NULL
            )
        """)
        conn.commit()


def add_topic(content):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO topics (content) VALUES (?)",
                    (content, ))
        # 予約にも自動で追加
        cur.execute("INSERT OR IGNORE INTO reservations (topic) VALUES (?)",
                    (content, ))
        conn.commit()


def get_random_topic():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT topic FROM reservations ORDER BY id LIMIT 1")
        row = cur.fetchone()
        if row:
            topic = row[0]
            cur.execute("DELETE FROM reservations WHERE topic = ?", (topic, ))
            conn.commit()
            return topic
        else:
            # fallback：登録お題からランダム
            cur.execute("SELECT content FROM topics ORDER BY RANDOM() LIMIT 1")
            return cur.fetchone()[0]


def get_all_topics():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT content FROM topics ORDER BY id")
        return [row[0] for row in cur.fetchall()]


def get_latest_thread_id():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT value FROM meta WHERE key = 'latest_thread_id'")
        row = cur.fetchone()
        return int(row[0]) if row else None


def set_latest_thread_id(thread_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('latest_thread_id', ?)",
            (str(thread_id), ))
        conn.commit()


def reserve_topic(content):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # 登録済のお題のみ予約可能
        cur.execute("SELECT 1 FROM topics WHERE content = ?", (content, ))
        if cur.fetchone():
            cur.execute(
                "INSERT OR IGNORE INTO reservations (topic) VALUES (?)",
                (content, ))
            conn.commit()
            return True
        return False
