import discord
from discord import app_commands
from discord.ext import commands


# --- نافذة تغيير اسم الروم ---
class RenameModal(discord.ui.Modal, title="تغيير اسم الروم الصوتية"):
  new_name = discord.ui.TextInput(
      label="اسم الروم الجديد",
      placeholder="اكتب الاسم الجديد هنا...",
      max_length=100,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    voice_state = interaction.user.voice
    if not voice_state or not voice_state.channel:
      return await interaction.followup.send(
          "❌ يجب أن تكون متصلاً برومتك الصوتية لتتمكن من تغيير اسمها.",
          ephemeral=True,
      )

    channel = voice_state.channel
    target_name = self.new_name.value.strip()

    try:
      # تعديل الاسم مباشرة مع السبب
      await channel.edit(
          name=target_name, reason=f"تم التغيير بواسطة {interaction.user}"
      )
      await interaction.followup.send(
          f"✅ تم تغيير اسم الروم بنجاح إلى: **{target_name}**", ephemeral=True
      )
    except discord.Forbidden:
      await interaction.followup.send(
          "❌ ليس لدى البوت أو لديك الصلاحية الكافية لتعديل اسم الروم.",
          ephemeral=True,
      )
    except Exception as e:
      await interaction.followup.send(
          f"❌ حدث خطأ أثناء تغيير الاسم: `{e}`", ephemeral=True
      )


# --- نافذة دعوة عضو ---
class InviteModal(discord.ui.Modal, title="دعوة عضو للروم الصوتية"):
  user_input = discord.ui.TextInput(
      label="يوزر أو آي دي العضو المراد دعوته",
      placeholder="اكتب يوزر العضو هنا...",
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    voice_state = interaction.user.voice
    if not voice_state or not voice_state.channel:
      return await interaction.followup.send(
          "❌ يجب أن تكون متصلاً برومتك.", ephemeral=True
      )

    channel = voice_state.channel
    target_text = self.user_input.value.strip().strip("<@!>")
    target_member = None

    if target_text.isdigit():
      target_member = interaction.guild.get_member(int(target_text))
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
          "❌ لم يتم العثور على هذا العضو.", ephemeral=True
      )

    channel_link = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}"
    try:
      await target_member.send(
          f"📢 دعوة لك من {interaction.user.mention}!\nاقلط/ي بالسالفه القوية الي"
          f" هنا 👇\n🔗 {channel_link}"
      )
      await interaction.followup.send(
          f"✅ تم إرسال الدعوة إلى {target_member.mention} بنجاح!", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ تعذر إرسال رسالة خاصة (رسائله مغلقة).", ephemeral=True
      )


# --- نافذة طرد عضو ---
class KickModal(discord.ui.Modal, title="طرد عضو من الروم الصوتية"):
  user_input = discord.ui.TextInput(
      label="يوزر أو آي دي العضو المراد طرده",
      placeholder="اكتب يوزر العضو هنا...",
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    voice_state = interaction.user.voice
    if not voice_state or not voice_state.channel:
      return await interaction.followup.send(
          "❌ يجب أن تكون متصلاً برومتك.", ephemeral=True
      )

    channel = voice_state.channel
    target_text = self.user_input.value.strip().strip("<@!>")
    target_member = None

    if target_text.isdigit():
      target_member = interaction.guild.get_member(int(target_text))
    else:
      for m in interaction.guild.members:
        if (
            target_text.lower() in m.name.lower()
            or target_text.lower() in m.display_name.lower()
        ):
          target_member = m
          break

    if (
        not target_member
        or not target_member.voice
        or not target_member.voice.channel
        or target_member.voice.channel.id != channel.id
    ):
      return await interaction.followup.send(
          "❌ العضو غير موجود في رومك حالياً.", ephemeral=True
      )

    try:
      await target_member.move_to(None)
      await interaction.followup.send(
          f"👢 تم طرد {target_member.mention} من رومك.", ephemeral=True
      )
    except Exception:
      await interaction.followup.send("❌ حدث خطأ أثناء الطرد.", ephemeral=True)


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
    if after.channel and (
        "انشاء" in after.channel.name.lower()
        or after.channel.name.startswith("+")
    ):
      category = after.channel.category
      guild = member.guild
      channel_name = f"🔊 | روم {member.display_name}"

      overwrites = {
          guild.default_role: discord.PermissionOverwrite(connect=True),
          member: discord.PermissionOverwrite(
              manage_channel=True,
              connect=True,
              speak=True,
              move_members=True,
              view_channel=True,
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
