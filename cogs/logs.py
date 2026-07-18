import discord
from discord.ext import commands


LOG_CHANNEL = 1526625037808046241


class Logs(commands.Cog):

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
    async def on_member_join(self, member):

        await self.send_log(
            "📥 عضو دخل",
            f"{member.mention}\nID: `{member.id}`"
        )


    @commands.Cog.listener()
    async def on_member_remove(self, member):

        await self.send_log(
            "📤 عضو خرج",
            f"{member.name}\nID: `{member.id}`"
        )


    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if message.author.bot:
            return

        await self.send_log(
            "🗑️ حذف رسالة",
            f"العضو: {message.author.mention}\n"
            f"المحتوى:\n{message.content}"
        )


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        if before.author.bot:
            return

        await self.send_log(
            "✏️ تعديل رسالة",
            f"العضو: {before.author.mention}\n\n"
            f"قبل:\n{before.content}\n\n"
            f"بعد:\n{after.content}"
        )


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if before.channel is None and after.channel:

            await self.send_log(
                "🎙️ دخول فويس",
                f"{member.mention} دخل {after.channel.name}"
            )


        elif before.channel and after.channel is None:

            await self.send_log(
                "🔇 خروج فويس",
                f"{member.mention} خرج من {before.channel.name}"
            )



async def setup(bot):
    await bot.add_cog(Logs(bot))
