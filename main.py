import discord
from discord.ext import commands
import asyncio

# إعدادات الـ Intents
intents = discord.Intents.all()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    # هذا هو الحل الجذري: نضع التحميل هنا في setup_hook
    async def setup_hook(self):
        # ضع هنا قائمة بجميع ملفاتك في مجلد cogs
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
        
        # مزامنة أوامر السلاش مرة واحدة فقط
        await self.tree.sync()
        print("🚀 تم مزامنة الأوامر وبدء البوت بنجاح!")

# إنشاء البوت
bot = MyBot()

@bot.event
async def on_ready():
    # هنا لا تضع أي شيء سوى رسالة الترحيب (لا تضع load_extension هنا أبداً)
    print(f"🔥 {bot.user} يعمل الآن بكامل قوته!")

# تشغيل البوت
bot.run("YOUR_TOKEN_HERE") # استبدل هذا بالتوكن الخاص بك
ض
