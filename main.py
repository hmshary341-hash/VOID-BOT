import discord
from discord.ext import commands
import os
import asyncio


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


async def load_cogs():

    for file in os.listdir("./cogs"):

        if file.endswith(".py"):

            await bot.load_extension(
                f"cogs.{file[:-3]}"
            )


async def main():

    await load_cogs()

    TOKEN = os.getenv("TOKEN")

    await bot.start(TOKEN)


asyncio.run(main())
