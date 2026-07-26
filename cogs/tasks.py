import datetime
import json
import os
import random
import discord
from discord import app_commands
from discord.ext import commands

DATA_FILE = "/app/data/economy.json"

TASK_CHANNEL_ID = 1530834779833106543
LOG_CHANNEL_ID = 1530835629573673031
SPECIAL_ROLE_ID = 1530838834130976779


def load_data():
  if not os.path.exists(DATA_FILE):
    return {}
  try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except:
    return {}


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)


def get_user_data(data, user_id):
  user_id = str(user_id)
  if user_id not in data:
    data[user_id] = {
        "coins": 0,
        "last_task_date": "",
        "daily_transferred": 0,
        "last_date": "",
        "last_daily_date": "",
        "last_work_date": "",
        "nerd_count": 0,
        "last_nerd_date": "",
    }
  else:
    user_data = data[user_id]
    if isinstance(user_data, int):
      data[user_id] = {
          "coins": user_data,
          "last_task_date": "",
          "daily_transferred": 0,
          "last_date": "",
          "last_daily_date": "",
          "last_work_date": "",
          "nerd_count": 0,
          "last_nerd_date": "",
      }
    elif "last_task_date" not in user_data:
      user_data["last_task_date"] = ""
  return data[user_id]


class TaskButtons(discord.ui.View):

  def __init__(self, bot):
    super().__init__(timeout=None)
    self.bot = bot

  @discord.ui.button(
      label="إكمال المهمة (500 كوينز)",
      style=discord.ButtonStyle.success,
      emoji="🎁",
      custom_id="claim_task_reward",
  )
  async def claim_task_reward(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    user = interaction.user
    guild = interaction.guild
    today_str = str(datetime.date.today())

    data = load_data()
    user_data = get_user_data(data, user.id)

    if user_data.get("last_task_date") == today_str:
      await interaction.response.send_message(
          "❌ لقد أتممت مهمتك اليومية بالفعل! تتجدد المهمة كل يوم، تعال غداً.",
          ephemeral=True,
      )
      return

    reward = 500
    user_data["coins"] += reward
    user_data["last_task_date"] = today_str
    save_data(data)

    current_balance = user_data["coins"]

    await interaction.response.send_message(
        f"🎉 مبروك يا وحش! أتممت المهمة بنجاح وتمت إضافة **{reward:,} كوينز**"
        f" إلى حسابك البنكي 🏦!\nرصيدك الحالي: **{current_balance:,} كوينز**",
        ephemeral=True,
    )

    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
      embed_log = discord.Embed(
          title="📜 سجل المهام - إنجاز مهمة",
          description=(
              f"👤 **العضو:** {user.mention}\n"
              "✅ **الحالة:** تم التحقق وإنجاز المهمة بنجاح\n"
              f"💰 **العملات:** +{reward:,} كوينز (الرصيد الكلي في البنك:"
              f" {current_balance:,})"
          ),
          color=0x00FF00,
      )
      await log_channel.send(embed=embed_log)

  @discord.ui.button(
      label="فتح صندوق عشوائي",
      style=discord.ButtonStyle.danger,
      emoji="📦",
      custom_id="open_mystery_box",
  )
  async def open_mystery_box(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    user = interaction.user
    guild = interaction.guild

    prizes = [
        {"name": "100 كوينز عادية", "coins": 100, "rarity": "عادي 🟢"},
        {"name": "500 كوينز ممتازة", "coins": 500, "rarity": "ممتاز 🔵"},
        {"name": "1500 كوينز أسطورية", "coins": 1500, "rarity": "أسطوري 🟡"},
        {
            "name": "👑 جائزة نادرة: 5000 كوينز + رتبة ملك الحظ",
            "coins": 5000,
            "rarity": "نادرة وحصرية 💎",
        },
        {"name": "صندوق فاضي (هواء طازة)", "coins": 0, "rarity": "منحوس 🔴"},
    ]

    won_prize = random.choice(prizes)

    data = load_data()
    user_data = get_user_data(data, user.id)

    if won_prize["coins"] > 0:
      user_data["coins"] += won_prize["coins"]
      save_data(data)

    current_balance = user_data["coins"]

    if won_prize["coins"] == 5000:
      role = guild.get_role(SPECIAL_ROLE_ID)
      if role:
        try:
          await user.add_roles(role)
          role_status = f"✅ وتم إعطاؤك رتبة **{role.name}** بنجاح!"
        except:
          role_status = "⚠️ فزت بالرتبة بس البوت ما عنده صلاحية."
      else:
        role_status = "⚠️ رتبة ملك الحظ غير موجودة أو الأيدي خطأ."

      reply_msg = (
          "🚨 **يا إلهييي!** فتحت الصندوق وطاحت في يدك الكبرى:\n"
          f"**{won_prize['name']}**!\n{role_status} 🔥💎\nرصيدك الحالي:"
          f" **{current_balance:,} كوينز** 🏦"
      )
      log_color = 0x9B59B6
      log_title = "📜 سجل المهام - 🏆 الحصول على جائزة نادرة ورتبة ملك الحظ!"

    elif won_prize["coins"] == 0:
      reply_msg = (
          "📦 فتحه.. والصندوق طلع **فاضي وهيوا صصافي**! حظاً أوفر مرة ثانية يا"
          f" منحوس 😂\nرصيدك الحالي: **{current_balance:,} كوينز** 🏦"
      )
      log_color = 0xED4245
      log_title = "📜 سجل المهام - فتح صندوق"
    else:
      reply_msg = (
          f"📦 فتحت الصندوق وطلع لك: **{won_prize['name']}**!\nرصيدك الجديد:"
          f" **{current_balance:,} كوينز** 🏦"
      )
      log_color = 0xF1C40F
      log_title = "📜 سجل المهام - فتح صندوق"

    await interaction.response.send_message(reply_msg, ephemeral=True)

    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
      embed_log = discord.Embed(
          title=log_title,
          description=(
              f"👤 **العضو:** {user.mention}\n"
              f"📦 **الجائزة:** {won_prize['name']}\n"
              f"✨ **التصنيف:** {won_prize['rarity']}\n"
              f"💰 **الرصيد البنكي:** {current_balance:,} كوينز"
          ),
          color=log_color,
      )
      await log_channel.send(embed=embed_log)


class TaskSystemCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  # مجموعة الأوامر الفرعية تحت الأمر الرئيسي /task
  task_group = app_commands.Group(
      name="task", description="أوامر نظام المهام والصناديق اليومية"
  )

  @task_group.command(
      name="panel", description="نشر لوحة المهام اليومية في السيرفر"
  )
  @app_commands.default_permissions(administrator=True)
  async def panel(self, interaction: discord.Interaction):
    target_channel = self.bot.get_channel(TASK_CHANNEL_ID)
    if not target_channel:
      target_channel = interaction.channel

    embed = discord.Embed(
        title="🎯 لوحة المهام اليومية والصناديق",
        description=(
            "مرحبًا بك في نظام المهام والصناديق العشوائية.\n\n"
            "✨ **ما يمكنك فعله هنا:**\n\n"
            "• 🎁 إنجاز المهام واستلام **500 كوينز** (**تتجدد يومياً تلقائياً**).\n"
            "• 📦 فتح الصناديق العشوائية (تنضاف كوينزاتها لحسابك البنكي أو"
            " **رتبة ملك الحظ**!).\n\n"
            "⬇️ **اختر أحد الأزرار بالأسفل:**"
        ),
        color=0x2B2D31,
    )

    await target_channel.send(embed=embed, view=TaskButtons(self.bot))
    await interaction.response.send_message(
        "✅ تم نشر لوحة المهام وربطها بالبنك وتفعيل التجديد اليومي بنجاح!",
        ephemeral=True,
    )


async def setup(bot):
  await bot.add_cog(TaskSystemCog(bot))
