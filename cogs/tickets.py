import io
import random
from datetime import datetime
import chat_exporter
import discord
from discord import app_commands
from discord.ext import commands

# --- الإعدادات الأساسية ---
CATEGORY_ID = 1530047675028865175         # آي دي فئة التذاكر
TICKET_CHANNEL_ID = 1530048038666506290   # آي دي روم التكت الأساسي
LOG_CHANNEL_ID = 1527750890952462408      # آي دي روم اللوجز

# 📌 استبدل الرابط أدناه برابط الصورة الجديدة الخاصة بك لتغطي المربع بالكامل
IMAGE_URL = "ضع_رابط_الصورة_هنا"

# --- أسماء الرتب الإدارية والدعم الفني (بدون رتب الإيفنت) ---
SUPPORT_ROLE_NAMES = [
    "Owner",
    "Co-Owner",
    "Bot server",
    "Support Manager",
    "Senior Support",
    "Support Staff"
]

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
        target = self.opener if self.opener else interaction.user
        await interaction.channel.set_permissions(target, send_messages=False)
        await interaction.response.send_message("🔒 تم قفل التذكرة لصاحبها.", ephemeral=True)

    @discord.ui.button(label="حذف", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="delete_ticket")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
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

        transcript = await chat_exporter.export(interaction.channel)
        transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{interaction.channel.name}.html")
        
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(file=transcript_file)
            
        await interaction.channel.delete()

# --- نموذج الشكاوى (إداري أو عضو) ---
class ReportModal(discord.ui.Modal, title='نموذج الشكوى'):
    target = discord.ui.TextInput(label='يوزر الشخص المبلغ عنه', style=discord.TextStyle.short, required=True)
    reason = discord.ui.TextInput(label='السبب بالتفصيل', style=discord.TextStyle.paragraph, required=True)
    proof = discord.ui.TextInput(label='الدليل (رابط الصورة/فيديو)', style=discord.TextStyle.short, required=True)

    def __init__(self, report_type):
        super().__init__()
        self.report_type = report_type

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        ticket_num = random.randint(1000, 9999) 
        category = interaction.guild.get_channel(CATEGORY_ID)
        channel = await interaction.guild.create_text_channel(name=f"ticket-{ticket_num}", category=category)
        
        await channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        
        for r_name in SUPPORT_ROLE_NAMES:
            role = discord.utils.get(interaction.guild.roles, name=r_name)
            if role:
                await channel.set_permissions(role, read_messages=True, send_messages=True)
        
        embed = discord.Embed(title=f"{self.report_type} | #{ticket_num}", color=discord.Color.dark_purple())
        embed.add_field(name="👤 المشتكي", value=interaction.user.mention, inline=False)
        embed.add_field(name="المبلغ عنه", value=self.target.value, inline=False)
        embed.add_field(name="📝 السبب", value=self.reason.value, inline=False)
        embed.add_field(name="🖼️ الدليل", value=self.proof.value, inline=False)
        if IMAGE_URL and IMAGE_URL != "ضع_رابط_الصورة_هنا":
            embed.set_image(url=IMAGE_URL)
        
        support_role = discord.utils.get(interaction.guild.roles, name="Support Staff")
        mention_text = support_role.mention if support_role else "@here"
        
        await channel.send(mention_text, embed=embed, view=TicketActions(opener=interaction.user))
        await interaction.followup.send(f"✅ تم فتح تذكرتك بنجاح: {channel.mention}", ephemeral=True)

