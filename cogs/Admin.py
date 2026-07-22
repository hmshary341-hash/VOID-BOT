import datetime
import discord
from discord import app_commands
from discord.ext import commands

# --- الإعدادات ---
PRISON_ROLE_ID = 1526011928433135810  # آي دي رتبة السجن
ADMIN_ROLE_ID = 1527513659704606740   # رتبة الإدارة المحددة

# --- آي دي رتب التحذيرات ---
WARN_ROLE_1_ID = 1529362841696735353
WARN_ROLE_2_ID = 1529362930997661807
WARN_ROLE_3_ID = 1529363013382176830

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

    # --- أمر التحذير التصاعدي ---
    @app_commands.command(name="warn", description="تحذير عضو وإعطائه رتبة تحذير تصاعدية")
    @admin_only()
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد"):
        await interaction.response.defer(ephemeral=True)
        
        r1 = interaction.guild.get_role(WARN_ROLE_1_ID)
        r2 = interaction.guild.get_role(WARN_ROLE_2_ID)
        r3 = interaction.guild.get_role(WARN_ROLE_3_ID)

        if not r1 or not r2 or not r3:
            return await interaction.followup.send("❌ حدث خطأ: تأكد من صحة آي دي رتب التحذيرات في السيرفر.", ephemeral=True)

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
        
        r1 = interaction.guild.get_role(WARN_ROLE_1_ID)
        r2 = interaction.guild.get_role(WARN_ROLE_2_ID)
        r3 = interaction.guild.get_role(WARN_ROLE_3_ID)

        if not r1 or not r2 or not r3:
            return await interaction.followup.send("❌ حدث خطأ: تأكد من صحة آي دي رتب التحذيرات في السيرفر.", ephemeral=True)

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
        role = interaction.guild.get_role(PRISON_ROLE_ID)
        if not role:
            return await interaction.followup.send("❌ رتبة السجن غير موجودة، تأكد من آي دي الرتبة في الكود.", ephemeral=True)
        try:
            await member.add_roles(role)
            await interaction.followup.send(f"⛓️ تم سجن {member.mention} بنجاح.", ephemeral=True)
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
        except Exception:
            await interaction.followup.send("❌ حدث خطأ أثناء محاولة الإفراج عن العضو.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
