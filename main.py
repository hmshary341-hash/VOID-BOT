import discord
import os
import asyncio
from discord.ext import commands

# إعداد الصلاحيات (Intents) - ضرورية لعمل الأحداث (Events) مثل الترحيب
intents = discord.Intents.all()

# تعريف البوت
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    # هذا اللوب سيحمل كل الملفات الموجودة في مجلد cogs فقط
    # طالما أنك حذفت الملفات المشبوهة، البوت لن يحملها ولن يسبب خطأ
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ تم تحميل: {filename}")
            except Exception as e:
                print(f"❌ فشل تحميل {filename}: {e}")

async def main():
    async with bot:
        await load_extensions()
        # ضع التوكين الخاص بك هنا (أو استخدم secrets في Railway)
        await bot.start('ضع_التوكين_الخاص_ببوتك_هنا')

if __name__ == '__main__':
    asyncio.run(main())
