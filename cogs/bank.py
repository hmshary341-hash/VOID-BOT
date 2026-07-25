import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import datetime

DATA_FILE = "economy.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_data(data, user_id):
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {"coins": 0, "daily_transferred": 0, "last_date": ""}
    elif isinstance(data[user_id], int):
        old_coins = data[user_id]
        data[user_id] = {"coins": old_coins, "daily_transferred": 0, "last_date": ""}
    return data[user_id]

class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="balance", description="معرفة رصيدك البنكي الحالي")
    async def balance(self, interaction: discord.Interaction):
        data = load_data()
        user_data = get_user_data(data, interaction.user.id)
        coins = user_data["coins"]
        await interaction.response.send_message(f"🏦 رصيدك في البنك هو: **{coins:,} كوينز**", ephemeral=True)

    @app_commands.command(name="daily", description="الحصول على جائزتك اليومية من الكوينز (1000 كوينز)")
    async def daily(self, interaction: discord.Interaction):
        data = load_data()
        user_data = get_user_data(data, interaction.user.id)
        
        reward = 1000
        user_data["coins"] += reward
        save_data(data)

        await interaction.response.send_message(f"🎉 لقد استلمت جائزتك اليومية بنجاح! تم إضافة **{reward:,} كوينز** إلى رصيدك البنكي.", ephemeral=True)

    @app_commands.command(name="work", description="العمل لكسب بعض الكوينز في البنك (بين 2000 و 4000)")
    async def work(self, interaction: discord.Interaction):
        data = load_data()
        user_data = get_user_data(data, interaction.user.id)
        
        earned = random.randint(2000, 4000)
        user_data["coins"] += earned
        save_data(data)

        await interaction.response.send_message(f"🛠️ عملت بجد وربحت **{earned:,} كوينز** أضيفت لحسابك البنكي!", ephemeral=True)

    @app_commands.command(name="coinflip", description="لعبة مراهنة البنك: ضعفك أو تخسر كوينزك")
    @app_commands.describe(amount="عدد الكوينز التي تريد المراهنة بها")
    async def coinflip(self, interaction: discord.Interaction, amount: int):
        data = load_data()
        user_data = get_user_data(data, interaction.user.id)
        current_balance = user_data["coins"]

        if amount <= 0:
            await interaction.response.send_message("❌ يجب أن تكون المراهنة أكبر من الصفر!", ephemeral=True)
            return

        if current_balance < amount:
            await interaction.response.send_message("❌ ليس لديك رصيد كافٍ في البنك لهذه المراهنة!", ephemeral=True)
            return

        if random.choice([True, False]):
            user_data["coins"] += amount
            save_data(data)
            await interaction.response.send_message(f"🎉 مبروك! فزت بالرهان وضاعفت مبلغك. ربحت **{amount:,} كوينز**! رصيدك الجديد: **{user_data['coins']:,} كوينز**")
        else:
            user_data["coins"] -= amount
            save_data(data)
            await interaction.response.send_message(f"😢 للأسف خسرت الرهان وخسرت **{amount:,} كوينز**. رصيدك الجديد: **{user_data['coins']:,} كوينز**")

    @app_commands.command(name="نرد", description="لعبة نرد البنك: مكافآت (3000، 2000، 1000 أو صفر)")
    async def nerd(self, interaction: discord.Interaction):
        data = load_data()
        user_data = get_user_data(data, interaction.user.id)
        
        rewards = [3000, 1000, 2000, 0, 0, 0]
        reward = random.choice(rewards)
        
        user_data["coins"] += reward
        save_data(data)
        
        if reward > 0:
            await interaction.response.send_message(
                f"🎲 رميت النرد وحالفك الحظ! ربحت **{reward:,} كوينز**.\n"
                f"🏦 رصيدك الجديد: **{user_data['coins']:,} كوينز**"
            )
        else:
            await interaction.response.send_message(
                f"🎲 رميت النرد وللأسف جاء الحظ صفيراً (0 كوينز).\n"
                f"🏦 رصيدك الحالي: **{user_data['coins']:,} كوينز**"
            )

    @app_commands.command(name="transfer", description="تحويل كوينز لعضو آخر (الحد اليومي 2,000 كوينز)")
    @app_commands.describe(member="العضو المراد التحويل إليه", amount="عدد الكوينز")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if member.id == interaction.user.id:
            await interaction.response.send_message("❌ لا يمكنك تحويل الكوينز لنفسك!", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message("❌ يجب أن يكون المبلغ أكبر من الصفر!", ephemeral=True)
            return

        data = load_data()
        sender_data = get_user_data(data, interaction.user.id)
        receiver_data = get_user_data(data, member.id)

        if sender_data["coins"] < amount:
            await interaction.response.send_message("❌ ليس لديك رصيد كافٍ في البنك لإتمام عملية التحويل!", ephemeral=True)
            return

        today_str = str(datetime.date.today())
        if sender_data["last_date"] != today_str:
            sender_data["last_date"] = today_str
            sender_data["daily_transferred"] = 0

        MAX_DAILY_LIMIT = 2000

        if sender_data["daily_transferred"] + amount > MAX_DAILY_LIMIT:
            remaining = MAX_DAILY_LIMIT - sender_data["daily_transferred"]
            await interaction.response.send_message(
                f"❌ لقد تجاوزت **الحد اليومي** للتحويل في البنك!\n"
                f"الحد الأقصى: **{MAX_DAILY_LIMIT:,} كوينز**\n"
                f"المتبقي لك اليوم: **{max(0, remaining):,} كوينز**", 
                ephemeral=True
            )
            return

        sender_data["coins"] -= amount
        sender_data["daily_transferred"] += amount
        receiver_data["coins"] += amount

        save_data(data)

        await interaction.response.send_message(
            f"✅ تم تحويل **{amount:,} كوينز** بنجاح إلى العضو {member.mention} عبر البنك!\n"
            f"📊 ما تم تحويله اليوم: **{sender_data['daily_transferred']:,} / {MAX_DAILY_LIMIT:,} كوينز**",
            ephemeral=True
        )

    @app_commands.command(name="top", description="عرض قائمة أغنى الأعضاء في البنك")
    async def top(self, interaction: discord.Interaction):
        data = load_data()
        if not data:
            await interaction.response.send_message("❌ لا توجد بيانات أعضاء مسجلة في البنك حتى الآن!", ephemeral=True)
            return

        sorted_users = sorted(
            data.items(), 
            key=lambda x: x[1].get("coins", 0) if isinstance(x[1], dict) else x[1], 
            reverse=True
        )
        
        description = ""
        for index, (user_id, user_info) in enumerate(sorted_users[:10], start=1):
            coins = user_info.get("coins", 0) if isinstance(user_info, dict) else user_info
            description += f"**{index}.** <@{user_id}> ➔ **{coins:,}** 🪙\n"

        embed = discord.Embed(
            title="🏆 قائمة أغنى الأعضاء في البنك",
            description=description if description else "لا توجد بيانات.",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Bank(bot))
