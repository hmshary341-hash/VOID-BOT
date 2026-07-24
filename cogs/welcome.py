from io import BytesIO
import aiohttp
import discord
from discord.ext import commands
from PIL import Image, ImageDraw

# --- الإعدادات الأساسية ---
WELCOME_CHANNEL_ID = 1530041963284529262  # آي دي روم الترحيب
GOODBYE_CHANNEL_ID = 1530301291182428250  # آي دي روم المغادرة

# --- روابط الصور الأساسية ---
WELCOME_IMAGE_URL = "https://cdn.discordapp.com/attachments/1529890271582486660/1530304966382714931/file_0000000008888246b4d2751df8b9b359.png?ex=6a65170f&is=6a63c58f&hm=542c5d6cba67078eda564bb07e3a7ac0ea473af1d1bbfe7e826735144ffb5cb5&"
GOODBYE_IMAGE_URL = "https://cdn.discordapp.com/attachments/1529890271582486660/1530305816064950502/file_0000000068548246a1b7a5f97361f560.png?ex=6a6517da&is=6a63c65a&hm=bb8706d4d55bb6448297b6d9277a0879dcff541d2793c84e74b38b7eab778cfe&"

async def create_custom_card(member, bg_url, circle_coords=(65, 65), circle_size=265):
    """وظيفة لدمج صورة بروفايل العضو داخل الدائرة في التصميم"""
    try:
        async with aiohttp.ClientSession() as session:
            # تحميل صورة الخلفية
            async with session.get(bg_url) as resp:
                if resp.status != 200: return None
                bg_data = await resp.read()

            # تحميل صورة بروفايل العضو
            avatar_url = member.display_avatar.with_format("png").url
            async with session.get(avatar_url) as resp:
                if resp.status != 200: return None
                avatar_data = await resp.read()

        # معالجة الصور باستخدام Pillow
        bg = Image.open(BytesIO(bg_data)).convert("RGBA")
        avatar = Image.open(BytesIO(avatar_data)).convert("RGBA")

        # تغيير حجم الأفتار ليطابق حجم الدائرة
        avatar = avatar.resize((circle_size, circle_size), Image.Resampling.LANCZOS)

        # إنشاء قناع دائري لقص الصورة
        mask = Image.new("L", (circle_size, circle_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, circle_size, circle_size), fill=255)

        # لصق الأفتار الدائري فوق الخلفية
        bg.paste(avatar, circle_coords, mask)

        # حفظ النتيجة في ذاكرة مؤقتة
        output = BytesIO()
        bg.save(output, format="PNG")
        output.seek(0)
        return discord.File(output, filename="card.png")
    except Exception as e:
        print(f"❌ خطأ في معالجة بطاقة الترحيب/المغادرة: {e}")
        return None

class WelcomeGoodbye(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- حدث انضمام عضو جديد (الترحيب) ---
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel: return

        card_file = await create_custom_card(member, WELCOME_IMAGE_URL)
        if card_file:
            await channel.send(content=f"مرحبًا بك {member.mention}!", file=card_file)
        else:
            await channel.send(f"مرحبًا بك {member.mention}!")

    # --- حدث مغادرة عضو (وداعاً) ---
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = member.guild.get_channel(GOODBYE_CHANNEL_ID)
        if not channel: return

        card_file = await create_custom_card(member, GOODBYE_IMAGE_URL)
        if card_file:
            await channel.send(file=card_file)
        else:
            await channel.send(f"نشكر لك وجودك معنا **{member.name}**، نتمنى لك التوفيق.")

async def setup(bot):
    await bot.add_cog(WelcomeGoodbye(bot))
