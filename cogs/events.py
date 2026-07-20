import discord
from discord import app_commands
from discord.ext import commands

# الثوابت (تأكد أن هذه القيم هي نفس القيم الموجودة في ملفك الأصلي)
EVENT_CHANNEL = 1526824130391834644
KING_GAME_ROLE = 1527871033665654824

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="فعالية", description="إعلان فائز الفعالية وإعطاؤه رتبة الملك")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def event_winner(self, interaction: discord.Interaction, member: discord.Member):
        
        # التحقق من القناة
        if interaction.channel_id != EVENT_CHANNEL:
            return await interaction.response.send_message("❌ هذا الأمر لا يعمل في هذه القناة.", ephemeral=True)

        role = interaction.guild.get_role(KING_GAME_ROLE)

        if role:
            await member.add_roles(role)
            
            embed = discord.Embed(
                title="🏆 EVENT WINNER",
                description=(
                    f"مبروك {member.mention} 🎉\n\n"
                    "حصلت على رتبة 👑 King Game"
                ),
                color=0x8000FF
            )

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ رتبة King Game غير موجودة (تأكد من الـ ID في الكود).", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Events(bot))
