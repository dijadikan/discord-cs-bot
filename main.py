import os
import discord
from discord.ext import commands
from discord.ui import View, Button, Select, Modal, TextInput
import random

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Temp storage per user untuk side
bot.user_temp = {}

# ====== SERVER SELECTION ======
class ServerSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="SSRP", description="Buat CS untuk server State Side RP."),
            discord.SelectOption(label="Virtual RP", description="Buat CS untuk server Virtual RP."),
            discord.SelectOption(label="AARP", description="Buat CS untuk server Air Asia RP."),
            discord.SelectOption(label="GCRP", description="Buat CS untuk server Grand Country RP."),
            discord.SelectOption(label="TEN ROLEPLAY", description="Buat CS untuk server 10RP."),
            discord.SelectOption(label="CPRP", description="Buat CS untuk server Crystal Pride RP."),
            discord.SelectOption(label="Relative RP", description="Buat CS untuk server Relative RP."),
            discord.SelectOption(label="JGRP", description="Buat CS untuk server JGRP."),
            discord.SelectOption(label="FMRP", description="Buat CS untuk server FAMERLONE RP."),
        ]
        super().__init__(placeholder="Pilih Server Roleplay", options=options)

    async def callback(self, interaction: discord.Interaction):
        bot.user_temp[interaction.user.id] = {"server": self.values[0]}
        embed = discord.Embed(
            title="📌 Pilih Sisi Karakter",
            description="Pilih sisi karakter kamu untuk menentukan cerita Roleplay:\n\n"
                        "😇 Good Side: Karakter yang hidup secara legal dan membantu masyarakat.\n"
                        "😈 Bad Side: Karakter yang hidup di dunia kriminal dan street life.",
            color=0x7289da
        )
        await interaction.response.send_message(embed=embed, view=SideView(), ephemeral=True)

class ServerView(View):
    def __init__(self):
        super().__init__()
        self.add_item(ServerSelect())

