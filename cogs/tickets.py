import discord
from discord import app_commands
from discord.ext import commands
import io
import chat_exporter
import random
from datetime import datetime

# الإعدادات
CATEGORY_ID = 1525952823156801576
STAFF_ROLE_ID = 1527807423186862080
LOG_CHANNEL_ID = 1527750890952462408
IMAGE_URL = "https://cdn.discordapp.com/attachments/1526978453826699324/1528190964215320778/file_00000000da1c71f4863b28202a995e4e.png"

# --- الأزرار الخاصة داخل التذكرة ---
class TicketActions(discord.ui.View):
    def __init__(self, opener=None):
        super().__init__(timeout=None)
        self.opener = opener
        self.claimed_by = None

    @discord.ui.button(label="استلام التذكرة", style=discord.ButtonStyle.primary, emoji="✅", custom_id="claim_ticket")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.claimed_by: 
            return await interaction.response.send_message("❌ التذكرة مستلمة بالفعل!", ephemeral=True)
        self.claimed_by = interaction.user
        button.disabled = True
        embed = interaction.message.embeds[0]
        embed.add_field(name="🛡️ مستلمة بواسطة", value=interaction.user.mention, inline=False)
        embed.color = discord.Color.green()
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"✅ تم استلام التذكرة.", ephemeral=True)

    @discord.ui.button(label="قفل", style=discord.ButtonStyle.secondary, emoji="🔒", custom_id="lock_ticket")
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.set_permissions(interaction.user, send_messages=False)
        await interaction.response.send_message("🔒 تم قفل التذكرة.", ephemeral=True)

    @discord.ui.button(label="حذف", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="delete_ticket")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # 1. إرسال اللوج عبر كوج اللوجز
        logs_cog = interaction.client.get_cog("Logs")
        if logs_cog:
            opener_user = self.opener if self.opener else interaction.user 
            await logs_cog.send_ticket_log(
                ticket_name=interaction.channel.name,
                opener=opener_user,
                claimer=self.claimed_by,
                closer=interaction.user,
                open_time=interaction.channel.created_at,
                close_time=datetime.now(),
                reason="تم حذف التذكرة",
                transcript_url="https://transcript-service.com/"
            )

        # 2. التوثيق (Chat Exporter)
        transcript = await chat_exporter.export(interaction.channel)
        transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{interaction.channel.name}.html")
        
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(file=transcript_file)
            
        await interaction.channel.delete()

# --- المودال (للإبلاغات) ---
class ReportModal(discord.ui.Modal, title='نموذج الإبلاغ'):
    target = discord.ui.TextInput(label='يوزر الشخص المبلغ عنه', style=discord.TextStyle.short, required=True)
    reason = discord.ui.TextInput(label='السبب', style=discord.TextStyle.paragraph, required=True)
    proof = discord.ui.TextInput(label='الدليل (رابط الصورة)', style=discord.TextStyle.short, required=True)

    def __init__(self, report_type):
        super().__init__()
        self.report_type = report_type

    async def on_submit(self, interaction: discord.Interaction):
        # استخدام defer مع ephemeral لمنع انتهاء وقت التفاعل (Interaction failed)
        await interaction.response.defer(ephemeral=True)
        
        ticket_num = random.randint(1000, 9999) 
        category = interaction.guild.get_channel(CATEGORY_ID)
        channel = await interaction.guild.create_text_channel(name=f"ticket-{ticket_num}", category=category)
        
        await channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        
        embed = discord.Embed(title=f"تذكرة {self.report_type} | #{ticket_num}", color=discord.Color.dark_purple())
        embed.add_field(name="👤 المشتكي", value=interaction.user.mention, inline=False)
        embed.add_field(name="المبلغ عنه", value=self.target.value, inline=False)
        embed.add_field(name="📝 السبب", value=self.reason.value, inline=False)
        embed.add_field(name="🖼️ الدليل", value=self.proof.value, inline=False)
        embed.set_image(url=IMAGE_URL)
        
        await channel.send(f"<@&{STAFF_ROLE_ID}>", embed=embed, view=TicketActions(opener=interaction.user))
        await interaction.followup.send(f"✅ تم فتح تذكرتك: {channel.mention}", ephemeral=True)

# --- قائمة الاختيار ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder='اختر نوع التذكرة...', options=[
            discord.SelectOption(label='إبلاغ عن إداري', value='إبلاغ عن إداري', emoji='🛡️'),
            discord.SelectOption(label='إبلاغ عن عضو', value='إبلاغ عن عضو', emoji='👤'),
            discord.SelectOption(label='استفسار', value='استفسار', emoji='❓'),
        ], custom_id="ticket_select_persistent")

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] in ['إبلاغ عن إداري', 'إبلاغ عن عضو']:
            await interaction.response.send_modal(ReportModal(report_type=self.values[0]))
        else:
            # تم إصلاح الاستفسار هنا ليقوم بإنشاء القناة مباشرة مثل البقية بدون تعليق
            await interaction.response.defer(ephemeral=True)
            
            ticket_num = random.randint(1000, 9999)
            category = interaction.guild.get_channel(CATEGORY_ID)
            channel = await interaction.guild.create_text_channel(name=f"inquiry-{ticket_num}", category=category)
            
            await channel.set_permissions(interaction.guild.default_role, read_messages=False)
            await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
            
            embed = discord.Embed(title=f"تذكرة استفسار | #{ticket_num}", description="يرجى كتابة استفسارك هنا وسيقوم الإدارة بالرد عليك قريباً.", color=discord.Color.blue())
            embed.add_field(name="👤 صاحب الاستفسار", value=interaction.user.mention, inline=False)
            embed.set_image(url=IMAGE_URL)
            
            await channel.send(f"<@&{STAFF_ROLE_ID}>", embed=embed, view=TicketActions(opener=interaction.user))
            await interaction.followup.send(f"✅ تم فتح تذكرة الاستفسار بنجاح: {channel.mention}", ephemeral=True)

class OpenTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ارسل_تكت", description="إرسال رسالة نظام التذاكر")
    @app_commands.checks.has_permissions(administrator=True)
    async def send_ticket(self, interaction: discord.Interaction):
        embed = discord.Embed(title="VOID | مركز الدعم", description="اختر نوع الطلب أدناه:", color=discord.Color.blue())
        embed.set_image(url=IMAGE_URL)
        await interaction.response.send_message(embed=embed, view=OpenTicketView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))
