import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # هنا ضع أي أوامر أخرى لديك في الملف (مثل أوامر المعلومات أو الترحيب إلخ...)
    # تأكد فقط أنك حذفت أي شيء مكتوب فيه @app_commands.command(name="clear")
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"General Cog loaded.")

async def setup(bot):
    await bot.add_cog(General(bot))
