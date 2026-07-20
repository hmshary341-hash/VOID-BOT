import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# --- الإعدادات ---
STATS_CHANNEL = 1526712984531894292
DATA_FILE = "xp_data.json"

# --- نظام أزرار التنقل (لجعل التوب فخم وممتد) ---
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

        embed = discord.Embed(title="🏆 أفضل نقاط الكتابة", color=0x8000FF)
        
        description = ""
        for i, (user_id, info) in enumerate(page_data, start=start + 1):
            # محاولة جلب الاسم من السيرفر
            member = self.interaction.guild.get_member(int(user_id))
            display_name = member.display_name if member else info['name']
            
            # أيقونات فخمة للمراكز الأولى
            rank_icon = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "✨"
            
            description += f"{rank_icon} | **{display_name}** — خبرة: `{info['xp']}`\n\n"
        
        embed.description = description if description else "لا يوجد بيانات."
        embed.set_footer(text=f"صفحة {self.page + 1} | إجمالي الأعضاء: {len(self.data)}")
        return embed

    @discord.ui.button(label="السابق", style=discord.ButtonStyle.blurple, emoji="⬅️")
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="التالي", style=discord.ButtonStyle.blurple, emoji="➡️")
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
        if message.author.bot or not message.guild:
            return
        
        data = self.load_data()
        user_id = str(message.author.id)
        
        if user_id not in data:
            data[user_id] = {"name": message.author.name, "xp": 0}
        
        data[user_id]["xp"] += 1
        self.save_data(data)

    # --- أمر تحديث الإحصائيات ---
    @app_commands.command(name="تحديث_الإحصائيات", description="تحديث إحصائيات السيرفر")
    @app_commands.checks.has_permissions(administrator=True)
    async def update_stats(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(STATS_CHANNEL)
        if not channel:
            return await interaction.response.send_message("❌ الروم غير موجود.", ephemeral=True)

        embed = discord.Embed(
            title="📊 VOID STATS",
            description=f"👥 الأعضاء: {interaction.guild.member_count}\n💬 الرومات: {len(interaction.guild.channels)}\n🎭 الرتب: {len(interaction.guild.roles)}",
            color=0x8000FF
        )
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ تم التحديث.", ephemeral=True)

    # --- أمر التوب الفخم ---
    @app_commands.command(name="top", description="عرض قائمة المتصدرين الكاملة")
    async def top(self, interaction: discord.Interaction):
        data = self.load_data()
        if not data:
            return await interaction.response.send_message("❌ لا توجد بيانات للنقاط حالياً.", ephemeral=True)
        
        # ترتيب حسب النقاط
        sorted_users = sorted(data.items(), key=lambda item: item[1]["xp"], reverse=True)
        
        # إرسال الرسالة مع الأزرار
        view = TopView(sorted_users, interaction)
        await interaction.response.send_message(embed=view.get_embed(), view=view)

async def setup(bot):
    await bot.add_cog(Stats(bot))
