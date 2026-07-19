import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# الإعدادات (تأكد من الأيديات)
CATEGORY_ID = 1525952823156801576
STAFF_ROLE_ID = 1527807423186862080
LOG_CHANNEL_ID = 1527750890952462408 # روم اللوج
IMAGE_URL = "https://cdn.discordapp.com/attachments/1526978453826699324/1528190964215320778/file_00000000da1c71f4863b28202a995e4e.png"
FILE_PATH = "ticket_count.json"

# دالة لجلب رقم التكت التالي
def get_next_ticket_number():
    if not os.path.exists(FILE_PATH):
        count = 1
    else:
        with open(FILE_PATH, "r") as f:
            try:
                data = json.load(f)
                count = data.get("count", 1)
            except:
                count = 1
    
    with open(FILE_PATH, "w") as f:
        json.dump({"count": count + 1}, f)
    return count

# --- 1. الأزرار (استلام / قفل / حذف) ---
class TicketActions(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.claimed_by = None

    @discord.ui.button(label="استلام التذكرة", style=discord.ButtonStyle.primary, emoji="✅", custom_id="claim_ticket")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if self.claimed_by:
            await interaction.followup.send(f"⚠️ مستلمة بالفعل بواسطة {self.claimed_by.mention}", ephemeral=True)
            return
        
        self.claimed_by = interaction.user
        button.disabled = True
        embed = interaction.message.embeds[0]
        embed.add_field(name="🛡️ مستلمة بواسطة", value=interaction.user.mention, inline=False)
        embed.color = discord.Color.green()
        await interaction.message.edit(embed=embed, view=self)
        await interaction.followup.send(f"✅ تم استلام التذكرة.")

    @discord.ui.button(label="قفل", style=discord.ButtonStyle.secondary, emoji="🔒", custom_id="lock_ticket")
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.channel.set_permissions(interaction.user, send_messages=False)
        await interaction.followup.send("🔒 تم قفل التذكرة.")

    @discord.ui.button(label="حذف", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="delete_ticket")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # إرسال لوج قبل الحذف
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🗑️ حذف تذكرة", color=discord.Color.red())
            embed.add_field(name="القناة", value=interaction.channel.name, inline=True)
            embed.add_field(name="بواسطة", value=interaction.user.mention, inline=True)
            await log_channel.send(embed=embed)
            
        await interaction.channel.delete()

# --- 2. نافذة البيانات للشكاوى ---
class ReportModal(discord.ui.Modal, title='نموذج الإبلاغ'):
    target = discord.ui.TextInput(label='يوزر الشخص المبلغ عنه', style=discord.TextStyle.short, required=True)
    reason = discord.ui.TextInput(label='السبب', style=discord.TextStyle.paragraph, required=True)
    proof = discord.ui.TextInput(label='الدليل (رابط الصورة)', style=discord.TextStyle.short, required=True)

    def __init__(self, report_type):
        super().__init__()
        self.report_type = report_type

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            ticket_num = get_next_ticket_number()
            category = interaction.guild.get_channel(CATEGORY_ID)
            
            # إنشاء القناة برقم تسلسلي
            channel = await interaction.guild.create_text_channel(
                name=f"ticket-{ticket_num:04d}", 
                category=category
            )
            
            await channel.set_permissions(interaction.guild.default_role, read_messages=False)
            await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
            
            embed = discord.Embed(title=f"تذكرة {self.report_type} | #{ticket_num:04d}", color=discord.Color.red())
            embed.add_field(name="👤 المشتكي", value=interaction.user.mention, inline=False)
            embed.add_field(name="المبلغ عنه", value=self.target.value, inline=False)
            embed.add_field(name="📝 السبب", value=self.reason.value, inline=False)
            embed.add_field(name="🖼️ الدليل", value=self.proof.value, inline=False)
            embed.set_image(url=IMAGE_URL)

            await channel.send(f"<@&{STAFF_ROLE_ID}>", embed=embed, view=TicketActions())
            await interaction.followup.send(f"✅ تم فتح تذكرتك: {channel.mention}", ephemeral=True)
            
        except Exception as e:
            print(f"خطأ في إنشاء التكت: {e}")
            await interaction.followup.send("❌ حدث خطأ! تأكد من صلاحيات البوت.", ephemeral=True)

# --- 3. القائمة المنسدلة ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='إبلاغ عن إداري', value='إبلاغ عن إداري', emoji='🛡️'),
            discord.SelectOption(label='إبلاغ عن عضو', value='إبلاغ عن عضو', emoji='👤'),
            discord.SelectOption(label='استفسار', value='استفسار', emoji='❓'),
        ]
        super().__init__(placeholder='اختر نوع التذكرة...', options=options, custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] in ['إبلاغ عن إداري', 'إبلاغ عن عضو']:
            await interaction.response.send_modal(ReportModal(report_type=self.values[0]))
        else:
            # يمكن تعديلها لفتح تكت استفسار بنفس المنطق
            await interaction.response.send_message("تم فتح تذكرة استفسار...", ephemeral=True)

class OpenTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- 4. أمر البوت ---
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
