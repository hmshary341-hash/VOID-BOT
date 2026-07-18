import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # تحميل جميع الملفات من مجلد cogs
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{file[:-3]}")
                    print(f"📦 تم تحميل: {file}")
                except Exception as e:
                    print(f"❌ خطأ في {file}: {e}")
        
        # المزامنة الإجبارية للأوامر لتظهر في ديسكورد
        await self.tree.sync()
        print("✅ تم مزامنة الأوامر مع ديسكورد بنجاح!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ البوت يعمل الآن: {bot.user}")

async def main():
    token = os.getenv("TOKEN")
    if not token:
        print("❌ خطأ: لم يتم العثور على TOKEN")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
