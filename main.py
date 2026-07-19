import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env (أو متغيرات Railway)
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعداد الصلاحيات (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ البوت يعمل الآن: {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'🔄 تم مزامنة {len(synced)} أمر.')
    except Exception as e:
        print(f'❌ خطأ في المزامنة: {e}')

async def load_extensions():
    # هذا الجزء يبحث تلقائياً عن أي ملف .py داخل مجلد cogs
    path = './cogs'
    if not os.path.exists(path):
        print(f"⚠️ المجلد {path} غير موجود!")
        return

    for filename in os.listdir(path):
        if filename.endswith('.py') and filename != '__init__.py':
            extension_name = f'cogs.{filename[:-3]}'
            try:
                await bot.load_extension(extension_name)
                print(f'📂 تم تحميل: {extension_name}')
            except Exception as e:
                print(f'❌ فشل تحميل {extension_name}: {e}')

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
