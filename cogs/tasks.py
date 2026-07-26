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

# قائمة المهام العشوائية المتنوعة
TASK_POOL = [
    "💬 اكتب 'سبحان الله وبحمده' في الشات العام.",
    "🎮 العب أي لعبة في الديسكورد أو جهازك لمدة 5 دقائق.",
    "📸 صور أطرف شيء جنبك أو في غرفتك.",
    "🤝 ساعد شخص في الشات أو رد على استفساره.",
    "☕ قم اشرب كاسة موية وخذ لك راحة قصيرة.",
    "😂 ارسل نكتة مضحكة أو موقف محرج في الشات العام.",
    "⭐ حط تفاعل (إيموجي) على آخر رسائل في السيرفر.",
    "🎤 ادخل روم صوتي لمدة دقيقة وسلم على الموجودين.",
    "✍️ اكتب اسمك بالعربي معكوس في الشات العام.",
    "🔥 حط شعار السيرفر أو اسم مميز في حالتك لمدة ساعة.",
]


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
        "last_box_date": "",
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
          "last_box_date": "",
          "daily_transferred": 0,
          "last_date": "",
          "last_daily_date": "",
          "last_work_date": "",
          "nerd_count": 0,
          "last_nerd_date": "",
      }
    else:
      if "last_task_date" not in user_data:
        user_data["last_task_date"] = ""
      if "last_box_date" not in user_data:
        user_data["last_box_date"] = ""
  return data[user_id]


