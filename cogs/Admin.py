import datetime
import discord
from discord import app_commands
from discord.ext import commands

# --- الإعدادات (آي دي الرتب المسموح لها حصرياً بالأوامر) ---
ALLOWED_ROLE_IDS = [
    1531823302824427561,  # رتبتك
    1531824508770455683,  # رتبة نائبتك
    1531824107413573763,  # رتبة نائبك
    1529997933011795968,  # آي دي إدارة الدعم
    1529998973539057785,  # الآي دي الأول
    1529999244155420763,  # الآي دي الثاني
]

ALLOWED_USER_IDS = []

# --- أسماء رتب السجن والتحذيرات ---
PRISON_ROLE_NAME = "Prison"
WARN_ROLE_1_NAME = "تحذير 1"
WARN_ROLE_2_NAME = "تحذير 2"
WARN_ROLE_3_NAME = "تحذير 3"


# --- دالة التحقق من الصلاحية عبر الأي دي ---
def admin_only():
  async def predicate(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
      return True
    if interaction.user.id in ALLOWED_USER_IDS:
      return True
    user_role_ids = [role.id for role in interaction.user.roles]
    if any(role_id in user_role_ids for role_id in ALLOWED_ROLE_IDS):
      return True

    await interaction.response.send_message(
        "❌ عذراً، هذا الأمر مخصص للإدارة العليا وطاقم الدعم فقط.",
        ephemeral=True,
    )
    return False

  return app_commands.check(predicate)


class Admin(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

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

    full_reason = f"بواسطة: {interaction.user} | السبب: {reason}"

    try:
      if r3 in member.roles:
        return await interaction.followup.send(
            f"⚠️ العضو {member.mention} لديه بالفعل **تحذير 3** (الحد الأقصى).",
            ephemeral=True,
        )
      elif r2 in member.roles:
        await member.remove_roles(r2, reason=full_reason)
        await member.add_roles(r3, reason=full_reason)
        warning_level = "تحذير 3"
      elif r1 in member.roles:
        await member.remove_roles(r1, reason=full_reason)
        await member.add_roles(r2, reason=full_reason)
        warning_level = "تحذير 2"
      else:
        await member.add_roles(r1, reason=full_reason)
        warning_level = "تحذير 1"

      await interaction.followup.send(
          f"⚠️ تم إعطاء {member.mention} **{warning_level}** بنجاح. السبب: {reason}",
          ephemeral=True,
      )

      try:
        await member.send(
            f"⚠️ لقد تلقيت **{warning_level}** في سيرفر **{interaction.guild.name}**.\nالسبب: {reason}"
        )
      except:
        pass

    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ، تأكد أن رتبة البوت أعلى من رتب التحذيرات والرتبة المستهدفة.",
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

    full_reason = f"بواسطة: {interaction.user} | السبب: {reason}"

    try:
      if r3 in member.roles:
        await member.remove_roles(r3, reason=full_reason)
        await member.add_roles(r2, reason=full_reason)
        warning_level = "تحذير 2 (تخفيض)"
      elif r2 in member.roles:
        await member.remove_roles(r2, reason=full_reason)
        await member.add_roles(r1, reason=full_reason)
        warning_level = "تحذير 1 (تخفيض)"
      elif r1 in member.roles:
        await member.remove_roles(r1, reason=full_reason)
        warning_level = "إزالة جميع التحذيرات"
      else:
        return await interaction.followup.send(
            f"❌ العضو {member.mention} ليس لديه أي تحذيرات لإزالتها.",
            ephemeral=True,
        )

      await interaction.followup.send(
          f"✅ تم تحديث حالة العضو {member.mention}. السبب: {reason}",
          ephemeral=True,
      )

      try:
        await member.send(
            f"✅ تم تخفيض أو إزالة تحذير منك في سيرفر **{interaction.guild.name}**.\nالسبب: {reason}"
        )
      except:
        pass

    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ، تأكد أن رتبة البوت أعلى من رتب التحذيرات والرتبة المستهدفة.",
          ephemeral=True,
      )

  # ==========================================
  # 2. أوامر الإسكات وفك الإسكات (Timeout & Untimeout)
  # ==========================================
  @admin.command(name="timeout", description="إسكات عضو (تايم أوت)")
  @admin_only()
  async def timeout(
      self,
      interaction: discord.Interaction,
      member: discord.Member,
      minutes: int,
      reason: str = "لا يوجد",
  ):
    await interaction.response.defer(ephemeral=True)
    full_reason = f"بواسطة: {interaction.user} | السبب: {reason}"
    try:
      await member.timeout(
          datetime.timedelta(minutes=minutes), reason=full_reason
      )
      await interaction.followup.send(
          f"🔇 تم إسكات {member.mention} بنجاح.", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ: تأكد أن رتبة البوت أعلى من العضو المراد إسكاته.",
          ephemeral=True,
      )

  @admin.command(name="untimeout", description="فك السكات عن عضو")
  @admin_only()
  async def untimeout(
      self, interaction: discord.Interaction, member: discord.Member
  ):
    await interaction.response.defer(ephemeral=True)
    full_reason = f"بواسطة: {interaction.user} | فك التايم أوت"
    try:
      await member.timeout(None, reason=full_reason)
      await interaction.followup.send(
          f"✅ تم فك السكات عن {member.mention}.", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ أثناء محاولة فك السكات.", ephemeral=True
      )

  # ==========================================
  # 3. أوامر الحظر وفك الحظر (Ban & Unban)
  # ==========================================
  @admin.command(name="ban", description="حظر عضو نهائياً من السيرفر")
  @admin_only()
  async def ban(
      self,
      interaction: discord.Interaction,
      member: discord.Member,
      reason: str = "لا يوجد",
  ):
    await interaction.response.defer(ephemeral=True)
    full_reason = f"بواسطة: {interaction.user} | السبب: {reason}"
    try:
      await member.ban(reason=full_reason)
      await interaction.followup.send(
          f"🔨 تم حظر {member.mention} بنجاح.", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ أثناء محاولة الحظر.", ephemeral=True
      )

  @admin.command(name="unban", description="فك الحظر عن مستخدم بواسطة الآي دي")
  @admin_only()
  async def unban(self, interaction: discord.Interaction, user_id: str):
    await interaction.response.defer(ephemeral=True)
    try:
      target_id = int(user_id.strip("<@!>"))
      user = await self.bot.fetch_user(target_id)
      full_reason = f"بواسطة: {interaction.user} | فك الحظر"
      await interaction.guild.unban(user, reason=full_reason)
      await interaction.followup.send(
          "✅ تم فك الحظر عن المستخدم بنجاح.", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ، تأكد من صحة الآي دي المدخل.", ephemeral=True
      )

  # ==========================================
  # 4. أوامر السجن والإفراج (Prison & Unprison)
  # ==========================================
  @admin.command(name="prison", description="سجن عضو")
  @admin_only()
  async def prison(
      self, interaction: discord.Interaction, member: discord.Member
  ):
    await interaction.response.defer(ephemeral=True)
    role = discord.utils.get(interaction.guild.roles, name=PRISON_ROLE_NAME)
    if not role:
      return await interaction.followup.send(
          "❌ رتبة السجن غير موجودة، تأكد من مطابقة اسم الرتبة في الكود.",
          ephemeral=True,
      )
    full_reason = f"بواسطة: {interaction.user} | سجن"
    try:
      await member.add_roles(role, reason=full_reason)
      await interaction.followup.send(
          f"⛓️ تم سجن {member.mention} بنجاح.", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ، تأكد أن رتبة البوت أعلى من رتبة السجن والرتبة المستهدفة.",
          ephemeral=True,
      )

  @admin.command(name="unprison", description="الإفراج عن عضو من السجن")
  @admin_only()
  async def unprison(
      self, interaction: discord.Interaction, member: discord.Member
  ):
    await interaction.response.defer(ephemeral=True)
    role = discord.utils.get(interaction.guild.roles, name=PRISON_ROLE_NAME)
    if not role:
      return await interaction.followup.send(
          "❌ رتبة السجن غير موجودة، تأكد من مطابقة اسم الرتبة في الكود.",
          ephemeral=True,
      )
    full_reason = f"بواسطة: {interaction.user} | إفراج من السجن"
    try:
      await member.remove_roles(role, reason=full_reason)
      await interaction.followup.send(
          f"🔓 تم الإفراج عن {member.mention} بنجاح.", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ أثناء محاولة الإفراج عن العضو.", ephemeral=True
      )

  # ==========================================
  # 5. أوامر قفل وفتح الشات (Lock & Unlock)
  # ==========================================
  @app_commands.command(
      name="قفل", description="قفل الشات الحالي لمنع الأعضاء من الكتابة"
  )
  @admin_only()
  async def lock(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    try:
      await channel.set_permissions(
          interaction.guild.default_role,
          send_messages=False,
          reason=f"بواسطة: {interaction.user}",
      )
      await interaction.followup.send("🔒 تم قفل الشات بنجاح.", ephemeral=True)
      await channel.send("🔒 **تم قفل هذه القناة من قبل الإدارة.**")
    except Exception as e:
      await interaction.followup.send(
          f"❌ حدث خطأ أثناء قفل القناة: `{e}`", ephemeral=True
      )

  @app_commands.command(
      name="فتح", description="فتح الشات الحالي والسماح للأعضاء بالكتابة"
  )
  @admin_only()
  async def unlock(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    try:
      await channel.set_permissions(
          interaction.guild.default_role,
          send_messages=True,
          reason=f"بواسطة: {interaction.user}",
      )
      await interaction.followup.send("🔓 تم فتح الشات بنجاح.", ephemeral=True)
      await channel.send("🔓 **تم فتح هذه القناة.**")
    except Exception as e:
      await interaction.followup.send(
          f"❌ حدث خطأ أثناء فتح القناة: `{e}`", ephemeral=True
      )

  # ==========================================
  # 6. أوامر إخفاء وإظهار القنوات (Hide & Show)
  # ==========================================
  @admin.command(name="hide", description="إخفاء القناة الحالية عن الأعضاء")
  @admin_only()
  async def hide(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        view_channel=False,
        reason=f"بواسطة: {interaction.user}",
    )
    await interaction.followup.send("🙈 تم إخفاء القناة.", ephemeral=True)

  @admin.command(name="show", description="إظهار القناة الحالية للأعضاء")
  @admin_only()
  async def show(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        view_channel=True,
        reason=f"بواسطة: {interaction.user}",
    )
    await interaction.followup.send("👁️ تم إظهار القناة.", ephemeral=True)

  # ==========================================
  # 7. الأوامر الأخرى الفردية (Kick, Clear, ModHistory)
  # ==========================================
  @admin.command(name="kick", description="طرد عضو من السيرفر")
  @admin_only()
  async def kick(
      self,
      interaction: discord.Interaction,
      member: discord.Member,
      reason: str = "لا يوجد",
  ):
    await interaction.response.defer(ephemeral=True)
    full_reason = f"بواسطة: {interaction.user} | السبب: {reason}"
    try:
      await member.kick(reason=full_reason)
      await interaction.followup.send(
          f"🦵 تم طرد {member.mention} بنجاح.", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ أثناء محاولة الطرد.", ephemeral=True
      )

  @admin.command(name="clear", description="حذف عدد من الرسائل في القناة")
  @admin_only()
  async def clear(self, interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    try:
      deleted = await interaction.channel.purge(limit=amount)
      await interaction.followup.send(
          f"🗑️ تم حذف {len(deleted)} رسالة بنجاح.", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ، تأكد أن الرسائل قابلة للحذف وليست قديمة جداً.",
          ephemeral=True,
      )

  @admin.command(
      name="modhistory",
      description="فحص سجلات العضو الرسمية مع إظهار اسم الإداري ونوع العقوبة",
  )
  @admin_only()
  async def modhistory(
      self, interaction: discord.Interaction, member: discord.Member
  ):
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title=f"📜 سجل العقوبات المنظم لـ {member.display_name}",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )

    bans = []
    timeouts = []
    prisons = []
    kicks = []
    warns = []

    try:
      async for entry in interaction.guild.audit_logs(limit=150):
        if entry.target and entry.target.id == member.id:
          moderator = entry.user
          reason = entry.reason or "لا يوجد سبب مسجل"
          mod_name = moderator.mention if moderator else "مجهول"

          if entry.action == discord.AuditLogAction.ban:
            bans.append(f"🔨 **المسؤول:** {mod_name}\n📝 **السبب:** {reason}")

          elif entry.action == discord.AuditLogAction.member_update:
            if entry.after and getattr(
                entry.after, "communication_disabled_until", None
            ):
              timeout_until = entry.after.communication_disabled_until
              timeouts.append(
                  f"🔇 **المسؤول:** {mod_name}\n⏳ **حتى وقت:** {timeout_until.strftime('%Y-%m-%d %H:%M')}\n📝 **السبب:** {reason}"
              )

          elif entry.action == discord.AuditLogAction.kick:
            kicks.append(f"🦵 **المسؤول:** {mod_name}\n📝 **السبب:** {reason}")

          elif entry.action == discord.AuditLogAction.member_role_update:
            if entry.after and hasattr(entry.after, "roles") and entry.after.roles:
              role_names = [r.name for r in entry.after.roles]
              
              if PRISON_ROLE_NAME in role_names:
                prisons.append(f"⛓️ **المسؤول:** {mod_name}\n📝 **السبب:** {reason}")
              
              for r_name in [WARN_ROLE_1_NAME, WARN_ROLE_2_NAME, WARN_ROLE_3_NAME]:
                if r_name in role_names:
                  warns.append(f"⚠️ **المسؤول:** {mod_name} (الرتبة: {r_name})\n📝 **السبب:** {reason}")

      if bans:
        embed.add_field(name="🔨 سجل الباند (Ban)", value="\n\n".join(bans[:5]), inline=False)
      
      if timeouts:
        embed.add_field(name="🔇 سجل التايم أوت (Timeout)", value="\n\n".join(timeouts[:5]), inline=False)
      
      if prisons:
        embed.add_field(name="⛓️ سجل السجن (Prison)", value="\n\n".join(prisons[:5]), inline=False)
      
      if kicks:
        embed.add_field(name="🦵 سجل الكيك (Kick)", value="\n\n".join(kicks[:5]), inline=False)
        
      if warns:
        embed.add_field(name="⚠️ سجل التحذيرات (Warns)", value="\n\n".join(warns[:5]), inline=False)

      if not (bans or timeouts or prisons or kicks or warns):
        embed.description = "❌ لا توجد أي سجلات عقوبات مسجلة لهذا العضو في السيرفر حتى الآن."

      await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
      await interaction.followup.send(
          f"❌ حدث خطأ أثناء جلب السجلات:\n`{e}`", ephemeral=True
      )


async def setup(bot):
  await bot.add_cog(Admin(bot))
