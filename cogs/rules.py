import discord
from discord.ext import commands


RULES_CHANNEL = 1525592697069502596
THE_VOID_ROLE = 1526653269743767562


class Rules(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="قوانين")
    async def rules(self, ctx):

        if ctx.channel.id != RULES_CHANNEL:
            return

        embed = discord.Embed(
            title="📜 قوانين VOID",
            description=(
                "🖤 احترام الجميع\n"
                "🖤 ممنوع السبام\n"
                "🖤 ممنوع الإساءة\n"
                "🖤 الالتزام بقوانين ديسكورد\n\n"
                "شكراً لالتزامك 🖤"
            ),
            color=0x8000FF
        )

        await ctx.send(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(Rules(bot))
