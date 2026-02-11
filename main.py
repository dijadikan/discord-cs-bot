import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio

# Ambil token dari environment variable
TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    print("Error: Token bot tidak ditemukan. Set environment variable TOKEN.")
    exit()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Voice channel khusus
VOICE_CHANNEL_ID = 1471285861546070172
voice_client = None

@bot.event
async def on_ready():
    print(f"Bot siap sebagai {bot.user}")
    try:
        await bot.tree.sync()
        print("Slash commands synced")
    except Exception as e:
        print(f"Gagal sync slash commands: {e}")

    # Mulai loop auto join
    auto_join_voice.start()

# Loop untuk memastikan bot AFK di voice 24/7
@tasks.loop(seconds=60)
async def auto_join_voice():
    global voice_client
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel is None:
        print("Voice channel tidak ditemukan!")
        return

    try:
        if voice_client is None or not voice_client.is_connected():
            voice_client = await channel.connect()
            await voice_client.edit(mute=True, deafen=True)
            print(f"Bot berhasil join {channel.name} dan AFK (mute+deafen)")
        elif not voice_client.is_deafened or not voice_client.is_muted:
            # Pastikan tetap mute+deafen
            await voice_client.edit(mute=True, deafen=True)
    except Exception as e:
        print(f"Error saat join voice: {e}")

# /join - bot join voice channel user
@bot.tree.command(name="join", description="Bot join voice channel kamu")
async def join(interaction: discord.Interaction):
    global voice_client
    if interaction.user.voice is None:
        await interaction.response.send_message("Kamu tidak berada di voice channel!", ephemeral=True)
        return

    channel = interaction.user.voice.channel

    try:
        if voice_client is None or not voice_client.is_connected():
            voice_client = await channel.connect()
            await voice_client.edit(mute=True, deafen=True)
            await interaction.response.send_message(f"✅ Bot berhasil join {channel.name} dan AFK (mute+deafen)")
        else:
            await interaction.response.send_message("Bot sudah berada di voice channel", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error join voice: {e}", ephemeral=True)

# /close - bot disconnect
@bot.tree.command(name="close", description="Bot keluar dari voice channel")
async def close(interaction: discord.Interaction):
    global voice_client
    if voice_client is not None and voice_client.is_connected():
        await voice_client.disconnect()
        voice_client = None
        await interaction.response.send_message("✅ Bot keluar dari voice channel")
    else:
        await interaction.response.send_message("Bot tidak sedang berada di voice channel", ephemeral=True)

# /ping - cek latency bot
@bot.tree.command(name="ping", description="Cek latency bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Latency: {latency}ms")

# Jalankan bot
bot.run(TOKEN)
