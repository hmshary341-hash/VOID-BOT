from io import BytesIO
import aiohttp
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

# --- الإعدادات الأساسية ---
WELCOME_CHANNEL_ID = 1530041963284529262  # آي دي روم الترحيب
GOODBYE_CHANNEL_ID = 1530301291182428250  # آي دي روم المغادرة

# --- روابط الصور الأساسية ---
WELCOME_IMAGE_URL = "https://cdn.discordapp.com/attachments/1529890271582486660/1530440858682265673/file_00000000393c81f4ae6ad623b7992a65.png?ex=6a65959e&is=6a64441e&hm=b86e603acee64fccf17340ebc03769b2e6f8aea895405a6120ddd3fc14bbc0d4&"
GOODBYE_IMAGE_URL = "https://cdn.discordapp.com/attachments/1529890271582486660/1530441184357646537/file_000000000cf08246ade14eaafd6f1730.png?ex=6a6595ec&is=6a64446c&hm=986edbf06b770b47e04278620b02489aa35b81c2cc1a7513e8c8aff37096b9c6&"

# --- إعدادات الترحيب ---
WELCOME_CIRCLE_COORDS = (45, 40)    # موضع الأفتار (X, Y)
WELCOME_CIRCLE_SIZE = 180           # حجم دائرة الأفتار
WELCOME_TEXT_COORDS = (240, 95)     # موضع اسم المستخدم بعد التكبير (X, Y)

# --- إعدادات المغادرة ---
GOODBYE_CIRCLE_COORDS = (45, 40)    # موضع الأفتار (X, Y)
GOODBYE_CIRCLE_SIZE = 180           # حجم دائرة الأفتار
GOODBYE_TEXT_COORDS = (240, 95)     # موضع اسم المستخدم بعد التكبير (X, Y)

async def create_custom_card(member, bg_url, circle_coords, circle_size, text_to_draw, text_coords):
    """وظيفة لدمج صورة بروفايل العضو وكتابة اسمه بخط كبير داخل التصميم"""
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

        # تغيير حجم الأفتار ليطابق الإطار
        avatar = avatar.resize((circle_size, circle_size), Image.Resampling.LANCZOS)

        # إنشاء قناع دائري لقص الصورة
        mask = Image.new("L", (circle_size, circle_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, circle_size, circle_size), fill=255)

        # لصق الأفتار الدائري فوق الخلفية
        bg.paste(avatar, circle_coords, mask)

        # كتابة اسم المستخدم على الصورة بخط كبير واضح
        draw = ImageDraw.Draw(bg)
        try:
            # تم زيادة حجم الخط إلى 55 ليكون واضحاً وكبيراً
            font = ImageFont.truetype("arial.ttf", 55)
        except IOError:
            font = ImageFont.load_default()

        # رسم النص باللون الأبيض
        draw.text(text_coords, text_to_draw, fill=(255, 255, 255, 255), font=font)

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

        card_file = await create_custom_card(
            member, 
            WELCOME_IMAGE_URL, 
            WELCOME_CIRCLE_COORDS, 
            WELCOME_CIRCLE_SIZE, 
            member.name, 
            WELCOME_TEXT_COORDS
        )
        
        if card_file:
            await channel.send(file=card_file)
        else:
            await channel.send(f"مرحبًا بك {member.mention}!")

    # --- حدث مغادرة عضو (وداعاً) ---
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = member.guild.get_channel(GOODBYE_CHANNEL_ID)
        if not channel: return

        card_file = await create_custom_card(
            member, 
            GOODBYE_IMAGE_URL, 
            GOODBYE_CIRCLE_COORDS, 
            GOODBYE_CIRCLE_SIZE, 
            member.name, 
            GOODBYE_TEXT_COORDS
        )
        
        if card_file:
            await channel.send(file=card_file)
        else:
            await channel.send(f"نشكر لك وجودك معنا **{member.name}**، نتمنى لك التوفيق.")

async def setup(bot):
    await bot.add_cog(WelcomeGoodbye(bot))
