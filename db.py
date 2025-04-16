import sqlite3

DB_NAME = "topics.db"

# 📌 初期化（テーブルがなければ作成）
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # お題保存テーブル
        c.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
        """)

        # 状態管理テーブル（最新スレッドIDなど）
        c.execute("""
        CREATE TABLE IF NOT EXISTS state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        conn.commit()

# ➕ お題を追加
def add_topic(content):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO topics (content) VALUES (?)", (content,))
        conn.commit()

# 🎲 ランダムにお題を1つ取得
def get_random_topic():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("SELECT content FROM topics ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else "（お題が登録されていません）"

# 💾 最新スレッドIDを保存
def set_latest_thread_id(thread_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO state (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, ("latest_thread_id", str(thread_id)))
        conn.commit()

# 📤 最新スレッドIDを取得
def get_latest_thread_id():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("SELECT value FROM state WHERE key = ?", ("latest_thread_id",))
        row = cur.fetchone()
        return int(row[0]) if row else None
