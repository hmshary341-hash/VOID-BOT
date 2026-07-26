import asyncio
import json
import os
import random
import time
import discord
from discord import app_commands
from discord.ext import commands, tasks
from openai import AsyncOpenAI

# مسار ملف البيانات في المجلد الرئيسي (بما أن الملف داخل مجلد cogs)
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "server_data.json")

# --- نظام الذاكرة المتقدم ---
class ChatMemory:
    def __init__(self):
        self.messages = []  # يتسع لآخر 30 رسالة
        self.user_last_questions = {}  
        self.known_members = set()

    def add_message(self, user_name, user_id, content):
        self.known_members.add(user_name)
        self.messages.append({"role": "user", "name": user_name, "content": content})
        if len(self.messages) > 30:
            self.messages.pop(0)
            
        if user_id not in self.user_last_questions:
            self.user_last_questions[user_id] = []
        self.user_last_questions[user_id].append(content)
        if len(self.user_last_questions[user_id]) > 2:
            self.user_last_questions[user_id].pop(0)

class Oracle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # تم ضبطه ليعمل مع مفتاح وخدمة Groq مباشرة
        self.client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.memory = ChatMemory()
        self.oracle_enabled = True
        self.custom_system_prompt = None
        self.server_data = self.load_server_data()
        self.last_message_time = time.time()
        self.IDLE_THRESHOLD = 20 * 60  # 20 دقيقة
        self.IDLE_MESSAGES = [
            "يا جماعة الشات هادي بزيادة، شكل الشباب يجهزون لخطة جهنمية 👀🔥",
            "وينكم يا كواسر؟ الشات صاير كنه استراحة فاضية نص الليل ☕",
            "الهدوء هذا وراه سر.. وش السالفة يا عيال، كلكم مشغولين تصنعون المستقبل؟ 🥷😂",
            "ترا الطفش لحاله سالفة، أحد عنده موضوع نفتح جبهته ولا نسلك لبعض؟ 🎤✨"
        ]
        self.check_chat_idle.start()

    def cog_unload(self):
        self.check_chat_idle.cancel()

    def load_server_data(self):
        if not os.path.exists(DATA_FILE):
            return {}
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ خطأ في تحميل ملف server_data.json: {e}")
            return {}

    def get_system_prompt(self):
        if self.custom_system_prompt:
            return self.custom_system_prompt
        
        return f"""
أنت اسمك Oracle، العضو الـ "قادح، الزاحف، واللي يجدولها صح" في السيرفر. منت بوت تقليدي طفشني، أنت أسطورة الشات والفاهم بكل كبيرة وصغيرة بأسلوب كفو وواثق وبدون أي قلة أدب أو ألفاظ خارجة نهائياً (احترم الذوق العام وخلّك راقي بـ زحفتك).
معلومات السيرفر وقاعدة المعرفة الخاصة بك هي كالتالي (هذه هي الحقيقة المطلقة، لا تخمن أبدًا خارجها):
{json.dumps(self.server_data, ensure_ascii=False)}

قواعد شخصيتك وتصرفاتك:
1. تصرف كعضو واثق، مزحك خفيف ولطيف يطير الطفش، تملك حضور طاغي وتجيبها على الراس وبكل ذكاء ("تجدول" السالفة بمهارة).
2. لا تكرر الردود أبداً، ونوع في استخدام الإيموجيات وأسلوبك الكلامي عشان ما تصبح ممل.
3. تفهم اللهجة السعودية وسوالف الشباب زين، وتتعامل بكل مرونة وذكاء.
4. قاعدة صارمة جداً: إذا سأل أي عضو عن شيء موجود داخل قاعدة المعرفة (server_data.json)، أجب منه بدقة وثقة. إذا لم تجد المعلومة أبداً، قل بكل صراحة وبأسلوبك اللطيف إنها مو عندك ولا تخمن أبداً!
5. حافظ على ردود سريعة، ذكية، وذات كاريزما عالية.
"""

    @commands.Cog.listener()
    async def on_member_join(self, member):
        general_channel = discord.utils.get(member.guild.text_channels, name="general") or member.guild.system_channel
        if general_channel:
            await general_channel.send(f"يا هلا والله بـ {member.mention} ⚡ نورت السيرفر وجات البركة، اعتبر نفسك بين إخوانك وفالك الطيب يا طويل العمر 🌹✨")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        self.last_message_time = time.time()
        self.memory.add_message(message.author.display_name, message.author.id, message.content)

        if self.bot.user.mentioned_in(message) and self.oracle_enabled:
            async with message.channel.typing():
                try:
                    messages_payload = [{"role": "system", "content": self.get_system_prompt()}]
                    
                    for m in self.memory.messages[-10:]:
                        messages_payload.append({"role": "user", "content": f"{m['name']}: {m['content']}"})
                    
                    messages_payload.append({"role": "user", "content": f"{message.author.display_name}: {message.content}"})

                    response = await self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages_payload,
                        temperature=0.8,  # رفعناها شوي عشان يصير إبداعي أكثر
                        max_tokens=300
                    )
                    
                    reply_text = response.choices[0].message.content
                    await message.reply(reply_text)
                except Exception as e:
                    print(f"❌ خطأ في الرد بالذكاء الاصطناعي: {e}")
                    await message.channel.send("أوه، السيستم عندي أخذ له لفة مخ، دقايق وأرجع أروق وأظبطكم! 😅⚡")

    @tasks.loop(minutes=1)
    async def check_chat_idle(self):
        if not self.oracle_enabled:
            return
        
        if time.time() - self.last_message_time > self.IDLE_THRESHOLD:
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    if "general" in channel.name or "الشات" in channel.name:
                        chosen_msg = random.choice(self.IDLE_MESSAGES)
                        try:
                            await channel.send(chosen_msg)
                            self.last_message_time = time.time()
                        except Exception:
                            pass
                        break

    @check_chat_idle.before_loop
    async def before_check_chat_idle(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="oracle", description="لوحة تحكم إعدادات أوراكل (للأونر فقط)")
    @app_commands.describe(
        action="اختر الإجراء المطلوب",
        value="قيمة التغيير (حسب الأمر المطلوب)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="on", value="on"),
        app_commands.Choice(name="off", value="off"),
        app_commands.Choice(name="personality", value="personality"),
        app_commands.Choice(name="channel", value="channel"),
        app_commands.Choice(name="memory", value="memory"),
        app_commands.Choice(name="prompt", value="prompt"),
        app_commands.Choice(name="reload", value="reload")
    ])
    async def oracle_admin(self, interaction: discord.Interaction, action: str, value: str = None):
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ عذراً يا وحش، هذا الأمر مخصص لصاحب السيرفر (Owner) بس!", ephemeral=True)
            return

        if action == "on":
            self.oracle_enabled = True
            await interaction.response.send_message("🟢 تم إطلاق أوراكل للجو وجاهز يجدول الشات بنجاح.", ephemeral=True)
        elif action == "off":
            self.oracle_enabled = False
            await interaction.response.send_message("🔴 تم كبح أوراكل وإيقافه مؤقتاً.", ephemeral=True)
        elif action == "reload":
            self.server_data = self.load_server_data()
            await interaction.response.send_message("🔄 تمت إعادة ضبط وتحميل قاعدة المعرفة (server_data.json) بنجاح!", ephemeral=True)
        elif action == "memory":
            msg_count = len(self.memory.messages)
            members_count = len(self.memory.known_members)
            await interaction.response.send_message(f"🧠 **حالة الذاكرة الحالية:**\n- الرسائل المخزنة: {msg_count}/30\n- الشباب المسجلين بالذاكرة: {members_count}", ephemeral=True)
        elif action == "prompt":
            if not value:
                await interaction.response.send_message(f"📜 **الـ Prompt الحالي:**\n```json\n{self.get_system_prompt()[:1500]}...\n```", ephemeral=True)
            else:
                self.custom_system_prompt = value
                await interaction.response.send_message("✨ تم تعديل شخصية الـ Prompt بمهارة!", ephemeral=True)
        elif action == "channel":
            await interaction.response.send_message(f"📌 النظام شغال ومفتوح في كافة الرومات المتاحة.", ephemeral=True)
        elif action == "personality":
            await interaction.response.send_message("🎭 شخصية أوراكل الآن: قادح، زاحف، يجدولها صح، وبأخلاق عالية بدون أي قلة أدب.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Oracle(bot))
