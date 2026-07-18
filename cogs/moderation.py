import discord
from discord.ext import commands
from datetime import timedelta


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="سدها")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member):

        await member.timeout(
            discord.utils.utcnow() + timedelta(minutes=1)
        )

        await ctx.send(
            f"⏳ تم إعطاء {member.mention} تايم"
        )


    @commands.command(name="فكها")
    @commands.has_permissions(moderate_members=True)
    async def remove_timeout(self, ctx, member: discord.Member):

        await member.timeout(None)

        await ctx.send(
            f"🔓 تم فك التايم عن {member.mention}"
        )


    @commands.command(name="سقها")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member):

        await member.kick()

        await ctx.send(
            f"🚪 تم طرد {member.mention}"
        )


    @commands.command(name="القمها")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member):

        await member.ban()

        await ctx.send(
            f"🔨 تم تبنيد {member.mention}"
        )


    @commands.command(name="حذف")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):

        await ctx.channel.purge(
            limit=amount
        )


    @commands.command(name="قفل")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False
        )

        await ctx.send(
            "🔒 تم قفل الروم"
        )


    @commands.command(name="فتح")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=True
        )

        await ctx.send(
            "🔓 تم فتح الروم"
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
