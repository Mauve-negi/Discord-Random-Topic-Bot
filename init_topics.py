import db

# データベースを初期化（重複しないように CREATE IF NOT EXISTS）
# db.init_db()

# 好きなお題をリストで用意（自由に追加OK）
topics = [
    # "貞操帯"
]
# "競泳水着着ぐるみさん",
# "着ぐるみさんの呼吸音",
# "肌タイの感触",
# "後頭部ファスナー",
# "全頭面",
# "目閉じ、糸目着ぐるみさん",
# "はぁ…中の人は男性…",
# "着ぐるみさんマミー",
# "鍵",
# "動きが制限される衣装",
# "異色肌着ぐるみさん"

for t in topics:
    db.add_topic(t)

print("✅ お題を一括登録しました！")
