import discord
from discord.ext import commands
import os
import asyncio

# استدعاء الكلاسات عشان تثبيت الأزرار حتى بعد رستارت البوت
try:
    from cogs.suggestions import SuggestionView
    from cogs.tickets import TicketControl, OpenTicket
    from cogs.staff_review import ReviewLaunchView
except ImportError:
    SuggestionView = None
    TicketControl = None
    OpenTicket = None
    ReviewLaunchView = None

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await load_cogs()
        # تسجيل عروض الأزرار بشكل دائم
        if SuggestionView: self.add_view(SuggestionView())
        if TicketControl: self.add_view(TicketControl())
        if OpenTicket: self.add_view(OpenTicket())
        if ReviewLaunchView: self.add_view(ReviewLaunchView())

bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول باسم: {bot.user}")

async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
                print(f"📦 تم تحميل الكوج: {file}")
            except Exception as e:
                print(f"❌ فشل تحميل {file}: {e}")

async def main():
    token = os.getenv("TOKEN")
    if token is None:
        print("❌ خطأ: لم يتم العثور على TOKEN البوت في متغيرات البيئة")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
