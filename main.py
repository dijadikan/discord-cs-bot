import os
import discord
import asyncio
from discord.ext import commands, tasks

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")

VOICE_CHANNEL_ID = 1471285861546070172

# ================= INTENTS =================

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None

# ================= READY =================

@bot.event
async def on_ready():
    print(f"Online sebagai {bot.user}")
    try:
        await bot.tree.sync()
    except:
        pass
    auto_join_voice.start()

# ================= AUTO JOIN VOICE =================

@tasks.loop(seconds=60)
async def auto_join_voice():
    global voice_client
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        return

    try:
        if voice_client is None or not voice_client.is_connected():
            voice_client = await channel.connect()
            await voice_client.edit(mute=True, deafen=True)
    except:
        pass

# ================= START =================

bot.run(TOKEN)
