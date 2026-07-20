import discord
from discord.ext import commands

class AutoDivider(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_channels = [1526823698089119784, 1526227386117656586]

    @commands.Cog.listener()
    async def on_message(self, message):
        # منع البوت من الرد على نفسه
        if message.author.bot:
            return

        # التأكد أن الرسالة في أحد الرومات المحددة
        if message.channel.id in self.target_channels:
            # فاصل نصي طويل وأنيق يمتد بعرض الشات
            divider = "💜 ─── ⋆⋅『 **𝖵 𝖮 𝖨 𝖣** 』⋅⋆ ─── 💜"
            try:
                await message.channel.send(divider)
            except Exception as e:
                print(f"خطأ في إرسال الفاصل: {e}")

async def setup(bot):
    await bot.add_cog(AutoDivider(bot))
