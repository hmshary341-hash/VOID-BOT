import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.msg_log_id = 1526625037808046241    # قناة لوج الرسائل، الدخول والخروج
        self.ticket_log_id = 1527750890952462408 # قناة لوج التكت

    # --- 1. لوق دخول الأعضاء ---
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(self.msg_log_id)
        if not channel: return
        
        embed = discord.Embed(title="📥 عضو جديد", color=discord.Color.green())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="العضو", value=member.mention, inline=True)
        embed.add_field(name="تاريخ إنشاء الحساب", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)

    # --- 2. لوق خروج الأعضاء ---
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(self.msg_log_id)
        if not channel: return
        
        embed = discord.Embed(title="📤 مغادرة عضو", color=discord.Color.dark_red())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="العضو", value=member.name, inline=True)
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)

    # --- 3. لوق حذف الرسائل ---
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild: return
        channel = self.bot.get_channel(self.msg_log_id)
        if not channel: return
        
        embed = discord.Embed(title="🗑️ حذف رسالة", color=discord.Color.red())
        embed.add_field(name="المرسل", value=message.author.mention)
        embed.add_field(name="القناة", value=message.channel.mention)
        embed.add_field(name="المحتوى", value=message.content or "*(صورة أو رسالة فارغة)*")
        await channel.send(embed=embed)

    # --- 4. لوق تعديل الرسائل ---
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        channel = self.bot.get_channel(self.msg_log_id)
        if not channel: return
        
        embed = discord.Embed(title="✏️ تعديل رسالة", color=discord.Color.gold())
        embed.add_field(name="المرسل", value=before.author.mention)
        embed.add_field(name="قبل", value=before.content or "...", inline=False)
        embed.add_field(name="بعد", value=after.content or "...", inline=False)
        await channel.send(embed=embed)

    # --- 5. لوق الرتب ---
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles: return
        channel = self.bot.get_channel(self.msg_log_id)
        if not channel: return
        
        added = [r.mention for r in after.roles if r not in before.roles]
        removed = [r.mention for r in before.roles if r not in after.roles]
        
        if added:
            await channel.send(embed=discord.Embed(title="➕ إضافة رتبة", description=f"تم إعطاء {after.mention} رتبة: {', '.join(added)}", color=discord.Color.green()))
        if removed:
            await channel.send(embed=discord.Embed(title="➖ إزالة رتبة", description=f"تم إزالة رتبة {', '.join(removed)} من {after.mention}", color=discord.Color.dark_red()))

    # --- دالة لوق التكت ---
    async def send_ticket_log(self, ticket_name, opener, claimer, closer, open_time, close_time, reason, transcript_url):
        log_channel = self.bot.get_channel(self.ticket_log_id)
        if not log_channel: return

        embed = discord.Embed(title="تم إغلاق التذكرة", color=discord.Color.dark_theme())
        embed.add_field(name="اسم التذكرة", value=ticket_name, inline=False)
        embed.add_field(name="تم الفتح بواسطة", value=opener.mention if opener else "غير معروف", inline=False)
        embed.add_field(name="تم المطالبة بواسطة", value=claimer.mention if claimer else "لم يتم المطالبة", inline=False)
        embed.add_field(name="تم الإغلاق بواسطة", value=closer.mention, inline=False)
        embed.add_field(name="وقت الفتح", value=f"<t:{int(open_time.timestamp())}:F>", inline=False)
        embed.add_field(name="وقت الإغلاق", value=f"<t:{int(close_time.timestamp())}:F>", inline=False)
        embed.add_field(name="سبب الإغلاق", value=reason or "لم يتم تقديم سبب", inline=False)

        view = View()
        view.add_item(Button(label="عرض التذكرة", url=transcript_url, style=discord.ButtonStyle.link))
        
        await log_channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Logs(bot))
