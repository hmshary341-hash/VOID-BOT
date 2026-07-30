import discord
from discord.ext import commands


class Greetings(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot:
      return

    content = message.content.strip()

    if "السلام عليكم" in content:
      await message.channel.send(
          f"وعليكم السلام ورحمه الله وبركاته منور/ه يالأمير/ه ."
      )
    elif "مع السلامه" in content or "مع السلامة" in content:
      await message.channel.send(
          "في أمان الله وحفظه لا تنسى تجي لا تروح مانبي نفقدك ."
      )


async def setup(bot):
  await bot.add_cog(Greetings(bot))
