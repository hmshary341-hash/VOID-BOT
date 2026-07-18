import discord
from discord.ext import commands
import json
import os
from PIL import Image, ImageDraw, ImageFont
import io
import aiohttp


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


async def create_card(member, level, xp):

    img = Image.new(
        "RGB",
        (900, 300),
        (128, 0, 255)
    )

    draw = ImageDraw.Draw(img)


    avatar = await member.display_avatar.read()

    avatar_img = Image.open(
        io.BytesIO(avatar)
    ).convert("RGBA")

    avatar_img = avatar_img.resize(
        (180, 180)
    )

    img.paste(
        avatar_img,
        (50, 60),
        avatar_img
    )


    draw.text(
        (270, 70),
        member.name,
        fill="white"
    )

    draw.text(
        (270, 120),
        f"Level : {level}",
        fill="white"
    )

    draw.text(
        (270, 160),
        f"XP : {xp}",
        fill="white"
    )


    file = io.BytesIO()

    img.save(
        file,
        "PNG"
    )

    file.seek(0)

    return discord.File(
        file,
        filename="level.png"
    )



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

            level = self.data[user]["level"]


            card = await create_card(
                message.author,
                level,
                xp
            )


            await message.channel.send(
                content=(
                    f"🎉 ترقية جديدة!\n"
                    f"كفو كمل تفاعل 🔥"
                ),
                file=card
            )


            if level in LEVEL_ROLES:

                role = message.guild.get_role(
                    LEVEL_ROLES[level]
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


        card = await create_card(
            ctx.author,
            self.data[user]["level"],
            self.data[user]["xp"]
        )


        await ctx.send(
            file=card
        )



async def setup(bot):
    await bot.add_cog(Levels(bot))
