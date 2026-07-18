import discord
from discord.ext import commands
from datetime import timedelta


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def سدها(self, ctx, member: discord.Member):

        await member.timeout(
            discord.utils.utcnow() + timedelta(minutes=1)
        )

        await ctx.send(
            f"⏳ تم إعطاء {member.mention} تايم"
        )


    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def فكها(self, ctx, member: discord.Member):

        await member.timeout(None)

        await ctx.send(
            f"🔓 تم فك التايم عن {member.mention}"
        )


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def سقها(self, ctx, member: discord.Member):

        await member.kick()

        await ctx.send(
            f"🚪 تم طرد {member.mention}"
        )


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def القمها(self, ctx, member: discord.Member):

        await member.ban()

        await ctx.send(
            f"🔨 تم تبنيد {member.mention}"
        )


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def حذف(self, ctx, amount: int):

        await ctx.channel.purge(
            limit=amount
        )


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def قفل(self, ctx):

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False
        )

        await ctx.send(
            "🔒 تم قفل الروم"
        )


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def فتح(self, ctx):

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=True
        )

        await ctx.send(
            "🔓 تم فتح الروم"
        )


    @commands.command()
    async def بنق(self, ctx):

        await ctx.send(
            f"🏓 {round(self.bot.latency * 1000)}ms"
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