class TaskButtons(discord.ui.View):

  def __init__(self, bot):
    super().__init__(timeout=None)
    self.bot = bot

  # 1. زر إكمال المهمة (يعطي 3 مهمات عشوائية مخفية مرة كل يوم)
  @discord.ui.button(
      label="إكمال المهام اليومية (500 كوينز)",
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

    # التحقق هل خلص مهمته اليوم ولا لا
    if user_data.get("last_task_date") == today_str:
      await interaction.response.send_message(
          "❌ لا أنت تلعب على من! أقول روح.. خلصت مهمتك اليومية، تعال بكرة 🤨",
          ephemeral=True,
      )
      return

    # اختيار 3 مهمات عشوائية لكل مستخدم بحظه
    assigned_tasks = random.sample(TASK_POOL, min(3, len(TASK_POOL)))
    tasks_list_str = "\n".join(
        [f"**{i+1}.** {task}" for i, task in enumerate(assigned_tasks)]
    )

    reward = 500
    user_data["coins"] += reward
    user_data["last_task_date"] = today_str
    save_data(data)

    current_balance = user_data["coins"]

    # رسالة مخفية بالمهام الثلاث والرصيد
    await interaction.response.send_message(
        f"🎯 **مهامك اليومية الخاصة بك يا وحش:**\n\n{tasks_list_str}\n\n🎉"
        f" تم إضافة **{reward:,} كوينز** إلى حسابك البنكي 🏦!\nرصيدك الحالي:"
        f" **{current_balance:,} كوينز**",
        ephemeral=True,
    )

    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
      embed_log = discord.Embed(
          title="📜 سجل المهام - إنجاز مهام",
          description=(
              f"👤 **العضو:** {user.mention}\n"
              "✅ **الحالة:** تم جلب المهام الثلاث بنجاح\n"
              f"💰 **العملات:** +{reward:,} كوينز (الرصيد الكلي في البنك:"
              f" {current_balance:,})"
          ),
          color=0x00FF00,
      )
      await log_channel.send(embed=embed_log)

  # 2. زر فتح الصناديق العشوائية (مرة واحدة يومياً + رتبة نادرة وصعبة)
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
    today_str = str(datetime.date.today())

    data = load_data()
    user_data = get_user_data(data, user.id)

    # التحقق من فتح الصندوق مرة واحدة يومياً
    if user_data.get("last_box_date") == today_str:
      await interaction.response.send_message(
          "❌ لا أنت تلعب على من! أقول روح.. فتحت صندوقك اليوم، تعال بكرة 🤨",
          ephemeral=True,
      )
      return

    user_data["last_box_date"] = today_str

    # نظام الجوائز مع جعل رتبة ملك الحظ نادرة جداً وصعبة (نسبة ضعيفة جداً)
    prizes = [
        {"name": "صندوق فاضي (هواء طازة)", "coins": 0, "rarity": "منحوس 🔴", "is_role": False},
        {"name": "50 كوينز خفيفة", "coins": 50, "rarity": "عادي 🟢", "is_role": False},
        {"name": "150 كوينز ممتازة", "coins": 150, "rarity": "ممتاز 🔵", "is_role": False},
        {"name": "500 كوينز أسطورية", "coins": 500, "rarity": "أسطوري 🟡", "is_role": False},
        {"name": "👑 ملك الحظ (5000 كوينز + رتبة ملك الحظ)", "coins": 5000, "rarity": "نادرة جداً وصعبة 💎", "is_role": True},
    ]
    # أوزان الاحتمالات (تخلي الصندوق الفاضي والكوينز العادية أكثر شيوعاً، ورتبة ملك الحظ نادرة وصعبة)
    weights = [45, 30, 15, 8, 2] # 2% فقط لملك الحظ

    won_prize = random.choices(prizes, weights=weights, k=1)[0]

    if won_prize["coins"] > 0:
      user_data["coins"] += won_prize["coins"]

    save_data(data)
    current_balance = user_data["coins"]

    if won_prize["is_role"]:
      role = guild.get_role(SPECIAL_ROLE_ID)
      if role:
        try:
          await user.add_roles(role)
          role_status = f"✅ وتم إعطاؤك رتبة **{role.name}** بنجاح!"
        except:
          role_status = "⚠️ فزت بالرتبة بس البوت ما عنده صلاحية رتب."
      else:
        role_status = "⚠️ رتبة ملك الحظ غير موجودة أو الأيدي خطأ."

      reply_msg = (
          "🚨 **يا إلهييي!** مستحيل! فتحت الصندوق وطاحت في يدك الجائزة الكبرى:\n"
          f"**{won_prize['name']}**!\n{role_status} 🔥💎\nرصيدك الحالي:"
          f" **{current_balance:,} كوينز** 🏦"
      )
      log_color = 0x9B59B6
      log_title = "📜 سجل الصناديق - 🏆 فوز أسطوري برتبة ملك الحظ!"

      # إرسال رسالة علنية في الشات العام منشن للكل وللاعبي الرتبة
      try:
        await interaction.channel.send(
            f"@everyone يا جماعة الخير! شوفوا الحظ الخرافي عند {user.mention}، فتح الصندوق وفاز برتبة **ملك الحظ**! 🔥👑 **اشفحو عليه تراه اخذ الرتبه!**"
        )
      except:
        pass

    elif won_prize["coins"] == 0:
      reply_msg = (
          "📦 فتحه.. والصندوق طلع **فاضي وهواء صصافي**! حظاً أوفر مرة ثانية يا"
          f" منحوس 😂\nرصيدك الحالي: **{current_balance:,} كوينز** 🏦"
      )
      log_color = 0xED4245
      log_title = "📜 سجل الصناديق - صندوق فارغ"
    else:
      reply_msg = (
          f"📦 فتحت الصندوق وطلع لك: **{won_prize['name']}**!\nرصيدك الجديد:"
          f" **{current_balance:,} كوينز** 🏦"
      )
      log_color = 0xF1C40F
      log_title = "📜 سجل الصناديق - فتح صندوق"

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
            "مرحبًا بك في نظام المهام والصناديق العشوائية الحصرية.\n\n"
            "✨ **ما يمكنك فعله هنا:**\n\n"
            "• 🎁 استلام **المهام الثلاث اليومية** و500 كوينز (تتجدد يومياً لكل"
            " شخص).\n"
            "• 📦 فتح **الصندوق العشوائي اليومي** (بحظك.. قد تفوز بكوينز أو"
            " **رتبة ملك الحظ** النادرة والصعبة!).\n\n"
            "⬇️ **اختر أحد الأزرار بالأسفل:**"
        ),
        color=0x2B2D31,
    )

    await target_channel.send(embed=embed, view=TaskButtons(self.bot))
    await interaction.response.send_message(
        "✅ تم نشر لوحة المهام وتطبيق الشروط والقواعد الجديدة بنجاح!",
        ephemeral=True,
    )


async def setup(bot):
  await bot.add_cog(TaskSystemCog(bot))