# --- نموذج توثيق البنات ---
class VerificationModal(discord.ui.Modal, title='نموذج توثيق البنات'):
    proof = discord.ui.TextInput(label='رابط صورة التحقق / الدليل', style=discord.TextStyle.short, required=True, placeholder="ضع رابط الصورة هنا")
    notes = discord.ui.TextInput(label='ملاحظات إضافية (اختياري)', style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        ticket_num = random.randint(1000, 9999)
        category = interaction.guild.get_channel(CATEGORY_ID)
        channel = await interaction.guild.create_text_channel(name=f"verify-{ticket_num}", category=category)
        
        await channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        
        for r_name in SUPPORT_ROLE_NAMES:
            role = discord.utils.get(interaction.guild.roles, name=r_name)
            if role:
                await channel.set_permissions(role, read_messages=True, send_messages=True)
        
        embed = discord.Embed(title=f"تذكرة توثيق البنات | #{ticket_num}", description="يرجى انتظار مراجعة الإدارة للطلب الخاص بك.", color=discord.Color.magenta())
        embed.add_field(name="👤 صاحبة الطلب", value=interaction.user.mention, inline=False)
        embed.add_field(name="🖼️ الدليل المقدم", value=self.proof.value, inline=False)
        if self.notes.value:
            embed.add_field(name="📝 ملاحظات", value=self.notes.value, inline=False)
        if IMAGE_URL and IMAGE_URL != "ضع_رابط_الصورة_هنا":
            embed.set_image(url=IMAGE_URL)
        
        support_role = discord.utils.get(interaction.guild.roles, name="Support Staff")
        mention_text = support_role.mention if support_role else "@here"
        
        await channel.send(mention_text, embed=embed, view=TicketActions(opener=interaction.user))
        await interaction.followup.send(f"✅ تم فتح تذكرة التوثيق بنجاح: {channel.mention}", ephemeral=True)

# --- قائمة الاختيار للأقسام الأربعة ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder='اختر نوع التذكرة المناسبة من الخيارات أدناه...', options=[
            discord.SelectOption(label='شكوى على إداري', value='شكوى على إداري', description='تقديم شكوى ضد أحد الإداريين بسبب إساءة أو مخالفة', emoji='🛡️'),
            discord.SelectOption(label='شكوى على عضو', value='شكوى على عضو', description='تقديم شكوى ضد أحد الأعضاء بسبب إساءة أو مخالفة', emoji='👤'),
            discord.SelectOption(label='إستفسار', value='إستفسار', description='لطرح سؤال أو طلب مساعدة بخصوص أي موضوع', emoji='💬'),
            discord.SelectOption(label='توثيق البنات', value='توثيق البنات', description='لتوثيق حساب البنات للحصول على رتبة خاصة', emoji='👧'),
        ], custom_id="ticket_select_persistent")

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'شكوى على إداري':
            await interaction.response.send_modal(ReportModal(report_type='شكوى على إداري'))
        elif self.values[0] == 'شكوى على عضو':
            await interaction.response.send_modal(ReportModal(report_type='شكوى على عضو'))
        elif self.values[0] == 'توثيق البنات':
            await interaction.response.send_modal(VerificationModal())
        elif self.values[0] == 'إستفسار':
            await interaction.response.defer(ephemeral=True)
            
            ticket_num = random.randint(1000, 9999)
            category = interaction.guild.get_channel(CATEGORY_ID)
            channel = await interaction.guild.create_text_channel(name=f"inquiry-{ticket_num}", category=category)
            
            await channel.set_permissions(interaction.guild.default_role, read_messages=False)
            await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
            
            for r_name in SUPPORT_ROLE_NAMES:
                role = discord.utils.get(interaction.guild.roles, name=r_name)
                if role:
                    await channel.set_permissions(role, read_messages=True, send_messages=True)
            
            embed = discord.Embed(title=f"تذكرة إستفسار | #{ticket_num}", description="يرجى كتابة استفسارك هنا وسيقوم الدعم الفني بالرد عليك قريباً.", color=discord.Color.blue())
            embed.add_field(name="👤 صاحب الاستفسار", value=interaction.user.mention, inline=False)
            if IMAGE_URL and IMAGE_URL != "ضع_رابط_الصورة_هنا":
                embed.set_image(url=IMAGE_URL)
            
            support_role = discord.utils.get(interaction.guild.roles, name="Support Staff")
            mention_text = support_role.mention if support_role else "@here"
            
            await channel.send(mention_text, embed=embed, view=TicketActions(opener=interaction.user))
            await interaction.followup.send(f"✅ تم فتح تذكرة الاستفسار بنجاح: {channel.mention}", ephemeral=True)

class OpenTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket", description="إرسال لوحة نظام التذاكر")
    @app_commands.checks.has_permissions(administrator=True)
    async def send_ticket(self, interaction: discord.Interaction):
        if interaction.channel.id != TICKET_CHANNEL_ID:
            return await interaction.response.send_message(f"❌ عذراً، يجب استخدام هذا الأمر داخل روم التذاكر المخصص فقط <#{TICKET_CHANNEL_ID}>.", ephemeral=True)
            
        embed = discord.Embed(
            title="نظام التذاكر", 
            description="اختر نوع التذكرة المناسبة من الخيارات أدناه.\n\n> ⚠️ **ملاحظات مهمة:**\n> • يرجى اختيار القسم المناسب لمشكلتك.\n> • التذاكر غير المناسبة يتم إغلاقها دون مراجعة.\n> • سيتم الرد عليك في أقرب وقت ممكن.", 
            color=discord.Color.dark_gold()
        )
        if IMAGE_URL and IMAGE_URL != "ضع_رابط_الصورة_هنا":
            embed.set_image(url=IMAGE_URL)
            
        await interaction.response.send_message(embed=embed, view=OpenTicketView())
        await interaction.followup.send("✅ تم إرسال لوحة التذاكر بنجاح.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
