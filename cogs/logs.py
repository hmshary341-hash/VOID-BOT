import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # هذا هو الروم الوحيد لكل شيء
        self.log_channel_id = 1526625037808046241 

    # --- 1. لوق حذف الرسائل ---
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild: return
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel: return
        
        embed = discord.Embed(title="🗑️ حذف رسالة", color=discord.Color.red())
        embed.add_field(name="المرسل", value=message.author.mention)
        embed.add_field(name="القناة", value=message.channel.mention)
        embed.add_field(name="المحتوى", value=message.content or "*(صورة أو رسالة فارغة)*")
        await channel.send(embed=embed)

    # --- 2. لوق تعديل الرسائل ---
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content: return
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel: return
        
        embed = discord.Embed(title="✏️ تعديل رسالة", color=discord.Color.gold())
        embed.add_field(name="المرسل", value=before.author.mention)
        embed.add_field(name="قبل التعديل", value=before.content or "...", inline=False)
        embed.add_field(name="بعد التعديل", value=after.content or "...", inline=False)
        await channel.send(embed=embed)

    # --- 3. لوق حذف القنوات ---
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if not log_channel: return
        embed = discord.Embed(title="🚨 حذف قناة", color=discord.Color.dark_red(), description=f"تم حذف القناة: **{channel.name}**")
        await log_channel.send(embed=embed)

    # --- 4. لوق دخول الأعضاء ---
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel: return
        embed = discord.Embed(title="📥 عضو جديد", color=discord.Color.green(), description=f"{member.mention} انضم للسيرفر!")
        await channel.send(embed=embed)

    # --- 5. لوق خروج الأعضاء ---
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel: return
        embed = discord.Embed(title="📤 مغادرة عضو", color=discord.Color.orange(), description=f"{member.name} غادر السيرفر.")
        await channel.send(embed=embed)

    # --- 6. لوق الرتب ---
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles: return
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel: return
        
        added = [r.name for r in after.roles if r not in before.roles]
        removed = [r.name for r in before.roles if r not in after.roles]
        
        if added:
            await channel.send(f"➕ **إضافة رتبة:** {after.mention} حصل على: {', '.join(added)}")
        if removed:
            await channel.send(f"➖ **إزالة رتبة:** {after.mention} تمت إزالة: {', '.join(removed)}")

    # --- 7. لوق التكت (الموحد) ---
    async def send_ticket_log(self, ticket_name, opener, claimer, closer, open_time, close_time, reason, transcript_url):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if not log_channel: return

        embed = discord.Embed(title="🎟️ تم إغلاق التذكرة", color=discord.Color.dark_theme())
        embed.add_field(name="اسم التذكرة", value=ticket_name, inline=False)
        embed.add_field(name="تم الفتح بواسطة", value=opener.mention if opener else "غير معروف", inline=False)
        embed.add_field(name="تم الإغلاق بواسطة", value=closer.mention, inline=False)
        embed.add_field(name="وقت الإغلاق", value=f"<t:{int(close_time.timestamp())}:F>", inline=False)
        
        view = View()
        view.add_item(Button(label="عرض التذكرة", url=transcript_url, style=discord.ButtonStyle.link))
        
        await log_channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Logs(bot))
