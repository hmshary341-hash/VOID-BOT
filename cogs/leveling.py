import json
import os
import random
import time
import discord
from discord import app_commands
from discord.ext import commands

# --- إعدادات مسار التخزين الدائم (Volume) ---
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)
LEVELS_FILE = os.path.join(DATA_DIR, "levels.json")

# --- آي دي روم المستويات المحدد ---
LEVEL_CHANNEL_ID = 1530087509407563797

# --- ربط المستويات بأسماء الرتب (البحث التلقائي بالاسم) ---
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
    75: "Eternal",
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
    self.cooldowns = {}  # كولداون 60 ثانية

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot or not message.guild:
      return

    user_id = str(message.author.id)
    current_time = time.time()

    # فحص الكولداون (60 ثانية)
    if user_id in self.cooldowns:
      if current_time - self.cooldowns[user_id] < 60:
        return

    self.cooldowns[user_id] = current_time

    data = load_data()
    if user_id not in data:
      data[user_id] = {"xp": 0, "level": 1}

    user_data = data[user_id]
    xp_gain = random.randint(15, 25)
    user_data["xp"] += xp_gain

    current_level = user_data["level"]
    xp_needed = current_level * 200

    # التحقق من الصعود للمستوى الجديد
    if user_data["xp"] >= xp_needed:
      user_data["level"] += 1
      new_level = user_data["level"]
      save_data(data)

      # البحث عن الرتبة وإعطاؤها تلقائياً
      role_name = LEVEL_ROLES.get(new_level, "")
      if role_name:
        role = discord.utils.get(message.guild.roles, name=role_name)
        if role:
          try:
            await message.author.add_roles(role)
          except Exception as e:
            print(f"❌ خطأ في إعطاء الرتبة: {e}")

      # إرسال رسالة التلفيل حصرياً في الروم المحدد
      target_channel = message.guild.get_channel(LEVEL_CHANNEL_ID)
      if target_channel:
        try:
          msg = (
              f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
              f"          🎉  LEVEL UP!  🎉\n"
              f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
              f"أهلاً بك يا {message.author.mention} وصلت للمستوى **{new_level}**! 🔥\n\n"
              f"😂 هههههههههههههههههههههههههههههه\n\n"
              f"🥳 فلة صح؟\n\n"
              f"🚀 قاعد/ة تتطور/ين بسرعة!\n\n"
              f"✨ حلو/ة صح يا عيون بابا. 🫶\n\n"
              f"💬 أقول... كمل تفاعل بيني وبينك.\n\n"
              f"👀 وبيني وبينك...\n"
              f"🛡️ إذا شفت نفسك قدها، قدّم إدارة! 😏🔥\n\n"
              f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
              f"        🌟 استمر... والقادم أفضل! 🌟\n"
              f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
          )
          await target_channel.send(msg)
        except Exception as e:
          print(f"❌ خطأ في إرسال رسالة التلفيل: {e}")
    else:
      save_data(data)

  @app_commands.command(
      name="level", description="معرفة مستواك الحالي وكمية الـ XP"
  )
  @app_commands.describe(member="العضو المراد استعلام مستواه (اختياري)")
  async def level(
      self, interaction: discord.Interaction, member: discord.Member = None
  ):
    await interaction.response.defer(ephemeral=True)
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

    # معرفة الرتبة الحالية للعضو إن وجدت ضمن القائمة
    role_name = "لا يوجد"
    for lvl, r_name in sorted(LEVEL_ROLES.items(), reverse=True):
      if current_level >= lvl:
        role_name = r_name
        break

    await interaction.followup.send(
        f"📊 **مستوى العضو {target.display_name}**:\n"
        f"• المستوى: **{current_level}** 🌟\n"
        f"• الخبرة الحالية: **{current_xp:,} / {xp_needed:,} XP** ⚡\n"
        f"• الرتبة الحالية: **{role_name}** 🛡️",
        ephemeral=True,
    )


async def setup(bot):
  await bot.add_cog(Leveling(bot))
