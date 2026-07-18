import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1526823698089119784
SEPARATOR_IMAGE = "https://files.catbox.moe/7q1g3v.png"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == CHANNEL_ID:
        await message.channel.send(SEPARATOR_IMAGE)

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
