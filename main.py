import os
import discord
from discord.ext import commands
from discord import ui
import zipfile
import random

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1470767786652340390  # Channel khusus
MAX_SIZE = 3 * 1024 * 1024  # 3MB

# ================= BOT SETUP =================
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= READY =================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot online sebagai {bot.user}")

# ================= STATUS =================
@bot.tree.command(name="status", description="📊 Lihat status bot obfuscation")
async def status(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛡️ Status Bot Obfuscation",
        color=0x3498db
    )
    embed.add_field(name="🔹 Status", value="✅ Online", inline=True)
    embed.add_field(name="🔹 Channel Obfuscate", value=f"<#{CHANNEL_ID}>", inline=True)
    embed.add_field(name="🔹 Sistem", value="Obfuscation Lua", inline=True)
    embed.set_footer(text="Lua Obfuscator Bot 🔐")
    await interaction.response.send_message(embed=embed)

# ================= MENU =================
@bot.tree.command(name="menu", description="📖 Menu bantuan bot obfuscation")
async def menu(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 Menu Bot Obfuscation",
        description=f"Upload file `.lua` / `.luac` / `.zip` di <#{CHANNEL_ID}> kemudian pilih tingkat obfuscation menggunakan tombol di bawah.",
        color=0x9b59b6
    )
    embed.add_field(
        name="📌 Cara Pakai",
        value="1️⃣ Upload file di channel\n2️⃣ Klik tombol `Low`, `Medium`, atau `Hard`\n3️⃣ Bot akan mengirim hasil obfuscate",
        inline=False
    )
    embed.set_footer(text="Lua Obfuscator Bot 🔐")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ================= SIMPLE OBFUSCATOR =================
def obfuscate_lua(content: str, level: str) -> str:
    """
    Obfuscate sederhana berdasarkan level:
    Low: gampang dibaca
    Medium: agak sulit dibaca
    Hard: sulit dibaca, random variabel + komentar
    """
    lines = content.splitlines()
    ob_lines = []
    var_count = 1
    var_map = {}
    for line in lines:
        words = line.split()
        for i, w in enumerate(words):
            if w.isidentifier() and len(w) > 1:
                if w not in var_map:
                    var_map[w] = f"v{var_count}"
                    var_count += 1
                words[i] = var_map[w]
        ob_lines.append(" ".join(words))

    if level == "Low":
        ob_content = "\n".join(ob_lines)
    elif level == "Medium":
        ob_content = "\n".join(["  " * random.randint(0,2) + l for l in ob_lines])
    elif level == "Hard":
        ob_content = "\n".join(["  " * random.randint(0,3) + l + f" --{random.randint(1000,9999)}" for l in ob_lines])
    else:
        ob_content = "\n".join(ob_lines)
    return ob_content

# ================= UI BUTTONS =================
class ObfButtons(ui.View):
    def __init__(self, temp_file, filename, is_zip):
        super().__init__(timeout=None)
        self.temp_file = temp_file
        self.filename = filename
        self.is_zip = is_zip

    @ui.button(label="Low 🟢", style=discord.ButtonStyle.green)
    async def low(self, interaction: discord.Interaction, button: ui.Button):
        await self.process_obf(interaction, "Low")

    @ui.button(label="Medium 🟡", style=discord.ButtonStyle.blurple)
    async def medium(self, interaction: discord.Interaction, button: ui.Button):
        await self.process_obf(interaction, "Medium")

    @ui.button(label="Hard 🔴", style=discord.ButtonStyle.red)
    async def hard(self, interaction: discord.Interaction, button: ui.Button):
        await self.process_obf(interaction, "Hard")

    async def process_obf(self, interaction, level):
        output_file = f"obf_{self.filename}"
        # Process file
        if self.is_zip:
            with zipfile.ZipFile(self.temp_file, "r") as z:
                with zipfile.ZipFile(output_file, "w") as new_z:
                    for name in z.namelist():
                        if name.endswith((".lua", ".luac")):
                            data = z.read(name).decode(errors="ignore")
                            ob_data = obfuscate_lua(data, level)
                            new_z.writestr(name, ob_data)
                        else:
                            new_z.writestr(name, z.read(name))
        else:
            with open(self.temp_file, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read()
            ob_data = obfuscate_lua(data, level)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(ob_data)

        await interaction.response.send_message(
            f"✅ File `{self.filename}` berhasil diobfuscate (Level {level})", 
            file=discord.File(output_file)
        )
        import os
        os.remove(self.temp_file)
        os.remove(output_file)
        self.stop()

# ================= AUTO DETECT UPLOAD =================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.id != CHANNEL_ID:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.size > MAX_SIZE:
                await message.channel.send(f"⚠️ File `{attachment.filename}` terlalu besar (>3MB).")
                return

            filename = attachment.filename.lower()
            temp = f"temp_{filename}"
            await attachment.save(temp)
            is_zip = filename.endswith(".zip")

            # Kirim tombol pilih level
            view = ObfButtons(temp, filename, is_zip)
            embed = discord.Embed(
                title="🛠️ Pilih tingkat obfuscation",
                description="Klik tombol sesuai tingkat obfuscation yang diinginkan:",
                color=0x00bfff
            )
            embed.add_field(name="🟢 Low", value="📖 Tingkat gampang dibaca", inline=False)
            embed.add_field(name="🟡 Medium", value="🔐 Tingkat sedang, agak sulit dibaca", inline=False)
            embed.add_field(name="🔴 Hard", value="💀 Tingkat sulit dibaca, variabel & komentar diacak", inline=False)

            await message.channel.send(embed=embed, view=view)

    await bot.process_commands(message)

# ===== RUN BOT =====
bot.run(TOKEN)
