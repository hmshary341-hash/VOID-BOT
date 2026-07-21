import io
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import arabic_reshaper
from bidi.algorithm import get_display

# الإعدادات
WELCOME_CHANNEL_ID = 1527750890952462408  # آي دي قناة الترحيب
LEAVE_CHANNEL_ID = 1527750890952462408    # آي دي قناة المغادرة (يمكنك جعلها نفس القناة أو قناة أخرى)
BACKGROUND_IMAGE_URL = "https://cdn.discordapp.com/attachments/1526978453826699324/1528190964215320778/file_00000000da1c71f4863b28202a995e4e.png"

class WelcomeLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_card(self, member: discord.Member, card_type="welcome"):
        # 1. إنشاء خلفية البطاقة (أبعاد 800×400)
        card = Image.new("RGBA", (800, 400), (20, 20, 25, 255))
        draw = ImageDraw.Draw(card)

        # محاولة جلب الصورة الخلفية
        try:
            async with member.client.http._session.get(BACKGROUND_IMAGE_URL) as resp:
                if resp.status == 200:
                    bg_bytes = await resp.read()
                    bg = Image.open(io.BytesIO(bg_bytes)).convert("RGBA")
                    bg = bg.resize((800, 400))
                    card.paste(bg, (0, 0))
        except Exception:
            pass

        # طبقة تعتيم خفيفة لإبراز النصوص
        overlay = Image.new("RGBA", (800, 400), (0, 0, 0, 160))
        card = Image.alpha_composite(card, overlay)
        draw = ImageDraw.Draw(card)

        # 2. جلب صورة البروفايل وقصها بشكل دائري
        avatar_asset = member.avatar or member.default_avatar
        avatar_bytes = await avatar_asset.read()
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
        avatar = avatar.resize((150, 150))

        mask = Image.new("L", (150, 150), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 150, 150), fill=255)
        
        avatar_masked = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        avatar_masked.putalpha(mask)
        card.paste(avatar_masked, (325, 45), avatar_masked)

        # 3. إعداد الخطوط والنصوص
        try:
            font_large = ImageFont.truetype("arial.ttf", 34)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # تحديد النص بحسب الحالة (دخول أو خروج)
        if card_type == "welcome":
            main_text = "أهلاً بك في السيرفر!"
            text_color = (255, 255, 255, 255)
        else:
            main_text = "لقد غادر السيرفر"
            text_color = (255, 100, 100, 255)

        reshaped_text = arabic_reshaper.reshape(main_text)
        bidi_text = get_display(reshaped_text)
        member_name = f"{member.name}"

        # رسم النصوص في البطاقة
        draw.text((400, 235), bidi_text, font=font_large, fill=text_color, anchor="mm")
        draw.text((400, 285), member_name, font=font_small, fill=(200, 170, 255, 255), anchor="mm")

        # حفظ البطاقة في الذاكرة
        final_buffer = io.BytesIO()
        card.save(final_buffer, format="PNG")
        final_buffer.seek(0)
        return final_buffer

    # --- حدث دخول العضو ---
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        card_file = await self.create_card(member, card_type="welcome")
        file = discord.File(card_file, filename="welcome-card.png")

        embed = discord.Embed(
            title="🎉 عضو جديد انضم إلينا!",
            description=f"مرحباً بك {member.mention} في سيرفر **VOID**.\n\n"
                        f"📌 **يرجى قراءة القوانين جيداً لضمان عدم مخالفتها.**",
            color=discord.Color.dark_purple()
        )
        embed.set_image(url="attachment://welcome-card.png")
        embed.set_footer(text=f"عدد الأعضاء: {len(member.guild.members)}")

        await channel.send(embed=embed, file=file)

    # --- حدث خروج العضو ---
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = member.guild.get_channel(LEAVE_CHANNEL_ID)
        if not channel:
            return

        card_file = await self.create_card(member, card_type="leave")
        file = discord.File(card_file, filename="leave-card.png")

        embed = discord.Embed(
            title="👋 غادر أحد الأعضاء",
            description=f"وداعاً **{member.name}**، نتمنى لك التوفيق!",
            color=discord.Color.red()
        )
        embed.set_image(url="attachment://leave-card.png")

        await channel.send(embed=embed, file=file)

async def setup(bot):
    await bot.add_cog(WelcomeLeave(bot))
