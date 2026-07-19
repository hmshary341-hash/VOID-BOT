import os
import discord
import asyncio
from discord.ext import commands

# 1. تعريف الـ intents والـ bot في البداية
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. قائمة الملفات
extensions = [
    "cogs.logs", "cogs.tickets", "cogs.Admin", "cogs.staff_review", 
    "cogs.warnings", "cogs.welcome", "cogs.events", "cogs.moderation", 
    "cogs.rules", "cogs.AutoDivider", "cogs.suggestions", "cogs.anti_raid", 
    "cogs.stats", "cogs.general", "cogs.anti_nuke", "cogs.security", 
    "cogs.giveaway", "cogs.levels"
]

# 3. دالة التحميل
async def load_all():
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ تم تحميل: {ext}")
        except Exception as e:
            print(f"❌ خطأ في {ext}: {e}")

@bot.event
async def on_ready():
    print(f"🔥 {bot.user} يعمل الآن!")

async def main():
    async with bot:
        await load_all()
        token = os.getenv("TOKEN")
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
