import discord
from discord.ext import commands


EVENT_CHANNEL = 1526824130391834644
KING_GAME_ROLE = 1527871033665654824


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="فعالية")
    @commands.has_permissions(manage_guild=True)
    async def event_winner(
        self,
        ctx,
        member: discord.Member
    ):

        if ctx.channel.id != EVENT_CHANNEL:
            return


        role = ctx.guild.get_role(
            KING_GAME_ROLE
        )


        if role:

            await member.add_roles(
                role
            )

            embed = discord.Embed(
                title="🏆 EVENT WINNER",
                description=(
                    f"مبروك {member.mention} 🎉\n\n"
                    "حصلت على رتبة 👑 King Game"
                ),
                color=0x8000FF
            )


            await ctx.send(
                embed=embed
            )

        else:

            await ctx.send(
                "❌ رتبة King Game غير موجودة"
            )


async def setup(bot):
    await bot.add_cog(Events(bot))
