import discord
import os
from discord.ext import commands
from discord import app_commands

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")

ALLOWED_CHANNEL = 1471225787129532641
LOG_CHANNEL_ID = 1471225787129532641

if not TOKEN:
    raise RuntimeError("TOKEN tidak ditemukan di Railway Variables")

# ================= BOT SETUP =================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

tree = bot.tree
user_data = {}

# ================= ERROR HANDLER =================

@bot.event
async def on_command_error(ctx, error):
    print("Command Error:", error)

# ================= CHECK CHANNEL =================

async def check_channel(interaction):
    if interaction.channel_id != ALLOWED_CHANNEL:
        await interaction.response.send_message(
            "❌ Command hanya bisa digunakan di channel CS.",
            ephemeral=True
        )
        return False
    return True

# ================= EMBED PANEL =================

def panel_embed():
    embed = discord.Embed(
        title="📝 Panel Character Story",
        description=(
            "Klik tombol di bawah untuk membuat Character Story\n\n"
            "📌 Step:\n"
            "1️⃣ Pilih Server\n"
            "2️⃣ Pilih Sisi\n"
            "3️⃣ Isi Detail"
        ),
        color=0x5865F2
    )
    return embed

# ================= SERVER SELECT =================

class ServerSelect(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(label="AARP", emoji="🌍"),
            discord.SelectOption(label="SSRP", emoji="🏙"),
            discord.SelectOption(label="VRP", emoji="🚓"),
        ]

        super().__init__(
            placeholder="🌐 Pilih Server",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        user_data[interaction.user.id] = {
            "server": self.values[0]
        }

        embed = discord.Embed(
            title="🎭 Pilih Sisi Karakter",
            color=0x2ecc71
        )

        await interaction.response.send_message(
            embed=embed,
            view=AlignmentView(),
            ephemeral=True
        )

class ServerView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ServerSelect())

# ================= ALIGNMENT =================

class AlignmentView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Sisi Baik", emoji="😇", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_data[interaction.user.id]["side"] = "Good"
        await interaction.response.send_modal(BasicModal())

    @discord.ui.button(label="Sisi Jahat", emoji="😈", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_data[interaction.user.id]["side"] = "Bad"
        await interaction.response.send_modal(BasicModal())

# ================= MODAL 1 =================

class BasicModal(discord.ui.Modal, title="📋 Detail Karakter (1/2)"):

    nama = discord.ui.TextInput(label="👤 Nama")
    level = discord.ui.TextInput(label="⭐ Level")
    gender = discord.ui.TextInput(label="🚻 Gender")
    ttl = discord.ui.TextInput(label="🎂 TTL")
    kota = discord.ui.TextInput(label="🏙 Kota")

    async def on_submit(self, interaction: discord.Interaction):

        data = user_data.get(interaction.user.id, {})

        data.update({
            "nama": self.nama.value,
            "level": self.level.value,
            "gender": self.gender.value,
            "ttl": self.ttl.value,
            "kota": self.kota.value
        })

        user_data[interaction.user.id] = data

        await interaction.response.send_message(
            "✅ Detail tersimpan, lanjut isi cerita.",
            view=NextView(),
            ephemeral=True
        )

# ================= NEXT BUTTON =================

class NextView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Lanjutkan", emoji="➡", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StoryModal())

# ================= MODAL 2 =================

class StoryModal(discord.ui.Modal, title="📖 Detail Cerita (2/2)"):

    skill = discord.ui.TextInput(label="🎯 Skill")
    tambahan = discord.ui.TextInput(
        label="📜 Cerita Tambahan",
        style=discord.TextStyle.paragraph,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

        data = user_data.get(interaction.user.id, {})

        data.update({
            "skill": self.skill.value,
            "tambahan": self.tambahan.value
        })

        embed = discord.Embed(
            title="📄 Character Story",
            color=0x5865F2
        )

        embed.add_field(name="👤 Nama", value=data["nama"])
        embed.add_field(name="⭐ Level", value=data["level"])
        embed.add_field(name="🎭 Sisi", value=data["side"])
        embed.add_field(name="🌐 Server", value=data["server"])
        embed.add_field(name="🎯 Skill", value=data["skill"])

        if data["tambahan"]:
            embed.add_field(
                name="📜 Tambahan",
                value=data["tambahan"],
                inline=False
            )

        embed.set_footer(text=f"Dibuat oleh {interaction.user}")

        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        if log_channel:
            await log_channel.send(embed=embed)

        await interaction.response.send_message(
            "✅ CS berhasil dikirim!",
            ephemeral=True
        )

# ================= MENU VIEW =================

class MenuView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buat CS", emoji="📝", style=discord.ButtonStyle.primary)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="🌐 Pilih Server",
            color=0x5865F2
        )

        await interaction.response.send_message(
            embed=embed,
            view=ServerView(),
            ephemeral=True)

# ================= COMMANDS =================

@tree.command(name="menu", description="Panel CS")
async def menu(interaction: discord.Interaction):

    if not await check_channel(interaction):
        return

    await interaction.response.send_message(
        embed=panel_embed(),
        view=MenuView()
    )

@tree.command(name="status", description="Status bot")
async def status(interaction: discord.Interaction):

    if not await check_channel(interaction):
        return

    embed = discord.Embed(
        title="🤖 Status Bot",
        color=0x2ecc71
    )

    embed.add_field(
        name="📡 Ping",
        value=f"{round(bot.latency * 1000)} ms"
    )

    embed.add_field(
        name="🌍 Server",
        value=len(bot.guilds)
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

# ================= READY =================

@bot.event
async def on_ready():

    try:
        await tree.sync()
        print(f"✅ Bot aktif sebagai {bot.user}")

        # Register persistent views
        bot.add_view(MenuView())
        bot.add_view(ServerView())
        bot.add_view(AlignmentView())
        bot.add_view(NextView())

    except Exception as e:
        print("Sync error:", e)

# ================= RUN =================

bot.run(TOKEN)
