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
            # رابط الصورة الذي أرسلته ليكون الفاصل
            divider = "https://cdn.discordapp.com/attachments/1508247176457748620/1528894060553699378/file_000000004f248246927824ed07370dd2.png?ex=6a5ff50d&is=6a5ea38d&hm=1f161e6269d6fcb4d0ed41c60e821e06cc359a96692b125f684c5ac7d4b93a1a&"
            try:
                await message.channel.send(divider)
            except Exception as e:
                print(f"خطأ في إرسال الفاصل: {e}")

async def setup(bot):
    await bot.add_cog(AutoDivider(bot))
