import discord
import os
import asyncio
from discord.ext import commands

# إعداد الصلاحيات (Intents) - ضرورية لتشغيل البوت بجميع ميزاته
intents = discord.Intents.all()

# تعريف البوت
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    # هذا اللوب سيحمل كل الملفات الموجودة في مجلد cogs تلقائياً
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✅ تم تحميل: {filename}")
                except Exception as e:
                    print(f"❌ فشل تحميل {filename}: {e}")
    else:
        print("⚠️ مجلد cogs غير موجود!")

async def main():
    # جلب التوكين من إعدادات Railway (Variables)
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في المتغيرات (Variables)!")
        return

    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
