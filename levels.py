import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import os

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "/app/data/levels.db"

    # تهيئة قاعدة البيانات عند بدء التشغيل
    async def cog_load(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, xp INTEGER, level INTEGER)")
            await db.commit()

    # نظام الـ XP عند إرسال رسالة
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT xp, level FROM users WHERE user_id = ?", (message.author.id,))
            row = await cursor.fetchone()

            if row is None:
                await db.execute("INSERT INTO users (user_id, xp, level) VALUES (?, ?, ?)", (message.author.id, 1, 1))
            else:
                xp, level = row
                new_xp = xp + 1
                new_level = (new_xp // 100) + 1 # كل 100 نقطة لفل
                await db.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (new_xp, new_level, message.author.id))
            await db.commit()

    # أمر الترتيب (Slash Command)
    @app_commands.command(name="top", description="عرض قائمة المتصدرين في السيرفر")
    async def top(self, interaction: discord.Interaction):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id, xp, level FROM users ORDER BY xp DESC LIMIT 10")
            rows = await cursor.fetchall()

        embed = discord.Embed(title="🏆 أفضل نقاط الكتابة", color=discord.Color.gold())
        
        description = ""
        for index, (uid, xp, lvl) in enumerate(rows, start=1):
            user = self.bot.get_user(uid)
            name = user.name if user else f"User {uid}"
            description += f"**#{index}** | @{name} - خبرة: {xp} | مستوى: {lvl}\n"
        
        embed.description = description if description else "لا توجد بيانات بعد."
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Levels(bot))
