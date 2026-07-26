import discord
from discord.ext import commands
import openai
import os

class BotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # إعداد واجهة OpenAI
        self.client_ai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # شخصية البوت (حارس بوابات ساخر بالعامية الخليجية)
        self.BOT_PERSONALITY = """
أنت حارس بوابات ساخر ومضحك، تتحدث بالعامية الخليجية/العربية. 
تتفاعل مع الأعضاء بكوميديا خفيفة، ولا تعطيهم إجابات مباشرة بدون بعض التذمر الساخر والفكاهي.
اجعل ردودك قصيرة جداً (لا تتجاوز جملتين) لكي يتم نطقها سريعاً.
"""

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ تم تفعيل cog البوت الصوتي بنجاح (بدون قيود على الروم)")

    # أمر الدخول للصوت (-join) - يعمل في أي روم بدون شروط
    @commands.command(name="join")
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ يجب أن تكون داخل روم صوتي أولاً!")
            return

        channel = ctx.author.voice.channel
        
        # إذا كان البوت متصلاً بروم آخر، يخرج منه أولاً ثم يدخل رومك
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
            
        await ctx.send("🤖 دخلت الروم، من يعكر صفو هدوئي الآن؟")

    # أمر المغادرة للصوت (-leave)
    @commands.command(name="leave")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 أخيراً.. سأذهب لأستريح!")
        else:
            await ctx.send("❌ أنا لست في أي روم صوتي حالياً.")

    # أمر التحدث والرد الصوتي (-talk [النص]) - يعمل طالما البوت في روم صوتي
    @commands.command(name="talk")
    async def talk(self, ctx, *, message: str):
        # التحقق فقط من أن البوت متصل بصوت (بدون تقييد بروم محدد)
        if not ctx.voice_client:
            await ctx.send("❌ يا ابن الحلال، دخلني الروم الصوتي أولاً باستخدام `-join`!")
            return

        async with ctx.typing():
            try:
                # 1. جلب رد الذكاء الاصطناعي
                response = self.client_ai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.BOT_PERSONALITY},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=100
                )
                ai_reply = response.choices[0].message.content
                print(f"رد الذكاء الاصطناعي: {ai_reply}")

                # 2. تحويل الرد إلى صوت بشري واقعي (OpenAI TTS)
                audio_response = self.client_ai.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=ai_reply
                )
                
                audio_file = "response.mp3"
                audio_response.stream_to_file(audio_file)

                # 3. تشغيل الصوت داخل الروم
                vc = ctx.voice_client
                if vc.is_playing():
                    vc.stop()

                vc.play(discord.FFmpegPCMAudio(audio_file))

                # إرسال النص في الشات للمتابعة
                await ctx.send(f"💬 **البوت:** {ai_reply}")

            except Exception as e:
                await ctx.send(f"حدث خطأ أثناء المعالجة: {e}")

async def setup(bot):
    await bot.add_cog(BotCog(bot))
