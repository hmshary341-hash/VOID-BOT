import discord
from discord.ext import commands


WELCOME_CHANNEL = 1525595451607486535
GOODBYE_CHANNEL = 1527103575946297415
THE_VOID_ROLE = 1526653269743767562


class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(self, member):

        role = member.guild.get_role(
            THE_VOID_ROLE
        )

        if role:
            await member.add_roles(role)


        channel = self.bot.get_channel(
            WELCOME_CHANNEL
        )

        if channel:

            embed = discord.Embed(
                title="🖤 WELCOME TO VOID",
                description=(
                    f"أهلاً بك {member.mention} 💜\n\n"
                    "نتمنى لك وقت ممتع معنا."
                ),
                color=0x8000FF
            )

            await channel.send(
                embed=embed
            )


    @commands.Cog.listener()
    async def on_member_remove(self, member):

        channel = self.bot.get_channel(
            GOODBYE_CHANNEL
        )

        if channel:

            embed = discord.Embed(
                title="🖤 GOODBYE",
                description=(
                    f"غادر السيرفر {member.mention}\n\n"
                    "نتمنى رؤيتك مرة أخرى 💜"
                ),
                color=0x8000FF
            )

            await channel.send(
                embed=embed
            )


async def setup(bot):
    await bot.add_cog(Welcome(bot))
