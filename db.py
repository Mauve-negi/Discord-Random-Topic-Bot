import sqlite3
import random


# データベース初期化
def init_db():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.cursor()
        # お題管理テーブル（既存）
        cur.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        """)
        # 未集計スレッド管理テーブル（新設）
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pending_threads (
                thread_id INTEGER PRIMARY KEY
            )
        """)
        conn.commit()


# お題を追加
def add_topic(content):
    with sqlite3.connect("topics.db") as conn:
        conn.execute("INSERT INTO topics (content) VALUES (?)", (content, ))
        conn.commit()


# ランダムにお題を取得
def get_random_topic():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.execute(
            "SELECT content FROM topics ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else "（お題が登録されていません）"


# スレッドIDを未集計リストに登録
def add_pending_thread(thread_id):
    with sqlite3.connect("topics.db") as conn:
        conn.execute(
            "INSERT OR IGNORE INTO pending_threads (thread_id) VALUES (?)",
            (thread_id, ))
        conn.commit()


# 未集計のスレッドID一覧を取得
def get_pending_threads():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.execute("SELECT thread_id FROM pending_threads")
        return [row[0] for row in cur.fetchall()]


# スレッドIDを未集計リストから削除
def remove_pending_thread(thread_id):
    with sqlite3.connect("topics.db") as conn:
        conn.execute("DELETE FROM pending_threads WHERE thread_id = ?",
                     (thread_id, ))
        conn.commit()


# 全お題を取得
def get_all_topics():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.execute("SELECT id, content FROM topics ORDER BY id ASC")
        return cur.fetchall()
