# show_topics.py

import sqlite3


def show_all_topics():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.execute("SELECT id, content FROM topics ORDER BY id")
        topics = cur.fetchall()

    print("🗂 現在登録されているお題一覧：")
    for tid, content in topics:
        print(f"{tid}: {content}")


if __name__ == "__main__":
    show_all_topics()
