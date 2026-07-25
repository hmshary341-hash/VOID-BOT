from io import BytesIO
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
import random
import sqlite3
import traceback
from PIL import Image, ImageDraw, ImageFont
import os
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import asyncio

# --- الإعدادات الأساسية ---
LEVEL_UP_CHANNEL_ID = 1530087509407563797  # آي دي روم إرسال رسائل التلفل
ALLOWED_ROLE_ID = 1529995977203777566  # آي دي الرتبة المسموح لها باستخدام أمر التصفير

# --- إعدادات المخزن المؤقت ---
CACHE_DIR = Path("/app/data/image_cache")
CACHE_MAX_AGE_DAYS = 7  # إعادة تحميل الصور كل 7 أيام
REQUEST_COOLDOWN = 1.0  # تأخير بين الطلبات (بالثواني) لتجنب 429

# --- رسالة التشجيع عند الترقية ---
LEVEL_UP_ENCOURAGEMENT = "كفو على التفاعل كمل تفاعلك يا فله"

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

# --- رابط بطاقة الرانك الدائم ---
CARD_BG_URL = "https://i.imgur.com/OWCueg0.png"

# --- ألوان الخلفية البديلة (RGB) ---
FALLBACK_BG_COLOR = (30, 30, 50)  # لون أزرق داكن
CARD_WIDTH = 800
CARD_HEIGHT = 450

# --- إعدادات شريط التقدم ---
PROGRESS_BAR_WIDTH = 350
PROGRESS_BAR_HEIGHT = 20
PROGRESS_BAR_X = 440
PROGRESS_BAR_Y = 310
PROGRESS_BAR_COLOR = (0, 229, 255)  # سماوي
PROGRESS_BAR_BG_COLOR = (60, 60, 100)  # رمادي مزرق
PROGRESS_BAR_BORDER_COLOR = (100, 150, 255)  # أزرق فاتح


def create_fallback_background(width: int = CARD_WIDTH, height: int = CARD_HEIGHT) -> bytes:
  """إنشاء خلفية بديلة بسيطة باستخدام لون صلب"""
  try:
    bg = Image.new("RGBA", (width, height), FALLBACK_BG_COLOR)
    
    # إضافة تدرج بسيط للمظهر
    draw = ImageDraw.Draw(bg)
    
    # رسم خطوط زخرفية
    for i in range(0, width, 50):
      draw.line([(i, 0), (i + 20, height)], fill=(100, 100, 150, 80), width=2)
    
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()
  except Exception as e:
    print(f"❌ خطأ في إنشاء الخلفية البديلة: {e}")
    return None


