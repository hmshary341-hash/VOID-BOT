import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
                print(f"✅ Loaded {file}")
            except Exception as e:
                print(f"❌ Error loading {file}: {e}")


TOKEN = os.getenv("TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ TOKEN غير موجود")
