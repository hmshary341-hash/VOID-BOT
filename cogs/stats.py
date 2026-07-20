import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# --- الإعدادات ---
# تأكد من وضع رقم الروم الصحيح هنا
STATS_CHANNEL = 1526712984531894292
DATA_FILE = "xp_data.json"

# --- نظام أزرار التنقل (للتنقل بين الصفحات) ---
class TopView(discord.ui.View):
    def __init__(self, sorted_data, interaction):
        super().__init__(timeout=60)
        self.data = sorted_data
        self.interaction = interaction
        self.page = 0
        self.per_page = 10 

    def get_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        page_data = self.data[start:end]

        # شكل الإمبد "نوفا" النظيف
        embed = discord.Embed(
            title="💬 أفضل نقاط الكتابة", 
            color=0x2F3136
        )
        
        description = ""
        for i, (user_id, info) in enumerate(page_data, start=start + 1):
            member = self.interaction.guild.get_member(int(user_id))
            display_name = member.display_name if member else info['name']
            
            # حساب مستوى تقريبي
            xp = info['xp']
            level = xp // 100 
            
            # ترتيب الأيقونات (💎 للأول، 🔸 للبقية)
            rank_icon = "💎" if i == 1 else "🔸"
            
            # التنسيق النظيف (بدون backticks)
            description += f"{rank_icon} #{i} | **{display_name}** — خبرة: {xp} | مستوى: {level}\n\n"
        
        embed.description = description if description else "لا توجد بيانات حالياً."
        embed.set_footer(text=f"صفحة {self.page + 1} من { (len(self.data) // self.per_page) + 1 }")
        return embed

    @discord.ui.button(label="السابق", style=discord.ButtonStyle.secondary, emoji="⬅️")
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="التالي", style=discord.ButtonStyle.secondary, emoji="➡️")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (self.page + 1) * self.per_page < len(self.data):
            self.page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

# --- الكلاس الأساسي ---
class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- تحميل وحفظ البيانات ---
    def load_data(self):
        if not os.path.exists(DATA_FILE): return {}
        with open(DATA_FILE, "r") as f:
            try: return json.load(f)
            except: return {}

    def save_data(self, data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # --- احتساب النقاط عند الكتابة ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return
        
        data = self.load_data()
        user_id = str(message.author.id)
        
        if user_id not in data:
            data[user_id] = {"name": message.author.name, "xp": 0}
        
        data[user_id]["xp"] += 1
        self.save_data(data)

    # --- أمر التوب الفخم ---
    @app_commands.command(name="top", description="عرض قائمة المتصدرين الكاملة")
    async def top(self, interaction: discord.Interaction):
        data = self.load_data()
        if not data:
            return await interaction.response.send_message("❌ لا توجد بيانات للنقاط حالياً.", ephemeral=True)
        
        # ترتيب البيانات
        sorted_users = sorted(data.items(), key=lambda item: item[1]["xp"], reverse=True)
        
        # إرسال الرسالة مع الأزرار
        view = TopView(sorted_users, interaction)
        await interaction.response.send_message(embed=view.get_embed(), view=view)

async def setup(bot):
    await bot.add_cog(Stats(bot))
