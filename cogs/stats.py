import discord
from discord import app_commands
from discord.ext import commands

STATS_CHANNEL = 1526712984531894292

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="تحديث_الإحصائيات", description="تحديث إحصائيات السيرفر في الروم المخصص")
    @app_commands.checks.has_permissions(administrator=True)
    async def update_stats(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(STATS_CHANNEL)
        
        if not channel:
            return await interaction.response.send_message("❌ روم الإحصائيات غير موجود.", ephemeral=True)

        embed = discord.Embed(
            title="📊 VOID STATS",
            description=(
                f"👥 الأعضاء: {interaction.guild.member_count}\n"
                f"💬 الرومات: {len(interaction.guild.channels)}\n"
                f"🎭 الرتب: {len(interaction.guild.roles)}"
            ),
            color=0x8000FF
        )

        await channel.send(embed=embed)
        await interaction.response.send_message("✅ تم تحديث الإحصائيات بنجاح.", ephemeral=True)

    # --- أمر التوب (تمت إضافته هنا) ---
    @app_commands.command(name="top", description="عرض قائمة المتصدرين")
    async def top(self, interaction: discord.Interaction):
        # هنا تضع كود جلب البيانات من الداتابيس الخاص بك
        embed = discord.Embed(
            title="🏆 قائمة المتصدرين",
            description="جاري جلب البيانات من النظام...",
            color=0x8000FF
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))
