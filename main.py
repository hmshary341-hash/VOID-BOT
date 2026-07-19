import os
import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=bot.intents) # تأكد أن الـ intents معرفة

extensions = [
    "cogs.logs", "cogs.tickets", "cogs.Admin", "cogs.staff_review", 
    "cogs.warnings", "cogs.welcome", "cogs.events", "cogs.moderation", 
    "cogs.rules", "cogs.AutoDivider", "cogs.suggestions", "cogs.anti_raid", 
    "cogs.stats", "cogs.general", "cogs.anti_nuke", "cogs.security", 
    "cogs.giveaway", "cogs.levels"
]

# 1. تعريف وظيفة التحميل "خارج" أي حدث
async def load_all_extensions():
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ تم تحميل: {ext}")
        except Exception as e:
            print(f"❌ فشل تحميل {ext}: {e}")

# 2. الحدث الوحيد للتشغيل
@bot.event
async def on_ready():
    print(f"🔥 {bot.user} متصل ويعمل الآن بكامل طاقته!")

# 3. الوظيفة الأساسية التي تبدأ كل شيء
async def main():
    async with bot:
        print("🚀 جاري تهيئة البوت...")
        await load_all_extensions() # تحميل الملفات مرة واحدة فقط قبل الاتصال
        token = os.getenv("TOKEN")
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
