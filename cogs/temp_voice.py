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


# --- نافذة إدخال بيانات الدعوة (Modal) ---
class InviteModal(discord.ui.Modal, title="دعوة عضو للروم الصوتية"):
  user_input = discord.ui.TextInput(
      label="يوزر أو آي دي العضو المراد دعوته",
      placeholder="مثال: username أو الآي دي الخاص به",
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.user.voice.channel

    if not channel:
      return await interaction.followup.send(
          "❌ يجب أن تكون متصلاً برومتك الصوتية لتتمكن من دعوة الأعضاء.",
          ephemeral=True,
      )

    target_text = self.user_input.value.strip()
    clean_id = target_text.strip("<@!>")

    target_member = None
    if clean_id.isdigit():
      target_member = interaction.guild.get_member(int(clean_id))
    else:
      for m in interaction.guild.members:
        if (
            target_text.lower() in m.name.lower()
            or target_text.lower() in m.display_name.lower()
        ):
          target_member = m
          break

    if not target_member:
      return await interaction.followup.send(
          "❌ لم يتم العثور على هذا العضو، تأكد من صحة اليوزر أو الآي دي.",
          ephemeral=True,
      )

    channel_link = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}"

    try:
      await target_member.send(
          f"📢 دعوة لك من {interaction.user.mention}!\nاقلط/ي بالسالفه القوية الي"
          f" هنا 👇\n🔗 {channel_link}"
      )
      await interaction.followup.send(
          f"✅ تم إرسال الدعوة إلى {target_member.mention} بنجاح عبر الخاص!",
          ephemeral=True,
      )
    except Exception:
      await interaction.followup.send(
          f"❌ تعذر إرسال رسالة خاصة إلى {target_member.mention} (قد تكون رسائله"
          " الخاصة مغلقة).",
          ephemeral=True,
      )


# --- نافذة إدخال بيانات الطرد (Modal) ---
class KickModal(discord.ui.Modal, title="طرد عضو من الروم الصوتية"):
  user_input = discord.ui.TextInput(
      label="يوزر أو آي دي العضو المراد طرده",
      placeholder="مثال: username أو الآي دي الخاص به",
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.user.voice.channel

    if not channel:
      return await interaction.followup.send(
          "❌ يجب أن تكون متصلاً برومتك الصوتية لتتمكن من طرد الأعضاء.",
          ephemeral=True,
      )

    target_text = self.user_input.value.strip()
    clean_id = target_text.strip("<@!>")

    target_member = None
    if clean_id.isdigit():
      target_member = interaction.guild.get_member(int(clean_id))
    else:
      for m in interaction.guild.members:
        if (
            target_text.lower() in m.name.lower()
            or target_text.lower() in m.display_name.lower()
        ):
          target_member = m
          break

    if not target_member:
      return await interaction.followup.send(
          "❌ لم يتم العثور على هذا العضو في السيرفر.", ephemeral=True
      )

    if (
        not target_member.voice
        or not target_member.voice.channel
        or target_member.voice.channel.id != channel.id
    ):
      return await interaction.followup.send(
          f"❌ العضو {target_member.mention} ليس موجوداً في رومك الصوتية حالياً.",
          ephemeral=True,
      )

    try:
      await target_member.move_to(None)
      await interaction.followup.send(
          f"👢 تم طرد {target_member.mention} من رومك بنجاح.", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ أثناء محاولة طرد العضو، تأكد من صلاحيات البوت.",
          ephemeral=True,
      )


# --- نافذة تغيير اسم الروم (Modal) ---
class RenameModal(discord.ui.Modal, title="تغيير اسم الروم الصوتية"):
  new_name = discord.ui.TextInput(
      label="اسم الروم الجديد",
      placeholder="اكتب الاسم الجديد هنا...",
      max_length=100,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.user.voice.channel

    if not channel:
      return await interaction.followup.send(
          "❌ يجب أن تكون متصلاً برومتك الصوتية لتتمكن من تغيير اسمها.",
          ephemeral=True,
      )

    try:
      await channel.edit(name=self.new_name.value.strip())
      await interaction.followup.send(
          f"✅ تم تغيير اسم الروم بنجاح إلى: **{self.new_name.value.strip()}**",
          ephemeral=True,
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ أثناء محاولة تغيير اسم الروم، تأكد من صلاحيات البوت.",
          ephemeral=True,
      )


# --- لوحة التحكم التفاعلية بالأزرار ---
class TempVoiceControlView(discord.ui.View):

  def __init__(self, bot):
    super().__init__(timeout=None)
    self.bot = bot

  async def interaction_check(self, interaction: discord.Interaction) -> bool:
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

  @discord.ui.button(
      label="تعديل الاسم",
      style=discord.ButtonStyle.secondary,
      emoji="✏️",
      custom_id="tv_rename",
  )
  async def rename_room(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(RenameModal())

  @discord.ui.button(
      label="دعوة",
      style=discord.ButtonStyle.blurple,
      emoji="📩",
      custom_id="tv_invite",
  )
  async def invite_member(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(InviteModal())

  @discord.ui.button(
      label="طرد",
      style=discord.ButtonStyle.danger,
      emoji="👢",
      custom_id="tv_kick",
  )
  async def kick_member(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(KickModal())


class TempVoice(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.temp_channels = {}

  @commands.Cog.listener()
  async def on_ready(self):
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
            " تامة!\n\n🔒 **قفل** | 🔓 **فتح**\n🙈 **إخفاء** | 👁️"
            " **إظهار**\n✏️ **تعديل الاسم**\n📩 **دعوة** | 👢 **طرد**"
        ),
        color=discord.Color.blurple(),
    )
    embed.set_footer(
        text="يجب أن تكون متصلاً برومتك لتتمكن من استخدام الأزرار."
    )

    await interaction.channel.send(
        embed=embed, view=TempVoiceControlView(self.bot)
    )
    await interaction.followup.send(
        "✅ تم إرسال لوحة التحكم بنجاح!", ephemeral=True
    )


async def setup(bot):
  await bot.add_cog(TempVoice(bot))
