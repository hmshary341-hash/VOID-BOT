import os
import discord
from discord import app_commands
from discord.ext import commands
import openai


class BotCog(commands.Cog):
  # إنشاء مجموعة الأوامر الرئيسية /voice
  voice_group = app_commands.Group(
      name="voice", description="أوامر البوت الصوتي والذكاء الاصطناعي"
  )

  def __init__(self, bot):
    self.bot = bot

    # إعداد واجهة Groq المجانية باستخدام مكتبة OpenAI
    self.client_ai = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )

    # شخصية البوت (حارس بوابات ساخر بالعامية الخليجية)
    self.BOT_PERSONALITY = """
أنت حارس بوابات ساخر ومضحك، تتحدث بالعامية الخليجية/العربية. 
تتفاعل مع الأعضاء بكوميديا خفيفة، ولا تعطيهم إجابات مباشرة بدون بعض التذمر الساخر والفكاهي.
اجعل ردودك قصيرة جداً (لا تتجاوز جملتين).
"""

  @commands.Cog.listener()
  async def on_ready(self):
    try:
      # مزامنة أوامر السلاش مع ديسكورد فور إقلاع البوت
      synced = await self.bot.tree.sync()
      print(f"✅ تمت مزامنة {len(synced)} من أوامر السلاش بنجاح.")
    except Exception as e:
      print(f"❌ خطأ في مزامنة الأوامر: {e}")
    print(f"✅ تم تفعيل cog البوت الصوتي (أوامر فرعية تحت /voice) بنجاح")

  # أمر فرعي: /voice join
  @voice_group.command(
      name="join", description="يدخل البوت إلى الروم الصوتي الذي أنت فيه"
  )
  async def join(self, interaction: discord.Interaction):
    if not interaction.user.voice:
      await interaction.response.send_message(
          "❌ يجب أن تكون داخل روم صوتي أولاً!", ephemeral=True
      )
      return

    # تأجيل الرد فوراً لمنع خطأ انتهاء المهلة
    await interaction.response.defer()

    channel = interaction.user.voice.channel

    try:
      if interaction.guild.voice_client:
        await interaction.guild.voice_client.move_to(channel)
      else:
        await channel.connect(timeout=10.0)

      await interaction.followup.send(
          "🤖 دخلت الروم، من يعكر صفو هدوئي الآن؟"
      )
    except Exception as e:
      await interaction.followup.send(
          f"❌ فشل الاتصال بالروم الصوتي أو انتهت المهلة. الخطأ: {e}",
          ephemeral=True,
      )

  # أمر فرعي: /voice leave
  @voice_group.command(name="leave", description="يغادر البوت الروم الصوتي")
  async def leave(self, interaction: discord.Interaction):
    if interaction.guild.voice_client:
      await interaction.guild.voice_client.disconnect()
      await interaction.response.send_message("👋 أخيراً.. سأذهب لأستريح!")
    else:
      await interaction.response.send_message(
          "❌ أنا لست في أي روم صوتي حالياً.", ephemeral=True
      )

  # أمر فرعي: /voice talk
  @voice_group.command(
      name="talk", description="تحدث مع البوت الصوتي بالذكاء الاصطناعي"
  )
  @app_commands.describe(message="اكتب رسالتك أو سؤالك للبوت")
  async def talk(self, interaction: discord.Interaction, message: str):
    if not interaction.guild.voice_client:
      await interaction.response.send_message(
          "❌ يا ابن الحلال، دخلني الروم الصوتي أولاً باستخدام `/voice join`!",
          ephemeral=True,
      )
      return

    # تأجيل الرد لتفادي انتهاء مهلة ديسكورد
    await interaction.response.defer()

    try:
      # 1. جلب رد الذكاء الاصطناعي باستخدام نموذج Llama 3 المجاني من Groq
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

      # إرسال النص النتيجة في الشات
      await interaction.followup.send(f"💬 **البوت:** {ai_reply}")

    except Exception as e:
      await interaction.followup.send(
          f"حدث خطأ أثناء المعالجة: {e}", ephemeral=True
      )


async def setup(bot):
  await bot.add_cog(BotCog(bot))
