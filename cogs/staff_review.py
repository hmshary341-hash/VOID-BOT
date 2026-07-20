import discord
from discord import app_commands
from discord.ext import commands

PUBLIC_REVIEW_CHANNEL_ID = 1528075992546148544  # روم التقييم العام
ADMIN_LOG_CHANNEL_ID = 1528077108729876620  # روم الإدارة السري
SERVER_LOGO_URL = "https://i.ibb.co/3mN68wM/VOID-Logo.png"

class ReviewModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="إرسال تقييم للإدارة")
        self.staff_name = discord.ui.TextInput(label="اسم الإداري", placeholder="اكتب اسم الإداري المعني هنا...")
        self.rating = discord.ui.TextInput(label="التقييم من 10", placeholder="مثال: 8/10", max_length=5)
        self.feedback = discord.ui.TextInput(label="الملاحظات أو السبب", style=discord.TextStyle.paragraph, placeholder="اكتب رأيك بكل صراحة...")
        self.add_item(self.staff_name); self.add_item(self.rating); self.add_item(self.feedback)

    async def on_submit(self, interaction: discord.Interaction):
        log_channel = interaction.guild.get_channel(ADMIN_LOG_CHANNEL_ID)
        if not log_channel: return await interaction.response.send_message("❌ خطأ بالروم السري", ephemeral=True)
        
        embed = discord.Embed(title="📥 تقييم إداري جديد", color=0x8000FF, timestamp=interaction.created_at)
        embed.set_thumbnail(url=SERVER_LOGO_URL)
        embed.add_field(name="👤 صاحب التقييم:", value=interaction.user.mention, inline=False)
        embed.add_field(name="👮 الإداري المقصود:", value=str(self.staff_name), inline=True)
        embed.add_field(name="⭐ التقييم:", value=str(self.rating), inline=True)
        embed.add_field(name="📝 الملاحظات:", value=str(self.feedback), inline=False)
        
        await log_channel.send(embed=embed)
        await interaction.response.send_message("✅ تم إرسال تقييمك للإدارة العليا بنجاح وبسرية تامة.", ephemeral=True)

class ReviewLaunchView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="اضغط هنا للتقييم", style=discord.ButtonStyle.secondary, emoji="⭐", custom_id="start_review_btn")
    async def start_review(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReviewModal())

class StaffReview(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(ReviewLaunchView())

    # أمر السلاش لإرسال اللوحة يدوياً
    @app_commands.command(name="setup_review", description="إرسال لوحة تقييم الإدارة في القناة الحالية")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_review(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⭐ تقييم الطاقم الإداري", 
            description="مرحباً بك في قسم تقييم الإدارة لـ **VOID**.\n\nيسعدنا سماع آرائكم بكل شفافية وبسرية تامة.\n\n**اضغط على الزر بالأسفل للبدء 👇**", 
            color=0x8000FF
        )
        embed.set_image(url=SERVER_LOGO_URL)
        await interaction.response.send_message("✅ تم إرسال لوحة التقييم بنجاح.", ephemeral=True)
        await interaction.channel.send(embed=embed, view=ReviewLaunchView())

    # هذه الوظيفة تبقى لإرسال اللوحة تلقائياً عند التشغيل (إذا كنت تفضل ذلك)
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ReviewLaunchView())

async def setup(bot): await bot.add_cog(StaffReview(bot))
