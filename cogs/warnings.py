import discord
from discord.ext import commands
import json
import os


PUNISHMENTS_CHANNEL = 1527936774566056097
DATA = "warnings.json"


def load_data():
    if os.path.exists(DATA):
        with open(DATA, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA, "w") as f:
        json.dump(data, f, indent=4)


class Warnings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()


    @commands.command(name="تحذير")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="بدون سبب"):

        user = str(member.id)

        if user not in self.data:
            self.data[user] = []

        self.data[user].append(reason)

        save_data(self.data)


        embed = discord.Embed(
            title="⚠️ تحذير جديد",
            color=0x8000FF
        )

        embed.add_field(
            name="👤 العضو",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="🛡️ الإداري",
            value=ctx.author.mention,
            inline=False
        )

        embed.add_field(
            name="📌 السبب",
            value=reason,
            inline=False
        )

        embed.add_field(
            name="📊 عدد التحذيرات",
            value=str(len(self.data[user])),
            inline=False
        )


        channel = self.bot.get_channel(
            PUNISHMENTS_CHANNEL
        )

        if channel:
            await channel.send(
                embed=embed
            )


        await ctx.send(
            f"✅ تم تحذير {member.mention}"
        )



    @commands.command(name="تحذيرات")
    async def warnings(self, ctx, member: discord.Member):

        user = str(member.id)

        warns = self.data.get(user, [])


        if not warns:
            await ctx.send(
                "✅ هذا العضو لا يملك تحذيرات"
            )
            return


        embed = discord.Embed(
            title=f"⚠️ تحذيرات {member}",
            color=0x8000FF
        )


        for i, warn in enumerate(warns, 1):
            embed.add_field(
                name=f"تحذير {i}",
                value=warn,
                inline=False
            )


        await ctx.send(
            embed=embed
        )



    @commands.command(name="مسح_تحذيرات")
    @commands.has_permissions(manage_messages=True)
    async def clear_warns(self, ctx, member: discord.Member):

        user = str(member.id)

        self.data[user] = []

        save_data(self.data)


        await ctx.send(
            f"🧹 تم مسح تحذيرات {member.mention}"
        )


async def setup(bot):
    await bot.add_cog(Warnings(bot))
