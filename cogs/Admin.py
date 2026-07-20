import discord
from discord import app_commands
from discord.ext import commands
import datetime

# --- الإعدادات ---
PRISON_ROLE_ID = 1527936774566056097
LOG_CHANNEL_ID = 1527936774566056097

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild, title, member, moderator, details):
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title=f"🛡️ سجل الإدارة | {title}", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
            embed.add_field(name="👤 المستهدف", value=f"{member.mention}", inline=True)
            embed.add_field(name="👮 المسؤول", value=f"{moderator.mention}", inline=True)
            embed.add_field(name="📝 التفاصيل", value=details, inline=False)
            await log_channel.send(embed=embed)

    # --- أوامر الإدارة الأساسية ---
    @app_commands.command(name="سدها", description="إسكات عضو (تايم أوت)")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "لا يوجد"):
        await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
        await interaction.response.send_message(f"🔇 تم إسكات {member.mention}.", ephemeral=True)
        await self.send_log(interaction.guild, "تايم أوت", member, interaction.user, f"المدة: {minutes} دقيقة")

    @app_commands.command(name="سقها", description="طرد عضو")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"🦵 تم طرد {member.mention}.", ephemeral=True)
        await self.send_log(interaction.guild, "طرد", member, interaction.user, f"السبب: {reason}")

    @app_commands.command(name="القم", description="حظر عضو (باند)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 تم حظر {member.mention}.", ephemeral=True)
        await self.send_log(interaction.guild, "حظر", member, interaction.user, f"السبب: {reason}")

    @app_commands.command(name="فكها", description="إلغاء عقوبة (اكتب تايم أو باند)")
    @app_commands.checks.has_permissions(administrator=True)
    async def unban_or_timeout(self, interaction: discord.Interaction, نوع: str, id_او_منشن: str):
        target_id = int(id_او_منشن.strip('<@!>'))
        if نوع == "تايم":
            member = interaction.guild.get_member(target_id)
            await member.edit(timed_out_until=None)
            await interaction.response.send_message("✅ تم فك السكات.", ephemeral=True)
        else:
            user = await self.bot.fetch_user(target_id)
            await interaction.guild.unban(user)
            await interaction.response.send_message("✅ تم فك الحظر.", ephemeral=True)

    # --- أوامر التحكم بالقنوات ---
    @app_commands.command(name="قفل", description="قفل القناة الحالية")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 تم قفل القناة.", ephemeral=True)

    @app_commands.command(name="افتح", description="فتح القناة الحالية")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message("🔓 تم فتح القناة.", ephemeral=True)

    @app_commands.command(name="اخفها", description="إخفاء القناة عن الأعضاء")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def hide(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await interaction.response.send_message("🙈 تم إخفاء القناة.", ephemeral=True)

    @app_commands.command(name="ظهرها", description="إظهار القناة للأعضاء")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def show(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=True)
        await interaction.response.send_message("👁️ تم إظهار القناة.", ephemeral=True)

    # --- أوامر الصيانة ---
    @app_commands.command(name="clear", description="حذف عدد معين من الرسائل")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"تم حذف {len(deleted)} رسالة.", ephemeral=True)

    # --- أوامر المعلومات ---
    @app_commands.command(name="يوزر", description="معلومات عضو")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member):
        embed = discord.Embed(title=f"معلومات {member.name}", color=discord.Color.blue())
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="تاريخ الانضمام", value=member.joined_at.strftime("%Y-%m-%d"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="سيرفر", description="معلومات السيرفر")
    async def server_info(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"معلومات {interaction.guild.name}", color=discord.Color.green())
        embed.add_field(name="الأعضاء", value=interaction.guild.member_count)
        embed.add_field(name="صاحب السيرفر", value=interaction.guild.owner.name)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- أوامر متنوعة ---
    @app_commands.command(name="اعلان", description="إرسال إعلان")
    @app_commands.checks.has_permissions(administrator=True)
    async def announce(self, interaction: discord.Interaction, عنوان: str, محتوى: str):
        embed = discord.Embed(title=f"📢 {عنوان}", description=محتوى, color=discord.Color.gold())
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ تم إرسال الإعلان.", ephemeral=True)

    @app_commands.command(name="سجن", description="سجن عضو")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def prison(self, interaction: discord.Interaction, member: discord.Member):
        role = interaction.guild.get_role(PRISON_ROLE_ID)
        await member.add_roles(role)
        await interaction.response.send_message("⛓️ تم سجن العضو.", ephemeral=True)
        await self.send_log(interaction.guild, "سجن", member, interaction.user, "تم تقييده برتبة السجين.")

    @app_commands.command(name="افراج", description="إفراج عن عضو")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def unprison(self, interaction: discord.Interaction, member: discord.Member):
        role = interaction.guild.get_role(PRISON_ROLE_ID)
        await member.remove_roles(role)
        await interaction.response.send_message("🔓 تم الإفراج عن العضو.", ephemeral=True)
        await self.send_log(interaction.guild, "إفراج", member, interaction.user, "تمت إزالة رتبة السجين.")

async def setup(bot):
    await bot.add_cog(Admin(bot))
