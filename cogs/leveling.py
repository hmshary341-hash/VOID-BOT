import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import time

# --- إعدادات مسار التخزين الدائم (Volume) ---
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)
LEVELS_FILE = os.path.join(DATA_DIR, "levels.json")

# --- ربط المستويات بأسماء الرتب تماماً كما هي في سيرفرك (يبحث عنها البوت بالاسم تلقائياً) ---
LEVEL_ROLES = {
    5: "Bronze",
    10: "Silver",
    15: "Gold",
    20: "Platinum",
    25: "Emerald",
    30: "Sapphire",
    35: "Ruby",
    40: "Diamond",
    45: "Crystal",
    50: "Master",
    55: "Elite",
    60: "Champion",
    65: "Legend",
    70: "Mythic",
    75: "Eternal"
}

def load_data():
    if not os.path.exists(LEVELS_FILE):
        return {}
    try:
        with open(LEVELS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data):
    with open(LEVELS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}  # لتخزين وقت آخر رسالة لكل عضو (كولداون 60 ثانية)

    @commands.Cog.listener()
    async def on_message(self, message):
        # تجاهل بوتات السيرفر والرسائل الخاصة
        if message.author.bot or not message.guild:
            return

        user_id = str(message.author.id)
        current_time = time.time()

        # فحص الكولداون (60 ثانية)
        if user_id in self.cooldowns:
            if current_time - self.cooldowns[user_id] < 60:
                return  # لم تنتهِ الـ 60 ثانية، تجاهل احتساب الـ XP

        # تحديث وقت آخر رسالة صحيحة تم احتساب نقاط لها
        self.cooldowns[user_id] = current_time

        data = load_data()
        if user_id not in data:
            data[user_id] = {"xp": 0, "level": 1}

        user_data = data[user_id]
        
        # كسب نقاط XP عشوائية (بين 15 و 25 نقطة)
        xp_gain = random.randint(15, 25)
        user_data["xp"] += xp_gain

        # معادلة حساب الـ XP المطلوبة للمستوى التالي (المستوى الحالي * 200)
        current_level = user_data["level"]
        xp_needed = current_level * 200

        # التحقق مما إذا دخل مستوى جديداً فعلياً
        if user_data["xp"] >= xp_needed:
            user_data["level"] += 1
            new_level = user_data["level"]
            save_data(data)

            # البحث عن الرتبة وإعطاؤها تلقائياً بالاسم
            role_msg = ""
            if new_level in LEVEL_ROLES:
                role_name = LEVEL_ROLES[new_level]
                role = discord.utils.get(message.guild.roles, name=role_name)
                if role:
                    try:
                        await message.author.add_roles(role)
                        role_msg = f"\n🎁 وحصلت على رتبة: **{role.name}**!"
                    except Exception as e:
                        print(f"❌ خطأ في إعطاء رتبة المستوى: {e}")

            # المنشن ورسالة الصعود للمستوى الجديد فقط
            try:
                await message.channel.send(
                    f"🎉 مبروك يا {message.author.mention}! لقد صعدت إلى المستوى **{new_level}** 🚀{role_msg}"
                )
            except Exception as e:
                print(f"❌ خطأ في إرسال رسالة التلفيل: {e}")
        else:
            save_data(data)

    @app_commands.command(name="level", description="معرفة مستواك الحالي ونقاط الـ XP")
    @app_commands.describe(member="العضو المراد استعلام مستواه (اختياري)")
    async def level(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        user_id = str(target.id)

        data = load_data()
        if user_id not in data:
            current_xp = 0
            current_level = 1
        else:
            current_xp = data[user_id].get("xp", 0)
            current_level = data[user_id].get("level", 1)

        xp_needed = current_level * 200

        embed = discord.Embed(
            title=f"📊 رتبة ومستوى: {target.name}",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="✨ المستوى الحالي", value=str(current_level), inline=True)
        embed.add_field(name="⭐ نقاط الـ XP", value=f"{current_xp:,} / {xp_needed:,}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
