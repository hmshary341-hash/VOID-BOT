import datetime
import json
import os
import random
import discord
from discord import app_commands
from discord.ext import commands

# --- الإعدادات والثوابت ---
DATA_FILE = "/app/data/economy.json"

TASK_CHANNEL_ID = 1530834779833106543
LOG_CHANNEL_ID = 1530835629573673031
SPECIAL_ROLE_ID = 1530838834130976779  # رتبة ملك الحظ (من الصناديق)
RESET_ROLE_ID = 1529995977203777566  # الرتبة المسموح لها استخدام أمر التصفير

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
  today_str = str(datetime.date.today())

  if user_id not in data:
    data[user_id] = {
        "coins": 0,
        "last_task_date": "",
        "box_count": 0,
        "last_box_date": today_str,
        "daily_transferred": 0,
        "last_date": "",
        "last_daily_date": "",
        "last_work_date": "",
        "nerd_count": 0,
        "last_nerd_date": "",
        "task_request_time": "",
        "last_message_time": "",
    }
  else:
    user_data = data[user_id]
    if isinstance(user_data, int):
      data[user_id] = {
          "coins": user_data,
          "last_task_date": "",
          "box_count": 0,
          "last_box_date": today_str,
          "daily_transferred": 0,
          "last_date": "",
          "last_daily_date": "",
          "last_work_date": "",
          "nerd_count": 0,
          "last_nerd_date": "",
          "task_request_time": "",
          "last_message_time": "",
      }
    else:
      if "last_task_date" not in user_data:
        user_data["last_task_date"] = ""
      if "task_request_time" not in user_data:
        user_data["task_request_time"] = ""
      if "last_message_time" not in user_data:
        user_data["last_message_time"] = ""

      # التحقق من إعادة تعيين الصناديق إذا تغير اليوم
      if user_data.get("last_box_date") != today_str:
        user_data["last_box_date"] = today_str
        user_data["box_count"] = 0
      if "box_count" not in user_data:
        user_data["box_count"] = 0

  return data[user_id]


