import os
import discord
import asyncio
import random
import string
from discord.ext import commands, tasks

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")

OPF_CHANNEL_ID = 1470767786652340390
VOICE_CHANNEL_ID = 1471285861546070172

# ================= INTENTS =================

intents = discord.Intents.default()
intents.message_content = True
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

# ================= LUA OBFUSCATOR =================

def random_string(length=12):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def obfuscate_lua(code):
    wrapper_name = random_string()
    junk_var = random_string()

    obf = f"""
-- TTKPJ OBF

local {junk_var} = "{random_string(20)}"

local function {wrapper_name}()

{code}

end

{wrapper_name}()
"""

    return obf

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

    # Kirim animasi loading
    loading = await message.channel.send("⏳ Sedang mengobfuscate file...")

    input_file = f"input_{file.filename}"
    output_file = f"obf_{file.filename}"

    try:
        await file.save(input_file)

        # Simulasi proses biar kelihatan real
        await asyncio.sleep(2)

        with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()

        obf_code = obfuscate_lua(code)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(obf_code)

        await message.channel.send(
            file=discord.File(output_file)
        )

        # Hapus pesan loading
        await loading.delete()

        # Hapus file asli user
        try:
            await message.delete()
        except:
            pass

        # Hapus file temp
        try:
            os.remove(input_file)
        except:
            pass

        try:
            os.remove(output_file)
        except:
            pass

    except Exception as e:
        await loading.edit(content=f"Error: {e}")

# ================= START =================

bot.run(TOKEN)
