import discord
from discord.ext import commands

# --- آي دي روم البوستات ورتبة البوست ---
BOOST_CHANNEL_ID = 1530681348816375849
BOOST_ROLE_ID = 1530037784755179555


class BoostNotifier(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_member_update(
      self, before: discord.Member, after: discord.Member
  ):
    # التحقق مما إذا قام العضو بعمل بوست للسيرفر للتو
    if before.premium_since is None and after.premium_since is not None:
      guild = after.guild

      # 1. إعطاء رتبة البوست تلقائياً للعضو
      role = guild.get_role(BOOST_ROLE_ID)
      if role:
        try:
          await after.add_roles(role, reason="شكراً لعمل بوست للسيرفر")
        except Exception as e:
          print(f"❌ خطأ في إعطاء رتبة البوست: {e}")

      # 2. إرسال رسالة الشكر والقصيدة في روم البوستات المحددة
      channel = guild.get_channel(BOOST_CHANNEL_ID)
      if channel:
        poem = (
            "يا هلا باللي نوّر الدار وسـطـاها ... جاب البوست وطيب أفعاله"
            " طرأها\nأهلاً عدد ما ترعد وبرقها سـرى ... ياللي جودك يبين وما"
            " يخفى ضياها\nلك منّا الشكر يا راعي الوفا والزود ... يا عسى"
            " أيامك هنية ومسـعـودة"
        )

        message = (
            f"🎉 شكراً لك {after.mention} على البوست ما تقصر يا كحيلان!\n\n"
            f"**وذي قصيدة لعيونك:**\n> {poem}"
        )

        try:
          await channel.send(message)
        except Exception as e:
          print(f"❌ خطأ أثناء إرسال رسالة البوست: {e}")


async def setup(bot):
  await bot.add_cog(BoostNotifier(bot))
