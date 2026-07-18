import discord
from discord import app_commands
from discord.ext import commands

# 1. النافذة التي تظهر للمستخدم بعد اختيار نوع التذكرة لتعبئة بياناته
class TicketModal(discord.ui.Modal):
    def __init__(self, title_name):
        super().__init__(title=title_name)
    
    username = discord.ui.TextInput(label='يوزر الديسكورد', placeholder='اكتب يوزرك هنا')
    reason = discord.ui.TextInput(label='السبب / المشكلة', style=discord.TextStyle.paragraph, placeholder='اشرح بالتفصيل')
    proof = discord.ui.TextInput(label='الدليل (رابط)', required=False, placeholder='ضع رابط الصورة أو الدليل')

    async def on_submit(self, interaction: discord.Interaction):
        # إنشاء القناة
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="TICKETS")
        channel = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=category)
        
        # اللوحة الداخلية للتذكرة
        embed = discord.Embed(title="نظام التذاكر - Raven Support", color=discord.Color.red())
        embed.add_field(name="👤 المالك", value=interaction.user.mention, inline=False)
        embed.add_field(name="📝 السبب", value=self.reason.value, inline=False)
        embed.add_field(name="🔗 الدليل", value=self.proof.value if self.proof.value else "لا يوجد", inline=False)
        
        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ تم فتح التذكرة بنجاح: {channel.mention}", ephemeral=True)

# 2. القائمة المنسدلة
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
        await interaction.response.send_modal(TicketModal(title_name=self.values[0]))

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# 3. الأمر لبدء النظام (اكتب !setup في ديسكورد)
@commands.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="الدعم الفني",
        description="يمنع فتح تكت للعبث أو لأسباب غير جدية.\nاختر سبب فتح التكت من القائمة أدناه.",
        color=discord.Color.blue()
    )
    # ضع رابط صورتك هنا
    embed.set_image(url="https://cdn.discordapp.com/attachments/1508247176457748620/1528159877502074890/file_00000000da1c71f4863b28202a995e4e.png")
    
    await ctx.send(embed=embed, view=TicketView())
