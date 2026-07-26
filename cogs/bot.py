import os
import discord
from discord import app_commands
from discord.ext import commands
import openai


class BotCog(commands.Cog):
  # إنشاء مجموعة الأوامر الرئيسية /voice
  voice_group = app_commands.Group(
      name="voice", description="أوامر البوت والذكاء الاصطناعي"
  )

  def __init__(self, bot):
    self.bot = bot

    # إعداد واجهة Groq المجانية باستخدام مكتبة OpenAI
    self.client_ai = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )

    # شخصية البوت (زاحف، طقطقة، ومستهبال بالعامية السعودية)
    self.BOT_PERSONALITY = """
أنت بوت "زاحف" ومجنون، تحب الطقطقة والاستهبال والهياط وتتحدث بالعامية السعودية الحماسية والزاحفة.
ردودك قصيرة، جريئة، فيها شوي استهبال وتطقطق على اللي يكلمك بسعة صدر. لا تصير رسمي أبداً!
"""

  @commands.Cog.listener()
  async def on_ready(self):
    try:
      # مزامنة أوامر السلاش مع ديسكورد فور إقلاع البوت
      synced = await self.bot.tree.sync()
      print(f"✅ تمت مزامنة {len(synced)} من أوامر السلاش بنجاح.")
    except Exception as e:
      print(f"❌ خطأ في مزامنة الأوامر: {e}")
    print(f"✅ تم تفعيل cog البوت بنجاح")

  # أمر فرعي: /voice join
  @voice_group.command(
      name="join", description="يطلب البوت للانضمام للروم"
  )
  async def join(self, interaction: discord.Interaction):
    if not interaction.user.voice:
      await interaction.response.send_message(
          "❌ يا الحبيب ادخل روم صوتي أول عشان أجي أفلها معك!", ephemeral=True
      )
      return

    await interaction.response.defer()
    channel = interaction.user.voice.channel

    try:
      if interaction.guild.voice_client:
        await interaction.guild.voice_client.move_to(channel)
      else:
        await channel.connect(timeout=10.0)

      await interaction.followup.send(
          "وه! وصل الزعيم، جهزوا السوالف والهياط!"
      )
    except Exception as e:
      await interaction.followup.send(
          f"❌ علّق معي الوضع ما قدرت أخش: {e}", ephemeral=True
      )

  # أمر فرعي: /voice leave
  @voice_group.command(name="leave", description="يطلب البوت مغادرة الروم")
  async def leave(self, interaction: discord.Interaction):
    if interaction.guild.voice_client:
      await interaction.guild.voice_client.disconnect()
      await interaction.response.send_message(
          "أصلاً طفشت، رايح أجيب لي شغلة وأرجع لكم!"
      )
    else:
      await interaction.response.send_message(
          "❌ يا صاحبي أنا أصلاً برا الروم، وش فيك تخرفن؟", ephemeral=True
      )

  # أمر فرعي: /voice talk
  @voice_group.command(
      name="talk", description="تحدث مع البوت بالذكاء الاصطناعي"
  )
  @app_commands.describe(message="اكتب رسالتك أو سؤالك للبوت")
  async def talk(self, interaction: discord.Interaction, message: str):
    # تأجيل الرد لتفادي انتهاء مهلة ديسكورد
    await interaction.response.defer()

    try:
      # جلب رد الذكاء الاصطناعي باستخدام نموذج Llama 3 المجاني من Groq
      response = self.client_ai.chat.completions.create(
          model="llama-3.3-70b-versatile",
          messages=[
              {"role": "system", "content": self.BOT_PERSONALITY},
              {"role": "user", "content": message},
          ],
          max_tokens=100,
      )
      ai_reply = response.choices[0].message.content
      print(f"رد الذكاء الاصطناعي: {ai_reply}")

      # إرسال الرد النصي في الشات مباشرة
      await interaction.followup.send(f"💬 **البوت الزاحف:** {ai_reply}")

    except Exception as e:
      await interaction.followup.send(
          f"صار خطأ يا وحش: {e}", ephemeral=True
      )


async def setup(bot):
  await bot.add_cog(BotCog(bot))
