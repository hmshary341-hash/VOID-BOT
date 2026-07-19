import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.msg_log_id = 1526625037808046241    # قناة لوق الرسائل
        self.ticket_log_id = 1527750890952462408 # قناة لوق التكت

    def is_ticket_channel(self, channel):
        # يتحقق إذا كان اسم القناة يحتوي على "ticket"
        return "ticket" in channel.name.lower()

    # --- 1. تسجيل حذف الرسائل ---
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild or self.is_ticket_channel(message.channel): return
        
        channel = self.bot.get_channel(self.msg_log_id)
        if not channel: return

        embed = discord.Embed(title="🗑️ رسالة محذوفة", color=discord.Color.red())
        embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
        embed.add_field(name="المحتوى:", value=message.content or "*(رسالة فارغة أو وسائط)*")
        embed.set_timestamp()
        
        await channel.send(embed=embed)

    # --- 2. تسجيل الرسائل المعدلة ---
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content or self.is_ticket_channel(before.channel): return
        
        channel = self.bot.get_channel(self.msg_log_id)
        if not channel: return

        embed = discord.Embed(title="✏️ رسالة معدلة", color=discord.Color.gold())
        embed.set_author(name=before.author.name, icon_url=before.author.display_avatar.url)
        embed.add_field(name="قبل التعديل:", value=before.content or "*(رسالة فارغة)*")
        embed.add_field(name="بعد التعديل:", value=after.content or "*(رسالة فارغة)*")
        embed.set_timestamp()
        
        await channel.send(embed=embed)

    # --- 3. لوق التكت (الذي طلبته سابقاً) ---
    async def send_ticket_log(self, ticket_name, opener, claimer, closer, open_time, close_time, reason, transcript_url):
        channel_log = self.bot.get_channel(self.ticket_log_id)
        if not channel_log: return

        embed = discord.Embed(title="تم إغلاق التذكرة", color=discord.Color.dark_theme())
        embed.add_field(name="اسم التذكرة", value=ticket_name, inline=False)
        embed.add_field(name="تم الفتح بواسطة", value=opener.mention, inline=False)
        embed.add_field(name="تم المطالبة بواسطة", value=claimer.mention if claimer else "لم يتم المطالبة", inline=False)
        embed.add_field(name="تم الإغلاق بواسطة", value=closer.mention, inline=False)
        embed.add_field(name="وقت الفتح", value=f"<t:{int(open_time.timestamp())}:F>", inline=False)
        embed.add_field(name="وقت الإغلاق", value=f"<t:{int(close_time.timestamp())}:F>", inline=False)
        embed.add_field(name="سبب الإغلاق", value=reason or "لم يتم تقديم سبب", inline=False)

        view = View()
        view.add_item(Button(label="عرض التذكرة", url=transcript_url, style=discord.ButtonStyle.link))
        
        await channel_log.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Logs(bot))
