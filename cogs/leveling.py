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

--- الإعدادات الأساسية ---

LEVEL_UP_CHANNEL_ID = 1530087509407563797  # آي دي روم إرسال رسائل التلفل
ALLOWED_ROLE_ID = 1529995977203777566     # آي دي الرتبة المسموح لها باستخدام أمر التصفير

--- إعدادات المخزن المؤقت ---

CACHE_DIR = Path("/app/data/image_cache")
CACHE_MAX_AGE_DAYS = 7
REQUEST_COOLDOWN = 1.0

--- رسالة التشجيع عند الترقية ---

LEVEL_UP_ENCOURAGEMENT = "كفو على التفاعل كمل تفاعلك يا فله"

--- إعدادات رتب الألفل ---

LEVEL_ROLES = {
    1: "Bronze",
    5: "Silver",
    10: "Gold",
    15: "Platinum",
    20: "Emerald",
    25: "Sapphire",
    30: "Diamond",
    35: "Crystal",
    40: "Master",
    45: "Elite",
    50: "Champion",
    60: "Legend",
    70: "Mythic",
    80: "Eternal",
}

CARD_BG_URL = "https://i.imgur.com/OWCueg0.png"
FALLBACK_BG_COLOR = (30, 30, 50)
CARD_WIDTH = 800
CARD_HEIGHT = 450

PROGRESS_BAR_WIDTH = 350
PROGRESS_BAR_HEIGHT = 20
PROGRESS_BAR_X = 440
PROGRESS_BAR_Y = 310
PROGRESS_BAR_COLOR = (0, 229, 255)
PROGRESS_BAR_BG_COLOR = (60, 60, 100)
PROGRESS_BAR_BORDER_COLOR = (100, 150, 255)

