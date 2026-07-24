import discord
from discord.ext import commands

class Separators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # تجاهل رسائل البوتات لتجنب التكرار
        if message.author.bot:
            return

        # 1. روم الشعر
        if message.channel.id == 1530050492938584124:
            await message.reply("صح لسانك يا الشاعر/ه 🤍")

        # 2. روم التكليجات
        elif message.channel.id == 1530051019608690708:
            await message.reply("ههههههههه يا وحش قفطت التكليجه")

        # 3. روم الإبداعات
        elif message.channel.id == 1530051188698120233:
            await message.reply("اي والله إبداع انت/ي بعيونا مبدع/ه")

async def setup(bot):
    await bot.add_cog(Separators(bot))