# فيو زر التأكيد مع التحقق الحقيقي من تفاعل العضو
class TaskConfirmView(discord.ui.View):

  def __init__(self, bot):
    super().__init__(timeout=180)
    self.bot = bot

  @discord.ui.button(
      label="تم إنجاز المهمة",
      style=discord.ButtonStyle.success,
      emoji="✅",
      custom_id="confirm_task_done",
  )
  async def confirm_task(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    user = interaction.user
    guild = interaction.guild
    today_str = str(datetime.date.today())

    data = load_data()
    user_data = get_user_data(data, user.id)

    # التأكد مرة أخرى من عدم إتمامها اليوم
    if user_data.get("last_task_date") == today_str:
      await interaction.response.send_message(
          "❌ أنت مسوي/ة المهمة أصلاً اليوم، لا تحاول تلف وتدور! 🤨",
          ephemeral=True,
      )
      return

    # البوت يتحقق هل العضو كتب رسالة أو تفاعل بعد طلب المهام ولا لا
    req_time_str = user_data.get("task_request_time", "")
    msg_time_str = user_data.get("last_message_time", "")

    is_cheating = True
    if req_time_str and msg_time_str:
      try:
        req_time = datetime.datetime.fromisoformat(req_time_str)
        msg_time = datetime.datetime.fromisoformat(msg_time_str)
        if msg_time > req_time:
          is_cheating = False
      except:
        pass

    if is_cheating:
      await interaction.response.send_message(
          "❌ تبي/ن تلعب/ين علي؟ أقول روح/ي خلصي المهمات ورجع/ي بعدين! 🤨",
          ephemeral=True,
      )
      return

    # إذا اجتاز الفحص بنجاح
    user_data["last_task_date"] = today_str
    reward = 500
    user_data["coins"] += reward
    save_data(data)

    current_balance = user_data["coins"]

    await interaction.response.edit_message(
        content=(
            "🎉 **كفو يا وحش! تأكد البوت من إنجازك للمهمة بنجاح!**\n💰 تم إضافة"
            f" **{reward:,} كوينز** إلى حسابك البنكي 🏦!\nرصيدك الحالي:"
            f" **{current_balance:,} كوينز**"
        ),
        view=None,
    )

    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
      embed_log = discord.Embed(
          title="📜 سجل المهام - إنجاز مهام",
          description=(
              f"👤 **العضو:** {user.mention}\n"
              "✅ **الحالة:** تم إنجاز المهمة اليومية والتحقق منها بنجاح\n"
              f"💰 **العملات:** +{reward:,} كوينز (الرصيد الكلي في البنك:"
              f" {current_balance:,})"
          ),
          color=0x00FF00,
      )
      await log_channel.send(embed=embed_log)


class TaskButtons(discord.ui.View):

  def __init__(self, bot):
    super().__init__(timeout=None)
    self.bot = bot

  # 1. زر إكمال المهام اليومية (بدون كتابة 500 كوينز)
  @discord.ui.button(
      label="إكمال المهام اليومية",
      style=discord.ButtonStyle.success,
      emoji="🎁",
      custom_id="claim_task_reward",
  )
  async def claim_task_reward(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    user = interaction.user
    today_str = str(datetime.date.today())

    data = load_data()
    user_data = get_user_data(data, user.id)

    # التحقق هل أتم المهمة اليوم مسبقاً
    if user_data.get("last_task_date") == today_str:
      await interaction.response.send_message(
          "❌ لا أنت تلعب على من! أقول روح.. خلصت مهمتك اليومية، تعال بكرة 🤨",
          ephemeral=True,
      )
      return

    # تسجيل وقت طلب المهام بدقة للتحقق لاحقاً
    user_data["task_request_time"] = datetime.datetime.now().isoformat()
    save_data(data)

    # اختيار 3 مهمات عشوائية
    assigned_tasks = random.sample(TASK_POOL, min(3, len(TASK_POOL)))
    tasks_list_str = "\n".join(
        [f"**{i+1}.** {task}" for i, task in enumerate(assigned_tasks)]
    )

    await interaction.response.send_message(
        f"🎯 **مهامك اليومية الخاصة بك يا وحش:**\n\n{tasks_list_str}\n\n👇"
        " تفاعل في الشات ونفذ المهام ثم اضغط على زر **(تم إنجاز المهمة)**"
        " أدناه:",
        view=TaskConfirmView(self.bot),
        ephemeral=True,
    )

  # 2. زر فتح الصناديق العشوائية (3 محاولات يومياً بشكل مستقل)
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

    # التحقق من الحد اليومي للصناديق (3 محاولات)
    if user_data["box_count"] >= 3:
      await interaction.response.send_message(
          "❌ لا أنت تلعب على من! أقول روح.. استهلكت محاولاتك الـ 3 لفتح الصناديق اليوم، تعال بكرة 🤨",
          ephemeral=True,
      )
      return

    user_data["box_count"] += 1

    # نظام الجوائز مع رتبة ملك الحظ النادرة وصعبة
    prizes = [
        {"name": "صندوق فاضي (هواء طازة)", "coins": 0, "rarity": "منحوس 🔴", "is_role": False},
        {"name": "50 كوينز خفيفة", "coins": 50, "rarity": "عادي 🟢", "is_role": False},
        {"name": "150 كوينز ممتازة", "coins": 150, "rarity": "ممتاز 🔵", "is_role": False},
        {"name": "500 كوينز أسطورية", "coins": 500, "rarity": "أسطوري 🟡", "is_role": False},
        {"name": "👑 ملك الحظ (5000 كوينز + رتبة ملك الحظ)", "coins": 5000, "rarity": "نادرة جداً وصعبة 💎", "is_role": True},
    ]
    weights = [45, 30, 15, 8, 2]

    won_prize = random.choices(prizes, weights=weights, k=1)[0]

    if won_prize["coins"] > 0:
      user_data["coins"] += won_prize["coins"]

    save_data(data)
    current_balance = user_data["coins"]
    remaining_attempts = 3 - user_data["box_count"]

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
          f"🚨 **يا إلهييي!** مستحيل! فتحت الصندوق (محاولة {user_data['box_count']}/3) وطاحت في يدك الجائزة الكبرى:\n"
          f"**{won_prize['name']}**!\n{role_status} 🔥💎\nرصيدك الحالي:"
          f" **{current_balance:,} كوينز** 🏦"
      )
      log_color = 0x9B59B6
      log_title = "📜 سجل الصناديق - 🏆 فوز أسطوري برتبة ملك الحظ!"

      try:
        await interaction.channel.send(
            f"@everyone يا جماعة الخير! شوفوا الحظ الخرافي عند {user.mention}، فتح الصندوق وفاز برتبة **ملك الحظ**! 🔥👑 **اشفحو عليه تراه اخذ الرتبه!**"
        )
      except:
        pass

    elif won_prize["coins"] == 0:
      reply_msg = (
          f"📦 فتحه.. والصندوق (محاولة {user_data['box_count']}/3) طلع **فاضي وهواء صصافي**! حظاً أوفر يا"
          f" منحوس 😂\nرصيدك الحالي: **{current_balance:,} كوينز** 🏦\n📌 محاولات الصناديق المتبقية: {remaining_attempts}"
      )
      log_color = 0xED4245
      log_title = "📜 سجل الصناديق - صندوق فارغ"
    else:
      reply_msg = (
          f"📦 فتحت الصندوق (محاولة {user_data['box_count']}/3) وطلع لك: **{won_prize['name']}**!\nرصيدك الجديد:"
          f" **{current_balance:,} كوينز** 🏦\n📌 محاولات الصناديق المتبقية: {remaining_attempts}"
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
              f"📊 **محاولة الصندوق:** ({user_data['box_count']}/3)\n"
              f"💰 **الرصيد البنكي:** {current_balance:,} كوينز"
          ),
          color=log_color,
      )
      await log_channel.send(embed=embed_log)


class TaskSystemCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  # مراقب الرسائل لتحديث وقت آخر تفاعل للعضو تلقائياً
  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author.bot:
      return
    data = load_data()
    user_data = get_user_data(data, message.author.id)
    user_data["last_message_time"] = datetime.datetime.now().isoformat()
    save_data(data)

  task_group = app_commands.Group(
      name="task", description="أوامر نظام المهام والصناديق اليومية"
  )

  # 1. أمر نشر لوحة المهام (للأدمن فقط)
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
            "• 🎁 استلام **المهام اليومية** (مرة واحدة فقط يومياً).\n"
            "• 📦 فتح **الصناديق العشوائية** (**3 محاولات يومياً** بحظك.. قد تفوز"
            " بكوينز أو **رتبة ملك الحظ** النادرة والصعبة!).\n\n"
            "⬇️ **اختر أحد الأزرار بالأسفل:**"
        ),
        color=0x2B2D31,
    )

    await target_channel.send(embed=embed, view=TaskButtons(self.bot))
    await interaction.response.send_message(
        "✅ تم نشر لوحة المهام بنجاح!", ephemeral=True
    )

  # 2. أمر التصفير مع خيار تحديد العضو (اختياري)
  @task_group.command(
      name="reset",
      description=(
          "إعادة تعيين محاولات المهام والصناديق (لك أو لعضو تختاره)"
      ),
  )
  @app_commands.describe(
      member="العضو المراد تصفير مهامه وصناديقه (اختياري)"
  )
  async def reset_tasks(
      self, interaction: discord.Interaction, member: discord.Member = None
  ):
    has_role = any(role.id == RESET_ROLE_ID for role in interaction.user.roles)
    if not has_role and not interaction.user.guild_permissions.administrator:
      await interaction.response.send_message(
          "❌ عذراً، هذا الأمر مخصص فقط للأشخاص المخولين!", ephemeral=True
      )
      return

    # إذا تم تحديد عضو يصفر له، وإذا لم يتم التحديد يصفر للمنفذ نفسه
    target = member if member else interaction.user

    data = load_data()
    user_data = get_user_data(data, target.id)
    user_data["last_task_date"] = ""
    user_data["box_count"] = 0
    user_data["last_box_date"] = ""
    user_data["task_request_time"] = ""
    user_data["last_message_time"] = ""
    save_data(data)

    if member:
      await interaction.response.send_message(
          f"🔄 تم تصفير وإعادة تعيين محاولات المهام والصناديق للعضو"
          f" {member.mention} بنجاح! يقدر يعيدها الحين.",
          ephemeral=True,
      )
    else:
      await interaction.response.send_message(
          "🔄 تم تصفير وإعادة تعيين محاولات المهام والصناديق الخاصة بك بنجاح!",
          ephemeral=True,
      )


async def setup(bot):
  await bot.add_cog(TaskSystemCog(bot))
