import datetime
import discord
from discord import app_commands
from discord.ext import commands

# --- الإعدادات (أسماء الرتب المسموح لها حصرياً دون إداريي الإيفنت) ---
ALLOWED_ROLES = [
    "Owner",
    "Co-Owner",
    "Support Manager",
    "Senior Support",
    "Support Staff"
]

# --- أسماء رتب السجن والتحذيرات ---
PRISON_ROLE_NAME = "Prison"      # اسم رتبة السجن

WARN_ROLE_1_NAME = "تحذير 1"
WARN_ROLE_2_NAME = "تحذير 2"
WARN_ROLE_3_NAME = "تحذير 3"

# --- دالة التحقق من الصلاحية ---
def admin_only():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        
        user_role_names = [role.name for role in interaction.user.roles]
        if any(role_name in user_role_names for role_name in ALLOWED_ROLES):
            return True
            
        await interaction.response.send_message("❌ عذراً، هذا الأمر مخصص للإدارة العليا وطاقم الدعم (Support) فقط.", ephemeral=True)
        return False
    return app_commands.check(predicate)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- أمر التحذير التصاعدي ---
    @app_commands.command(name="warn", description="تحذير عضو وإعطائه رتبة تحذير تصاعدية")
    @admin_only()
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد"):
        await interaction.response.defer(ephemeral=True)
        
        r1 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_1_NAME)
        r2 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_2_NAME)
        r3 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_3_NAME)

        if not r1 or not r2 or not r3:
            return await interaction.followup.send("❌ حدث خطأ: تأكد من صحة أسماء رتب التحذيرات في السيرفر.", ephemeral=True)

        try:
            if r3 in member.roles:
                await interaction.followup.send(f"⚠️ العضو {member.mention} لديه بالفعل **تحذير 3** (الحد الأقصى).", ephemeral=True)
                return
            elif r2 in member.roles:
                await member.remove_roles(r2)
                await member.add_roles(r3)
                warning_level = "تحذير 3"
            elif r1 in member.roles:
                await member.remove_roles(r1)
                await member.add_roles(r2)
                warning_level = "تحذير 2"
            else:
                await member.add_roles(r1)
                warning_level = "تحذير 1"

            await interaction.followup.send(f"⚠️ تم إعطاء {member.mention} **{warning_level}** بنجاح. السبب: {reason}", ephemeral=True)
            
            try:
                await member.send(f"⚠️ لقد تلقيت **{warning_level}** في سيرفر **{interaction.guild.name}**.\nالسبب: {reason}")
            except:
                pass

        except Exception:
            await interaction.followup.send("❌ حدث خطأ، تأكد أن رتبة البوت أعلى من رتب التحذيرات والرتبة المستهدفة.", ephemeral=True)

    # --- أمر إزالة/تخفيض التحذير ---
    @app_commands.command(name="unwarn", description="إزالة تحذير من العضو (تخفيض مستوى التحذير)")
    @admin_only()
    async def unwarn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد"):
        await interaction.response.defer(ephemeral=True)
        
        r1 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_1_NAME)
        r2 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_2_NAME)
        r3 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_3_NAME)

        if not r1 or not r2 or not r3:
            return await interaction.followup.send("❌ حدث خطأ: تأكد من صحة أسماء رتب التحذيرات في السيرفر.", ephemeral=True)

        try:
            if r3 in member.roles:
                await member.remove_roles(r3)
                await member.add_roles(r2)
                warning_level = "تحذير 2"
            elif r2 in member.roles:
                await member.remove_roles(r2)
                await member.add_roles(r1)
                warning_level = "تحذير 1"
            elif r1 in member.roles:
                await member.remove_roles(r1)
                warning_level = "بدون تحذيرات (تمت إزالة جميع التحذيرات)"
            else:
                return await interaction.followup.send(f"❌ العضو {member.mention} ليس لديه أي تحذيرات لإزالتها.", ephemeral=True)

            await interaction.followup.send(f"✅ تم تحديث حالة العضو {member.mention} وأصبح الآن: **{warning_level}**. السبب: {reason}", ephemeral=True)
            
            try:
                await member.send(f"✅ تم تخفيض أو إزالة تحذير منك في سيرفر **{interaction.guild.name}**.\nالحالة الجديدة: **{warning_level}**\nالسبب: {reason}")
            except:
                pass

        except Exception:
            await interaction.followup.send("❌ حدث خطأ، تأكد أن رتبة البوت أعلى من رتب التحذيرات والرتبة المستهدفة.", ephemeral=True)

    # --- أمر كشف المسؤول عن العقوبات والتحذيرات والتايم أوت ---
    @app_commands.command(name="modhistory", description="فحص سجلات العضو لمعرفة من أعطاه تحذير أو تايم أوت أو عقوبة")
    @admin_only()
    async def modhistory(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title=f"📜 سجل العقوبات لـ {member.display_name}", 
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        actions_found = 0
        
        try:
            async for entry in interaction.guild.audit_logs(limit=150):
                if entry.target and entry.target.id == member.id:
                    if entry.action == discord.AuditLogAction.kick:
                        embed.add_field(name="🦵 طرد (Kick)", value=f"المسؤول: {entry.user.mention}\nالسبب: {entry.reason or 'لا يوجد'}", inline=False)
                        actions_found += 1
                    elif entry.action == discord.AuditLogAction.ban:
                        embed.add_field(name="🔨 حظر (Ban)", value=f"المسؤول: {entry.user.mention}\nالسبب: {entry.reason or 'لا يوجد'}", inline=False)
                        actions_found += 1
                    elif entry.action == discord.AuditLogAction.member_update:
                        if entry.after and getattr(entry.after, 'communication_disabled_until', None):
                            embed.add_field(name="🔇 تايم أوت (Timeout)", value=f"المسؤول: {entry.user.mention}\nالسبب: {entry.reason or 'لا يوجد'}", inline=False)
                            actions_found += 1
                    elif entry.action == discord.AuditLogAction.member_role_update:
                        if entry.after and getattr(entry.after, 'roles', None):
                            role_names = [r.name for r in entry.after.roles]
                            target_names = [WARN_ROLE_1_NAME, WARN_ROLE_2_NAME, WARN_ROLE_3_NAME, PRISON_ROLE_NAME]
                            for r_name in target_names:
                                if r_name in role_names:
                                    display_name = "تحذير 1" if r_name == WARN_ROLE_1_NAME else ("تحذير 2" if r_name == WARN_ROLE_2_NAME else ("تحذير 3" if r_name == WARN_ROLE_3_NAME else "سجن"))
                                    embed.add_field(name=f"⚠️ رتبة إدارية ({display_name})", value=f"المسؤول: {entry.user.mention}", inline=False)
                                    actions_found += 1
                                    break
                                        
            if actions_found == 0:
                embed.description = "لا توجد سجلات عقوبات أو تحذيرات أو تايم أوت حديثة مسجلة لهذا العضو في سجل السيرفر."
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ حدث خطأ تقني:\n`{e}`", ephemeral=True)

    @app_commands.command(name="timeout", description="إسكات عضو (تايم أوت)")
    @admin_only()
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "لا يوجد"):
        await interaction.response.defer(ephemeral=True)
        try:
            await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
            await interaction.followup.send(f"🔇 تم إسكات {member.mention} بنجاح.", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ حدث خطأ: تأكد أن رتبة البوت أعلى من العضو المراد إسكاته.", ephemeral=True)

    @app_commands.command(name="kick", description="طرد عضو من السيرفر")
    @admin_only()
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد"):
        await interaction.response.defer(ephemeral=True)
        try:
            await member.kick(reason=reason)
            await interaction.followup.send(f"🦵 تم طرد {member.mention} بنجاح.", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ حدث خطأ أثناء محاولة الطرد.", ephemeral=True)

    @app_commands.command(name="ban", description="حظر عضو نهائياً من السيرفر")
    @admin_only()
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد"):
        await interaction.response.defer(ephemeral=True)
        try:
            await member.ban(reason=reason)
            await interaction.followup.send(f"🔨 تم حظر {member.mention} بنجاح.", ephemeral=True)
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
        role = discord.utils.get(interaction.guild.roles, name=PRISON_ROLE_NAME)
        if not role:
            return await interaction.followup.send("❌ رتبة السجن غير موجودة، تأكد من مطابقة اسم الرتبة في الكود.", ephemeral=True)
        try:
            await member.add_roles(role)
            await interaction.followup.send(f"⛓️ تم سجن {member.mention} بنجاح.", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ حدث خطأ، تأكد أن رتبة البوت أعلى من رتبة السجن والرتبة المستهدفة.", ephemeral=True)

    @app_commands.command(name="unprison", description="الإفراج عن عضو من السجن")
    @admin_only()
    async def unprison(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer(ephemeral=True)
        role = discord.utils.get(interaction.guild.roles, name=PRISON_ROLE_NAME)
        if not role:
            return await interaction.followup.send("❌ رتبة السجن غير موجودة، تأكد من مطابقة اسم الرتبة في الكود.", ephemeral=True)
        try:
            await member.remove_roles(role)
            await interaction.followup.send(f"🔓 تم الإفراج عن {member.mention} بنجاح.", ephemeral=True)
        except Exception:
            await interaction.followup.send("❌ حدث خطأ أثناء محاولة الإفراج عن العضو.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
