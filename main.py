import os
import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# متغير لمنع التكرار
is_started = False

extensions = [
    "cogs.logs", "cogs.tickets", "cogs.Admin", "cogs.staff_review", 
    "cogs.warnings", "cogs.welcome", "cogs.events", "cogs.moderation", 
    "cogs.rules", "cogs.AutoDivider", "cogs.suggestions", "cogs.anti_raid", 
    "cogs.stats", "cogs.general", "cogs.anti_nuke", "cogs.security", 
    "cogs.giveaway", "cogs.levels"
]

@bot.event
async def on_ready():
    global is_started
    if not is_started:
        print(f"✅ {bot.user} متصل ويعمل الآن!")
        # تحميل الملفات مرة واحدة فقط عند التشغيل الأول
        for ext in extensions:
            try:
                # التحقق إذا كان الملف محملاً مسبقاً لمنع أي خطأ
                if ext not in bot.extensions:
                    await bot.load_extension(ext)
                    print(f"✅ تم تحميل: {ext}")
            except Exception as e:
                print(f"❌ فشل تحميل {ext}: {e}")
        is_started = True
    else:
        print("⚠️ البوت أعاد الاتصال (Reconnected) ولكن لن يتم إعادة تحميل الملفات.")

token = os.getenv("TOKEN")
bot.run(token)
