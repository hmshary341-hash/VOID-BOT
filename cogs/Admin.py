import datetime
import discord
from discord import app_commands
from discord.ext import commands

# --- الإعدادات ---
PRISON_ROLE_ID = 1526011928433135810  # آي دي رتبة السجن
LOG_CHANNEL_ID = 1526625037808046241  # آي دي قناة السجلات
ADMIN_ROLE_ID = 1527513659704606740   # رتبة الإدارة المحددة

# --- دالة التحقق من الصلاحية ---
def admin_only():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        if any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
            return True
        await interaction.response.send_message("❌ عذراً، هذا الأمر مخصص للمشرفين فقط.", ephemeral=True)
        return False
    return app_commands.check(predicate)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild, title, member, moderator, details):
        if LOG_CHANNEL_ID == 0:
            return
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            try:
                embed = discord.Embed(
                    title=f"🛡️ سجل الإدارة | {title}", 
                    color=discord.Color.red(), 
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                embed.add_field(name="👤 المستهدف", value=f"{member.mention}", inline=True)
                embed.add_field(name="👮 المسؤول", value=f"{moderator.mention}", inline=True)
                embed.add_field(name="📝 التفاصيل", value=details, inline=False)
                await log_channel.send(embed=embed)
            except Exception:
                pass

    # --- أوامر الأعضاء العامة (تم إبقاء أوامر الألوان) ---
    @app_commands.command(name="color", description="اختر لونك المفضّل")
    async def color(self, interaction: discord.Interaction, اختيار_اللون: str):
        await interaction.response.send_message(f"🎨 تم طلب لون: {اختيار_اللون}.", ephemeral=True)

    @app_commands.command(name="colors", description="عرض الألوان المتاحة في السيرفر")
    async def colors(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎨 الألوان المتاحة", description="قائمة الألوان المتوفرة للأعضاء.", color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- أوامر الإدارة والمشرفين ---
    @app_commands.command(name="timeout", description="إسكات عضو (تايم أوت)")
    @admin_only()
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "لا يوجد"):
        await interaction.response.defer(ephemeral=True)
        try:
            await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
            await interaction.followup.send(f"🔇 تم إسكات {member.mention} بنجاح.", ephemeral=True)
            await self.send_log(interaction.guild, "تايم أوت", member, interaction.user, f"المدة: {minutes} دقيقة | السبب: {reason}")
        except Exception:
            await interaction.followup.send("❌ حدث خطأ: تأكد أن رتبة البوت أعلى من العضو المراد إسكاته.", ephemeral=True)

    @app_commands.command(name="kick", description="طرد عضو من السيرفر")
    @admin_only()
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد"):
        await interaction.response.defer(ephemeral=True)
        try:
            await member.kick(reason=reason)
            await interaction.followup.send(f"🦵 تم طرد {member.mention} بنجاح.", ephemeral=True)
            await self.send_log(interaction.guild, "طرد", member, interaction.user, f"السبب: {reason}")
        except Exception:
            await interaction.followup.send("❌ حدث خطأ أثناء محاولة الطرد.", ephemeral=True)

    @app_commands.command(name="ban", description="حظر عضو نهائياً من السيرفر")
    @admin_only()
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد"):
        await interaction.response.defer(ephemeral=True)
        try:
            await member.ban(reason=reason)
            await interaction.followup.send(f"🔨 تم حظر {member.mention} بنجاح.", ephemeral=True)
            await self.send_log(interaction.guild, "حظر", member, interaction.user, f"السبب: {reason}")
        except Exception:
            await interaction.followup.send("❌ حدث خطأ أثناء محاولة الحظر.", ephemeral=True)

    @app_commands.command(name="unban", description="فك الحظر عن مستخدم بواسطة الآي دي")
    @admin_only()
    async def unban(self, interaction: discord.Interaction, user_id: str):
        await interaction.response.defer(ephemeral=True)
        try:
            target_id = int(user_id.strip('<@!>'))
            user = await self.bot.fetch_user(target_id)
            await interaction.guild.unban(user)
            await interaction.followup.send("✅ تم فك الحظر عن المستخدم بنجاح.", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ حدث خطأ، تأكد من صحة الآي دي المدخل.", ephemeral=True)

    @app_commands.command(name="untimeout", description="فك السكات عن عضو")
    @admin_only()
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True)
        try:
            await member.timeout(None)
            await interaction.followup.send(f"✅ تم فك السكات عن {member.mention}.", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ حدث خطأ أثناء محاولة فك السكات.", ephemeral=True)

    @app_commands.command(name="hide", description="إخفاء القناة الحالية عن الأعضاء")
    @admin_only()
    async def hide(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await interaction.followup.send("🙈 تم إخفاء القناة.", ephemeral=True)

    @app_commands.command(name="show", description="إظهار القناة الحالية للأعضاء")
    @admin_only()
    async def show(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=True)
        await interaction.followup.send("👁️ تم إظهار القناة.", ephemeral=True)

    @app_commands.command(name="clear", description="حذف عدد من الرسائل في القناة")
    @admin_only()
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        try:
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f"🗑️ تم حذف {len(deleted)} رسالة بنجاح.", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ حدث خطأ، تأكد أن الرسائل قابلة للحذف وليست قديمة جداً.", ephemeral=True)

    @app_commands.command(name="prison", description="سجن عضو")
    @admin_only()
    async def prison(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True)
        role = interaction.guild.get_role(PRISON_ROLE_ID)
        if not role:
            return await interaction.followup.send("❌ رتبة السجن غير موجودة، تأكد من آي دي الرتبة في الكود.", ephemeral=True)
        try:
            await member.add_roles(role)
            await interaction.followup.send(f"⛓️ تم سجن {member.mention} بنجاح.", ephemeral=True)
            await self.send_log(interaction.guild, "سجن", member, interaction.user, "تم تقييده برتبة السجين.")
        except Exception:
            await interaction.followup.send("❌ حدث خطأ، تأكد أن رتبة البوت أعلى من رتبة السجن والرتبة المستهدفة.", ephemeral=True)

    @app_commands.command(name="unprison", description="الإفراج عن عضو من السجن")
    @admin_only()
    async def unprison(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True)
        role = interaction.guild.get_role(PRISON_ROLE_ID)
        if not role:
            return await interaction.followup.send("❌ رتبة السجن غير موجودة، تأكد من آي دي الرتبة في الكود.", ephemeral=True)
        try:
            await member.remove_roles(role)
            await interaction.followup.send(f"🔓 تم الإفراج عن {member.mention} بنجاح.", ephemeral=True)
            await self.send_log(interaction.guild, "إفراج", member, interaction.user, "تمت إزالة رتبة السجين.")
        except Exception:
            await interaction.followup.send("❌ حدث خطأ أثناء محاولة الإفراج عن العضو.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
