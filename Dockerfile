# ベースは軽量なPython公式イメージ
FROM python:3.11-slim

# 作業ディレクトリ作成
WORKDIR /app

# すべてのファイルをコピー
COPY . .
COPY topics.db /app/topics.db  # ⬅️この行を追加する

# パッケージをインストール（キャッシュ削除で軽量化）
RUN pip install --no-cache-dir -r requirements.txt

# Botを起動
CMD ["python", "bot.py"]
