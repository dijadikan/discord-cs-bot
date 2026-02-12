import os
import discord
from discord.ext import commands, tasks
import asyncio
import time

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("TOKEN tidak ditemukan!")
    exit()

# intents full supaya stabil
intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    reconnect=True
)

VOICE_CHANNEL_ID = 1471285861546070172
voice_client = None

# =========================
# READY EVENT
# =========================

@bot.event
async def on_ready():
    print(f"✅ Bot online sebagai {bot.user}")

    try:
        await bot.tree.sync()
        print("✅ Slash command synced")
    except Exception as e:
        print(f"Sync error: {e}")

    if not auto_join_voice.is_running():
        auto_join_voice.start()

# =========================
# AUTO JOIN VOICE LOOP
# =========================

@tasks.loop(seconds=60)
async def auto_join_voice():
    global voice_client

    try:
        channel = bot.get_channel(VOICE_CHANNEL_ID)

        if channel is None:
            print("Voice channel tidak ditemukan")
            return

        if voice_client is None or not voice_client.is_connected():
            voice_client = await channel.connect(
                reconnect=True,
                timeout=30
            )

            await voice_client.edit(
                mute=True,
                deafen=True
            )

            print(f"✅ Joined voice: {channel.name}")

        else:
            # pastikan tetap mute + deafen
            if not voice_client.is_muted or not voice_client.is_deafened:
                await voice_client.edit(
                    mute=True,
                    deafen=True
                )

    except Exception as e:
        print(f"Voice error: {e}")
        voice_client = None

# =========================
# SLASH COMMAND JOIN
# =========================

@bot.tree.command(name="join", description="Join voice channel kamu")
async def join(interaction: discord.Interaction):

    global voice_client

    try:

        if interaction.user.voice is None:
            await interaction.response.send_message(
                "Masuk voice channel dulu",
                ephemeral=True
            )
            return

        channel = interaction.user.voice.channel

        if voice_client is None or not voice_client.is_connected():

            voice_client = await channel.connect(
                reconnect=True
            )

            await voice_client.edit(
                mute=True,
                deafen=True
            )

            await interaction.response.send_message(
                f"Joined {channel.name}"
            )

        else:
            await interaction.response.send_message(
                "Bot sudah di voice",
                ephemeral=True
            )

    except Exception as e:
        await interaction.response.send_message(
            f"Error: {e}",
            ephemeral=True
        )

# =========================
# SLASH COMMAND CLOSE
# =========================

@bot.tree.command(name="close", description="Disconnect voice")
async def close(interaction: discord.Interaction):

    global voice_client

    try:

        if voice_client and voice_client.is_connected():

            await voice_client.disconnect()

            voice_client = None

            await interaction.response.send_message(
                "Disconnected"
            )

        else:

            await interaction.response.send_message(
                "Bot tidak di voice",
                ephemeral=True
            )

    except Exception as e:
        await interaction.response.send_message(
            f"Error: {e}",
            ephemeral=True
        )

# =========================
# PING
# =========================

@bot.tree.command(name="ping", description="Cek latency")
async def ping(interaction: discord.Interaction):

    latency = round(bot.latency * 1000)

    await interaction.response.send_message(
        f"Pong: {latency}ms"
    )

# =========================
# SUPER STABLE RUN LOOP
# =========================

while True:

    try:

        print("Starting bot...")

        bot.run(
            TOKEN,
            reconnect=True,
            log_handler=None
        )

    except discord.errors.HTTPException as e:

        print("Rate limited. Tunggu 30 detik...")
        time.sleep(30)

    except Exception as e:

        print(f"Crash detected: {e}")
        print("Restart dalam 15 detik...")
        time.sleep(15)
