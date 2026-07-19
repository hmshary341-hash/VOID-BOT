import os
import discord
import traceback
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

extensions = [
    "cogs.logs", "cogs.tickets", "cogs.Admin", "cogs.staff_review", 
    "cogs.warnings", "cogs.welcome", "cogs.events", "cogs.moderation", 
    "cogs.rules", "cogs.AutoDivider", "cogs.suggestions", "cogs.anti_raid", 
    "cogs.stats", "cogs.general", "cogs.anti_nuke", "cogs.security", 
    "cogs.giveaway", "cogs.levels"
]

@bot.event
async def on_ready():
    print(f"✅ {bot.user} متصل ويعمل الآن!")

async def load_extensions():
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ تم تحميل: {ext}")
        except Exception as e:
            print(f"❌ فشل تحميل {ext}:")
            traceback.print_exc() # هذا السطر سيطبع سبب الكراش الحقيقي في الـ Logs

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("TOKEN")
        if not token:
            print("❌ خطأ: التوكن غير موجود في الـ Variables!")
            return
        await bot.start(token)

import asyncio
if __name__ == "__main__":
    asyncio.run(main())
