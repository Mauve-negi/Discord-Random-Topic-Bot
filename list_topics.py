import sqlite3


def list_all_topics():
    with sqlite3.connect("topics.db") as conn:
        cur = conn.execute("SELECT id, content FROM topics ORDER BY id")
        rows = cur.fetchall()

        if not rows:
            print("⚠️ 登録されているお題はありません。")
            return

        print("📚 登録済みお題一覧：")
        for row in rows:
            print(f"{row[0]:03d}: {row[1]}")


# 実行
if __name__ == "__main__":
    list_all_topics()
