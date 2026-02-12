import os
import discord
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
    print("Bot siap! Gunakan /join atau /close")

# ================= SLASH COMMANDS =================

@bot.tree.command(name="join", description="Bot join ke voice channel")
async def join(interaction: discord.Interaction):
    global voice_client
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("Channel tidak ditemukan!", ephemeral=True)
        return

    if voice_client is None or not voice_client.is_connected():
        voice_client = await channel.connect()
        await voice_client.edit(mute=True, deafen=True)
        await interaction.response.send_message(f"✅ Bergabung ke {channel.name}")
    else:
        await interaction.response.send_message("Bot sudah berada di voice channel!", ephemeral=True)

@bot.tree.command(name="close", description="Bot disconnect dari voice channel")
async def close(interaction: discord.Interaction):
    global voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        voice_client = None
        await interaction.response.send_message("✅ Bot telah disconnect dari voice channel")
    else:
        await interaction.response.send_message("Bot tidak sedang berada di voice channel!", ephemeral=True)

# ================= START =================

bot.run(TOKEN)
