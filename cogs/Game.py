import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import json
import os

DATA_FILE = "xp_data.json"
QUESTIONS_CHANNEL_ID = 1525971090705219654  # روم الأسئلة

# قائمة ضخمة من الأسئلة النظيفة والممتعة
CLEAN_QUESTIONS = [
    "لو ملكت القوة لتغيير شيء واحد في العالم، ماذا ستغير؟",
    "ما هو حلم الطفولة الذي تمنيت تحقيقه دائماً؟",
    "لو اضطررت للعيش في عصر تاريخي آخر، أي عصر ستختار ولماذا؟",
    "ما هي أفضل نصيحة تلقيتها في حياتك؟",
    "لو كسبت مليون دولار الآن، ما أول شيء ستشتريه؟",
    "ما هي المهارة التي تود تعلمها لو كان لديك الوقت الكافي؟",
    "ما هو المكان الأكثر هدوءاً وراحة بالنسبة لك؟",
    "لو كتب لك أن تعيش يومك الأخير، كيف ستضيه؟",
    "ما هو أكثر شيء تفتخر به في حياتك حتى الآن؟",
    "لو كان بإمكانك السفر لأي مكان في العالم الآن، إلى أين ستذهب؟",
    "ما هي الكتاب أو القصة التي أثرت في شخصيتك بشكل كبير؟",
    "لو استطعت اختراع جهاز يسهل حياة الناس، ماذا سيكون؟",
    "ما هي الصفة التي تحبها أكثر في نفسك؟",
    "لو خيروك أن تعيش في مدينة ساحلية أو مدينة جبلية، ماذا تختار؟",
    "ما هو أكثر موقف مضحك تعرضت له في حياتك؟",
    "لو كان بإمكانك تناول طعام واحد فقط بقية حياتك، ماذا ستختار؟",
    "ما هي الهواية التي تمارسها لتفريغ طاقتك السلبية؟",
    "لو أتيحت لك الفرصة لمقابلة شخصية تاريخية، من ستختار؟",
    "ما هو الهدف الأساسي الذي تسعى لتحقيقه هذا العام؟",
    "لو طُلب منك إلقاء خطبة أمام العالم كله في دقيقة واحدة، ماذا ستكون رسالتك؟",
    "ما هو الشيء البسيط الذي يجعلك سعيداً فوراً؟",
    "لو كان بإمكانك العودة بالزمني لتغيير قرار واحد، هل ستفعل؟",
    "ما هي أجمل رسالة أو كلمة سمعتها من شخص غريب؟",
    "لو فتحت مشروعك الخاص اليوم، في أي مجال سيكون؟",
    "ما هو الفيلم أو المسلسل الذي لا تمل من إعادة مشاهدته؟",
    "لو طُلب منك وصف نفسك في ثلاث كلمات، ماذا ستختار؟",
    "ما هي العادة الجديدة التي تتمنى اكتسابها؟",
    "لو كان اليوم بأكمله مجاناً وبدون مسؤوليات، كيف ستستغله؟",
    "ما هو المشروب المفضل لديك أثناء العمل أو الدراسة؟",
    "لو استطاعت التحدث بلغة الحيوانات، أي حيوان ستبدأ محادثته؟",
    "ما هو المكان الذي تذهب إليه عندما تريد الاختلاء بنفسك؟",
    "لو كان بإمكانك العيش داخل عالم خيالي (أنمي، ألعاب، أفلام)، أين ستستقر؟",
    "ما هي أقيم هدية تلقيتها في حياتك؟",
    "لو خيروك بين الذكاء الخارق أو السعادة الدائمة، ماذا تختار؟",
    "ما هو الصوت الذي يمنحك شعوراً بالراحة والسلام؟",
    "لو أصبحت رئيساً لدولة ليوم واحد، ما أول قرار ستتخذه؟",
    "ما هي أفضل مهارة تجيدها في حياتك اليومية؟",
    "لو كان لديك وقت فراغ غير محدود، كيف ستنقضي يومك؟",
    "ما هو الفصل المفضل لديك في السنة ولماذا؟",
    "لو استطعت السفر عبر المستقبل 100 سنة، ماذا تتمنى أن ترى؟",
    "ما هو التحدي الصعب الذي تجاوزته وفخور به؟",
    "لو طُلب منك تدريس مادة للأطفال، ماذا ستكون؟",
    "ما هي العبارة أو الحكمة التي تكررها دائماً لنفسك؟",
    "لو كنت شخصية كرتونية، من تتمنى أن تكون؟",
    "ما هو الشيء الذي تفعله دائماً عندما تشعر بالملل؟",
    "لو أتيحت لك الفرصة لتصميم ديكور غرفتك من جديد، كيف ستكون؟",
    "ما هو أكثر لون تشعر أنه يمثل شخصيتك؟",
    "لو كان بإمكانك تعلم لغة جديدة فوراً، أي لغة ستختار؟",
    "ما هو أجمل شعور مررت به في حياتك؟",
    "لو طُلب منك تلخيص حياتك في جملة واحدة، ماذا ستكون؟"
]

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self):
        if not os.path.exists(DATA_FILE): return {}
        with open(DATA_FILE, "r") as f:
            try: return json.load(f)
            except: return {}

    def save_data(self, data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @app_commands.command(name="سؤال", description="يسألك البوت سؤالاً ممتعاً وعند الإجابة تكسب نقاط خبرة!")
    async def ask_question(self, interaction: discord.Interaction):
        if interaction.channel.id != QUESTIONS_CHANNEL_ID:
            return await interaction.response.send_message(
                f"❌ عذراً، هذا الأمر مخصص للاستخدام داخل <#{QUESTIONS_CHANNEL_ID}> فقط!", 
                ephemeral=True
            )

        question = random.choice(CLEAN_QUESTIONS)
        
        embed = discord.Embed(
            title="🤔 تحدي الأسئلة والنقاط",
            description=f"**{interaction.user.mention}**، إليك سؤالك:\n\n> **{question}**\n\n⏳ **لديك 30 ثانية للإجابة في الشات وكسب النقاط!**",
            color=0x8000FF
        )
        
        await interaction.response.send_message(embed=embed)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            
            data = self.load_data()
            user_id = str(interaction.user.id)
            if user_id not in data:
                data[user_id] = {"name": interaction.user.name, "xp": 0}
            
            points_reward = 15
            data[user_id]["xp"] += points_reward
            self.save_data(data)
            
            await msg.add_reaction("✨")
            
            success_embed = discord.Embed(
                title="✅ كسبت نقاط جديدة!",
                description=f"**إجابتك:** > {msg.content}\n\n🏆 **تمت إضافة +{points_reward} نقطة إلى رصيدك!** (تظهر في `/top`)",
                color=0x00FF00
            )
            await interaction.followup.send(embed=success_embed)
            
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⌛ انتهى الوقت!",
                description=f"للأسف يا {interaction.user.mention}, لم تقم بالإجابة في الوقت المحدد ولم تحصل على نقاط.",
                color=0xFF0000
            )
            await interaction.followup.send(embed=timeout_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Game(bot))
