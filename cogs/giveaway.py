import discord
from discord.ext import commands
import asyncio
import random


GIVEAWAY_START = 1526628744020754594
GIVEAWAY_END = 1526709276083490949


class Giveaway(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="قيف")
    @commands.has_permissions(manage_guild=True)
    async def giveaway(
        self,
        ctx,
        time: int,
        winners: int,
        *,
        prize
    ):

        if ctx.channel.id != GIVEAWAY_START:
            return


        embed = discord.Embed(
            title="🎉 GIVEAWAY",
            description=(
                f"🎁 الجائزة: {prize}\n\n"
                f"⏳ المدة: {time} ثانية\n"
                f"🏆 عدد الفائزين: {winners}\n\n"
                "اضغط 🎉 للمشاركة"
            ),
            color=0x8000FF
        )


        msg = await ctx.send(
            embed=embed
        )

        await msg.add_reaction("🎉")


        await asyncio.sleep(time)


        msg = await ctx.channel.fetch_message(
            msg.id
        )


        users = []

        for reaction in msg.reactions:

            if str(reaction.emoji) == "🎉":

                users = [
                    user async for user in reaction.users()
                    if not user.bot
                ]


        if users:

            winners_list = random.sample(
                users,
                min(winners, len(users))
            )


            channel = self.bot.get_channel(
                GIVEAWAY_END
            )

            if channel:

                await channel.send(
                    "🎉 الفائزين:\n" +
                    " ".join(
                        user.mention
                        for user in winners_list
                    )
                )

        else:

            await ctx.send(
                "❌ لا يوجد مشاركين"
            )


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
