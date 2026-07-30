import datetime
import json
import os
import random
import discord
from discord.ext import commands

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
        "last_nerd_date": "",
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
        "last_nerd_date": "",
    }
  else:
    user_data = data[user_id]
    if "daily_transferred" not in user_data:
      user_data["daily_transferred"] = 0
    if "last_date" not in user_data:
      user_data["last_date"] = ""
    if "last_daily_date" not in user_data:
      user_data["last_daily_date"] = ""
    if "last_work_date" not in user_data:
      user_data["last_work_date"] = ""
    if "nerd_count" not in user_data:
      user_data["nerd_count"] = 0
    if "last_nerd_date" not in user_data:
      user_data["last_nerd_date"] = ""
  return data[user_id]


class Bank(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  async def check_channel(self, ctx) -> bool:
    if ctx.channel.id != BANK_CHANNEL_ID:
      await ctx.send(
          f"❌ عذراً، يمكنك استخدام أوامر البنك والاقتصاد فقط في روم"
          f" <#{BANK_CHANNEL_ID}> ولا يمكن استخدامها هنا نهائياً!"
      )
      return False
    return True

  @commands.command(name="رصيدي_البنكي", aliases=["رصيدي البنكي"])
  async def balance(self, ctx):
    if not await self.check_channel(ctx):
      return
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)
    coins = user_data["coins"]
    await ctx.send(f"🏦 رصيدك في البنك هو: **{coins:,} كوينز**")

  @commands.command(
      name="استلام_الضمان_اليومي",
      aliases=["أستلام الضمان اليومي", "استلام الضمان اليومي"],
  )
  async def daily(self, ctx):
    if not await self.check_channel(ctx):
      return
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)

    today_str = str(datetime.date.today())
    if user_data.get("last_daily_date") == today_str:
      await ctx.send(
          "❌ لقد استلمت جائزتك اليومية بالفعل اليوم! يمكنك استلامها مرة أخرى غداً."
      )
      return

    reward = 1000
    user_data["coins"] += reward
    user_data["last_daily_date"] = today_str
    save_data(data)

    await ctx.send(
        f"🎉 لقد استلمت جائزتك اليومية بنجاح! تم إضافة **{reward:,} كوينز** إلى"
        " رصيدك البنكي."
    )

  @commands.command(
      name="استلام_راتبي", aliases=["أستلام راتبي", "استلام راتبي"]
  )
  async def work(self, ctx):
    if not await self.check_channel(ctx):
      return
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)

    today_str = str(datetime.date.today())
    if user_data.get("last_work_date") == today_str:
      await ctx.send(
          "❌ لقد قمت بالعمل بالفعل اليوم! يمكنك العمل مرة أخرى غداً."
      )
      return

    earned = random.randint(2000, 4000)
    user_data["coins"] += earned
    user_data["last_work_date"] = today_str
    save_data(data)

    await ctx.send(
        f"🛠️ عملت بجد وربحت **{earned:,} كوينز** أضيفت لحسابك البنكي!"
    )

  @commands.command(name="حظ")
  async def coinflip(self, ctx, amount: int = None):
    if not await self.check_channel(ctx):
      return
    if amount is None:
      await ctx.send("❌ يرجى تحديد المبلغ المراد المراهنة به! مثال: `-حظ 500`")
      return

    data = load_data()
    user_data = get_user_data(data, ctx.author.id)
    current_balance = user_data["coins"]

    if amount <= 0:
      await ctx.send("❌ يجب أن تكون المراهنة أكبر من الصفر!")
      return

    if current_balance < amount:
      await ctx.send("❌ ليس لديك رصيد كافٍ في البنك لهذه المراهنة!")
      return

    if random.choice([True, False]):
      user_data["coins"] += amount
      save_data(data)
      await ctx.send(
          f"🎉 مبروك! فزت بالرهان وضاعفت مبلغك. ربحت **{amount:,} كوينز**! رصيدك"
          f" الجديد: **{user_data['coins']:,} كوينز**"
      )
    else:
      user_data["coins"] -= amount
      save_data(data)
      await ctx.send(
          f"😢 للأسف خسرت الرهان وخسرت **{amount:,} كوينز**. رصيدك الجديد:"
          f" **{user_data['coins']:,} كوينز**"
      )

  @commands.command(name="نرد")
  async def nerd(self, ctx):
    if not await self.check_channel(ctx):
      return
    data = load_data()
    user_data = get_user_data(data, ctx.author.id)

    today_str = str(datetime.date.today())
    if user_data.get("last_nerd_date") != today_str:
      user_data["last_nerd_date"] = today_str
      user_data["nerd_count"] = 0

    MAX_NERD_LIMIT = 2
    if user_data["nerd_count"] >= MAX_NERD_LIMIT:
      await ctx.send(
          "❌ لقد استهلكت محاولاتك لـ (النرد) لهذا اليوم (مرتان فقط). تجدد"
          " المحاولات غداً!"
      )
      return

    user_data["nerd_count"] += 1

    rewards = [3000, 1000, 2000, 0, 0, 0]
    reward = random.choice(rewards)

    user_data["coins"] += reward
    save_data(data)

    remaining_attempts = MAX_NERD_LIMIT - user_data["nerd_count"]
    if reward > 0:
      await ctx.send(
          f"🎲 رميت النرد وحالفك الحظ! ربحت **{reward:,} كوينز**.\n🏦 رصيدك الجديد:"
          f" **{user_data['coins']:,} كوينز**\n📌 المحاولات المتبقية لك اليوم:"
          f" {remaining_attempts}"
      )
    else:
      await ctx.send(
          "🎲 رميت النرد وللأسف جاء الحظ صفيراً (0 كوينز).\n🏦 رصيدك الحالي:"
          f" **{user_data['coins']:,} كوينز**\n📌 المحاولات المتبقية لك اليوم:"
          f" {remaining_attempts}"
      )

  @commands.command(name="تحويل")
  async def transfer(self, ctx, member: discord.Member = None, amount: int = None):
    if not await self.check_channel(ctx):
      return
    if member is None or amount is None:
      await ctx.send(
          "❌ الاستخدام الصحيح:\n`-تحويل @العضو المبلغ`\nمثال: `-تحويل @فلان"
          " 500`"
      )
      return

    if member.id == ctx.author.id:
      await ctx.send("❌ لا يمكنك تحويل الكوينز لنفسك!")
      return

    if amount <= 0:
      await ctx.send("❌ يجب أن يكون المبلغ أكبر من الصفر!")
      return

    data = load_data()
    sender_data = get_user_data(data, ctx.author.id)
    receiver_data = get_user_data(data, member.id)

    if sender_data["coins"] < amount:
      await ctx.send(
          "❌ ليس لديك رصيد كافٍ في البنك لإتمام عملية التحويل!"
      )
      return

    today_str = str(datetime.date.today())
    if sender_data["last_date"] != today_str:
      sender_data["last_date"] = today_str
      sender_data["daily_transferred"] = 0

    MAX_DAILY_LIMIT = 2000

    if sender_data["daily_transferred"] + amount > MAX_DAILY_LIMIT:
      remaining = MAX_DAILY_LIMIT - sender_data["daily_transferred"]
      await ctx.send(
          "❌ لقد تجاوزت **الحد اليومي** للتحويل في البنك!\nالحد الأقصى:"
          f" **{MAX_DAILY_LIMIT:,} كوينز**\nالمتبقي لك اليوم:"
          f" **{max(0, remaining):,} كوينز**"
      )
      return

    sender_data["coins"] -= amount
    sender_data["daily_transferred"] += amount
    receiver_data["coins"] += amount

    save_data(data)

    await ctx.send(
        f"✅ تم تحويل **{amount:,} كوينز** بنجاح إلى العضو {member.mention} عبر"
        f" البنك!\n📊 ما تم تحويله اليوم:"
        f" **{sender_data['daily_transferred']:,} / {MAX_DAILY_LIMIT:,} كوينز**"
    )

  @commands.command(name="إضافة_كوينز", aliases=["إضافة كوينز"])
  async def add_coins(
      self, ctx, member: discord.Member = None, amount: int = None
  ):
    if not await self.check_channel(ctx):
      return

    if ctx.author.id != ctx.guild.owner_id:
      await ctx.send("❌ هذا الأمر مخصص لمالك السيرفر وحدك!")
      return

    if member is None or amount is None:
      await ctx.send(
          "❌ الاستخدام الصحيح:\n`-إضافة كوينز @العضو المبلغ`\nمثال: `-إضافة"
          " كوينز @فلان 1000`"
      )
      return

    if amount <= 0:
      await ctx.send("❌ يجب أن يكون المبلغ أكبر من الصفر!")
      return

    data = load_data()
    target_data = get_user_data(data, member.id)

    target_data["coins"] += amount
    save_data(data)

    await ctx.send(
        f"✅ تم إضافة **{amount:,} كوينز** إلى رصيد العضو {member.mention}"
        f" بنجاح!\n🏦 رصيده الجديد: **{target_data['coins']:,} كوينز**"
    )

  @commands.command(name="توب")
  async def top(self, ctx):
    if not await self.check_channel(ctx):
      return
    data = load_data()
    if not data:
      await ctx.send("❌ لا توجد بيانات أعضاء مسجلة في البنك حتى الآن!")
      return

    sorted_users = sorted(
        data.items(),
        key=lambda x: (x[1].get("coins", 0) if isinstance(x[1], dict) else x[1]),
        reverse=True,
    )

    description = ""
    for index, (user_id, user_info) in enumerate(sorted_users[:10], start=1):
      coins = (
          user_info.get("coins", 0) if isinstance(user_info, dict) else user_info
      )
      description += f"**{index}.** <@{user_id}> ➔ **{coins:,}** 🪙\n"

    embed = discord.Embed(
        title="🏆 قائمة أغنى الأعضاء في البنك",
        description=description if description else "لا توجد بيانات.",
        color=discord.Color.gold(),
    )
    await ctx.send(embed=embed)


async def setup(bot):
  await bot.add_cog(Bank(bot))
