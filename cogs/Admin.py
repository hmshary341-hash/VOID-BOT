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
    "Support Staff",
]

# --- أسماء رتب السجن والتحذيرات ---
PRISON_ROLE_NAME = "Prison"  # اسم رتبة السجن

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

    await interaction.response.send_message(
        "❌ عذراً، هذا الأمر مخصص للإدارة العليا وطاقم الدعم (Support) فقط.",
        ephemeral=True,
    )
    return False

  return app_commands.check(predicate)


class Admin(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  # تعريف مجموعة أوامر الإدارة الأساسية
  admin = app_commands.Group(
      name="admin", description="أوامر الإدارة والإشراف والعقوبات"
  )

  # ==========================================
  # 1. أوامر التحذير وإزالتها (Warn & Unwarn)
  # ==========================================
  @admin.command(
      name="warn", description="تحذير عضو وإعطائه رتبة تحذير تصاعدية"
  )
  @admin_only()
  async def warn(
      self,
      interaction: discord.Interaction,
      member: discord.Member,
      reason: str = "لا يوجد",
  ):
    await interaction.response.defer(ephemeral=True)

    r1 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_1_NAME)
    r2 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_2_NAME)
    r3 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_3_NAME)

    if not r1 or not r2 or not r3:
      return await interaction.followup.send(
          "❌ حدث خطأ: تأكد من صحة أسماء رتب التحذيرات في السيرفر.",
          ephemeral=True,
      )

    try:
      if r3 in member.roles:
        await interaction.followup.send(
            f"⚠️ العضو {member.mention} لديه بالفعل **تحذير 3** (الحد الأقصى).",
            ephemeral=True,
        )
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

      await interaction.followup.send(
          f"⚠️ تم إعطاء {member.mention} **{warning_level}** بنجاح. السبب:"
          f" {reason}",
          ephemeral=True,
      )

      try:
        await member.send(
            f"⚠️ لقد تلقيت **{warning_level}** في سيرفر"
            f" **{interaction.guild.name}**.\nالسبب: {reason}"
        )
      except:
        pass

    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ، تأكد أن رتبة البوت أعلى من رتب التحذيرات والرتبة"
          " المستهدفة.",
          ephemeral=True,
      )

  @admin.command(
      name="unwarn", description="إزالة تحذير من العضو (تخفيض مستوى التحذير)"
  )
  @admin_only()
  async def unwarn(
      self,
      interaction: discord.Interaction,
      member: discord.Member,
      reason: str = "لا يوجد",
  ):
    await interaction.response.defer(ephemeral=True)

    r1 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_1_NAME)
    r2 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_2_NAME)
    r3 = discord.utils.get(interaction.guild.roles, name=WARN_ROLE_3_NAME)

    if not r1 or not r2 or not r3:
      return await interaction.followup.send(
          "❌ حدث خطأ: تأكد من صحة أسماء رتب التحذيرات في السيرفر.",
          ephemeral=True,
      )

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
        return await interaction.followup.send(
            f"❌ العضو {member.mention} ليس لديه أي تحذيرات لإزالتها.",
            ephemeral=True,
        )

      await interaction.followup.send(
          f"✅ تم تحديث حالة العضو {member.mention} وأصبح الآن:"
          f" **{warning_level}**. السبب: {reason}",
          ephemeral=True,
      )

      try:
        await member.send(
            f"✅ تم تخفيض أو إزالة تحذير منك في سيرفر"
            f" **{interaction.guild.name}**.\nالحالة الجديدة:"
            f" **{warning_level}**\nالسبب: {reason}"
        )
      except:
        pass

    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ،
