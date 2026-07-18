import discord
from discord.ext import commands

# آيدي الروم العام (اللي يشوفونه الأعضاء ويضغطون الزر فيه)
PUBLIC_REVIEW_CHANNEL_ID = 1528075992546148544  

# آيدي الروم السري (الخاص بالإدارة العليا اللي توصله التقييمات)
ADMIN_LOG_CHANNEL_ID = 1528077108729876620  

# لوقو سيرفرك الفخم
SERVER_LOGO_URL = "https://i.ibb.co/3mN68wM/VOID-Logo.png"

class ReviewModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="إرسال تقييم للإدارة")

        self.staff_name = discord.ui.TextInput(
            label="اسم الإداري",
            placeholder="اكتب اسم الإداري المعني هنا...",
            required=True
        )

        self.rating = discord.ui.TextInput(
            label="التقييم من 10",
            placeholder="مثال: 8/10",
            max_length=5,
            required=True
        )

        self.feedback = discord.ui.TextInput(
            label="الملاحظات أو السبب",
            style=discord.TextStyle.paragraph,
            placeholder="اكتب رأيك بكل صراحة أو اذكر الموقف...",
            required=True
        )

        self.add_item(self.staff_name)
        self.add_item(self.rating)
        self.add_item(self.feedback)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        log_channel = guild.get_channel(ADMIN_LOG_CHANNEL_ID)

        if not log_channel:
            return await interaction.response.send_message("❌ خطأ: لم يتم العثور على روم تسجيل التقييمات السري، تواصل مع المطور.", ephemeral=True)

        # إنشاء إمبيد التقييم الذي سيصل للإدارة
        embed = discord.Embed(
            title="📥 تقييم إداري جديد",
            color=0x8000FF,
            timestamp=interaction.created_at
        )
        embed.set_thumbnail(url=SERVER_LOGO_URL)
        embed.add_field(name="👤 صاحب التقييم:", value=f"{interaction.user.mention} ({interaction.user.name})", inline=False)
        embed.add_field(name="👮 الإداري المقصود:", value=str(self.staff_name), inline=True)
        embed.add_field(name="⭐ التقييم:", value=str(self.rating), inline=True)
        embed.add_field(name="📝 التفاصيل والملاحظات:", value=str(self.feedback), inline=False)
        embed.set_footer(text=f"ID المستخدم: {interaction.user.id}")

        await log_channel.send(embed=embed)
        await interaction.response.send_message("✅ شكراً لك! تم إرسال تقييمك للإدارة العليا بنجاح وبسرية تامة.", ephemeral=True)


class ReviewLaunchView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="اضغط هنا للتقييم", style=discord.ButtonStyle.secondary, emoji="⭐", custom_id="start_review_btn")
    async def start_review(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReviewModal())


class StaffReview(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ كوج تقييم الإدارة جاهز ويعمل بنجاح!")
        
        # ربط الأزرار بشكل دائم عشان تشتغل حتى بعد رستارت البوت
        self.bot.add_view(ReviewLaunchView())
        
        # إرسال رسالة التقييم تلقائياً في الروم العام عند تشغيل البوت إذا كان الروم فاضي
        channel = self.bot.get_channel(PUBLIC_REVIEW_CHANNEL_ID)
        if channel:
            # نتأكد إذا البوت قد أرسل الرسالة سابقاً عشان ما يكررها
            async for message in channel.history(limit=5):
                if message.author == self.bot.user:
                    return 
            
            # إذا الروم ما فيه رسالة البوت، يرسلها الحين:
            embed = discord.Embed(
                title="⭐ تقييم الطاقم الإداري",
                description=(
                    "مرحباً بك في قسم تقييم الإدارة لـ **VOID**.\n\n"
                    "حرصاً منا على تطوير السيرفر وتقديم أفضل تجربة لكم، "
                    "يسعدنا سماع آرائكم وتقييمكم لأداء أعضاء الإدارة بكل شفافية وبسرية تامة.\n\n"
                    "**اضغط على الزر بالأسفل للبدء 👇**"
                ),
                color=0x8000FF
            )
            embed.set_image(url=SERVER_LOGO_URL)
            await channel.send(embed=embed, view=ReviewLaunchView())


async def setup(bot):
    await bot.add_cog(StaffReview(bot))
