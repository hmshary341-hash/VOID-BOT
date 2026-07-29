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

  # --- 1. نظام مراقبة الإداريين (فك العقوبات) ---
  @commands.Cog.listener()
  async def on_audit_log_entry_create(self, entry):
    log_channel = self.bot.get_channel(self.log_channel_id)
    if not log_channel:
      return

    # رصد فك الحظر (Unban)
    if entry.action == discord.AuditLogAction.unban:
      admin = entry.user
      target = entry.target

      embed = discord.Embed(
          title="🚨 تنبيه: تم فك عقوبة عن عضو!",
          color=discord.Color.red(),
          timestamp=discord.utils.utcnow(),
      )
      embed.add_field(name="نوع الإجراء", value="فك باند", inline=False)
      embed.add_field(
          name="اسم الإداري", value=f"{admin.mention} (`{admin}`)", inline=False
      )
      embed.add_field(
          name="الشخص المفكوك عنه العقوبة",
          value=f"{target.mention} (`{target}`)",
          inline=False,
      )
      embed.set_footer(text="نظام مكافحة الفساد الإداري")
      await log_channel.send(embed=embed)

    # رصد إزالة التايم أوت (Timeout Removal)
    elif entry.action == discord.AuditLogAction.member_update:
      before = entry.before
      after = entry.after
      if (
          hasattr(before, "timed_out_until")
          and before.timed_out_until is not None
          and after.timed_out_until is None
      ):
        admin = entry.user
        target = entry.target

        embed = discord.Embed(
            title="🚨 تنبيه: تم فك عقوبة عن عضو!",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="نوع الإجراء", value="فك تايم أوت", inline=False)
        embed.add_field(
            name="اسم الإداري", value=f"{admin.mention} (`{admin}`)", inline=False
        )
        embed.add_field(
            name="الشخص المفكوك عنه العقوبة",
            value=f"{target.mention} (`{target}`)",
            inline=False,
        )
        embed.set_footer(text="نظام مكافحة الفساد الإداري")
        await log_channel.send(embed=embed)

  # --- 2. نظام الدفاع والتصدّي التلقائي للهجمات ---
  @commands.Cog.listener()
  async def on_member_join(self, member):
    global recent_joins  # تم وضعها في أول السطر لحل المشكلة نهائياً

    if member.bot:
      current_time = time.time()
      recent_joins.append(current_time)
      recent_joins = [t for t in recent_joins if current_time - t < 5]

      # إذا دخل أكثر من 4 بوتات دفعة واحدة في أقل من 5 ثوانٍ
      if len(recent_joins) >= 4:
        guild = member.guild
        log_channel = guild.get_channel(self.log_channel_id)

        # قفل الرومات عن العامة مع استثناء رتب الإدارة الخاصة بكم
        for channel in guild.text_channels:
          await channel.set_permissions(guild.default_role, send_messages=False)
          for role_id in self.management_roles:
            role = guild.get_role(role_id)
            if role:
              await channel.set_permissions(role, send_messages=True)

        if log_channel:
          embed_alert = discord.Embed(
              title="🚨 إنذار هجوم بوتات وهمية (Raid Detected)!",
              description=(
                  "تم رصد هجوم وتم قفل السيرفر **تلقائياً**.\n"
                  "🛡️ **غرفة العمليات:** تم ترك الرومات مفتوحة لكم (أنت،"
                  " خويك، ونائبتك) للسيطرة على الوضع."
              ),
              color=discord.Color.dark_red(),
              timestamp=discord.utils.utcnow(),
          )
          await log_channel.send(embed=embed_alert)

      # حظر البوت المهاجم تلقائياً
      try:
        await member.ban(reason="هجوم بوتات وهمية (Auto-Raid Ban)")
      except:
        pass

  # --- 3. أمر فتح السيرفر ---
  @commands.command(name="unlock")
  @commands.has_permissions(administrator=True)
  async def unlock(self, ctx):
    for channel in ctx.guild.text_channels:
      await channel.set_permissions(ctx.guild.default_role, send_messages=True)
      for role_id in self.management_roles:
        role = ctx.guild.get_role(role_id)
        if role:
          await channel.set_permissions(role, overwrite=None)

    embed = discord.Embed(
        title="✅ تم إلغاء وضع الطوارئ",
        description="تم فتح الكتابة في جميع الرومات للجميع. عاد كل شيء لطبيعته.",
        color=discord.Color.green(),
    )
    await ctx.send(embed=embed)


async def setup(bot):
  await bot.add_cog(AntiNuke(bot))