# ====== SIDE SELECTION ======
class SideView(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Good Side", style=discord.ButtonStyle.success, emoji="😇")
    async def good_side(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot.user_temp[interaction.user.id]["side"] = "Good Side"
        await interaction.response.send_modal(CharacterModal())

    @discord.ui.button(label="Bad Side", style=discord.ButtonStyle.danger, emoji="😈")
    async def bad_side(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot.user_temp[interaction.user.id]["side"] = "Bad Side"
        await interaction.response.send_modal(CharacterModal())

# ====== CHARACTER MODAL ======
class CharacterModal(Modal):
    def __init__(self):
        super().__init__(title="📝 Buat Character Story")

        self.add_item(TextInput(label="Lengkap Karakter (IC) *",
                               placeholder="Contoh: Tatang, Johan, Ayumi, Ratu_Valencino", required=True, max_length=50))
        self.add_item(TextInput(label="Level Karakter *",
                               placeholder="Contoh: 1", required=True, max_length=5))
        self.add_item(TextInput(label="Jenis Kelamin *",
                               placeholder="Contoh: Laki-laki / Perempuan", required=True, max_length=15))
        self.add_item(TextInput(label="Tanggal Lahir *",
                               placeholder="Contoh: 17 Agustus 1995", required=True, max_length=20))
        self.add_item(TextInput(label="Kota Asal *",
                               placeholder="Contoh: Chicago, Illinois", required=True, max_length=30))
        self.add_item(TextInput(label="Pekerjaan",
                               placeholder="Contoh: Officer / Street Gang Leader / Doctor (opsional)", required=False, max_length=30))

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        side = bot.user_temp[user_id].get("side", "Good Side")

        data = {
            "nama": self.children[0].value,
            "level": self.children[1].value,
            "gender": self.children[2].value,
            "tgl_lahir": self.children[3].value,
            "kota": self.children[4].value,
            "pekerjaan": self.children[5].value if len(self.children) > 5 else "N/A",
            "side": side
        }

        story = generate_long_story(data)

        embed = discord.Embed(
            title="📋 CHARACTER STORY SUBMISSION",
            color=0x1abc9c if side == "Good Side" else 0xe74c3c
        )

        embed.add_field(name="👤 Nama IC", value=data["nama"])
        embed.add_field(name="🎚 Level Karakter", value=data["level"])
        embed.add_field(name="⚧ Jenis Kelamin", value=data["gender"])
        embed.add_field(name="📅 Tanggal Lahir", value=data["tgl_lahir"])
        embed.add_field(name="🏙 Kota Asal", value=data["kota"])
        embed.add_field(name="💼 Pekerjaan", value=data["pekerjaan"])
        embed.add_field(name="📖 Character Story Sudah Dibuat", value=story, inline=False)
        embed.set_footer(text=f"Submitted by {interaction.user}")

        channel = bot.get_channel(1471225787129532641)
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Character Story berhasil dibuat!", ephemeral=True)

# ====== GENERATE STORY PANJANG & UNIK ======
def generate_long_story(data):
    good_extra = [
        "Ia sering terlibat dalam kegiatan sosial dan membimbing generasi muda.",
        "Warga menghormatinya karena integritas dan dedikasinya.",
        "Michael selalu menegakkan keadilan, bahkan dalam situasi sulit.",
        "Ia dikenal bijaksana dan menjadi teladan komunitas.",
        "Setiap tindakan Michael selalu bertujuan untuk kebaikan masyarakat."
    ]

    bad_extra = [
        "Tony menghadapi rival dan konflik antar gank dengan strategi matang.",
        "Pengaruhnya di kota terus bertambah berkat kecerdikannya.",
        "Tony Blaze dikenal berani dan selalu waspada terhadap lawan.",
        "Kehidupannya keras namun penuh perhitungan cermat.",
        "Setiap keputusan Tony selalu mempertimbangkan risiko tinggi."
    ]

    paragraphs = []

    if data["side"] == "Good Side":
        paragraphs.append(
            f"{data['nama']} adalah karakter level {data['level']} yang hidup secara legal dan membantu masyarakat. "
            f"Lahir pada {data['tgl_lahir']} di {data['kota']}, {data['nama']} dikenal disiplin dan bertanggung jawab."
        )
        paragraphs.append(
            f"Sebagai {data['pekerjaan']}, {data['nama']} berperan aktif menjaga keamanan dan kesejahteraan komunitasnya. "
            f"{random.choice(good_extra)} {random.choice(good_extra)}"
        )
        paragraphs.append(
            f"Pengalaman hidup {data['nama']} membentuknya menjadi individu yang dihormati dan menjadi teladan di komunitas. "
            "Karakternya selalu berusaha melakukan kebaikan dan menegakkan keadilan."
        )
    else:
        paragraphs.append(
            f"{data['nama']} hidup di dunia kriminal dan berjuang untuk bertahan di kerasnya kehidupan jalanan. "
            f"Lahir pada {data['tgl_lahir']} di {data['kota']}, {data['nama']} memimpin gank dan mengatur wilayahnya."
        )
        paragraphs.append(
            f"Sebagai {data['pekerjaan']}, {data['nama']} dikenal cerdik dan berani menghadapi lawan. "
            f"{random.choice(bad_extra)} {random.choice(bad_extra)}"
        )
        paragraphs.append(
            "Pengalaman hidup yang keras membentuk karakter kompleks, penuh strategi, keberanian, dan ketahanan. "
            f"{data['nama']} selalu siap menghadapi konsekuensi dari setiap keputusan yang diambil."
        )

    return "\n\n".join(paragraphs)

# ====== COMMAND PANEL ======
@bot.command()
async def cs(ctx):
    if ctx.channel.id != 1471225787129532641:
        await ctx.send("❌ Command hanya bisa digunakan di channel khusus CS!")
        return

    embed = discord.Embed(
        title="📜 CHARACTER STORY REGISTRATION",
        description=(
            "Selamat datang di sistem pembuatan Character Story (CS).\n"
            "CS adalah biodata dan latar belakang karakter Roleplay kamu.\n\n"
            "📌 Tujuan Character Story:\n"
            "• Membentuk identitas karakter RP\n"
            "• Menjelaskan latar belakang kehidupan karakter\n"
            "• Menentukan arah perkembangan story karakter\n\n"
            "🎮 Cara Membuat CS:\n"
            "1️⃣ Klik tombol 'Buat Character Story'\n"
            "2️⃣ Pilih server RP\n"
            "3️⃣ Pilih sisi karakter: Good Side / Bad Side\n"
            "4️⃣ Isi biodata karakter\n"
            "5️⃣ Submit untuk langsung mendapatkan Character Story"
        ),
        color=0x7289da
    )

    view = View()
    view.add_item(Button(label="Buat Character Story", style=discord.ButtonStyle.primary, emoji="📝",
                         custom_id="create_cs"))

    async def button_callback(interaction):
        await interaction.response.send_message("🌍 Silakan pilih server RP:", view=ServerView(), ephemeral=True)

    view.children[0].callback = button_callback
    await ctx.send(embed=embed, view=view)

# ====== RUN BOT ======
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
