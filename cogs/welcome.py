import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = 1525595451607486535
        self.leave_channel_id = 1527103575946297415

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(self.welcome_channel_id)
        if channel:
            embed = discord.Embed(
                title="✨ Welcome to VOID",
                description=(
                    f"أهلاً بك {member.mention} في سيرفر VOID! 🖤\n\n"
                    "يسعدنا انضمامك إلينا، ونتمنى لك تجربة ممتعة بين أفراد مجتمعنا.\n\n"
                    "**قبل أن تبدأ:**\n"
                    "・📜 اطلع على القوانين.\n"
                    "・🎭 اختر الرتب المناسبة لك.\n"
                    "・💬 شارك في الدردشة وتعرّف على الجميع.\n"
                    "・🎉 استمتع بالفعاليات والجوائز والمزايا الموجودة في السيرفر.\n\n"
                    "نتمنى لك وقتًا مليئًا بالمتعة والتفاعل.\n\n"
                    "أهلًا بك في عائلة VOID. 🌙"
                ),
                color=discord.Color.dark_gray()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"العضو رقم: {member.guild.member_count}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(self.leave_channel_id)
        if channel:
            embed = discord.Embed(
                title="🌑 Goodbye",
                description=(
                    f"لقد غادر {member.display_name} السيرفر.\n\n"
                    "شكرًا لك على الوقت الذي قضيته معنا، ونتمنى لك كل التوفيق في رحلتك القادمة.\n\n"
                    "ستبقى أبواب VOID مفتوحة دائمًا إن قررت العودة يومًا ما.\n\n"
                    "نتمنى لك كل الخير، وإلى اللقاء. 🖤"
                ),
                color=discord.Color.dark_gray()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
