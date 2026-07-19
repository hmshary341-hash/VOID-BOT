import os
import discord
from discord.ext import commands

# إعدادات الصلاحيات
intents = discord.Intents.all()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # قائمة الملفات التي سيتم تحميلها
        extensions = [
            "cogs.logs", "cogs.tickets", "cogs.Admin", "cogs.staff_review", 
            "cogs.warnings", "cogs.welcome", "cogs.events", "cogs.moderation", 
            "cogs.rules", "cogs.AutoDivider", "cogs.suggestions", "cogs.anti_raid", 
            "cogs.stats", "cogs.general", "cogs.anti_nuke", "cogs.security", 
            "cogs.giveaway", "cogs.levels"
        ]
        
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"✅ تم تحميل: {ext}")
            except Exception as e:
                print(f"❌ فشل تحميل {ext}: {e}")
        
        # لا يوجد Sync هنا! هذا هو سر الاستقرار.
        print("🚀 تم تحميل جميع الملفات بنجاح!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"🔥 {bot.user} يعمل الآن!")

# تشغيل البوت باستخدام الـ Variable الموجود في Railway
token = os.getenv("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ خطأ: لم يتم العثور على التوكن!")
