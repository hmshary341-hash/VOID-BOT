import discord
from discord.ext import commands
from collections import deque
from datetime import datetime, timedelta


LOG_CHANNEL = 1526625037808046241

joins = deque()


class AntiRaid(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(self, member):

        now = datetime.now()

        joins.append(now)


        # حذف الدخولات القديمة
        while joins and (now - joins[0]).seconds > 10:
            joins.popleft()


        # إذا دخل 5 أعضاء خلال 10 ثواني
        if len(joins) >= 5:

            channel = self.bot.get_channel(
                LOG_CHANNEL
            )

            if channel:

                embed = discord.Embed(
                    title="🚨 Anti Raid",
                    description=(
                        "تم اكتشاف دخول سريع للأعضاء!\n\n"
                        f"عدد الدخولات: {len(joins)} خلال 10 ثواني"
                    ),
                    color=0x8000FF
                )

                await channel.send(
                    embed=embed
                )

            joins.clear()



async def setup(bot):
    await bot.add_cog(AntiRaid(bot))
