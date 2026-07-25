import json
import os
import discord
from discord import app_commands
from discord.ext import commands

DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(DATA_DIR, "temp_voice.json")


def load_config():
  if not os.path.exists(CONFIG_FILE):
    return {}
  try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception:
    return {}


def save_config(data):
  with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)


# --- لوحة التحكم التفاعلية بالأزرار ---
class TempVoiceControlView(discord.ui.View):

  def __init__(self, bot):
    super().__init__(timeout=None)
    self.bot = bot

  async def interaction_check(self, interaction: discord.Interaction) -> bool:
    # التحقق مما إذا كان المستخدم متصلاً بروم صوتية مؤقتة ولديه صلاحية التحكم
    voice_state = interaction.user.voice
    if not voice_state or not voice_state.channel:
      await interaction.response.send_message(
          "❌ يجب أن تكون متصلاً برومتك الصوتية المؤقتة لاستخدام الأزرار!",
          ephemeral=True,
      )
      return False
    return True

  @discord.ui.button(
      label="قفل", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="tv_lock"
  )
  async def lock_room(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    channel = interaction.user.voice.channel
    await channel.set_permissions(interaction.guild.default_role, connect=False)
    await interaction.response.send_message(
        "🔒 تم قفل الروم بنجاح.", ephemeral=True
    )

  @discord.ui.button(
      label="فتح",
      style=discord.ButtonStyle.success,
      emoji="🔓",
      custom_id="tv_unlock",
  )
  async def unlock_room(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    channel = interaction.user.voice.channel
    await channel.set_permissions(interaction.guild.default_role, connect=True)
    await interaction.response.send_message(
        "🔓 تم فتح الروم للجميع.", ephemeral=True
    )

  @discord.ui.button(
      label="إخفاء",
      style=discord.ButtonStyle.secondary,
      emoji="🙈",
      custom_id="tv_hide",
  )
  async def hide_room(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    channel = interaction.user.voice.channel
    await channel.set_permissions(
        interaction.guild.default_role, view_channel=False
    )
    await interaction.response.send_message(
        "🙈 تم إخفاء الروم عن الأعضاء.", ephemeral=True
    )

  @discord.ui.button(
      label="إظهار",
      style=discord.ButtonStyle.primary,
      emoji="👁️",
      custom_id="tv_show",
  )
  async def show_room(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    channel = interaction.user.voice.channel
    await channel.set_permissions(
        interaction.guild.default_role, view_channel=True
    )
    await interaction.response.send_message(
        "👁️ تم إظهار الروم للجميع.", ephemeral=True
    )


class TempVoice(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.temp_channels = {}

  @commands.Cog.listener()
  async def on_ready(self):
    # تسجيل الـ View بشكل دائم لكي تعمل الأزرار حتى بعد إعادة تشغيل البوت
    self.bot.add_view(TempVoiceControlView(self.bot))

  @commands.Cog.listener()
  async def on_voice_state_update(
      self,
      member: discord.Member,
      before: discord.VoiceState,
      after: discord.VoiceState,
  ):
    data = load_config()
    guild_id = str(member.guild.id)
    guild_config = data.get(guild_id, {})
    creator_channel_id = guild_config.get("creator_channel_id")

    # 1. إنشاء روم جديدة عند دخول روم الإنشاء
    if after.channel and after.channel.id == creator_channel_id:
      category = after.channel.category
      guild = member.guild
      channel_name = f"🔊 | روم {member.display_name}"

      overwrites = {
          guild.default_role: discord.PermissionOverwrite(connect=True),
          member: discord.PermissionOverwrite(
              manage_channel=True, connect=True, speak=True, move_members=True
          ),
      }

      try:
        temp_channel = await guild.create_voice_channel(
            name=channel_name, category=category, overwrites=overwrites
        )
        await member.move_to(temp_channel)
        self.temp_channels[temp_channel.id] = member.id
      except Exception as e:
        print(f"❌ خطأ في إنشاء الروم المؤقتة: {e}")

    # 2. حذف الروم تلقائياً عند خروج الجميع منها
    if before.channel and before.channel.id in self.temp_channels:
      if len(before.channel.members) == 0:
        try:
          await before.channel.delete()
          del self.temp_channels[before.channel.id]
        except Exception as e:
          print(f"❌ خطأ في حذف الروم المؤقتة: {e}")

  @app_commands.command(
      name="set_temp_voice",
      description="تحديد روم إنشاء الروم الصوتية المؤقتة",
  )
  @app_commands.describe(channel="روم الصوت المخصصة للإنشاء")
  @app_commands.default_permissions(administrator=True)
  async def set_temp_voice(
      self, interaction: discord.Interaction, channel: discord.VoiceChannel
  ):
    await interaction.response.defer(ephemeral=True)
    data = load_config()
    guild_id = str(interaction.guild.id)

    if guild_id not in data:
      data[guild_id] = {}

    data[guild_id]["creator_channel_id"] = channel.id
    save_config(data)

    await interaction.followup.send(
        f"✅ تم تعيين روم الإنشاء بنجاح إلى: {channel.mention}", ephemeral=True
    )

  @app_commands.command(
      name="setup_temp_panel",
      description="إرسال لوحة التحكم الخاصة بالروم الصوتية في الشات الحالي",
  )
  @app_commands.default_permissions(administrator=True)
  async def setup_temp_panel(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title="🎛️ لوحة التحكم بالروم الصوتية المؤقتة",
        description=(
            "قم بالضغط على الأزرار أدناه للتحكم برومك الصوتية الخاصة بك بسهولة"
            " تامة!\n\n🔒 **قفل** | 🔓 **فتح**\n🙈 **إخفاء** | 👁️ **إظهار**"
        ),
        color=discord.Color.blurple(),
    )
    embed.set_footer(text="يجب أن تكون متصلاً برومتك لتتمكن من استخدام الأزرار.")

    await interaction.channel.send(
        embed=embed, view=TempVoiceControlView(self.bot)
    )
    await interaction.followup.send(
        "✅ تم إرسال لوحة التحكم بنجاح!", ephemeral=True
    )


async def setup(bot):
  await bot.add_cog(TempVoice(bot))
