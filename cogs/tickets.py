import discord
from discord.ext import commands
from datetime import datetime

# عداد للتذاكر
ticket_counter = 3567 # يمكنك تغيير الرقم لتبدأ من بعده

class CustomModal(discord.ui.Modal):
    def __init__(self, title_name):
        super().__init__(title=title_name)
        self.add_item(discord.ui.TextInput(label='السبب بالتفصيل', style=discord.TextStyle.paragraph))
        self.add_item(discord.ui.TextInput(label='الدليل (رابط)', required=False))

    async def on_submit(self, interaction: discord.Interaction):
        global ticket_counter
        ticket_counter += 1
        
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="TICKETS")
        channel = await guild.create_text_channel(name=f"🎫・{ticket_counter}", category=category)
        
        # تنسيق الـ Embed مطابق للصورة
        embed = discord.Embed(color=discord.Color.dark_theme())
        embed.add_field(name="👤 : مالك التذكرة", value=interaction.user.mention, inline=False)
        embed.add_field(name="🛡️ : مشرفي التذاكر", value="@Staff", inline=False) # يمكنك تغيير الرول هنا
        embed.add_field(name="📅 : تاريخ التذكرة", value=datetime.now().strftime("%A, %B %d, %Y %I:%M %p"), inline=False)
        embed.add_field(name="🔢 : رقم التذكرة", value=str(ticket_counter), inline=False)
        embed.add_field(name="❓ : قسم التذكرة", value=self.title, inline=False)
        
        # الصورة الخاصة بك
        embed.set_image(url="https://cdn.discordapp.com/attachments/1508247176457748620/1528159877502074890/file_00000000da1c71f4863b28202a995e4e.png")
        
        await channel.send(content=f"{interaction.user.mention} | @Staff", embed=embed)
        await interaction.response.send_message(f"✅ تم فتح التذكرة بنجاح: {channel.mention}", ephemeral=True)

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
        await interaction.response.send_modal(CustomModal(title_name=self.values[0]))

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
        embed = discord.Embed(
            title="الدعم الفني",
            description="اختر سبب فتح التكت من القائمة أدناه.",
            color=discord.Color.blue()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1508247176457748620/1528159877502074890/file_00000000da1c71f4863b28202a995e4e.png")
        await ctx.send(embed=embed, view=TicketView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))
