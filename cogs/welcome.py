import discord
from discord.ext import commands

# --- الأيديات المحددة ---
WELCOME_CHANNEL_ID = 1530041963284529262
LEAVE_CHANNEL_ID = 1530301291182428250

ROLE_18_PLUS = 1530039168573636688
ROLE_18_MINUS = 1530039223485202442


class WelcomeLeaveCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  def get_age_group(self, member: discord.Member):
    """التحقق من الفئة العمرية بناءً على أيديات الرتب المحددة"""
    for role in member.roles:
      if role.id == ROLE_18_PLUS:
        return "فوق 18 (+18)"
      elif role.id == ROLE_18_MINUS:
        return "تحت 18 (-18)"
    return "غير محدد"

  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member):
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
      return

    age_group = self.get_age_group(member)

    embed = discord.Embed(
        title="✨ حيّ الله من طفا الضو وحضر ✨",
        description=(
            f"يا هلا ومية هلا، ويسلم راس من لفانا! 🇸🇦\n\n"
            f"حيّ الله الطارش الجديد **{member.mention}**، يا مرحبا بك يا طال"
            " عمرك بين إخوانك وفي دارك.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **الاسم:** {member.name}\n"
            f"🎂 **الفئة العمرية:** {age_group}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "يا مرحباً ترحيبةٍ تسبق الشوق ... ترجح بك كفوف الميازيب.\n"
            "أنست وشرفت، وعسى تواجدك معنا يكون فاتحة خير وبركة! ☕ عزّ الله"
            " إنك نورتنا."
        ),
        color=0xD4AF37,
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(
        text=f"سيرفر {member.guild.name} • نورتنا يالغالي",
        icon_url=member.guild.icon.url if member.guild.icon else None,
    )

    try:
      await channel.send(
          content=f"حيا الله {member.mention} 🤍", embed=embed
      )
    except Exception as e:
      print(f"❌ خطأ في إرسال رسالة الترحيب: {e}")

  @commands.Cog.listener()
  async def on_member_remove(self, member: discord.Member):
    channel = member.guild.get_channel(LEAVE_CHANNEL_ID)
    if not channel:
      return

    age_group = self.get_age_group(member)

    embed = discord.Embed(
        title="🚶‍♂️ مقفية دروبك يا غالي 🚶‍♂️",
        description=(
            f"عسىدرب السلامة يوصلك وين ما رحت يا **{member.name}**. 🇸🇦\n\n"
            f"غادرتنا اليوم، لكن الباب يبقى مفتوح لمن قدر العشرة والربع.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **الاسم:** {member.name}\n"
            f"🎂 **الفئة العمرية:** {age_group}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "ممشاك زين، وعسى الأيام تجمعتنا على خير وبركة مرة ثانية.\n"
            "درب السلامة وموفق في كل خطوة يا طويل العمر! ☕"
        ),
        color=0x8B0000,  # لون أحمر هادئ للمغادرة
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(
        text=f"سيرفر {member.guild.name} • في أمان الله",
        icon_url=member.guild.icon.url if member.guild.icon else None,
    )

    try:
      await channel.send(embed=embed)
    except Exception as e:
      print(f"❌ خطأ في إرسال رسالة المغادرة: {e}")


async def setup(bot):
  await bot.add_cog(WelcomeLeaveCog(bot))
