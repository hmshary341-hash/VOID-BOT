import discord
from discord.ext import commands
import json
import os


DATA = "levels.json"

LEVEL_ROLES = {
    5: 1526291094747353189,
    10: 1526291235118252094,
    15: 1526291447761080572,
    20: 1526291542568996924,
    25: 1526292403705610471,
    30: 1526292553689862294,
    35: 1526292677564567724,
    40: 1526434244665278575,
    45: 1526825876967264339
}


def load_data():
    if os.path.exists(DATA):
        with open(DATA, "r") as f:
            return json.load(f)

    return {}


def save_data(data):
    with open(DATA, "w") as f:
        json.dump(data, f, indent=4)


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()


    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        user = str(message.author.id)

        if user not in self.data:
            self.data[user] = {
                "xp": 0,
                "level": 1
            }


        old_level = self.data[user]["level"]

        self.data[user]["xp"] += 5


        xp = self.data[user]["xp"]
        level = self.data[user]["level"]


        if xp >= level * 100:

            self.data[user]["level"] += 1

            new_level = self.data[user]["level"]


            await message.channel.send(
                f"🎉 ترقية جديدة!\n\n"
                f"مبروك {message.author.mention} 🖤💜\n"
                f"وصلت المستوى **{new_level}** ✨\n\n"
                "كفو كمل تفاعل 🔥\n"
                "يلا توكل واستمر، الجايات أقوى 💪\n\n"
                "VOID 🖤"
            )


            if new_level in LEVEL_ROLES:

                role = message.guild.get_role(
                    LEVEL_ROLES[new_level]
                )

                if role:
                    await message.author.add_roles(role)


        save_data(self.data)


    @commands.command(name="مستواي")
    async def my_level(self, ctx):

        user = str(ctx.author.id)

        if user not in self.data:

            await ctx.send(
                "❌ ما عندك مستوى للحين"
            )

            return


        embed = discord.Embed(
            title="📊 مستواك",
            description=(
                f"⭐ المستوى: {self.data[user]['level']}\n"
                f"✨ النقاط: {self.data[user]['xp']}"
            ),
            color=0x800080
        )


        await ctx.send(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(Levels(bot))
