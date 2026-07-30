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

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot:
      return

    content = message.content.strip()
    if not content.startswith("-"):
      return

    command_text = content[1:].strip()
    parts = command_text.split()
    if not parts:
      return

    # التحقق من روم البنك
    if message.channel.id != BANK_CHANNEL_ID:
      return

    # 1. رصيدي البنكي
    if command_text in ["رصيدي البنكي", "رصيدي"]:
      data = load_data()
      user_data = get_user_data(data, message.author.id)
      coins = user_data["coins"]
      await message.channel.send(
          f"🏦 رصيدك في البنك هو: **{coins:,} كوينز**", reference=message
      )

    # 2. استلام الضمان اليومي (تدعم بالهمزة وبدونها)
    elif command_text in ["أستلام الضمان اليومي", "استلام الضمان اليومي"]:
      data = load_data()
      user_data = get_user_data(data, message.author.id)
      today_str = str(datetime.date.today())
      if user_data.get("last_daily_date") == today_str:
        return await message.channel.send(
            "❌ لقد استلمت جائزتك اليومية بالفعل اليوم! يمكنك استلامها مرة أخرى"
            " غداً.",
            reference=message,
        )

      reward = 1000
      user_data["coins"] += reward
      user_data["last_daily_date"] = today_str
      save_data(data)
      await message.channel.send(
          f"🎉 لقد استلمت جائزتك اليومية بنجاح! تم إضافة **{reward:,} كوينز** إلى"
          " رصيدك البنكي.",
          reference=message,
      )

    # 3. استلام راتبي (تدعم بالهمزة وبدونها)
    elif command_text in ["أستلام راتبي", "استلام راتبي"]:
      data = load_data()
      user_data = get_user_data(data, message.author.id)
      today_str = str(datetime.date.today())
      if user_data.get("last_work_date") == today_str:
        return await message.channel.send(
            "❌ لقد قمت بالعمل بالفعل اليوم! يمكنك العمل مرة أخرى غداً.",
            reference=message,
        )

      earned = random.randint(2000, 4000)
      user_data["coins"] += earned
      user_data["last_work_date"] = today_str
      save_data(data)
      await message.channel.send(
          f"🛠️ عملت بجد وربحت **{earned:,} كوينز** أضيفت لحسابك البنكي!",
          reference=message,
      )

    # 4. حظ
    elif parts[0] in ["حظ"]:
      if len(parts) < 2:
        return await message.channel.send(
            "❌ يرجى تحديد المبلغ المراد المراهنة به! مثال: `-حظ 500`",
            reference=message,
        )
      try:
        amount = int(parts[1])
      except ValueError:
        return await message.channel.send(
            "❌ يرجى كتابة رقم صحيح للمبلغ!", reference=message
        )

      data = load_data()
      user_data = get_user_data(data, message.author.id)
      current_balance = user_data["coins"]

      if amount <= 0:
        return await message.channel.send(
            "❌ يجب أن تكون المراهنة أكبر من الصفر!", reference=message
        )
      if current_balance < amount:
        return await message.channel.send(
            "❌ ليس لديك رصيد كافٍ في البنك لهذه المراهنة!", reference=message
        )

      if random.choice([True, False]):
        user_data["coins"] += amount
        save_data(data)
        await message.channel.send(
            f"🎉 مبروك! فزت بالرهان وضاعفت مبلغك. ربحت **{amount:,} كوينز**! رصيدك"
            f" الجديد: **{user_data['coins']:,} كوينز**",
            reference=message,
        )
      else:
        user_data["coins"] -= amount
        save_data(data)
        await message.channel.send(
            f"😢 للأسف خسرت الرهان وخسرت **{amount:,} كوينز**. رصيدك الجديد:"
            f" **{user_data['coins']:,} كوينز**",
            reference=message,
        )

    # 5. نرد
    elif command_text in ["نرد"]:
      data = load_data()
      user_data = get_user_data(data, message.author.id)
      today_str = str(datetime.date.today())
      if user_data.get("last_nerd_date") != today_str:
        user_data["last_nerd_date"] = today_str
        user_data["nerd_count"] = 0

      MAX_NERD_LIMIT = 2
      if user_data["nerd_count"] >= MAX_NERD_LIMIT:
        return await message.channel.send(
            "❌ لقد استهلكت محاولاتك لـ (النرد) لهذا اليوم (مرتان فقط). تجدد"
            " المحاولات غداً!",
            reference=message,
        )

      user_data["nerd_count"] += 1
      rewards = [3000, 1000, 2000, 0, 0, 0]
      reward = random.choice(rewards)
      user_data["coins"] += reward
      save_data(data)

      remaining_attempts = MAX_NERD_LIMIT - user_data["nerd_count"]
      if reward > 0:
        await message.channel.send(
            f"🎲 رميت النرد وحالفك الحظ! ربحت **{reward:,} كوينز**.\n🏦 رصيدك الجديد:"
            f" **{user_data['coins']:,} كوينز**\n📌 المحاولات المتبقية لك اليوم:"
            f" {remaining_attempts}",
            reference=message,
        )
      else:
        await message.channel.send(
            "🎲 رميت النرد وللأسف جاء الحظ صفيراً (0 كوينز).\n🏦 رصيدك الحالي:"
            f" **{user_data['coins']:,} كوينز**\n📌 المحاولات المتبقية لك اليوم:"
            f" {remaining_attempts}",
            reference=message,
        )

    # 6. تحويل
    elif parts[0] in ["تحويل"]:
      if len(parts) < 3 or not message.mentions:
        return await message.channel.send(
            "❌ الاستخدام الصحيح:\n`-تحويل @العضو المبلغ`\nمثال: `-تحويل @فلان"
            " 500`",
            reference=message,
        )
      member = message.mentions[0]
      try:
        amount = int(parts[2])
      except (ValueError, IndexError):
        return await message.channel.send(
            "❌ يرجى كتابة المبلغ بشكل صحيح بعد منشن العضو!", reference=message
        )

      if member.id == message.author.id:
        return await message.channel.send(
            "❌ لا يمكنك تحويل الكوينز لنفسك!", reference=message
        )
      if amount <= 0:
        return await message.channel.send(
            "❌ يجب أن يكون المبلغ أكبر من الصفر!", reference=message
        )

      data = load_data()
      sender_data = get_user_data(data, message.author.id)
      receiver_data = get_user_data(data, member.id)

      if sender_data["coins"] < amount:
        return await message.channel.send(
            "❌ ليس لديك رصيد كافٍ في البنك لإتمام عملية التحويل!",
            reference=message,
        )

      today_str = str(datetime.date.today())
      if sender_data["last_date"] != today_str:
        sender_data["last_date"] = today_str
        sender_data["daily_transferred"] = 0

      MAX_DAILY_LIMIT = 2000
      if sender_data["daily_transferred"] + amount > MAX_DAILY_LIMIT:
        remaining = MAX_DAILY_LIMIT - sender_data["daily_transferred"]
        return await message.channel.send(
            "❌ لقد تجاوزت **الحد اليومي** للتحويل في البنك!\nالحد الأقصى:"
            f" **{MAX_DAILY_LIMIT:,} كوينز**\nالمتبقي لك اليوم:"
            f" **{max(0, remaining):,} كوينز**",
            reference=message,
        )

      sender_data["coins"] -= amount
      sender_data["daily_transferred"] += amount
      receiver_data["coins"] += amount
      save_data(data)

      await message.channel.send(
          f"✅ تم تحويل **{amount:,} كوينز** بنجاح إلى العضو {member.mention} عبر"
          f" البنك!\n📊 ما تم تحويله اليوم:"
          f" **{sender_data['daily_transferred']:,} / {MAX_DAILY_LIMIT:,} كوينز**",
          reference=message,
      )

    # 7. إضافة كوينز (مالك السيرفر فقط وتدعم بالهمزة وبدونها)
    elif (
        command_text.startswith("إضافة كوينز")
        or command_text.startswith("اضافه كوينز")
        or command_text.startswith("أضافة كوينز")
    ):
      if message.author.id != message.guild.owner_id:
        return await message.channel.send(
            "❌ هذا الأمر مخصص لمالك السيرفر وحدك!", reference=message
        )

      if not message.mentions or len(parts) < 3:
        return await message.channel.send(
            "❌ الاستخدام الصحيح:\n`-إضافة كوينز @العضو المبلغ`\nمثال: `-إضافة"
            " كوينز @فلان 1000`",
            reference=message,
        )

      member = message.mentions[0]
      try:
        amount = int(parts[-1])
      except ValueError:
        return await message.channel.send(
            "❌ يرجى كتابة المبلغ بشكل صحيح في نهاية الأمر!", reference=message
        )

      if amount <= 0:
        return await message.channel.send(
            "❌ يجب أن يكون المبلغ أكبر من الصفر!", reference=message
        )

      data = load_data()
      target_data = get_user_data(data, member.id)
      target_data["coins"] += amount
      save_data(data)

      await message.channel.send(
          f"✅ تم إضافة **{amount:,} كوينز** إلى رصيد العضو {member.mention}"
          f" بنجاح!\n🏦 رصيده الجديد: **{target_data['coins']:,} كوينز**",
          reference=message,
      )

    # 8. توب
    elif command_text in ["توب"]:
      data = load_data()
      if not data:
        return await message.channel.send(
            "❌ لا توجد بيانات أعضاء مسجلة في البنك حتى الآن!",
            reference=message,
        )

      sorted_users = sorted(
          data.items(),
          key=lambda x: (
              x[1].get("coins", 0) if isinstance(x[1], dict) else x[1]
          ),
          reverse=True,
      )

      description = ""
      for index, (user_id, user_info) in enumerate(
          sorted_users[:10], start=1
      ):
        coins = (
            user_info.get("coins", 0)
            if isinstance(user_info, dict)
            else user_info
        )
        description += f"**{index}.** <@{user_id}> ➔ **{coins:,}** 🪙\n"

      embed = discord.Embed(
          title="🏆 قائمة أغنى الأعضاء في البنك",
          description=description if description else "لا توجد بيانات.",
          color=discord.Color.gold(),
      )
      await message.channel.send(embed=embed, reference=message)


async def setup(bot):
  await bot.add_cog(Bank(bot))
