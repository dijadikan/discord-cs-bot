import os
import discord
from discord.ext import commands, tasks
from discord import app_commands

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")
OPF_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
VOICE_CHANNEL_ID = 1471285861546070172

# ================= INTENTS =================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None

# ================= VOICE AUTO JOIN =================

@bot.event
async def on_ready():
    print(f"Online sebagai {bot.user}")

    try:
        await bot.tree.sync()
        print("Slash command synced")
    except Exception as e:
        print(e)

    auto_join_voice.start()


@tasks.loop(seconds=60)
async def auto_join_voice():
    global voice_client

    channel = bot.get_channel(VOICE_CHANNEL_ID)

    if channel is None:
        return

    try:
        if voice_client is None or not voice_client.is_connected():
            voice_client = await channel.connect()
            await voice_client.edit(mute=True, deafen=True)
            print("Voice connected")

        elif not voice_client.is_deafened() or not voice_client.is_muted():
            await voice_client.edit(mute=True, deafen=True)

    except Exception as e:
        print(e)


# ================= SLASH COMMAND =================

@bot.tree.command(name="join")
async def join(interaction: discord.Interaction):

    global voice_client

    if interaction.user.voice is None:
        await interaction.response.send_message(
            "Kamu tidak di voice",
            ephemeral=True
        )
        return

    channel = interaction.user.voice.channel

    try:
        if voice_client is None or not voice_client.is_connected():

            voice_client = await channel.connect()
            await voice_client.edit(mute=True, deafen=True)

            await interaction.response.send_message(
                f"Join {channel.name}"
            )

        else:

            await interaction.response.send_message(
                "Bot sudah di voice",
                ephemeral=True
            )

    except Exception as e:
        await interaction.response.send_message(str(e), ephemeral=True)


@bot.tree.command(name="close")
async def close(interaction: discord.Interaction):

    global voice_client

    if voice_client and voice_client.is_connected():

        await voice_client.disconnect()
        voice_client = None

        await interaction.response.send_message("Voice disconnected")

    else:

        await interaction.response.send_message(
            "Bot tidak di voice",
            ephemeral=True
        )


@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):

    latency = round(bot.latency * 1000)

    await interaction.response.send_message(
        f"Pong {latency}ms"
    )


# ================= LUA OBFUSCATOR =================

def obfuscate_lua(code: str) -> str:

    return f"""
-- Obfuscated by TTKPJ

local function _TTKPJ_RUN()

{code}

end

_TTKPJ_RUN()
"""


# ================= OPF SYSTEM =================

@bot.event
async def on_message(message):

    await bot.process_commands(message)

    if message.author.bot:
        return

    if message.channel.id != OPF_CHANNEL_ID:
        return

    if not message.attachments:
        return

    file = message.attachments[0]

    if not file.filename.lower().endswith(".lua"):
        return

    input_path = f"input_{file.filename}"
    output_path = f"opf_{file.filename}"

    try:

        await file.save(input_path)

        with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()

        obf_code = obfuscate_lua(code)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(obf_code)

        await message.channel.send(
            file=discord.File(output_path)
        )

        try:
            await message.delete()
        except:
            pass

        try:
            os.remove(input_path)
        except:
            pass

        try:
            os.remove(output_path)
        except:
            pass

    except Exception as e:
        print(e)


# ================= RUN =================

bot.run(TOKEN)
