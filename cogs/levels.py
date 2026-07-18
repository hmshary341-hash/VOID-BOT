import discord
from discord.ext import commands
import json
import os


DATA = "levels.json"


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

        self.data[user]["xp"] += 5

        xp = self.data[user]["xp"]
        level = self.data[user]["level"]

        if xp >= level * 100:
            self.data[user]["level"] += 1

            await message.channel.send(
                f"🎉 مبروك {message.author.mention} وصلت مستوى {self.data[user]['level']}"
            )

        save_data(self.data)


    @commands.command(name="مستواي")
    async def my_level(self, ctx):

        user = str(ctx.author.id)

        if user not in self.data:
            await ctx.send("❌ ما عندك مستوى للحين")
            return

        embed = discord.Embed(
            title="📊 مستواك",
            description=(
                f"⭐ المستوى: {self.data[user]['level']}\n"
                f"✨ النقاط: {self.data[user]['xp']}"
            ),
            color=0x800080
        )

        await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Levels(bot))
