@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"📩 メッセージ受信：{message.content}")

    # お題を強制投稿（管理者用）
    if message.content == "!topic":
        print("✅ !topic コマンド受信")
        await post_daily_topic(message.channel)
        return

    # お題一覧の表示
    if message.content == "!alltopics":
        print("✅ !alltopics コマンド受信")
        all_topics = db.get_all_topics()
        print(f"🔢 お題件数: {len(all_topics)}")

        if not all_topics:
            await message.channel.send("⚠️ 登録されたお題がありません。")
            return

        embed = discord.Embed(title="🗂 現在登録されているお題一覧",
                              color=discord.Color.blue())
        for i, topic in enumerate(all_topics, 1):
            embed.add_field(name=f"{i}.", value=topic, inline=False)

            # Embedフィールド上限対策（25個まで）
            if i >= 25:
                break

        await message.channel.send(embed=embed)
        return

    # MVP手動集計（スレッド内のみ）
    if message.content == "!mvp" and isinstance(message.channel,
                                                discord.Thread):
        print("✅ !mvp コマンド受信")
        await process_mvp(message.channel)
        return

    # お題を次回に予約
    if message.content.startswith("!yoyaku "):
        print("✅ !yoyaku コマンド受信")
        content = message.content[len("!yoyaku "):].strip()
        if db.topic_exists(content):
            db.reserve_topic(content)
            await message.reply(f"✅ お題『{content}』を次回の候補として予約しました！")
        else:
            await message.reply("⚠️ そのお題は登録されていません。!alltopicsで確認できます。")
        return

    # チケットロールを持つユーザーのテーマ投稿（コマンド不要）
    if message.channel.id == THEME_CHANNEL_ID and TICKET_ROLE_NAME in [
            r.name for r in message.author.roles
    ]:
        print("✅ チケット所持者によるお題投稿を検出")
        db.add_topic(message.content)
        db.reserve_topic(message.content)

        guild = message.guild
        role = discord.utils.get(guild.roles, name=TICKET_ROLE_NAME)
        if role:
            await message.author.remove_roles(role)

        await message.reply("✅ お題を登録＆予約しました！\n🎟 チケットは回収されました。")

        latest_topics = db.get_latest_topics(5)
        embed = discord.Embed(title="🗂 現在のお題一覧（最新5件）",
                              color=discord.Color.blue())
        for i, topic in enumerate(reversed(latest_topics), 1):
            embed.add_field(name=f"{i}.", value=topic, inline=False)
        await message.channel.send(embed=embed)
        return
