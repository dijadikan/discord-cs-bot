import os
import discord
from discord.ext import commands, tasks
import subprocess
import zipfile
import tempfile
import shutil

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")

VOICE_CHANNEL_ID = 1471285861546070172
CHANNEL_ID = 1470767786652340390

# ================= INTENTS =================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None


# ================= READY =================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        await bot.tree.sync()
    except Exception as e:
        print("Slash sync error:", e)

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
            print("Joined voice channel")
    except Exception as e:
        print("Voice error:", e)


# ================= AUTO OBF LUA =================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.id != CHANNEL_ID:
        return

    if not message.attachments:
        return

    attachment = message.attachments[0]

    if not attachment.filename.endswith(".lua"):
        await message.reply("Kirim file .lua saja")
        return

    await message.reply("Processing...")

    temp_dir = tempfile.mkdtemp()

    try:
        lua_path = os.path.join(temp_dir, attachment.filename)
        luac_path = lua_path + "c"
        zip_path = os.path.join(temp_dir, attachment.filename.replace(".lua", ".zip"))

        await attachment.save(lua_path)

        subprocess.run(
            ["luac", "-o", luac_path, lua_path],
            check=True
        )

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(luac_path, os.path.basename(luac_path))

        await message.reply(file=discord.File(zip_path))

    except Exception as e:
        await message.reply(f"Error: {e}")

    finally:
        shutil.rmtree(temp_dir)


# ================= SLASH COMMANDS =================

@bot.tree.command(name="ping", description="Ping bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Pong {round(bot.latency * 1000)}ms"
    )


@bot.tree.command(name="join", description="Join voice channel kamu")
async def join(interaction: discord.Interaction):
    global voice_client

    if not interaction.user.voice:
        await interaction.response.send_message("Masuk voice dulu")
        return

    channel = interaction.user.voice.channel

    voice_client = await channel.connect()
    await voice_client.edit(mute=True, deafen=True)

    await interaction.response.send_message("Joined")


@bot.tree.command(name="close", description="Keluar voice")
async def close(interaction: discord.Interaction):
    global voice_client

    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await interaction.response.send_message("Disconnected")
    else:
        await interaction.response.send_message("Tidak di voice")


# ================= RUN =================

bot.run(TOKEN)
