import os
import discord
from discord.ext import commands, tasks
from discord import app_commands

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")

OPF_CHANNEL_ID = 1470767786652340390
VOICE_CHANNEL_ID = 1471285861546070172

# ================= INTENTS =================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

voice_client = None

# ================= READY =================

@bot.event
async def on_ready():

    print(f"Online sebagai {bot.user}")

    try:
        await bot.tree.sync()
        print("Slash command synced")
    except Exception as e:
        print(e)

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

            await voice_client.edit(
                mute=True,
                deafen=True
            )

            print("Voice connected")

        else:

            if not voice_client.is_muted():
                await voice_client.edit(mute=True)

            if not voice_client.is_deafened():
                await voice_client.edit(deafen=True)

    except Exception as e:
        print(e)


# ================= SLASH COMMAND =================

@bot.tree.command(name="join")
async def join(interaction: discord.Interaction):

    global voice_client

    if not interaction.user.voice:

        await interaction.response.send_message(
            "Kamu tidak di voice",
            ephemeral=True
        )
        return

    channel = interaction.user.voice.channel

    try:

        if voice_client is None or not voice_client.is_connected():

            voice_client = await channel.connect()

            await voice_client.edit(
                mute=True,
                deafen=True
            )

            await interaction.response.send_message(
                f"Join {channel.name}"
            )

        else:

            await interaction.response.send_message(
                "Bot sudah di voice",
                ephemeral=True
            )

    except Exception as e:

        await interaction.response.send_message(
            str(e),
            ephemeral=True
        )


@bot.tree.command(name="close")
async def close(interaction: discord.Interaction):

    global voice_client

    if voice_client and voice_client.is_connected():

        await voice_client.disconnect()

        voice_client = None

        await interaction.response.send_message(
            "Voice disconnected"
        )

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


# ================= LUA OPF =================

def obfuscate_lua(code):

    return f"""-- Obfuscated by TTKPJ

local function _TTKPJ_RUN()

{code}

end

_TTKPJ_RUN()
"""


# ================= OPF EVENT =================

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

    input_file = f"input_{file.filename}"
    output_file = f"opf_{file.filename}"

    try:

        await file.save(input_file)

        with open(
            input_file,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            code = f.read()

        obf = obfuscate_lua(code)

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(obf)

        await message.channel.send(
            file=discord.File(output_file)
        )

        try:
            await message.delete()
        except:
            pass

        try:
            os.remove(input_file)
        except:
            pass

        try:
            os.remove(output_file)
        except:
            pass

    except Exception as e:

        print(e)


# ================= START =================

bot.run(TOKEN)
