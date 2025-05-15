import sqlite3

DB_NAME = "themes.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS themes (
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
        CREATE TABLE IF NOT EXISTS mvp_counts (
            user_id INTEGER PRIMARY KEY,
            count INTEGER NOT NULL DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()


def register_theme(theme):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO themes (content) VALUES (?)", (theme, ))
    conn.commit()
    conn.close()


def get_random_theme():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT content FROM themes ORDER BY RANDOM() LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def get_all_topics():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT content FROM themes ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_latest_topics(n=5):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT content FROM themes ORDER BY id DESC LIMIT ?", (n, ))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]


def topic_exists(theme):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM themes WHERE content = ?", (theme, ))
    result = c.fetchone()
    conn.close()
    return result is not None


def set_reserved_theme(theme):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO config (key, value) VALUES ('reserved_theme', ?)",
              (theme, ))
    conn.commit()
    conn.close()


def get_reserved_theme():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key = 'reserved_theme'")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def reserve_topic(theme):
    set_reserved_theme(theme)


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


def get_mvp_count(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT count FROM mvp_counts WHERE user_id = ?", (user_id, ))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0


def increment_mvp_count(user_id):
    current = get_mvp_count(user_id)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if current == 0:
        c.execute("INSERT INTO mvp_counts (user_id, count) VALUES (?, ?)",
                  (user_id, 1))
    else:
        c.execute("UPDATE mvp_counts SET count = ? WHERE user_id = ?",
                  (current + 1, user_id))
    conn.commit()
    conn.close()


def get_reserved_or_random_topic():
    topic = get_reserved_theme()
    if topic:
        return topic
    return get_random_theme()


# 初期化
init_db()
