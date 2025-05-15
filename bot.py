import db
from datetime import datetime, timedelta
import os
import discord
from discord.ext import tasks

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents=intents)

TOPIC_CHANNEL_ID = int(os.environ["TOPIC_CHANNEL_ID"])
THEME_CHANNEL_ID = int(os.environ["THEME_CHANNEL_ID"])
TICKET_ROLE_NAME = "テーマ追加チケット"

LEVEL_ROLES = [
    "ふぇちのわかり手Lv.1", "ふぇちのわかり手Lv.2", "ふぇちのわかり手Lv.3", "ふぇちのわかり手Lv.4",
    "ふぇちのわかり手Lv.5"
]


@bot.event
async def on_ready():
    try:
        db.init_db()
        channel = bot.get_channel(TOPIC_CHANNEL_ID)
        if channel:
            await channel.send("✅ Botが起動しました！（on_ready）")
            topics = db.get_all_topics()
            reserved = db.get_reserved_theme()
            embed = discord.Embed(title="🗂 起動時のDB状態",
                                  color=discord.Color.green())
            embed.add_field(name="登録お題数", value=str(len(topics)), inline=False)
            embed.add_field(name="予約お題", value=reserved or "なし", inline=False)
            await channel.send(embed=embed)
        schedule_mvp.start()
        schedule_topic.start()
    except Exception as e:
        channel = bot.get_channel(TOPIC_CHANNEL_ID)
        if channel:
            await channel.send(f"❌ 起動エラー: `{e}`")


@tasks.loop(seconds=60)
async def schedule_mvp():
    now = datetime.utcnow() + timedelta(hours=9)
    if now.hour == 8 and now.minute == 59:
        thread_id = db.get_latest_thread_id()
        if thread_id:
            thread = bot.get_channel(thread_id)
            if isinstance(thread, discord.Thread):
                await process_mvp(thread)


@tasks.loop(seconds=60)
async def schedule_topic():
    now = datetime.utcnow() + timedelta(hours=9)
    if now.hour == 9 and now.minute == 0:
        channel = bot.get_channel(TOPIC_CHANNEL_ID)
        await post_daily_topic(channel)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "!topic":
        await post_daily_topic(message.channel)
        return

    if message.content == "!alltopics":
        topics = db.get_all_topics()
        if not topics:
            await message.channel.send("⚠️ お題が登録されていません。")
            return
        for i in range(0, len(topics), 25):
            chunk = topics[i:i + 25]
            embed = discord.Embed(title="🗂 登録済みのお題一覧",
                                  description=f"{i+1} ～ {i+len(chunk)} 件目",
                                  color=discord.Color.blue())
            for j, topic in enumerate(chunk, start=i + 1):
                embed.add_field(name=f"{j}.", value=topic, inline=False)
            await message.channel.send(embed=embed)
        return

    if message.content == "!mvp" and isinstance(message.channel,
                                                discord.Thread):
        await process_mvp(message.channel)
        return

    if message.content.startswith("!yoyaku "):
        topic = message.content.replace("!yoyaku ", "").strip()
        if db.topic_exists(topic):
            if db.reserve_topic(topic):
                await message.reply(f"✅ お題『{topic}』を次回予約しました。")
            else:
                await message.reply(f"⚠️ 『{topic}』はすでに予約済みです。")
        else:
            await message.reply("⚠️ 指定されたお題は存在しません。")
        return

    if message.channel.id == THEME_CHANNEL_ID and TICKET_ROLE_NAME in [
            r.name for r in message.author.roles
    ]:
        db.add_topic(message.content)
        db.reserve_topic(message.content)
        role = discord.utils.get(message.guild.roles, name=TICKET_ROLE_NAME)
        if role:
            await message.author.remove_roles(role)
        await message.reply("✅ お題を登録＆予約しました！\n🎟 チケットは回収されました。")
        latest = db.get_latest_topics(5)
        embed = discord.Embed(title="🗂 最新のお題", color=discord.Color.blue())
        for i, t in enumerate(reversed(latest), 1):
            embed.add_field(name=f"{i}.", value=t, inline=False)
        await message.channel.send(embed=embed)
        return


async def post_daily_topic(channel):
    topic = db.pop_reserved_topic() or db.get_random_topic()
    embed = discord.Embed(title="📌 今日のお題",
                          description=f"『{topic}』",
                          color=discord.Color.purple())
    embed.set_footer(text="語ってみましょう！")
    msg = await channel.send(embed=embed)
    name = f"{datetime.utcnow().strftime('%Y/%m/%d')}【{topic}】"
    if len(name) > 100:
        name = name[:97] + "…"
    thread = await channel.create_thread(name=name,
                                         message=msg,
                                         auto_archive_duration=1440)
    db.set_latest_thread_id(thread.id)


async def process_mvp(thread):
    await thread.send("📊 MVP集計中...")
    counts = {}
    async for msg in thread.history(limit=None):
        c = sum(r.count for r in msg.reactions)
        if c > 0:
            counts[msg.author] = counts.get(msg.author, 0) + c
    if not counts:
        await thread.send("⚠️ MVP候補なし。")
        return
    max_c = max(counts.values())
    winners = [u for u, c in counts.items() if c == max_c]
    for user in winners:
        member = thread.guild.get_member(user.id)
        if not member:
            continue
        level = next((i for i, r in enumerate(LEVEL_ROLES)
                      if any(role.name == r for role in member.roles)), -1)
        next_level = level + 1
        if next_level < len(LEVEL_ROLES):
            if level >= 0:
                old = discord.utils.get(thread.guild.roles,
                                        name=LEVEL_ROLES[level])
                if old: await member.remove_roles(old)
            new = discord.utils.get(thread.guild.roles,
                                    name=LEVEL_ROLES[next_level])
            if new: await member.add_roles(new)
            await thread.send(
                embed=discord.Embed(title="🏆 MVP",
                                    description=f"{member.mention} が昇格！",
                                    color=discord.Color.gold()).add_field(
                                        name="ロール昇格",
                                        value=f"→ {LEVEL_ROLES[next_level]}",
                                        inline=False))
        else:
            ticket = discord.utils.get(thread.guild.roles,
                                       name=TICKET_ROLE_NAME)
            if ticket: await member.add_roles(ticket)
            await thread.send(
                embed=discord.Embed(title="🏆 MVP",
                                    description=f"{member.mention} がチケットを獲得！",
                                    color=discord.Color.gold()).
                add_field(name="🎟 ご褒美", value="→ テーマ追加チケット", inline=False))
    await thread.edit(archived=True, locked=True)


token = os.environ["DISCORD_TOKEN"]
bot.run(token)
