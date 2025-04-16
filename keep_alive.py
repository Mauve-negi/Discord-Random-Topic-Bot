from flask import Flask
from threading import Thread

app = Flask(__name__)

# メイン表示
@app.route('/')
def home():
    return "I'm alive!"

# ヘルスチェック用エンドポイント
@app.route('/health')
def health():
    return "ok", 200  # 200 OKを返すことで正常と判定される

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()
