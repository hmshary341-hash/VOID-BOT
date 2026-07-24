from io import BytesIO
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
import random
import sqlite3
from PIL import Image, ImageDraw, ImageFont

# --- الإعدادات الأساسية ---
LEVEL_UP_CHANNEL_ID = 1530087509407563797  # آي دي روم إرسال رسائل التلفل
ALLOWED_ROLE_ID = 1529995977203777566  # آي دي الرتبة المسموح لها باستخدام أمر التصفير

# --- إعدادات رتب الألفل (بالكلمات المفتاحية الأساسية) ---
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
    70: "Legend",
    85: "Mythic",
    100: "Eternal",
}

# --- رابط بطاقة الرانك الجديدة ---
CARD_BG_URL = "https://cdn.discordapp.com/attachments/1529890271582486660/1530331458055700500/1784929816717.png?ex=6a652fbb&is=6a63de3b&hm=9aeb5f7845e52ac5d08dab6a36a16475d37737976215c00a21fa19a59ad0f33b&"


async def generate_card(member, xp, level, role_name="Member"):
  """وظيفة تصميم البطاقة ووضع صورة العضو داخل الإطار الدائري بدقة"""
  try:
    async with aiohttp.ClientSession() as session:
      # تحميل الخلفية
      async with session.get(CARD_BG_URL) as resp:
        if resp.status != 200:
          return None
        bg_data = await resp.read()

      # تحميل صورة بروفايل العضو
      avatar_url = member.display_avatar.with_format("png").url
      async with session.get(avatar_url) as resp:
        if resp.status != 200:
          return None
        avatar_data = await resp.read()

    # فتح الصور باستخدام Pillow
    bg = Image.open(BytesIO(bg_data)).convert("RGBA")
    avatar = Image.open(BytesIO(avatar_data)).convert("RGBA")

    # حجم وإحداثيات الأفتار لتغطية الدائرة
    avatar_size = 230
    avatar = avatar.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)

    # إنشاء قناع دائري لقص الأفتار
    mask = Image.new("L", (avatar_size, avatar_size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)

    # إحداثيات مركز الدائرة في البطاقة الجديدة
    avatar_coords = (115, 135)
    bg.paste(avatar, avatar_coords, mask)

    # رسم النصوص
    draw = ImageDraw.Draw(bg)

    try:
      font_level = ImageFont.truetype("arial.ttf", 65)
      font_text = ImageFont.truetype("arial.ttf", 20)
    except:
      font_level = ImageFont.load_default()
      font_text = ImageFont.load_default()

    # 1. كتابة رقم اللفل
    level_text = str(level)
    draw.text((460, 105), level_text, fill=(0, 229, 255), font=font_level)

    # 2. كتابة معلومات الـ XP
    next_level_xp = (level + 1) * 100
    xp_text = f"{xp} / {next_level_xp} XP"
    draw.text((610, 245), xp_text, fill=(255, 179, 71), font=font_text)

    # 3. كتابة اسم الرتبة
    draw.text((580, 370), f"CYBERNETIC", fill=(216, 180, 255), font=font_text)

    # حفظ الصورة في ذاكرة مؤقتة للإرسال
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return discord.File(output, filename="card.png")
  except Exception as e:
    print(f"❌ خطأ في إنشاء البطاقة: {e}")
    return None


class Leveling(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.db_setup()

  def db_setup(self):
    self.conn = sqlite3.connect("levels.db")
    self.cursor = self.conn.cursor()
    self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER,
                guild_id INTEGER,
                xp INTEGER,
                level INTEGER,
                PRIMARY KEY (user_id, guild_id)
            )
        """)
    self.conn.commit()

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot or not message.guild:
      return

    user_id = message.author.id
    guild_id = message.guild.id
    earned_xp = random.randint(15, 25)

    self.cursor.execute(
        "SELECT xp, level FROM users WHERE user_id = ? AND guild_id = ?",
        (user_id, guild_id),
    )
    result = self.cursor.fetchone()

    if result is None:
      xp, level = earned_xp, 0
      self.cursor.execute(
          "INSERT INTO users VALUES (?, ?, ?, ?)",
          (user_id, guild_id, xp, level),
      )
    else:
      xp, level = result
      xp += earned_xp
      next_level_xp = (level + 1) * 100

      if xp >= next_level_xp:
        level += 1
        xp -= next_level_xp

        current_role_name = "Member"
        for lvl, r_name in sorted(LEVEL_ROLES.items(), reverse=True):
          if level >= lvl:
            current_role_name = r_name
            break

        target_channel = message.guild.get_channel(LEVEL_UP_CHANNEL_ID)
        if target_channel:
          try:
            card_file = await generate_card(
                message.author, xp, level, current_role_name
            )
            if card_file:
              await target_channel.send(
                  content=f"{message.author.mention}", file=card_file
              )
            else:
              await target_channel.send(
                  f"🎉 مبروك {message.author.mention}! لقد صعدت للمستوى **{level}**!"
              )
          except Exception as e:
            print(f"❌ خطأ في إرسال بطاقة التلفل: {e}")

        if level in LEVEL_ROLES:
          keyword = LEVEL_ROLES[level].lower()
          new_role = None
          for r in message.guild.roles:
            if keyword in r.name.lower():
              new_role = r
              break

          if new_role:
            try:
              roles_to_remove = []
              all_keywords = [kw.lower() for kw in LEVEL_ROLES.values()]
              for r in message.author.roles:
                if any(kw in r.name.lower() for kw in all_keywords):
                  if r.id != new_role.id:
                    roles_to_remove.append(r)

              if roles_to_remove:
                await message.author.remove_roles(*roles_to_remove)

              await message.author.add_roles(new_role)
            except Exception as e:
              print(f"❌ خطأ في تحديث رتب التلفل: {e}")

      self.cursor.execute(
          "UPDATE users SET xp = ?, level = ? WHERE user_id = ? AND guild_id = ?",
          (xp, level, user_id, guild_id),
      )
    self.conn.commit()

  @app_commands.command(name="rank", description="عرض بطاقة مستواك ونقاط الخبرة")
  async def rank(
      self, interaction: discord.Interaction, member: discord.Member = None
  ):
    await interaction.response.defer(ephemeral=True)
    target = member or interaction.user

    self.cursor.execute(
        "SELECT xp, level FROM users WHERE user_id = ? AND guild_id = ?",
        (target.id, interaction.guild.id),
    )
    result = self.cursor.fetchone()

    if result is None:
      xp, level = 0, 0
    else:
      xp, level = result

    current_role_name = "Member"
    for lvl, r_name in sorted(LEVEL_ROLES.items(), reverse=True):
      if level >= lvl:
        current_role_name = r_name
        break

    card_file = await generate_card(target, xp, level, current_role_name)
    if card_file:
      await interaction.followup.send(file=card_file, ephemeral=True)
    else:
      await interaction.followup.send(
          f"❌ حدث خطأ أثناء إنشاء بطاقة الرانك لـ {target.mention}.",
          ephemeral=True,
      )

  @app_commands.command(
      name="reset_levels",
      description="تصفير مستويات ونقاط الجميع (مخصص لصاحب الرتبة المحددة)",
  )
  async def reset_levels(self, interaction: discord.Interaction):
    if not any(r.id == ALLOWED_ROLE_ID for r in interaction.user.roles):
      await interaction.response.send_message(
          "❌ | عذراً، هذا الأمر مخصص لأصحاب هذه الرتبة فقط!", ephemeral=True
      )
      return

    self.cursor.execute(
        "DELETE FROM users WHERE guild_id = ?", (interaction.guild.id,)
    )
    self.conn.commit()
    await interaction.response.send_message(
        "🔄 | تم تصفير جميع المستويات والنقاط في السيرفر بنجاح!", ephemeral=True
    )


async def setup(bot):
  await bot.add_cog(Leveling(bot))
