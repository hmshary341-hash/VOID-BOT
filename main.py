import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# تحميل المتغيرات
load_dotenv()
TOKEN = os.getenv("TOKEN")

# إعداد الصلاحيات
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# دالة تحميل الملفات (مرة واحدة فقط)
async def load_extensions():
    path = './cogs'
    if not os.path.exists(path):
        print(f"⚠️ المجلد {path} غير موجود!")
        return

    # استخدام set لتجنب التكرار إذا كان المجلد يحتوي على ملفات متشابهة
    loaded = set()
    for filename in os.listdir(path):
        if filename.endswith('.py') and filename != '__init__.py':
            extension_name = f'cogs.{filename[:-3]}'
            if extension_name not in loaded:
                try:
                    await bot.load_extension(extension_name)
                    print(f'📂 تم تحميل: {extension_name}')
                    loaded.add(extension_name)
                except Exception as e:
                    print(f'❌ فشل تحميل {extension_name}: {e}')

@bot.event
async def on_ready():
    print(f'✅ البوت يعمل الآن: {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'🔄 تم مزامنة {len(synced)} أمر.')
    except Exception as e:
        print(f'❌ خطأ في المزامنة: {e}')

async def main():
    # هنا يتم التحميل مرة واحدة فقط عند بدء التشغيل
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
