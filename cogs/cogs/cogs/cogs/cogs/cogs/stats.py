import discord
from discord.ext import commands


STATS_CHANNEL = 1526712984531894292
BOOST_CHANNEL = 1526828845762744320


class Stats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="تحديث_الإحصائيات")
    @commands.has_permissions(administrator=True)
    async def stats(self, ctx):

        channel = self.bot.get_channel(STATS_CHANNEL)

        if channel:

            embed = discord.Embed(
                title="📊 VOID STATS",
                description=(
                    f"👥 الأعضاء: {ctx.guild.member_count}\n"
                    f"💬 الرومات: {len(ctx.guild.channels)}\n"
                    f"🎭 الرتب: {len(ctx.guild.roles)}"
                ),
                color=0x8000FF
            )

            embed.set_footer(
                text="VOID • Statistics"
            )

            await channel.send(
                embed=embed
            )


    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        if before.premium_since != after.premium_since:

            if after.premium_since:

                channel = self.bot.get_channel(
                    BOOST_CHANNEL
                )

                if channel:

                    embed = discord.Embed(
                        title="🚀 BOOST",
                        description=(
                            f"شكراً {after.mention} على دعم VOID 💜"
                        ),
                        color=0x8000FF
                    )

                    await channel.send(
                        embed=embed
                    )


async def setup(bot):
    await bot.add_cog(Stats(bot))
