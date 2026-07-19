import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

# الإعدادات
CATEGORY_ID = 1525952823156801576
STAFF_ROLE_ID = 1527807423186862080
IMAGE_URL = "https://cdn.discordapp.com/attachments/1526978453826699324/1528188543321505833/file_00000000da1c71f4863b28202a995e4e.png"

# --- نافذة البيانات (Modal) للشكاوى ---
class ReportModal(discord.ui.Modal, title='نموذج الإبلاغ'):
    target = discord.ui.TextInput(label='يوزر الشخص المبلغ عنه', style=discord.TextStyle.short, required=True)
    reason = discord.ui.TextInput(label='السبب', style=discord.TextStyle.paragraph, required=True)
    proof = discord.ui.TextInput(label='الدليل (رابط الصورة)', style=discord.TextStyle.short, required=True)

    def __init__(self, report_type):
        super().__init__()
        self.report_type = report_type

    async def on_submit(self, interaction: discord.Interaction):
        # إنشاء القناة
        category = interaction.guild.get_channel(CATEGORY_ID)
        channel = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=category)
        
        await channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        embed = discord.Embed(title=f"تذكرة {self.report_type}", color=discord.Color.red())
        embed.add_field(name="👤 المشتكي", value=interaction.user.mention, inline=False)
        embed.add_field(name="Target", value=self.target.value, inline=False)
        embed.add_field(name="📝 السبب", value=self.reason.value, inline=False)
        embed.add_field(name="🖼️ الدليل", value=self.proof.value, inline=False)
        embed.set_image(url=IMAGE_URL)

        await channel.send(f"<@&{STAFF_ROLE_ID}>", embed=embed)
        await interaction.response.send_message(f"✅ تم فتح تذكرتك: {channel.mention}", ephemeral=True)

# --- القائمة المنسدلة ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='إبلاغ عن إداري', value='admin_report', emoji='🛡️'),
            discord.SelectOption(label='إبلاغ عن عضو', value='member_report', emoji='👤'),
            discord.SelectOption(label='استفسار', value='inquiry', emoji='❓'),
        ]
        super().__init__(placeholder='اختر نوع التذكرة...', options=options, custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] in ['admin_report', 'member_report']:
            await interaction.response.send_modal(ReportModal(report_type=self.values[0]))
        else:
            # معالجة الاستفسار العادي
            await interaction.response.send_message("تم فتح تذكرة استفسار...", ephemeral=True)

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
