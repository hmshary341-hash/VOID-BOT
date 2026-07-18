import discord
from discord.ext import commands


STATS_CHANNEL = 1526712984531894292


class Stats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="تحديث_الإحصائيات")
    @commands.has_permissions(administrator=True)
    async def update_stats(self, ctx):

        channel = self.bot.get_channel(
            STATS_CHANNEL
        )


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


            await channel.send(
                embed=embed
            )


        else:

            await ctx.send(
                "❌ روم الإحصائيات غير موجود"
            )


async def setup(bot):
    await bot.add_cog(Stats(bot))
