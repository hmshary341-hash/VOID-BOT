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

# --- رابط خلفية بطاقة الرانك ---
RANK_BG_URL = "https://cdn.discordapp.com/attachments/1529890271582486660/1530310291772936486/file_000000000fcc82469984187e529362ed.png?ex=6a651c05&is=6a63ca85&hm=51ebd4f8b36da10396d71d9db06a61ce5836d6ca7fb1587b41597118795d5387&"


async def generate_rank_card(member, xp, level):
  """وظيفة رسم وتصميم بطاقة الرانك تلقائياً"""
  try:
    async with aiohttp.ClientSession() as session:
      async with session.get(RANK_BG_URL) as resp:
        if resp.status != 200:
          return None
        bg_data = await resp.read()

      avatar_url = member.display_avatar.with_format("png").url
      async with session.get(avatar_url) as resp:
        if resp.status != 200:
          return None
        avatar_data = await resp.read()

    bg = Image.open(BytesIO(bg_data)).convert("RGBA")
    avatar = Image.open(BytesIO(avatar_data)).convert("RGBA")

    avatar_size = 150
    avatar = avatar.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)

    mask = Image.new("L", (avatar_size, avatar_size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)

    bg.paste(avatar, (50, 50), mask)

    draw = ImageDraw.Draw(bg)

    try:
      font_large = ImageFont.truetype("arial.ttf", 36)
      font_small = ImageFont.truetype("arial.ttf", 24)
    except:
      font_large = ImageFont.load_default()
      font_small = ImageFont.load_default()

    next_level_xp = (level + 1) * 100

    draw.text(
        (230, 60), f"{member.display_name}", fill=(255, 255, 255), font=font_large
    )
    draw.text((230, 110), f"Level: {level}", fill=(170, 130, 255), font=font_small)
    draw.text(
        (230, 150),
        f"XP: {xp} / {next_level_xp}",
        fill=(200, 200, 200),
        font=font_small,
    )

    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return discord.File(output, filename="rank.png")
  except Exception as e:
    print(f"❌ خطأ في إنشاء بطاقة الرانك: {e}")
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

        # إرسال رسالة التلفل في الروم المحدد فقط
        target_channel = message.guild.get_channel(LEVEL_UP_CHANNEL_ID)
        if target_channel:
          try:
            remaining_xp = (level + 1) * 100 - xp
            await target_channel.send(
                f"{message.author.mention}\n"
                f"⚡ | لفل جديد! {level}\n"
                f"يا فله، التفاعل حقك رهيب! 🔥\n"
                f"شد حيلك وكمل، القمة تنتظرك. 👑\n"
                f"📊 النقاط المطلوبة للفل التالي: `{remaining_xp} XP`"
            )
          except Exception as e:
            print(f"❌ خطأ في إرسال رسالة التلفل: {e}")

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
              if target_channel:
                await target_channel.send(
                    f"🎁 تم ترقيتك وحصولك على رتبة {new_role.mention} وإزالة"
                    " رتبتك السابقة!"
                )
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

    card_file = await generate_rank_card(target, xp, level)
    if card_file:
      await interaction.followup.send(file=card_file, ephemeral=True)
    else:
      await interaction.followup.send(
          f"❌ حدث خطأ أثناء إنشاء بطاقة الرانك لـ {target.mention}.",
          ephemeral=True,
      )


async def setup(bot):
  await bot.add_cog(Leveling(bot))
