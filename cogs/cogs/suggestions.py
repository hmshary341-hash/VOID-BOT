import discord
from discord.ext import commands


SUGGEST_CHANNEL = 1527099799038595192

CHANNEL_ID = 1526823698089119784
SEPARATOR_IMAGE = "https://files.catbox.moe/7q1g3v.png"


class Suggestions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return


        # الاقتراحات
        if message.channel.id == SUGGEST_CHANNEL:

            embed = discord.Embed(
                title="💡 اقتراح جديد",
                description=message.content,
                color=0x8000FF
            )

            embed.set_author(
                name=str(message.author),
                icon_url=message.author.display_avatar.url
            )

            embed.set_footer(
                text="VOID • Suggestions"
            )

            await message.delete()

            msg = await message.channel.send(
                embed=embed
            )

            await msg.add_reaction("👍")
            await msg.add_reaction("👎")


        # الفاصل
        if message.channel.id == CHANNEL_ID:

            embed = discord.Embed()

            embed.set_image(
                url=SEPARATOR_IMAGE
            )

            await message.channel.send(
                embed=embed
            )


async def setup(bot):
    await bot.add_cog(Suggestions(bot))
