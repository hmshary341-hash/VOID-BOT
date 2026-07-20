import discord
from discord import app_commands
from discord.ext import commands
import json
import os

STATS_CHANNEL = 1526712984531894292
DATA_FILE = "xp_data.json"

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_data = self.load_data()

    # --- إدارة البيانات ---
    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {}
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.xp_data, f, indent=4)

    # --- نظام النقاط (XP System) ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        user_id = str(message.author.id)
        
        if user_id not in self.xp_data:
            self.xp_data[user_id] = {"name": message.author.name, "xp": 0}
        
        # إضافة 1 نقطة لكل رسالة (يمكنك تغييرها)
        self.xp_data[user_id]["xp"] += 1
        self.save_data()

    # --- أوامر السلاش ---
    @app_commands.command(name="تحديث_الإحصائيات", description="تحديث إحصائيات السيرفر")
    @app_commands.checks.has_permissions(administrator=True)
    async def update_stats(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(STATS_CHANNEL)
        if not channel:
            return await interaction.response.send_message("❌ روم الإحصائيات غير موجود.", ephemeral=True)

        embed = discord.Embed(
            title="📊 VOID STATS",
            description=(
                f"👥 الأعضاء: {interaction.guild.member_count}\n"
                f"💬 الرومات: {len(interaction.guild.channels)}\n"
                f"🎭 الرتب: {len(interaction.guild.roles)}"
            ),
            color=0x8000FF
        )
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ تم تحديث الإحصائيات بنجاح.", ephemeral=True)

    @app_commands.command(name="top", description="عرض قائمة المتصدرين (أفضل 10 أعضاء)")
    async def top(self, interaction: discord.Interaction):
        # ترتيب الأعضاء حسب النقاط
        sorted_users = sorted(self.xp_data.items(), key=lambda item: item[1]["xp"], reverse=True)
        
        embed = discord.Embed(title="🏆 قائمة المتصدرين (Top 10)", color=0x8000FF)
        
        # عرض أول 10
        for i, (user_id, data) in enumerate(sorted_users[:10], start=1):
            embed.add_field(
                name=f"#{i} | {data['name']}",
                value=f"النقاط: {data['xp']}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))
