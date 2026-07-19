import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- إدارة الأعضاء ---
    @app_commands.command(name="سدها", description="إعطاء تايم أوت لعضو لمدة دقيقة")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(discord.utils.utcnow() + timedelta(minutes=1))
        await interaction.response.send_message(f"⏳ تم إعطاء {member.mention} تايم", ephemeral=True)

    @app_commands.command(name="فكها", description="فك التايم أوت عن عضو")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def remove_timeout(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        await interaction.response.send_message(f"🔓 تم فك التايم عن {member.mention}", ephemeral=True)

    @app_commands.command(name="سقها", description="طرد عضو من السيرفر")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member):
        await member.kick()
        await interaction.response.send_message(f"🚪 تم طرد {member.mention}", ephemeral=True)

    @app_commands.command(name="القمها", description="حظر عضو من السيرفر")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member):
        await member.ban()
        await interaction.response.send_message(f"🔨 تم تبنيد {member.mention}", ephemeral=True)

    # --- إدارة الرسائل ---
    @app_commands.command(name="حذف", description="مسح عدد من الرسائل")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ تم مسح {len(deleted)} رسالة بنجاح.", ephemeral=True)

    # --- إدارة القنوات (قفل/فتح/إخفاء/إظهار) ---
    @app_commands.command(name="قفل", description="قفل الروم الحالي (منع الكتابة)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 تم قفل الروم", ephemeral=True)

    @app_commands.command(name="فتح", description="فتح الروم الحالي (السماح بالكتابة)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message("🔓 تم فتح الروم", ephemeral=True)

    @app_commands.command(name="إخفاء", description="إخفاء الروم عن الجميع")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def hide(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await interaction.response.send_message("🙈 تم إخفاء الروم", ephemeral=True)

    @app_commands.command(name="إظهار", description="إظهار الروم للجميع")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def show(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=True)
        await interaction.response.send_message("👁️ تم إظهار الروم", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
