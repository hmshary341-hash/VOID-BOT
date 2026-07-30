import discord
from discord.ext import commands

# --- آي دي الرتبة التلقائية للعضو الجديد ---
AUTO_ROLE_ID = 1532245781929660446

# --- آي دي الرتب الخاصة بكل روم ---
POETRY_ROLE_ID = 1530446393838403705  # آي دي رتبة الشعر
GLITCH_ROLE_ID = 1530446666740531362  # آي دي رتبة التكليجات
CREATION_ROLE_ID = 1530446833435021413  # آي دي رتبة الإبداعات


class Separators(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  # حدث الانضمام لإعطاء الرتبة التلقائية لأي شخص يدخل السيرفر
  @commands.Cog.listener()
  async def on_member_join(self, member):
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
      try:
        await member.add_roles(role)
      except Exception as e:
        print(f"❌ لم يتمكن البوت من إعطاء الرتبة التلقائية للعضو الجديد: {e}")

  @commands.Cog.listener()
  async def on_message(self, message):
    # تجاهل رسائل البوتات أو الرسائل التي ليست في السيرفرات
    if message.author.bot or not message.guild:
      return

    # 1. روم الشعر
    if message.channel.id == 1530050492938584124:
      await message.reply("صح لسانك يا الشاعر/ه 🤍")
      role = message.guild.get_role(POETRY_ROLE_ID)
      if role and role not in message.author.roles:
        try:
          await message.author.add_roles(role)
        except Exception as e:
          print(f"❌ لم يتمكن البوت من إعطاء رتبة الشعر: {e}")

    # 2. روم التكليجات
    elif message.channel.id == 1530051019608690708:
      await message.reply("ههههههههه يا وحش قفطت التكليجه")
      role = message.guild.get_role(GLITCH_ROLE_ID)
      if role and role not in message.author.roles:
        try:
          await message.author.add_roles(role)
        except Exception as e:
          print(f"❌ لم يتمكن البوت من إعطاء رتبة التكليجات: {e}")

    # 3. روم الإبداعات
    elif message.channel.id == 1530051188698120233:
      await message.reply("اي والله إبداع انت/ي بعيونا مبدع/ه")
      role = message.guild.get_role(CREATION_ROLE_ID)
      if role and role not in message.author.roles:
        try:
          await message.author.add_roles(role)
        except Exception as e:
          print(f"❌ لم يتمكن البوت من إعطاء رتبة الإبداعات: {e}")


async def setup(bot):
  await bot.add_cog(Separators(bot))
