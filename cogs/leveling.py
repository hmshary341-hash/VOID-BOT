import io
import json
import os
import random
import time
import aiohttp
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


# --- دالة لتوليد بطاقة المستوى (Rank Card) ---
async def create_rank_card(
    member: discord.Member,
    level: int,
    xp: int,
    xp_needed: int,
    role_name: str,
):
  # إنشاء خلفية البطاقة بحجم 930x280
  card = Image.new("RGBA", (930, 280), (25, 25, 35, 255))
  draw = ImageDraw.Draw(card)

  # رسم إطار خارجي خفيف جمالي
  draw.rounded_rectangle(
      [10, 10, 920, 270],
      radius=20,
      fill=(35, 39, 42, 255),
      outline=(114, 137, 218, 150),
      width=3,
  )

  # جلب صورة البروفايل الخاصة بالعضو
  avatar_url = member.display_avatar.replace(size=256, format="png").url
  try:
    async with aiohttp.ClientSession() as session:
      async with session.get(str(avatar_url)) as resp:
        if resp.status == 200:
          avatar_bytes = await resp.read()
          avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
          avatar = avatar.resize((160, 160))

          # جعل الصورة دائرية
          mask = Image.new("L", (160, 160), 0)
          mask_draw = ImageDraw.Draw(mask)
          mask_draw.ellipse((0, 0, 160, 160), fill=255)

          card.paste(avatar, (45, 60), mask)
  except Exception as e:
    print(f"❌ خطأ في تحميل الأفاتار: {e}")

  # محاولة تحميل خط افتراضي أو استخدام النظام
  try:
    font_large = ImageFont.truetype("arial.ttf", 36)
    font_medium = ImageFont.truetype("arial.ttf", 26)
    font_small = ImageFont.truetype("arial.ttf", 20)
  except:
    font_large = font_medium = font_small = ImageFont.load_default()

  # كتابة اسم العضو والمستوى
  draw.text((230, 65), member.name, fill=(255, 255, 255, 255), font=font_large)

  # حساب النسبة المئوية للـ XP لشريط التقدم
  percent = min(max(xp / xp_needed, 0.0), 1.0)

  # رسم شريط التقدم (Progress Bar)
  bar_x, bar_y, bar_w, bar_h = 230, 160, 630, 32
  draw.rounded_rectangle(
      [bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
      radius=16,
      fill=(50, 55, 65, 255),
  )

  if percent > 0:
    filled_w = int(bar_w * percent)
    draw.rounded_rectangle(
        [bar_x, bar_y, bar_x + filled_w, bar_y + bar_h],
        radius=16,
        fill=(0, 229, 255, 255),
    )

  # كتابة تفاصيل الـ XP والمستوى بجانب الشريط
  xp_text = f"{xp:,} / {xp_needed:,} XP"
  draw.text(
      (
          840 - font_small.getlength(xp_text)
          if hasattr(font_small, "getlength")
          else 750,
          120,
      ),
      xp_text,
      fill=(180, 190, 205, 255),
      font=font_medium,
  )

  level_text = f"LEVEL : {level}"
  draw.text(
      (720, 65), level_text, fill=(0, 229, 255, 255), font=font_large
  )

  if role_name:
    role_text = f"RANK : {role_name}"
    draw.text((230, 215), role_text, fill=(255, 215, 0, 255), font=font_small)

  # حفظ الصورة في الذاكرة لإرسالها عبر ديسكورد
  buffer = io.BytesIO()
  card.save(buffer, format="PNG")
  buffer.seek(0)
  return discord.File(buffer, filename="rank_card.png")


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

      # إرسال بطاقة وتنبيه التلفيل حصرياً في روم المستويات المحددة مع المنشن
      target_channel = message.guild.get_channel(LEVEL_CHANNEL_ID)
      if target_channel:
        try:
          card_file = await create_rank_card(
              message.author,
              new_level,
              user_data["xp"],
              new_level * 200,
              role_name,
          )
          await target_channel.send(
              content=(
                  f"🎉 مبروك يا {message.author.mention}! لقد صعدت إلى المستوى"
                  f" **{new_level}** 🚀"
              ),
              file=card_file,
          )
        except Exception as e:
          print(f"❌ خطأ في إرسال بطاقة التلفيل: {e}")
    else:
      save_data(data)

  @app_commands.command(
      name="level", description="معرفة مستواك الحالي وبطاقة الـ XP الخاصة بك"
  )
  @app_commands.describe(member="العضو المراد استعلام مستواه (اختياري)")
  async def level(
      self, interaction: discord.Interaction, member: discord.Member = None
  ):
    await interaction.response.defer()
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
    role_name = ""
    for lvl, r_name in sorted(LEVEL_ROLES.items(), reverse=True):
      if current_level >= lvl:
        role_name = r_name
        break

    card_file = await create_rank_card(
        target, current_level, current_xp, xp_needed, role_name
    )
    await interaction.followup.send(file=card_file)


async def setup(bot):
  await bot.add_cog(Leveling(bot))
