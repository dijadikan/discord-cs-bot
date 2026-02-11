import os
import discord
from discord.ext import commands
from discord import app_commands
import re

# ===== AMBIL TOKEN ENV DI ATAS =====
TOKEN = os.getenv("TOKEN")  # Pastikan di Railway kamu bikin ENV var "TOKEN"

# ===== INTENTS & BOT =====
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== DEOBFUSCATE LUA =====
def decode_hex_string(s):
    def repl(match):
        try:
            return bytes.fromhex(match.group(1)).decode("utf-8", errors="ignore")
        except:
            return match.group(0)
    return re.sub(r"\\x([0-9a-fA-F]{2})", repl, s)

def deobfuscate_lua(code: str) -> str:
    code = re.sub(r"--\[\[.*?\]\]", "", code, flags=re.DOTALL)
    code = re.sub(r"--.*", "", code)
    code = decode_hex_string(code)
    code = re.sub(r"[ \t]+", " ", code)
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    formatted = ""
    indent = 0
    for line in lines:
        if re.match(r"^\s*(end|elseif|else)", line):
            indent -= 1
        formatted += "  " * max(indent,0) + line + "\n"
        if re.match(r".*(function|then|do)\b", line):
            indent += 1
    return formatted.strip()

# ===== AUTO DETECT FILE UPLOAD =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.attachments:
        for file in message.attachments:
            if file.filename.endswith((".lua", ".luac")):
                await message.channel.send(f"📂 Menerima file `{file.filename}`. Sedang proses deobfuscate...")
                content = await file.read()
                try:
                    decoded = content.decode("utf-8", errors="ignore")
                except:
                    decoded = content.decode("latin-1", errors="ignore")

                deob_code = deobfuscate_lua(decoded)
                output_file = f"deob_{file.filename}"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(deob_code)

                await message.channel.send(f"✅ File `{file.filename}` berhasil deobfuscate:", file=discord.File(output_file))
                os.remove(output_file)
    await bot.process_commands(message)

# ===== SLASH COMMANDS =====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot logged in as {bot.user} ✅")

# /menu
@bot.tree.command(name="menu", description="📖 Lihat panduan penggunaan bot")
async def menu(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛠 Bot Deobfuscate Lua",
        description=(
            "Selamat datang! Berikut panduan penggunaan bot:\n\n"
            "📌 **Commands & fitur:**\n"
            "• `/menu` : Tampilkan panduan bot\n"
            "• `/status` : Cek status bot\n"
            "• Upload file `.lua / .luac` : Bot otomatis deobfuscate\n\n"
            "💡 Cara pakai upload file:\n"
            "1️⃣ User tinggal drag & drop file Lua di channel ini\n"
            "2️⃣ Bot akan otomatis mengirim hasil deobfuscate"
        ),
        color=0x7289da
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# /status
@bot.tree.command(name="status", description="📊 Cek status bot")
async def status(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📊 Status Bot",
        description=(
            f"• Status : ✅ Online\n"
            f"• Username : {bot.user}\n"
            f"• Server : {len(bot.guilds)}\n"
            f"• Total Users : {len(bot.users)}"
        ),
        color=0x1abc9c
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ===== RUN BOT =====
bot.run(TOKEN)
