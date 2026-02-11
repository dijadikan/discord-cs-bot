import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "ISI_TOKEN_KAMU"
ALLOWED_CHANNEL = 1471225787129532641
LOG_CHANNEL_ID = 1471225787129532641

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

user_data = {}

# ================= CHECK CHANNEL =================

async def check_channel(interaction):
    if interaction.channel_id != ALLOWED_CHANNEL:
        await interaction.response.send_message(
            "❌ Command hanya bisa dipakai di channel CS.",
            ephemeral=True
        )
        return False
    return True

# ================= EMBED PANEL =================

def panel_embed():
    return discord.Embed(
        title="📝 Panel Pembuatan Character Story",
        description=(
            "Tekan tombol di bawah untuk membuat **Character Story (CS)**\n\n"
            "📌 **Alur Pembuatan:**\n"
            "1️⃣ Pilih Server\n"
            "2️⃣ Pilih Sisi Cerita\n"
            "3️⃣ Isi Detail Karakter\n\n"
            "✨ Pastikan data diisi dengan benar."
        ),
        color=0x5865F2
    )

# ================= SERVER SELECT =================

class ServerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="AARP", emoji="🌍"),
            discord.SelectOption(label="SSRP", emoji="🏙"),
            discord.SelectOption(label="Virtual RP", emoji="🚓"),
            discord.SelectOption(label="GCRP", emoji="🌆"),
        ]

        super().__init__(
            placeholder="🌐 Pilih Server Tujuan",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        user_data[interaction.user.id] = {
            "server": self.values[0]
        }

        embed = discord.Embed(
            title="🎭 Pilih Sisi Karakter",
            description="Silakan pilih alur cerita karakter kamu.",
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

    @discord.ui.button(label="Sisi Baik", emoji="😇", style=discord.ButtonStyle.success)
    async def good(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_data[interaction.user.id]["side"] = "Good Side"
        await interaction.response.send_modal(BasicModal())

    @discord.ui.button(label="Sisi Jahat", emoji="😈", style=discord.ButtonStyle.danger)
    async def bad(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_data[interaction.user.id]["side"] = "Bad Side"
        await interaction.response.send_modal(BasicModal())

# ================= MODAL 1 =================

class BasicModal(discord.ui.Modal, title="📋 Detail Karakter (1/2)"):

    nama = discord.ui.TextInput(label="👤 Nama Karakter (IC)")
    level = discord.ui.TextInput(label="⭐ Level Karakter")
    gender = discord.ui.TextInput(label="🚻 Jenis Kelamin")
    ttl = discord.ui.TextInput(label="🎂 Tanggal Lahir")
    kota = discord.ui.TextInput(label="🏙 Kota Asal")

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

        embed = discord.Embed(
            title="✅ Detail Dasar Tersimpan",
            description="Tekan tombol di bawah untuk lanjut.",
            color=0x2ecc71
        )

        await interaction.response.send_message(
            embed=embed,
            view=NextView(),
            ephemeral=True
        )

# ================= NEXT BUTTON =================

class NextView(discord.ui.View):

    @discord.ui.button(label="Lanjutkan Detail Cerita", emoji="➡", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StoryModal())

# ================= MODAL 2 =================

class StoryModal(discord.ui.Modal, title="📖 Detail Cerita (2/2)"):

    skill = discord.ui.TextInput(label="🎯 Bakat / Keahlian")
    kultur = discord.ui.TextInput(label="🌏 Kultur / Etnis", required=False)
    tambahan = discord.ui.TextInput(
        label="📜 Detail Tambahan",
        style=discord.TextStyle.paragraph,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

        data = user_data.get(interaction.user.id, {})

        data.update({
            "skill": self.skill.value,
            "kultur": self.kultur.value,
            "tambahan": self.tambahan.value
        })

        embed = discord.Embed(
            title="📄 Character Story Baru",
            color=0x5865F2
        )

        embed.add_field(name="👤 Nama", value=data["nama"], inline=True)
        embed.add_field(name="⭐ Level", value=data["level"], inline=True)
        embed.add_field(name="🎭 Sisi", value=data["side"], inline=True)
        embed.add_field(name="🌐 Server", value=data["server"], inline=True)
        embed.add_field(name="🚻 Gender", value=data["gender"], inline=True)
        embed.add_field(name="🎂 TTL", value=data["ttl"], inline=True)
        embed.add_field(name="🏙 Kota", value=data["kota"], inline=False)
        embed.add_field(name="🎯 Skill", value=data["skill"], inline=False)

        if data["kultur"]:
            embed.add_field(name="🌏 Kultur", value=data["kultur"], inline=False)

        if data["tambahan"]:
            embed.add_field(name="📜 Tambahan", value=data["tambahan"], inline=False)

        embed.set_footer(text=f"Dibuat oleh {interaction.user}")

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await log_channel.send(embed=embed)

        await interaction.response.send_message(
            "✅ Character Story berhasil dikirim!",
            ephemeral=True
        )

# ================= MENU PANEL BUTTON =================

class MenuView(discord.ui.View):

    @discord.ui.button(label="Buat Character Story", emoji="📝", style=discord.ButtonStyle.primary)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="🌐 Pilih Server",
            description="Silakan pilih server tempat karakter kamu bermain.",
            color=0x5865F2
        )

        await interaction.response.send_message(
            embed=embed,
            view=ServerView(),
            ephemeral=True
        )

# ================= COMMANDS =================

@tree.command(name="menu", description="Buka panel CS")
async def menu(interaction: discord.Interaction):

    if not await check_channel(interaction):
        return

    await interaction.response.send_message(
        embed=panel_embed(),
        view=MenuView()
    )

@tree.command(name="status", description="Cek status bot")
async def status(interaction: discord.Interaction):

    if not await check_channel(interaction):
        return

    embed = discord.Embed(
        title="🤖 Status Bot",
        description="Bot aktif dan siap digunakan.",
        color=0x2ecc71
    )

    embed.add_field(name="📡 Ping", value=f"{round(bot.latency * 1000)} ms")
    embed.add_field(name="👥 Server", value=len(bot.guilds))

    await interaction.response.send_message(embed=embed, ephemeral=True)

# ================= READY =================

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot aktif: {bot.user}")

bot.run(TOKEN)
