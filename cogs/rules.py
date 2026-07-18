import discord
from discord.ext import commands


THE_VOID_ROLE = 1526653269743767562
RULES_CHANNEL = 1525592697069502596


class RulesButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="أوافق على القوانين",
        emoji="🖤",
        style=discord.ButtonStyle.success,
        custom_id="rules_accept"
    )
    async def agree(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        role = interaction.guild.get_role(THE_VOID_ROLE)

        if role:
            await interaction.user.add_roles(role)

            await interaction.response.send_message(
                "✅ تم إعطاؤك رتبة THE VOID",
                ephemeral=True
            )

        else:
            await interaction.response.send_message(
                "❌ الرتبة غير موجودة",
                ephemeral=True
            )


class Rules(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="قوانين")
    @commands.has_permissions(administrator=True)
    async def rules(self, ctx):

        if ctx.channel.id != RULES_CHANNEL:
            return

        embed = discord.Embed(
            title="📜 قوانين VOID",
            description=(
                "🖤 احترام الجميع\n"
                "🖤 ممنوع السبام\n"
                "🖤 ممنوع الإساءة\n\n"
                "اضغط الزر للموافقة"
            ),
            color=0x8000FF
        )

        await ctx.send(
            embed=embed,
            view=RulesButton()
        )


async def setup(bot):
    await bot.add_cog(Rules(bot))
