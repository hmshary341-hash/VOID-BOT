import discord
from discord.ext import commands
from datetime import datetime
import io

# --- الإعدادات (ثابتة) ---
CATEGORY_ID = 1525952823156801576
LOG_CHANNEL_ID = 1527750890952462408
ticket_counter = 3568 # البوت سيبدأ من هذا الرقم

# --- كلاس الأزرار (قفل وحذف) ---
class TicketActions(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="قفل التذكرة", style=discord.ButtonStyle.secondary, emoji="🔒", custom_id="lock_ticket")
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.set_permissions(interaction.user, send_messages=False)
        await interaction.response.send_message("🔒 تم قفل التذكرة.")

    @discord.ui.button(label="حذف التذكرة", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="delete_ticket")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🗑️ جاري حفظ المحادثة وحذف التذكرة...")
        
        transcript = []
        async for message in interaction.channel.history(limit=None, oldest_first=True):
            transcript.append(f"{message.author.name}: {message.content}")
        
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            file = discord.File(io.StringIO("\n".join(transcript)), filename=f"transcript-{interaction.channel.name}.txt")
            await log_channel.send(f"📋 نسخة من التذكرة المحذوفة: {interaction.channel.name}", file=file)
            
        await interaction.channel.delete()

# --- النماذج (Modals) ---
class ReportModal(discord.ui.Modal):
    def __init__(self, title_name):
        super().__init__(title=title_name)
        self.add_item(discord.ui.TextInput(label='يوزر الشخص', placeholder='اكتب يوزر العضو أو الإداري'))
        self.add_item(discord.ui.TextInput(label='السبب', style=discord.TextStyle.paragraph))
        self.add_item(discord.ui.TextInput(label='الدليل (رابط)', required=False))
    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.title, self.children[0].value, self.children[1].value, self.children[2].value)

class NormalModal(discord.ui.Modal):
    def __init__(self, title_name):
        super().__init__(title=title_name)
        self.add_item(discord.ui.TextInput(label='السبب', style=discord.TextStyle.paragraph))
        self.add_item(discord.ui.TextInput(label='الدليل (رابط)', required=False))
    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.title, "لا يوجد", self.children[0].value, self.children[1].value)

# --- دالة إنشاء القناة ---
async def create_ticket(interaction, title, user_target, reason, proof):
    global ticket_counter
    ticket_counter += 1
    guild = interaction.guild
    category = guild.get_channel(CATEGORY_ID)
    channel = await guild.create_text_channel(name=f"🎫・{ticket_counter}", category=category)
    
    embed = discord.Embed(color=discord.Color.dark_theme())
    embed.add_field(name="👤 : مالك التذكرة", value=interaction.user.mention, inline=False)
    embed.add_field(name="🛡️ : مشرفي التذاكر", value="@Staff", inline=False)
    embed.add_field(name="📅 : تاريخ التذكرة", value=datetime.now().strftime("%A, %B %d, %Y %I:%M %p"), inline=False)
    embed.add_field(name="🔢 : رقم التذكرة", value=str(ticket_counter), inline=False)
    embed.add_field(name="❓ : قسم التذكرة", value=title, inline=False)
    if user_target != "لا يوجد": embed.add_field(name="🎯 : المستهدف", value=user_target, inline=False)
    embed.add_field(name="📝 : السبب", value=reason, inline=False)
    embed.add_field(name="🔗 : الدليل", value=proof or "لا يوجد", inline=False)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1508247176457748620/1528159877502074890/file_00000000da1c71f4863b28202a995e4e.png")
    
    await channel.send(content=f"{interaction.user.mention} | @Staff", embed=embed, view=TicketActions())
    await interaction.response.send_message(f"✅ تم فتح التذكرة: {channel.mention}", ephemeral=True)

# --- كلاس القائمة والقسم ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='إبلاغ عن عضو', value='إبلاغ عن عضو', emoji='👤'),
            discord.SelectOption(label='إبلاغ عن إداري', value='إبلاغ عن إداري', emoji='🛡️'),
            discord.SelectOption(label='استفسار', value='استفسار', emoji='❓'),
            discord.SelectOption(label='حل مشكلة', value='حل مشكلة', emoji='🔧'),
        ]
        super().__init__(placeholder='اختر سبب فتح التذكرة...', options=options)
    async def callback(self, interaction: discord.Interaction):
        if 'إبلاغ' in self.values[0]: await interaction.response.send_modal(ReportModal(title_name=self.values[0]))
        else: await interaction.response.send_modal(NormalModal(title_name=self.values[0]))

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        embed = discord.Embed(title="الدعم الفني", description="اختر سبب فتح التكت من القائمة أدناه.", color=discord.Color.blue())
        embed.set_image(url="https://cdn.discordapp.com/attachments/1508247176457748620/1528159877502074890/file_00000000da1c71f4863b28202a995e4e.png")
        await ctx.send(embed=embed, view=TicketView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))
