import os
import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة الملفات
extensions = [
    "cogs.logs", "cogs.tickets", "cogs.Admin", "cogs.staff_review", 
    "cogs.warnings", "cogs.welcome", "cogs.events", "cogs.moderation", 
    "cogs.rules", "cogs.AutoDivider", "cogs.suggestions", "cogs.anti_raid", 
    "cogs.stats", "cogs.general", "cogs.anti_nuke", "cogs.security", 
    "cogs.giveaway", "cogs.levels"
]

async def setup():
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ تم تحميل: {ext}")
        except Exception as e:
            print(f"❌ فشل تحميل {ext}: {e}")

@bot.event
async def on_ready():
    print(f"🔥 {bot.user} يعمل الآن وبانتظار أوامرك!")
    # تنبيه: لا تضع هنا أي كود يقوم بـ load_extension أو reload_extension

async def main():
    async with bot:
        await setup()
        token = os.getenv("TOKEN")
        await bot.start(token)

import asyncio
if __name__ == "__main__":
    asyncio.run(main())
