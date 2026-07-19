import discord
from discord import app_commands
from discord.ext import commands

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # أمر Ping للتحقق من سرعة البوت
    @app_commands.command(name="ping", description="معرفة سرعة استجابة البوت")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 البوت يعمل بسرعة: {round(self.bot.latency * 1000)}ms")

    # أمر مسح الرسائل (إداري)
    @app_commands.command(name="clear", description="مسح عدد معين من الرسائل")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, count: int):
        if count < 1 or count > 100:
            await interaction.response.send_message("❌ يرجى اختيار عدد بين 1 و 100", ephemeral=True)
            return
        deleted = await interaction.channel.purge(limit=count)
        await interaction.response.send_message(f"✅ تم مسح {len(deleted)} رسالة بنجاح.", ephemeral=True)

    # أمر معلومات العضو
    @app_commands.command(name="userinfo", description="عرض معلومات العضو")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"معلومات {member.name}", color=discord.Color.green())
        embed.add_field(name="الآيدي:", value=member.id, inline=False)
        embed.add_field(name="تاريخ الانضمام:", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))
