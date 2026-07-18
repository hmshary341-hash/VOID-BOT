import discord
from discord.ext import commands


LOG_CHANNEL = 1526625037808046241


class AntiNuke(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    async def send_log(self, title, description):

        channel = self.bot.get_channel(LOG_CHANNEL)

        if channel:
            embed = discord.Embed(
                title=title,
                description=description,
                color=0x8000FF
            )

            await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        await self.send_log(
            "🚨 حذف روم",
            f"تم حذف الروم:\n`{channel.name}`"
        )


    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):

        await self.send_log(
            "🚨 حذف رتبة",
            f"تم حذف الرتبة:\n`{role.name}`"
        )


    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):

        await self.send_log(
            "📌 إنشاء روم",
            f"تم إنشاء روم:\n`{channel.name}`"
        )


    @commands.Cog.listener()
    async def on_guild_role_create(self, role):

        await self.send_log(
            "📌 إنشاء رتبة",
            f"تم إنشاء رتبة:\n`{role.name}`"
        )


async def setup(bot):
    await bot.add_cog(AntiNuke(bot))
