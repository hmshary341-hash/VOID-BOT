import discord
from discord.ext import commands
from collections import defaultdict
from datetime import timedelta
import time


LOG_CHANNEL = 1526625037808046241

spam_data = defaultdict(list)


class Security(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        user = message.author.id
        now = time.time()

        spam_data[user].append(now)

        # حذف الرسائل القديمة
        spam_data[user] = [
            t for t in spam_data[user]
            if now - t < 5
        ]


        # إذا أرسل 5 رسائل خلال 5 ثواني
        if len(spam_data[user]) >= 5:

            try:
                await message.author.timeout(
                    timedelta(minutes=5),
                    reason="Spam Protection"
                )

                embed = discord.Embed(
                    title="🛡️ حماية السيرفر",
                    description=(
                        f"تم إعطاء ميوت مؤقت لـ {message.author.mention}\n"
                        "السبب: Spam"
                    ),
                    color=0x8000FF
                )


                channel = self.bot.get_channel(
                    LOG_CHANNEL
                )

                if channel:
                    await channel.send(
                        embed=embed
                    )


                spam_data[user] = []


            except:
                pass



async def setup(bot):
    await bot.add_cog(Security(bot))
