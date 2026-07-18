import discord
from discord.ext import commands
from discord import app_commands

class TicketModal(discord.ui.Modal):
    def __init__(self, title_name):
        super().__init__(title=title_name)
    
    username = discord.ui.TextInput(label='يوزر الديسكورد', placeholder='اكتب يوزرك هنا')
    reason = discord.ui.TextInput(label='السبب', style=discord.TextStyle.paragraph)
    proof = discord.ui.TextInput(label='الدليل (رابط)', required=False)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="TICKETS")
        channel = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=category)
        
        embed = discord.Embed(title="تم فتح التذكرة", color=discord.Color.red())
        embed.add_field(name="👤 المالك", value=interaction.user.mention, inline=False)
        embed.add_field(name="📝 السبب", value=self.reason.value, inline=False)
        embed.add_field(name="🔗 الدليل", value=self.proof.value if self.proof.value else "لا يوجد", inline=False)
        
        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ تم فتح التذكرة: {channel.mention}", ephemeral=True)

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

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        embed = discord.Embed(
            title="الدعم الفني",
            description="يمنع فتح تكت للعبث أو لأسباب غير جدية.\nاختر سبب فتح التكت من القائمة أدناه.",
            color=discord.Color.blue()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1508247176457748620/1528159877502074890/file_00000000da1c71f4863b28202a995e4e.png")
        await ctx.send(embed=embed, view=TicketView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))