class ImageCache:
  """فئة لإدارة تخزين الصور مؤقتاً ومنع أخطاء 429"""
  
  def __init__(self, cache_dir: Path):
    self.cache_dir = cache_dir
    self.cache_dir.mkdir(parents=True, exist_ok=True)
    self.last_request_time = {}
  
  def get_cache_path(self, url: str) -> Path:
    """الحصول على مسار ملف الكاش لرابط معين"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return self.cache_dir / f"{url_hash}.png"
  
  def is_cache_valid(self, cache_path: Path) -> bool:
    """التحقق من صلاحية الملف المخزن مؤقتاً"""
    if not cache_path.exists():
      return False
    
    file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
    return file_age < timedelta(days=CACHE_MAX_AGE_DAYS)
  
  async def get_image(self, url: str, session: aiohttp.ClientSession, allow_fallback: bool = False) -> bytes:
    """الحصول على الصورة من الكاش أو تحميلها من الإنترنت"""
    cache_path = self.get_cache_path(url)
    
    # إرجاع من الكاش إذا كان صالحاً
    if self.is_cache_valid(cache_path):
      try:
        with open(cache_path, "rb") as f:
          return f.read()
      except Exception as e:
        print(f"⚠️ خطأ في قراءة الكاش: {e}")
    
    # تطبيق cooldown لتجنب 429
    if url in self.last_request_time:
      time_since_last = asyncio.get_event_loop().time() - self.last_request_time[url]
      if time_since_last < REQUEST_COOLDOWN:
        await asyncio.sleep(REQUEST_COOLDOWN - time_since_last)
    
    # تحميل من الإنترنت
    try:
      async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
        if resp.status != 200:
          print(f"⚠️ فشل تحميل الصورة من {url}، كود الاستجابة: {resp.status}")
          
          # إذا كانت الخلفية وسُمح بالبديل، استخدم الخلفية الافتراضية
          if allow_fallback:
            print("ℹ️ استخدام الخلفية البديلة")
            return create_fallback_background()
          return None
        
        image_data = await resp.read()
        
        # حفظ في الكاش
        try:
          with open(cache_path, "wb") as f:
            f.write(image_data)
        except Exception as e:
          print(f"⚠️ فشل حفظ الصورة في الكاش: {e}")
        
        self.last_request_time[url] = asyncio.get_event_loop().time()
        return image_data
    except asyncio.TimeoutError:
      print(f"⚠️ انتهت مهلة الاتصال عند تحميل {url}")
      if allow_fallback:
        print("ℹ️ استخدام الخلفية البديلة")
        return create_fallback_background()
      return None
    except Exception as e:
      print(f"⚠️ خطأ في تحميل الصورة من {url}: {e}")
      if allow_fallback:
        print("ℹ️ استخدام الخلفية البديلة")
        return create_fallback_background()
      return None


# إنشاء مثيل من ImageCache
image_cache = ImageCache(CACHE_DIR)


def draw_progress_bar(draw: ImageDraw.ImageDraw, current_xp: int, required_xp: int):
  """رسم شريط التقدم على البطاقة
  
  Args:
    draw: كائن ImageDraw لرسم العناصر
    current_xp: نقاط الخبرة الحالية
    required_xp: نقاط الخبرة المطلوبة للمستوى التالي
  """
  try:
    # التأكد من أن القيم صحيحة
    current_xp = max(0, min(current_xp, required_xp))
    
    # حساب نسبة التقدم
    progress_ratio = current_xp / required_xp if required_xp > 0 else 0
    filled_width = int(PROGRESS_BAR_WIDTH * progress_ratio)
    
    # رسم الخلفية (الجزء الفارغ)
    draw.rectangle(
      [(PROGRESS_BAR_X, PROGRESS_BAR_Y), 
       (PROGRESS_BAR_X + PROGRESS_BAR_WIDTH, PROGRESS_BAR_Y + PROGRESS_BAR_HEIGHT)],
      fill=PROGRESS_BAR_BG_COLOR,
      outline=PROGRESS_BAR_BORDER_COLOR,
      width=2
    )
    
    # رسم الجزء الممتلئ
    if filled_width > 0:
      draw.rectangle(
        [(PROGRESS_BAR_X, PROGRESS_BAR_Y), 
         (PROGRESS_BAR_X + filled_width, PROGRESS_BAR_Y + PROGRESS_BAR_HEIGHT)],
        fill=PROGRESS_BAR_COLOR
      )
    
    # رسم نسبة مئوية في وسط الشريط
    try:
      font_percent = ImageFont.truetype("arial.ttf", 14)
    except:
      font_percent = ImageFont.load_default()
    
    percentage = int(progress_ratio * 100)
    percent_text = f"{percentage}%"
    
    # حساب موضع النص في منتصف الشريط
    bbox = draw.textbbox((0, 0), percent_text, font=font_percent)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = PROGRESS_BAR_X + (PROGRESS_BAR_WIDTH - text_width) // 2
    text_y = PROGRESS_BAR_Y + (PROGRESS_BAR_HEIGHT - text_height) // 2
    
    # رسم النص بلون متناسب
    text_color = (255, 255, 255)  # أبيض للتباين
    draw.text((text_x, text_y), percent_text, fill=text_color, font=font_percent)
    
  except Exception as e:
    print(f"❌ خطأ في رسم شريط التقدم: {e}")
    traceback.print_exc()


async def generate_card(member, xp, level, role_name="Member"):
  """وظيفة تصميم البطاقة ووضع صورة العضو داخل الإطار الدائري بدقة"""
  try:
    async with aiohttp.ClientSession() as session:
      # تحميل الخلفية من الكاش (مع بديل)
      bg_data = await image_cache.get_image(CARD_BG_URL, session, allow_fallback=True)
      if not bg_data:
        print(f"❌ فشل الحصول على خلفية البطاقة حتى مع البديل")
        return None

      # تحميل صورة بروفايل العضو (بدون بديل - صورة العضو ضرورية)
      avatar_url = member.display_avatar.with_format("png").url
      avatar_data = await image_cache.get_image(avatar_url, session, allow_fallback=False)
      if not avatar_data:
        print(f"❌ فشل تحميل أفتار العضو")
        return None

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

    # إحداثيات مركز الدائرة في البطاقة
    avatar_coords = (115, 135)
    bg.paste(avatar, avatar_coords, mask)

    # رسم النصوص والعناصر
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

    # 3. رسم شريط التقدم
    draw_progress_bar(draw, xp, next_level_xp)

    # 4. كتابة اسم الرتبة
    draw.text((580, 370), f"CYBERNETIC", fill=(216, 180, 255), font=font_text)

    # حفظ الصورة في ذاكرة مؤقتة للإرسال
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return discord.File(output, filename="card.png")
  except Exception as e:
    print(f"❌ خطأ تفصيلي في إنشاء البطاقة:")
    traceback.print_exc()
    return None


def get_role_for_level(level: int) -> str:
  """الحصول على اسم الرتبة المناسبة للمستوى"""
  for lvl in sorted(LEVEL_ROLES.keys(), reverse=True):
    if level >= lvl:
      return LEVEL_ROLES[lvl]
  return "Member"


async def update_member_roles(member: discord.Member, level: int):
  """تحديث رتب العضو تلقائياً بناءً على مستواه
  
  Args:
    member: عضو السيرفر
    level: المستوى الجديد
  """
  try:
    target_role_name = get_role_for_level(level)
    
    # البحث عن الرتبة المستهدفة
    target_role = None
    for role in member.guild.roles:
      if target_role_name.lower() == role.name.lower():
        target_role = role
        break
    
    if not target_role:
      print(f"⚠️ لم يتم العثور على رتبة '{target_role_name}' في السيرفر")
      return
    
    # جمع الرتب ذات الصلة بالألفل التي يمتلكها العضو
    level_role_keywords = [name.lower() for name in LEVEL_ROLES.values()]
    roles_to_remove = []
    
    for role in member.roles:
      role_name_lower = role.name.lower()
      # إزالة أي رتبة ألفل أخرى (باستثناء الرتبة المستهدفة)
      if any(keyword in role_name_lower for keyword in level_role_keywords):
        if role.id != target_role.id:
          roles_to_remove.append(role)
    
    # تطبيق التغييرات
    changes_made = False
    
    if roles_to_remove:
      try:
        await member.remove_roles(*roles_to_remove, reason="Automatic level-based role update")
        print(f"✅ تمت إزالة {len(roles_to_remove)} رتب من {member.name}")
        changes_made = True
      except discord.Forbidden:
        print(f"❌ لا توجد صلاحيات كافية لإزالة الرتب من {member.name}")
        return
      except Exception as e:
        print(f"❌ خطأ في إزالة الرتب: {e}")
        return
    
    # إضافة الرتبة الجديدة إذا لم تكن موجودة
    if target_role not in member.roles:
      try:
        await member.add_roles(target_role, reason="Automatic level-based role assignment")
        print(f"✅ تمت إضافة رتبة '{target_role_name}' إلى {member.name}")
        changes_made = True
      except discord.Forbidden:
        print(f"❌ لا توجد صلاحيات كافية لإضافة رتبة إلى {member.name}")
        return
      except Exception as e:
        print(f"❌ خطأ في إضافة الرتبة: {e}")
        return
    
    if changes_made:
      print(f"✅ تم تحديث رتب {member.name} بنجاح (المستوى: {level})")
  
  except Exception as e:
    print(f"❌ خطأ عام في تحديث الرتب: {e}")
    traceback.print_exc()


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

        # إرسال رسالة التلفل
        target_channel = message.guild.get_channel(LEVEL_UP_CHANNEL_ID)
        if target_channel:
          try:
            card_file = await generate_card(
                message.author, xp, level
            )
            if card_file:
              await target_channel.send(
                  content=f"{message.author.mention}\n{LEVEL_UP_ENCOURAGEMENT}", file=card_file
              )
            else:
              await target_channel.send(
                  f"🎉 مبروك {message.author.mention}! لقد صعدت للمستوى **{level}**!\n{LEVEL_UP_ENCOURAGEMENT}"
              )
          except Exception as e:
            print(f"❌ خطأ في إرسال بطاقة التلفل: {e}")

        # تحديث الرتب بناءً على المستوى الجديد
        try:
          await update_member_roles(message.author, level)
        except Exception as e:
          print(f"❌ خطأ في تحديث الرتب تلقائياً: {e}")
          traceback.print_exc()

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

    card_file = await generate_card(target, xp, level)
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

  @app_commands.command(
      name="clear_cache",
      description="مسح ذاكرة الصور المؤقتة (مخصص لصاحب الرتبة المحددة)",
  )
  async def clear_cache(self, interaction: discord.Interaction):
    if not any(r.id == ALLOWED_ROLE_ID for r in interaction.user.roles):
      await interaction.response.send_message(
          "❌ | عذراً، هذا الأمر مخصص لأصحاب هذه الرتبة فقط!", ephemeral=True
      )
      return

    try:
      import shutil
      shutil.rmtree(CACHE_DIR)
      CACHE_DIR.mkdir(parents=True, exist_ok=True)
      await interaction.response.send_message(
          "🧹 | تم مسح ذاكرة الصور المؤقتة بنجاح!", ephemeral=True
      )
    except Exception as e:
      await interaction.response.send_message(
          f"❌ | خطأ في مسح الكاش: {e}", ephemeral=True
      )


async def setup(bot):
  await bot.add_cog(Leveling(bot))

