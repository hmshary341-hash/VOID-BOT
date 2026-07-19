import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    try:
        await bot.load_extension("cogs.admin")
        await bot.load_extension("cogs.tickets")
        print("✅ تم تحميل ملفات الأوامر (admin, tickets)")
    except Exception as e:
        print(f"❌ خطأ أثناء تحميل الملفات: {e}")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🚀 البوت {bot.user} جاهز الآن!")

async def main():
    # بدلاً من وضع التوكن في الكود، سنطلبه من المستخدم عند التشغيل
    token = input("يرجى إدخال توكن البوت الخاص بك: ").strip()
    
    async with bot:
        await load_extensions()
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
