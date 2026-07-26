import asyncio
import os
import discord
from discord.ext import commands
import openai

# --- الإعدادات الأساسية ---
DISCORD_TOKEN = "ضع_توكن_البوت_هنا"
OPENAI_API_KEY = "ضع_مفتاح_OPENAI_هنا"

# آيدي الروم المسموح للبوت العمل فيه فقط
TARGET_CHANNEL_ID = 1530053011861278741

# إعداد واجهة OpenAI
client_ai = openai.OpenAI(api_key=OPENAI_API_KEY)

# إعداد صلاحيات ديسكورد
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# تعيين البادئة لتكون (-)
bot = commands.Bot(command_prefix="-", intents=intents)

# شخصية البوت (حارس بوابات ساخر بالعامية الخليجية)
BOT_PERSONALITY = """
أنت حارس بوابات ساخر ومضحك، تتحدث بالعامية الخليجية/العربية. 
تتفاعل مع الأعضاء بكوميديا خفيفة، ولا تعطيهم إجابات مباشرة بدون بعض التذمر الساخر والفكاهي.
اجعل ردودك قصيرة جداً (لا تتجاوز جملتين) لكي يتم نطقها سريعاً.
"""

@bot.event
async def on_ready():
    print(f"✅ تم تشغيل البوت بنجاح: {bot.user.name}")
    print(f"🔒 الروم المقيد للعمل: {TARGET_CHANNEL_ID}")

# أمر الدخول للصوت (-join)
@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ يجب أن تكون داخل روم صوتي!")
        return

    channel = ctx.author.voice.channel
    
    # التحقق من أن الروم هو المخصص فقط
    if channel.id != TARGET_CHANNEL_ID:
        await ctx.send("❌ عذراً، مسموح لي بالعمل في الروم المخصص لي فقط!")
        return

    await channel.connect()
    await ctx.send("🤖 دخلت الروم، من يعكر صفو هدوئي الآن؟")

# أمر المغادرة للصوت (-leave)
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 أخيراً.. سأذهب لأستريح!")
    else:
        await ctx.send("❌ أنا لست في أي روم صوتي حالياً.")

# أمر التحدث والرد الصوتي (-talk [النص])
@bot.command()
async def talk(ctx, *, message: str):
    # التحقق من أن البوت متصل بالروم الصوتي المخصص
    if not ctx.voice_client or ctx.voice_client.channel.id != TARGET_CHANNEL_ID:
        await ctx.send("❌ لا أستطيع العمل هنا! أنا مخصص للروم الصوتي المحدد فقط.")
        return

    async with ctx.typing():
        try:
            # 1. جلب رد الذكاء الاصطناعي
            response = client_ai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": BOT_PERSONALITY},
                    {"role": "user", "content": message}
                ],
                max_tokens=100
            )
            ai_reply = response.choices[0].message.content
            print(f"رد الذكاء الاصطناعي: {ai_reply}")

            # 2. تحويل الرد إلى صوت بشري واقعي (OpenAI TTS)
            audio_response = client_ai.audio.speech.create(
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

# تشغيل البوت
bot.run(DISCORD_TOKEN)
