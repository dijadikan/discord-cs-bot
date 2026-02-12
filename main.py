import os
import discord
import subprocess
import zipfile
from discord import app_commands
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("Error: TOKEN tidak ditemukan")
    exit()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# ID CHANNEL (JANGAN DIUBAH)
# =========================

VOICE_CHANNEL_ID = 1471285861546070172
OBF_CHANNEL_ID = 1470767786652340390

voice_client = None


# =========================
# READY EVENT
# =========================

@bot.event
async def on_ready():

    print(f"Bot siap sebagai {bot.user}")

    try:
        await bot.tree.sync()
        print("Slash commands synced")
    except Exception as e:
        print(e)

    auto_join_voice.start()


# =========================
# AUTO JOIN VOICE 24/7
# =========================

@tasks.loop(seconds=60)
async def auto_join_voice():

    global voice_client

    channel = bot.get_channel(VOICE_CHANNEL_ID)

    if channel is None:
        print("Voice channel tidak ditemukan")
        return

    try:

        if voice_client is None or not voice_client.is_connected():

            voice_client = await channel.connect()
            await voice_client.edit(mute=True, deafen=True)

            print(f"Join voice: {channel.name}")

        elif not voice_client.is_muted or not voice_client.is_deafened:

            await voice_client.edit(mute=True, deafen=True)

    except Exception as e:

        print("Voice error:", e)


# =========================
# AUTO OBFUSCATE LUA
# =========================

@bot.event
async def on_message(message):

    await bot.process_commands(message)

    if message.author.bot:
        return

    if message.channel.id != OBF_CHANNEL_ID:
        return

    if not message.attachments:
        return

    for attachment in message.attachments:

        if not attachment.filename.endswith(".lua"):

            await message.reply("❌ Kirim file .lua saja")
            return

        try:

            await message.reply("⏳ Processing obfuscation...")

            lua_path = f"temp_{attachment.filename}"
            await attachment.save(lua_path)

            luac_path = lua_path.replace(".lua", ".luac")

            # compile lua -> luac
            subprocess.run(
                ["luac", "-o", luac_path, lua_path],
                check=True
            )

            zip_path = luac_path + ".zip"

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(luac_path, os.path.basename(luac_path))

            await message.reply(
                content="✅ Obfuscation berhasil",
                file=discord.File(zip_path)
            )

            # cleanup
            os.remove(lua_path)
            os.remove(luac_path)
            os.remove(zip_path)

        except Exception as e:

            await message.reply(f"❌ Error: {e}")


# =========================
# COMMAND JOIN
# =========================

@bot.tree.command(name="join", description="Join voice kamu")
async def join(interaction: discord.Interaction):

    global voice_client

    if interaction.user.voice is None:

        await interaction.response.send_message(
            "Kamu tidak di voice",
            ephemeral=True
        )
        return

    channel = interaction.user.voice.channel

    if voice_client is None:

        voice_client = await channel.connect()

    else:

        await voice_client.move_to(channel)

    await voice_client.edit(mute=True, deafen=True)

    await interaction.response.send_message(
        f"Join {channel.name}"
    )


# =========================
# COMMAND CLOSE
# =========================

@bot.tree.command(name="close", description="Keluar voice")
async def close(interaction: discord.Interaction):

    global voice_client

    if voice_client:

        await voice_client.disconnect()
        voice_client = None

        await interaction.response.send_message("Keluar voice")

    else:

        await interaction.response.send_message(
            "Tidak di voice",
            ephemeral=True
        )


# =========================
# COMMAND PING
# =========================

@bot.tree.command(name="ping", description="Cek latency")
async def ping(interaction: discord.Interaction):

    latency = round(bot.latency * 1000)

    await interaction.response.send_message(
        f"Pong {latency}ms"
    )


bot.run(TOKEN)
