import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

GIVEAWAY_START = 1526628744020754594
GIVEAWAY_END = 1526709276083490949

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="قيف", description="بدء مسابقة (قيف أواي)")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(time="مدة القيف أواي بالثواني", winners="عدد الفائزين", prize="اسم الجائزة")
    async def giveaway(self, interaction: discord.Interaction, time: int, winners: int, prize: str):
        
        # التحقق من الروم
        if interaction.channel_id != GIVEAWAY_START:
            return await interaction.response.send_message("❌ لا يمكنك استخدام هذا الأمر هنا.", ephemeral=True)

        embed = discord.Embed(
            title="🎉 GIVEAWAY",
            description=(
                f"🎁 الجائزة: {prize}\n\n"
                f"⏳ المدة: {time} ثانية\n"
                f"🏆 عدد الفائزين: {winners}\n\n"
                "اضغط 🎉 للمشاركة"
            ),
            color=0x8000FF
        )

        # الرد الأولي لكي لا تنتهي صلاحية التفاعل
        await interaction.response.send_message("✅ تم بدء القيف أواي!", ephemeral=True)
        
        # إرسال الرسالة في القناة
        msg = await interaction.channel.send(embed=embed)
        await msg.add_reaction("🎉")

        # الانتظار
        await asyncio.sleep(time)

        # جلب الرسالة مجدداً للتأكد من التفاعلات
        msg = await interaction.channel.fetch_message(msg.id)
        
        users = []
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎉":
                users = [user async for user in reaction.users() if not user.bot]

        if users:
            winners_list = random.sample(users, min(winners, len(users)))
            channel = self.bot.get_channel(GIVEAWAY_END)
            if channel:
                await channel.send("🎉 الفائزين:\n" + " ".join(user.mention for user in winners_list))
            else:
                await interaction.channel.send("❌ حدث خطأ: لا يمكن العثور على روم إعلان الفائزين.")
        else:
            await interaction.channel.send("❌ لا يوجد مشاركين.")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
