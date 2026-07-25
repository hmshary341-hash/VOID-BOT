import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import datetime

os.makedirs("/app/data", exist_ok=True)
DATA_FILE = "/app/data/economy.json"

ROLE_ID = 1529995977203777566
BANK_CHANNEL_ID = 1530413677222564062  # آي دي روم البنك المسموح فيه الأوامر

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user_data(data, user_id):
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "coins": 0, 
            "daily_transferred": 0, 
            "last_date": "", 
            "last_daily_date": "", 
            "last_work_date": "",
            "nerd_count": 0,
            "last_nerd_date": ""
        }
    elif isinstance(data[user_id], int):
        old_coins = data[user_id]
        data[user_id] = {
            "coins": old_coins, 
            "daily_transferred": 0, 
            "last_date": "", 
            "last_daily_date": "", 
            "last_work_date": "",
            "nerd_count": 0,
            "last_nerd_date": ""
        }
    else:
        user_data = data[user_id]
        if "daily_transferred" not in user_data: user_data["daily_transferred"] = 0
        if "last_date" not in user_data: user_data["last_date"] = ""
        if "last_daily_date" not in user_data: user_data["last_daily_date"] = ""
        if "last_work_date" not in user_data: user_data["last_work_date"] = ""
        if "nerd_count" not in user_data: user_data["nerd_count"] = 0
        if "last_nerd_date" not in user_data: user_data["last_nerd_date"] = ""
    return data[user_id]

class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_channel(self, interaction: discord.Interaction) -> bool:
        if interaction.channel.id != BANK_CHANNEL_ID:
            await interaction.response.send_message(
                f"❌ عذراً، يمكنك استخدام أوامر البنك فقط في روم <#{BANK_CHANNEL_ID}>!",
                ephemeral=True
            )
            return False
        return True

    @app_commands.command(name="balance", description="معرفة رصيدك البنكي الحالي")
    async def balance(self, interaction: discord.Interaction):
        if not await self.check_channel(interaction):
            return
        data = load_data()
        user_data = get_user_data(data, interaction.user.id)
        coins = user_data["coins"]
        await interaction.response.send_message(f"🏦 رصيدك في البنك هو: **{coins:,} كوينز**", ephemeral=True)

    @app_commands.command(name="daily", description="الحصول على جائزتك اليومية من الكوينز (مرة كل يوم)")
    async def daily(self, interaction: discord.Interaction):
        if not await self.check_channel(interaction):
            return
        data = load_data()
        user_data = get_user_data(data, interaction.user.id)
        
        today_str = str(datetime.date.today())
        if user_data.get("last_daily_date") == today_str:
            await interaction.response.send_message("❌ لقد استلمت جائزتك اليومية بالفعل اليوم! يمكنك استلامها مرة أخرى غداً.", ephemeral=True)
            return

        reward = 1000
        user_data["coins"] += reward
        user_data["last_daily_date"] = today_str
        save_data(data)

        await interaction.response.send_message(f"🎉 لقد استلمت جائزتك اليومية بنجاح! تم إضافة **{reward:,} كوينز** إلى رصيدك البنكي.", ephemeral=True)

    @app_commands.command(name="work", description="العمل لكسب بعض الكوينز في البنك (مرة كل يوم)")
    async def work(self, interaction: discord.Interaction):
        if not await self.check_channel(interaction):
            return
        data = load_data()
        user_data = get_user_data(data, interaction.user.id)
        
        today_str = str(datetime.date.today())
        if user_data.get("last_work_date") == today_str:
            await interaction.response.send_message("❌ لقد قمت بالعمل بالفعل اليوم! يمكنك العمل مرة أخرى غداً.", ephemeral=True)
            return

        earned = random.randint(2000, 4000)
        user_data["coins"] += earned
        user_data["last_work_date"] = today_str
        save_data(data)

        await interaction.response.send_message(f"🛠️ عملت بجد وربحت **{earned:,} كوينز** أضيفت لحسابك البنكي!", ephemeral=True)

    @app_commands.command(name="coinflip", description="لعبة مراهنة البنك: لا محدودة")
    @app_commands.describe(amount="عدد الكوينز التي تريد المراهنة بها")
    async def coinflip(self, interaction: discord.Interaction, amount: int):
        if not await self.check_channel(interaction):
            return
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

    @app_commands.command(name="نرد", description="لعبة نرد البنك: مكافآت عشوائية (متاحة مرتين فقط في اليوم)")
    async def nerd(self, interaction: discord.Interaction):
        if not await self.check_channel(interaction):
            return
        data = load_data()
        user_data = get_user_data(data, interaction.user.id)
        
        today_str = str(datetime.date.today())
        if user_data.get("last_nerd_date") != today_str:
            user_data["last_nerd_date"] = today_str
            user_data["nerd_count"] = 0

        MAX_NERD_LIMIT = 2
        if user_data["nerd_count"] >= MAX_NERD_LIMIT:
            await interaction.response.send_message("❌ لقد استهلكت محاولاتك لـ (النرد) لهذا اليوم (مرتان فقط). تجدد المحاولات غداً!", ephemeral=True)
            return

        user_data["nerd_count"] += 1

        rewards = [3000, 1000, 2000, 0, 0, 0]
        reward = random.choice(rewards)
        
        user_data["coins"] += reward
        save_data(data)
        
        remaining_attempts = MAX_NERD_LIMIT - user_data["nerd_count"]
        if reward > 0:
            await interaction.response.send_message(
                f"🎲 رميت النرد وحالفك الحظ! ربحت **{reward:,} كوينز**.\n"
                f"🏦 رصيدك الجديد: **{user_data['coins']:,} كوينز**\n"
                f"📌 المحاولات المتبقية لك اليوم: {remaining_attempts}"
            )
        else:
            await interaction.response.send_message(
                f"🎲 رميت النرد وللأسف جاء الحظ صفيراً (0 كوينز).\n"
                f"🏦 رصيدك الحالي: **{user_data['coins']:,} كوينز**\n"
                f"📌 المحاولات المتبقية لك اليوم: {remaining_attempts}"
            )

    @app_commands.command(name="transfer", description="تحويل كوينز لعضو آخر (الحد اليومي 2,000 كوينز)")
    @app_commands.describe(member="العضو المراد التحويل إليه", amount="عدد الكوينز")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if not await self.check_channel(interaction):
            return
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

    @app_commands.command(name="add_coins", description="أمر خاص بمالك السيرفر لإضافة كوينز لأي شخص")
    @app_commands.describe(member="العضو المراد إعطاؤه الكوينز", amount="عدد الكوينز المراد إضافتها")
    async def add_coins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if not await self.check_channel(interaction):
            return
        
        # السماح لمالك السيرفر فقط باستخدام الأمر
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ هذا الأمر مخصص لمالك السيرفر وحدك!", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message("❌ يجب أن يكون المبلغ أكبر من الصفر!", ephemeral=True)
            return

        data = load_data()
        target_data = get_user_data(data, member.id)
        
        target_data["coins"] += amount
        save_data(data)

        await interaction.response.send_message(f"✅ تم إضافة **{amount:,} كوينز** إلى رصيد العضو {member.mention} بنجاح!\n🏦 رصيده الجديد: **{target_data['coins']:,} كوينز**", ephemeral=True)

    @app_commands.command(name="top", description="عرض قائمة أغنى الأعضاء في البنك")
    async def top(self, interaction: discord.Interaction):
        if not await self.check_channel(interaction):
            return
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
