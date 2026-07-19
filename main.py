import os
import discord
from discord.ext import commands
import asyncio

# إعدادات الصلاحيات
intents = discord.Intents.all()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    # هذه الدالة تُشغل مرة واحدة فقط عند بداية البوت
    async def setup_hook(self):
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
        
        # مزامنة أوامر السلاش (Slash Commands)
        await self.tree.sync()
        print("🚀 تم مزامنة الأوامر وبدء البوت بنجاح!")

# إنشاء البوت
bot = MyBot()

@bot.event
async def on_ready():
    # لا تضع أي عمليات تحميل هنا، فقط رسالة تأكيد
    print(f"🔥 {bot.user} يعمل الآن بكامل قوته!")

# تشغيل البوت باستخدام التوكن من Railway Variables
token = os.getenv("TOKEN")
if token:
    bot.run(token)
else:
    print("❌ خطأ: لم يتم العثور على التوكن في Railway Variables! تأكد من تسميته TOKEN")
