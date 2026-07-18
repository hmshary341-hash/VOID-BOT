import discord
from discord.ext import commands

class SuggestionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="قبول", style=discord.ButtonStyle.success, emoji="✅", custom_id="approve_btn")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌ عذراً، هذا الزر مخصص للإدارة فقط!", ephemeral=True)
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = "💡 اقتراح مقبول"
        embed.add_field(name="الوضعية", value=f"🟢 تم القبول بواسطة: {interaction.user.mention}", inline=False)
        for child in self.children: child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="رفض", style=discord.ButtonStyle.danger, emoji="❌", custom_id="deny_btn")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌ عذراً، هذا الزر مخصص للإدارة فقط!", ephemeral=True)
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = "💡 اقتراح مرفوض"
        embed.add_field(name="الوضعية", value=f"🔴 تم الرفض بواسطة: {interaction.user.mention}", inline=False)
        for child in self.children: child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.suggestion_channel_id = 1527099799038595192 # روم الاقتراحات العام

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if message.channel.id == self.suggestion_channel_id:
            try:
                await message.delete()
                embed = discord.Embed(title="💡 اقتراح جديد!", description=message.content, color=discord.Color.blurple())
                avatar_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
                embed.set_author(name=message.author.display_name, icon_url=avatar_url)
                embed.set_footer(text=f"بواسطة: {message.author.name} • معرف المستخدم: {message.author.id}")
                await message.channel.send(embed=embed, view=SuggestionView())
            except Exception as e: print(f"❌ خطأ اقتراحات: {e}")

async def setup(bot):
    await bot.add_cog(Suggestions(bot))
