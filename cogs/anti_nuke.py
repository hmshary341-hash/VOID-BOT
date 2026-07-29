# Refresh Update - لتحديث البوت وإلغاء التعليق وتوسيع نظام اللوجز
import time
import discord
from discord.ext import commands

# متغير عام لتتبع هجمات البوتات الوهمية
recent_joins = []


class AntiNuke(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.log_channel_id = 1531827585216937994
    self.management_roles = [
        1531823302824427561,  # رتبتك
        1531824107413573763,  # رتبة خويك
        1531824508770455683,  # رتبة نائبتك
    ]

  # دالة مساعدة لجلب روم اللوق بشكل مضمون
  async def get_log_channel(self):
    channel = self.bot.get_channel(self.log_channel_id)
    if not channel:
      try:
        channel = await self.bot.fetch_channel(self.log_channel_id)
      except Exception:
        pass
    return channel

  # --- 1. نظام مراقبة الإداريين الشامل (العقوبات، السجن، وإزالتها) ---
  @commands.Cog.listener()
  async def on_audit_log_entry_create(self, entry):
    try:
      log_channel = await self.get_log_channel()
      if not log_channel:
        return

      admin = entry.user

      # تجاهل إذا كان الإجراء صادر من نفس البوت لمنع التداخل
      if admin and self.bot.user and admin.id == self.bot.user.id:
        return

      admin_str = (
          f"{admin.mention} (`{admin}`)" if admin else "إداري غير معروف"
      )
      target_str = (
          f"{entry.target.mention} (`{entry.target}`)"
          if entry.target
          else "عضو غير معروف"
      )

      # أ) رصد الباند (Ban)
      if entry.action == discord.AuditLogAction.ban:
        embed = discord.Embed(
            title="🚨 تنبيه: تم إعطاء عقوبة (باند)!",
            color=discord.Color.dark_red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="نوع الإجراء", value="باند", inline=False)
        embed.add_field(name="اسم الإداري", value=admin_str, inline=False)
        embed.add_field(name="العضو المعاقب", value=target_str, inline=False)
        embed.set_footer(text="نظام مراقبة الإدارة")
        await log_channel.send(embed=embed)

      # ب) رصد فك الباند (Unban)
      elif entry.action == discord.AuditLogAction.unban:
        embed = discord.Embed(
            title="🚨 تنبيه: تم فك عقوبة عن عضو!",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="نوع الإجراء", value="فك باند", inline=False)
        embed.add_field(
            name="اسم الإداري (الذي أزال العقوبة)",
            value=admin_str,
            inline=False,
        )
        embed.add_field(
            name="الشخص المفكوك عنه العقوبة", value=target_str, inline=False
        )
        embed.set_footer(text="نظام مراقبة الإدارة")
        await log_channel.send(embed=embed)

      # ج) رصد الكيك (Kick)
      elif entry.action == discord.AuditLogAction.kick:
        embed = discord.Embed(
            title="🚨 تنبيه: تم طرد عضو (كيك)!",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="نوع الإجراء", value="كيك (طرد)", inline=False)
        embed.add_field(name="اسم الإداري", value=admin_str, inline=False)
        embed.add_field(name="العضو المطرود", value=target_str, inline=False)
        embed.set_footer(text="نظام مراقبة الإدارة")
        await log_channel.send(embed=embed)

      # د) رصد التايم أوت (إعطاء أو إزالة)
      elif entry.action == discord.AuditLogAction.member_update:
        before = entry.before
        after = entry.after

        before_timeout = getattr(before, "communication_disabled_until", None)
        after_timeout = getattr(after, "communication_disabled_until", None)

        if before_timeout is None and after_timeout is not None:
          embed = discord.Embed(
              title="🚨 تنبيه: تم إعطاء عقوبة (تايم أوت)!",
              color=discord.Color.orange(),
              timestamp=discord.utils.utcnow(),
          )
          embed.add_field(name="نوع الإجراء", value="تايم أوت", inline=False)
          embed.add_field(name="اسم الإداري", value=admin_str, inline=False)
          embed.add_field(name="العضو المعاقب", value=target_str, inline=False)
          embed.set_footer(text="نظام مراقبة الإدارة")
          await log_channel.send(embed=embed)

        elif before_timeout is not None and after_timeout is None:
          embed = discord.Embed(
              title="🚨 تنبيه: تم فك عقوبة عن عضو!",
              color=discord.Color.blue(),
              timestamp=discord.utils.utcnow(),
          )
          embed.add_field(name="نوع الإجراء", value="فك تايم أوت", inline=False)
          embed.add_field(
              name="اسم الإداري (الذي أزال العقوبة)",
              value=admin_str,
              inline=False,
          )
          embed.add_field(
              name="الشخص المفكوك عنه العقوبة", value=target_str, inline=False
          )
          embed.set_footer(text="نظام مراقبة الإدارة")
          await log_channel.send(embed=embed)

      # هـ) رصد السجن/فك السجن وتعديل الرتب (Jail / Role Updates)
      elif entry.action == discord.AuditLogAction.member_role_update:
        # تتبع إضافة أو إزالة الرتب (مثل رتبة السجن)
        changes = entry.changes
        for change in changes:
          if change.key == "roles":
            # يمكن معرفة الرتب المضافة أو المزالة عبر التغييرات
            before_roles = change.before if hasattr(change, "before") else []
            after_roles = change.after if hasattr(change, "after") else []
            
            added_roles = [r for r in after_roles if r not in before_roles]
            removed_roles = [r for r in before_roles if r not in after_roles]

            for role in added_roles:
              embed = discord.Embed(
                  title="🚨 تنبيه: تم إعطاء رتبة / سجن عضو!",
                  color=discord.Color.purple(),
                  timestamp=discord.utils.utcnow(),
              )
              embed.add_field(name="نوع الإجراء", value="تعديل رتب / سجن", inline=False)
              embed.add_field(name="اسم الإداري", value=admin_str, inline=False)
              embed.add_field(name="العضو", value=target_str, inline=False)
              embed.add_field(name="الرتبة المضافة", value=f"`{role.name}`", inline=False)
              embed.set_footer(text="نظام مراقبة الإدارة")
              await log_channel.send(embed=embed)

            for role in removed_roles:
              embed = discord.Embed(
                  title="🚨 تنبيه: تم إزالة رتبة / فك سجن عن عضو!",
                  color=discord.Color.teal(),
                  timestamp=discord.utils.utcnow(),
              )
              embed.add_field(name="نوع الإجراء", value="إزالة رتبة / فك سجن", inline=False)
              embed.add_field(name="اسم الإداري (المسؤول)", value=admin_str, inline=False)
              embed.add_field(name="العضو", value=target_str, inline=False)
              embed.add_field(name="الرتبة المزالة", value=f"`{role.name}`", inline=False)
              embed.set_footer(text="نظام مراقبة الإدارة")
              await log_channel.send(embed=embed)

    except Exception as e:
      print(f"❌ خطأ في نظام مراقبة السجل: {e}")

  # --- 2. نظام أوامر التحذيرات (Warnings & Unwarnings) ---
  @commands.command(name="warn")
  @commands.has_permissions(kick_members=True)
  async def warn_member(self, ctx, member: discord.Member, *, reason="بدون سبب"):
    log_channel = await self.get_log_channel()
    
    embed = discord.Embed(
        title="⚠️ تنبيه: تم تحذير عضو!",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="نوع الإجراء", value="تحذير (Warn)", inline=False)
    embed.add_field(name="الإداري المحذر", value=f"{ctx.author.mention} (`{ctx.author}`)", inline=False)
    embed.add_field(name="العضو المحذر", value=f"{member.mention} (`{member}`)", inline=False)
    embed.add_field(name="السبب", value=reason, inline=False)
    embed.set_footer(text="نظام التحذيرات الإدارية")
    
    if log_channel:
      await log_channel.send(embed=embed)
    
    await ctx.send(f"✅ تم تحذير العضو {member.mention} بنجاح وتسجيل ذلك في اللوجز.", delete_after=5)

  @commands.command(name="unwarn", name_aliases=["delwarn"])
  @commands.has_permissions(kick_members=True)
  async def unwarn_member(self, ctx, member: discord.Member, *, reason="إلغاء التحذير"):
    log_channel = await self.get_log_channel()
    
    embed = discord.Embed(
        title="♻️ تنبيه: تم إزالة تحذير عن عضو!",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="نوع الإجراء", value="إلغاء تحذير (Unwarn)", inline=False)
    embed.add_field(name="الإداري المسؤول", value=f"{ctx.author.mention} (`{ctx.author}`)", inline=False)
    embed.add_field(name="العضو", value=f"{member.mention} (`{member}`)", inline=False)
    embed.add_field(name="التفاصيل/السبب", value=reason, inline=False)
    embed.set_footer(text="نظام التحذيرات الإدارية")
    
    if log_channel:
      await log_channel.send(embed=embed)
    
    await ctx.send(f"✅ تم إزالة التحذير عن العضو {member.mention} بنجاح وتسجيل ذلك في اللوجز.", delete_after=5)

  # --- 3. نظام الدفاع والتصدّي التلقائي للهجمات ---
  @commands.Cog.listener()
  async def on_member_join(self, member):
    global recent_joins

    if member.bot:
      current_time = time.time()
      recent_joins.append(current_time)
      recent_joins = [t for t in recent_joins if current_time - t < 5]

      if len(recent_joins) >= 4:
        guild = member.guild
        log_channel = await self.get_log_channel()

        for channel in guild.text_channels:
          try:
            await channel.set_permissions(guild.default_role, send_messages=False)
            for role_id in self.management_roles:
              role = guild.get_role(role_id)
              if role:
                await channel.set_permissions(role, send_messages=True)
          except Exception:
            pass

        if log_channel:
          embed_alert = discord.Embed(
              title="🚨 إنذار هجوم بوتات وهمية (Raid Detected)!",
              description=(
                  "تم رجوم هجوم وتم قفل السيرفر **تلقائياً**.\n"
                  "🛡️ **غرفة العمليات:** تم ترك الرومات مفتوحة لكم للسيطرة على"
                  " الوضع."
              ),
              color=discord.Color.dark_red(),
              timestamp=discord.utils.utcnow(),
          )
          await log_channel.send(embed=embed_alert)

      try:
        await member.ban(reason="هجوم بوتات وهمية (Auto-Raid Ban)")
      except:
        pass

  # --- 4. أمر فتح السيرفر (Unlock) ---
  @commands.command(name="unlock")
  @commands.has_permissions(administrator=True)
  async def unlock(self, ctx):
    for channel in ctx.guild.text_channels:
      try:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        for role_id in self.management_roles:
          role = ctx.guild.get_role(role_id)
          if role:
            await channel.set_permissions(role, send_messages=True)
      except Exception:
        pass

    embed = discord.Embed(
        title="✅ تم إلغاء وضع الطوارئ",
        description="تم فتح الكتابة في جميع الرومات للجميع. عاد كل شيء لطبيعته.",
        color=discord.Color.green(),
    )
    await ctx.send(embed=embed)


async def setup(bot):
  await bot.add_cog(AntiNuke(bot))
