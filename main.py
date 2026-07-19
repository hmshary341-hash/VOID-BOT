import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    # تحميل الملفات من مجلد cogs
    await bot.load_extension("cogs.admin")
    await bot.load_extension("cogs.tickets")
    print("✅ تم تحميل الملفات بنجاح!")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🚀 البوت {bot.user} متصل الآن!")

async def main():
    async with bot:
        await load_extensions()
        # هنا سيقرأ التوكن من Variables التي وضعتها في الموقع
        token = os.getenv("TOKEN")
        if not token:
            print("❌ خطأ: لم يتم العثور على التوكن في المتغيرات!")
            return
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
