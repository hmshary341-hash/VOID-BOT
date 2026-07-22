import datetime
import discord
from discord.ext import commands

# آي دي قناة السجلات لديك
LOG_CHANNEL_ID = 1527750890952462408

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # دالة مخصصة تستقبلها أوامر الإدارة فقط (مثل تايم، باند، كك)
    async def send_admin_log(self, guild, title, member, moderator, details):
        if LOG_CHANNEL_ID == 0:
            return
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            try:
                embed = discord.Embed(
                    title=f"🛡️ سجل الإدارة | {title}", 
                    color=discord.Color.red(), 
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                embed.add_field(name="👤 المستهدف", value=f"{member.mention}", inline=True)
                embed.add_field(name="👮 المسؤول", value=f"{moderator.mention}", inline=True)
                embed.add_field(name="📝 التفاصيل", value=details, inline=False)
                await log_channel.send(embed=embed)
            except Exception:
                pass

    # تسجيل حذف الرسائل في الشات
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return
        
        log_channel = message.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🗑️ حذف رسالة",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.add_field(name="👤 العضو", value=message.author.mention, inline=True)
            embed.add_field(name="📌 القناة", value=message.channel.mention, inline=True)
            
            content = message.content if message.content else "محتوى فارغ (صورة أو مرفق)"
            if len(content) > 1024:
                content = content[:1021] + "..."
            
            embed.add_field(name="📝 المحتوى المحذوف", value=content, inline=False)
            await log_channel.send(embed=embed)

    # تسجيل تعديل الرسائل في الشات
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild:
            return
        if before.content == after.content:
            return  # تجاهل لو تم تعديل الإمبد فقط بدون تغيير النص
        
        log_channel = before.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="✏️ تعديل رسالة",
                color=discord.Color.gold(),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.add_field(name="👤 العضو", value=before.author.mention, inline=True)
            embed.add_field(name="📌 القناة", value=before.channel.mention, inline=True)
            
            old_content = before.content if before.content else "فارغ"
            new_content = after.content if after.content else "فارغ"
            
            if len(old_content) > 1024: old_content = old_content[:1021] + "..."
            if len(new_content) > 1024: new_content = new_content[:1021] + "..."
            
            embed.add_field(name="❌ قبل التعديل", value=old_content, inline=False)
            embed.add_field(name="✅ بعد التعديل", value=new_content, inline=False)
            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logs(bot))
