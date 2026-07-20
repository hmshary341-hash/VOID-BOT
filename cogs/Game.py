import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import json
import os

DATA_FILE = "xp_data.json"

# قائمة الأسئلة النظيفة والممتعة
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
    "لو كان بإمكانك السفر لأي مكان في العالم الآن، إلى أين ستذهب؟"
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

    @app_commands.command(name="سؤال", description="يسألك البوت سؤالاً وعند الإجابة تكسب نقاط خبرة!")
    async def ask_question(self, interaction: discord.Interaction):
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
            
            # قراءة وحفظ النقاط في ملف xp_data.json
            data = self.load_data()
            user_id = str(interaction.user.id)
            if user_id not in data:
                data[user_id] = {"name": interaction.user.name, "xp": 0}
            
            # مكافأة الإجابة (مثلاً 15 نقطة)
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
