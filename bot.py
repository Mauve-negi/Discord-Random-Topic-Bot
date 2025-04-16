from keep_alive import keep_alive
import db
from datetime import datetime
import os
import discord
import random
import sqlite3

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents=intents)

TOPIC_CHANNEL_ID = int(os.environ["TOPIC_CHANNEL_ID"])
THEME_CHANNEL_ID = int(os.environ["THEME_CHANNEL_ID"])  # 🎯 チケット投稿専用チャンネル
TICKET_ROLE_NAME = "テーマ追加チケット"

LEVEL_ROLES = [
    "ふぇちのわかり手Lv.1", "ふぇちのわかり手Lv.2", "ふぇちのわかり手Lv.3",
    "ふぇちのわかり手Lv.4", "ふぇちのわかり手Lv.5"
]

@bot.event
async def on_ready():
    print(f"✅ Botがログインしました：{bot.user}")
    db.init_db()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 🎲 お題を即時投稿（!topic）
    if message.content == "!topic":
        await post_daily_topic(message.channel)
        return

    # 🏆 手動MVP集計（!mvp）
    if message.content == "!mvp" and isinstance(message.channel, discord.Thread):
        await process_mvp(message.channel)
        return

    # 🎟 チケット所持者によるテーマ投稿（専用チャンネルのみ）
    if message.channel.id == THEME_CHANNEL_ID and TICKET_ROLE_NAME in [r.name for r in message.author.roles]:
        db.add_topic(message.content)
        guild = message.guild
        role = discord.utils.get(guild.roles, name=TICKET_ROLE_NAME)
        if role:
            await message.author.remove_roles(role)
        await message.reply("✅ お題を登録しました！\n🎟 チケットは回収されました。")

        # 最新お題一覧をEmbedで表示
        latest_topics = get_latest_topics(5)
        embed = discord.Embed(title="🗂 現在のお題一覧（最新5件）", color=discord.Color.blue())
        for i, topic in enumerate(reversed(latest_topics), 1):
            embed.add_field(name=f"{i}.", value=topic, inline=False)
        await message.channel.send(embed=embed)
        return

# ✅ お題投稿＋スレッド生成
async def post_daily_topic(channel):
    topic = db.get_random_topic()
    embed = discord.Embed(
        title="📌 今日のお題",
        description=f"『{topic}』",
        color=discord.Color.purple()
    )
    embed.set_footer(text="遠慮なく語ってみてください！")

    message = await channel.send(embed=embed)

    today_str = datetime.utcnow().strftime("%Y/%m/%d")
    thread_name = f"{today_str}【{topic}】"
    if len(thread_name) > 100:
        thread_name = thread_name[:97] + "…"

    thread = await channel.create_thread(
        name=thread_name,
        message=message,
        auto_archive_duration=1440
    )

    db.set_latest_thread_id(thread.id)
    print(f"✅ {thread_name} を作成＆記録しました。")

# 🏆 MVP処理（!mvpで手動実行）
async def process_mvp(thread):
    await thread.send("📊 MVP集計を開始します...")

    max_reactions = 0
    mvp_user = None

    async for msg in thread.history(limit=None):
        total_reacts = sum(r.count for r in msg.reactions)
        if total_reacts > max_reactions:
            max_reactions = total_reacts
            mvp_user = msg.author

    if not mvp_user:
        await thread.send("⚠️ MVP候補が見つかりませんでした。")
        return

    guild = thread.guild
    member = guild.get_member(mvp_user.id)
    if member is None:
        await thread.send("⚠️ MVPのユーザー情報を取得できませんでした。")
        return

    current_level = -1
    for i, role_name in enumerate(LEVEL_ROLES):
        if any(role.name == role_name for role in member.roles):
            current_level = i
            break

    next_level = current_level + 1

    if next_level < len(LEVEL_ROLES):
        old_role = discord.utils.get(guild.roles, name=LEVEL_ROLES[current_level]) if current_level >= 0 else None
        new_role = discord.utils.get(guild.roles, name=LEVEL_ROLES[next_level])
        if old_role:
            await member.remove_roles(old_role)
        if new_role:
            await member.add_roles(new_role)

        embed = discord.Embed(
            title="🏆 今日のMVP",
            description=f"{member.mention} さんが最もリアクションを集めました！",
            color=discord.Color.gold()
        )
        embed.add_field(name="✨ ロール昇格", value=f"→ {LEVEL_ROLES[next_level]}", inline=False)
        embed.set_footer(text=f"リアクション数：{max_reactions}")
        await thread.send(embed=embed)
    else:
        old_role = discord.utils.get(guild.roles, name=LEVEL_ROLES[current_level])
        ticket_role = discord.utils.get(guild.roles, name=TICKET_ROLE_NAME)
        if old_role:
            await member.remove_roles(old_role)
        if ticket_role:
            await member.add_roles(ticket_role)

        embed = discord.Embed(
            title="🏆 今日のMVP",
            description=f"{member.mention} さんが最もリアクションを集めました！",
            color=discord.Color.gold()
        )
        embed.add_field(name="🎟 ご褒美", value="→ テーマ追加チケットを獲得！", inline=False)
        embed.set_footer(text=f"リアクション数：{max_reactions}")
        await thread.send(embed=embed)

    await thread.edit(archived=True, locked=True)

# 🔄 お題履歴取得
def get_latest_topics(n=5):
    with sqlite3.connect("topics.db") as conn:
        cur = conn.execute("SELECT content FROM topics ORDER BY id DESC LIMIT ?", (n,))
        return [row[0] for row in cur.fetchall()]

# 🌐 Keep Alive Flask Server
token = os.environ["DISCORD_TOKEN"]
keep_alive()
bot.run(token)
