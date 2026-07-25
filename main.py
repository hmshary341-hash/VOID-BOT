import discord
import os
import asyncio
from discord.ext import commands
# استيراد كلاسات الـ Views من مجلد cogs
from cogs.tickets import TicketActions, OpenTicketView
from cogs.shop import StoreView  # استيراد فيو المتجر لضمان عمل الأزرار بشكل دائم

# إعداد الصلاحيات (Intents)
intents = discord.Intents.all()

# تعريف البوت
bot = commands.Bot(command_prefix="!", intents=intents)

# إضافة حدث on_ready (يتم تنفيذه عند تشغيل البوت)
@bot.event
async def on_ready():
    # تسجيل الـ Views في ذاكرة البوت لتكون مستمرة (Persistent)
    bot.add_view(TicketActions())
    bot.add_view(OpenTicketView())
    bot.add_view(StoreView())  # تسجيل فيو المتجر الجديد
    
    # مزامنة الأوامر
    await bot.tree.sync()
    
    print(f"✅ تم تسجيل الدخول كـ {bot.user}")
    print(f"✅ تمت مزامنة أوامر السلاش (Slash Commands) بنجاح!")
    print(f"✅ تم تسجيل الـ Persistent Views بنجاح!")

async def load_extensions():
    # تحميل كل الملفات الموجودة في مجلد cogs تلقائياً
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
    # جلب التوكين من إعدادات Railway
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في المتغيرات (Variables)!")
        return

    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