def create_fallback_background(width: int = CARD_WIDTH, height: int = CARD_HEIGHT) -> bytes:
    try:
        bg = Image.new("RGBA", (width, height), FALLBACK_BG_COLOR)
        draw = ImageDraw.Draw(bg)
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
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.last_request_time = {}

    def get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.png"

    def is_cache_valid(self, cache_path: Path) -> bool:
        if not cache_path.exists():
            return False
        file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return file_age < timedelta(days=CACHE_MAX_AGE_DAYS)

    async def get_image(self, url: str, session: aiohttp.ClientSession, allow_fallback: bool = False) -> bytes:
        cache_path = self.get_cache_path(url)
        if self.is_cache_valid(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    return f.read()
            except Exception:
                pass

        if url in self.last_request_time:
            time_since_last = asyncio.get_event_loop().time() - self.last_request_time[url]
            if time_since_last < REQUEST_COOLDOWN:
                await asyncio.sleep(REQUEST_COOLDOWN - time_since_last)

        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    if allow_fallback:
                        return create_fallback_background()
                    return None
                image_data = await resp.read()
                try:
                    with open(cache_path, "wb") as f:
                        f.write(image_data)
                except Exception:
                    pass
                self.last_request_time[url] = asyncio.get_event_loop().time()
                return image_data
        except Exception:
            if allow_fallback:
                return create_fallback_background()
            return None 

image_cache = ImageCache(CACHE_DIR)

def draw_progress_bar(draw: ImageDraw.ImageDraw, current_xp: int, required_xp: int):
    try:
        current_xp = max(0, min(current_xp, required_xp))
        progress_ratio = current_xp / required_xp if required_xp > 0 else 0
        filled_width = int(PROGRESS_BAR_WIDTH * progress_ratio)

        draw.rectangle(
            [(PROGRESS_BAR_X, PROGRESS_BAR_Y), (PROGRESS_BAR_X + PROGRESS_BAR_WIDTH, PROGRESS_BAR_Y + PROGRESS_BAR_HEIGHT)],
            fill=PROGRESS_BAR_BG_COLOR,
            outline=PROGRESS_BAR_BORDER_COLOR,
            width=2
        )
        if filled_width > 0:
            draw.rectangle(
                [(PROGRESS_BAR_X, PROGRESS_BAR_Y), (PROGRESS_BAR_X + filled_width, PROGRESS_BAR_Y + PROGRESS_BAR_HEIGHT)],
                fill=PROGRESS_BAR_COLOR
            )
        try:
            font_percent = ImageFont.truetype("arial.ttf", 14)
        except:
            font_percent = ImageFont.load_default()
            
        percentage = int(progress_ratio * 100)
        percent_text = f"{percentage}%"
        bbox = draw.textbbox((0, 0), percent_text, font=font_percent)
        text_x = PROGRESS_BAR_X + (PROGRESS_BAR_WIDTH - (bbox[2] - bbox[0])) // 2
        text_y = PROGRESS_BAR_Y + (PROGRESS_BAR_HEIGHT - (bbox[3] - bbox[1])) // 2
        draw.text((text_x, text_y), percent_text, fill=(255, 255, 255), font=font_percent) 
    except Exception as e:
        print(f"❌ خطأ في رسم شريط التقدم: {e}")

async def generate_card(member, xp, level, role_name="Member"):
    try:
        async with aiohttp.ClientSession() as session:
            bg_data = await image_cache.get_image(CARD_BG_URL, session, allow_fallback=True)
            if not bg_data:
                return None
            avatar_url = member.display_avatar.with_format("png").url
            avatar_data = await image_cache.get_image(avatar_url, session, allow_fallback=False)
            if not avatar_data:
                return None

            bg = Image.open(BytesIO(bg_data)).convert("RGBA")
            avatar = Image.open(BytesIO(avatar_data)).convert("RGBA")
            avatar = avatar.resize((230, 230), Image.Resampling.LANCZOS)
            mask = Image.new("L", (230, 230), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 230, 230), fill=255)
            bg.paste(avatar, (115, 135), mask)
            
            draw = ImageDraw.Draw(bg)
            try:
                font_level = ImageFont.truetype("arial.ttf", 65)
                font_text = ImageFont.truetype("arial.ttf", 20)
            except:
                font_level = ImageFont.load_default()
                font_text = ImageFont.load_default()
                
            draw.text((460, 105), str(level), fill=(0, 229, 255), font=font_level)
            next_level_xp = (level + 1) * 100
            draw.text((610, 245), f"{xp} / {next_level_xp} XP", fill=(255, 179, 71), font=font_text)
            draw_progress_bar(draw, xp, next_level_xp)
            draw.text((580, 370), role_name.upper(), fill=(216, 180, 255), font=font_text)
            
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
        # إنشاء مجلد البيانات داخل الـ Volume
        os.makedirs("/app/data", exist_ok=True)

        db_path = "/app/data/levels.db"

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER,
                guild_id INTEGER,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id)
            )
        """)

        self.conn.commit()

        print(f"✅ Database loaded from: {db_path}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        guild_id = message.guild.id
        earned_xp = random.randint(15, 25)

        try:
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
                    card_file = await generate_card(message.author, xp, level, current_role_name)
                    if card_file:
                        await target_channel.send(content=f"{message.author.mention}\n{LEVEL_UP_ENCOURAGEMENT}", file=card_file)
                    else:
                        await target_channel.send(f"🎉 مبروك {message.author.mention}! لقد صعدت للمستوى **{level}**!\n{LEVEL_UP_ENCOURAGEMENT}")
                except Exception as e:
                    print(f"❌ خطأ في إرسال رسالة التلفل: {e}")

            if level in LEVEL_ROLES:
                keyword = LEVEL_ROLES[level].lower()
                new_role = discord.utils.find(lambda r: keyword in r.name.lower(), message.guild.roles)
                if new_role:
                    try:
                        all_keywords = [kw.lower() for kw in LEVEL_ROLES.values()]
                        roles_to_remove = [
                            r for r in message.author.roles 
                            if any(kw in r.name.lower() for kw in all_keywords) and r.id != new_role.id
                        ]
                        if roles_to_remove:
                            await message.author.remove_roles(*roles_to_remove)
                        if new_role not in message.author.roles:
                            await message.author.add_roles(new_role)
                    except Exception as e:
                        print(f"❌ خطأ في تحديث رتب التلفل: {e}")

            self.cursor.execute(
                "UPDATE users SET xp = ?, level = ? WHERE user_id = ? AND guild_id = ?",
                (xp, level, user_id, guild_id),
            )
            self.conn.commit()
        except Exception as e:
            print(f"❌ خطأ في قاعدة البيانات أثناء معالجة الرسالة: {e}") 

    @app_commands.command(name="rank", description="عرض بطاقة مستواك ونقاط الخبرة")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer(ephemeral=True)
        target = member or interaction.user

        self.cursor.execute(
            "SELECT xp, level FROM users WHERE user_id = ? AND guild_id = ?",
            (target.id, interaction.guild.id),
        )
        result = self.cursor.fetchone()
        xp, level = result if result else (0, 0)
        
        current_role_name = "Member"
        for lvl, r_name in sorted(LEVEL_ROLES.items(), reverse=True):
            if level >= lvl:
                current_role_name = r_name
                break
                
        card_file = await generate_card(target, xp, level, current_role_name)
        if card_file:
            await interaction.followup.send(file=card_file, ephemeral=True)
        else:
            await interaction.followup.send("❌ حدث خطأ أثناء إنشاء بطاقة الرانك.", ephemeral=True) 

    @app_commands.command(name="reset_levels", description="تصفير مستويات ونقاط الجميع")
    async def reset_levels(self, interaction: discord.Interaction):
        if not any(r.id == ALLOWED_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message("❌ | عذراً، هذا الأمر مخصص لأصحاب هذه الرتبة فقط!", ephemeral=True)
            return

        self.cursor.execute("DELETE FROM users WHERE guild_id = ?", (interaction.guild.id,))
        self.conn.commit()
        await interaction.response.send_message("🔄 | تم تصفير جميع المستويات والنقاط في السيرفر بنجاح!", ephemeral=True) 

    @app_commands.command(name="clear_cache", description="مسح ذاكرة الصور المؤقتة")
    async def clear_cache(self, interaction: discord.Interaction):
        if not any(r.id == ALLOWED_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message("❌ | عذراً، هذا الأمر مخصص لأصحاب هذه الرتبة فقط!", ephemeral=True)
            return

        try:
            import shutil
            shutil.rmtree(CACHE_DIR)
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            await interaction.response.send_message("🧹 | تم مسح ذاكرة الصور المؤقتة بنجاح!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ | خطأ في مسح الكاش: {e}", ephemeral=True) 

async def setup(bot):
    await bot.add_cog(Leveling(bot))
