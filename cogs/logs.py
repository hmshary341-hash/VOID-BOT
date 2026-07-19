import discord
from discord.ext import commands
from datetime import datetime

# الأيدي الخاص بروم السجلات
LOG_CHANNEL_ID = 1526625037808046241

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild, title, color, description, avatar_url=None):
        channel = guild.get_channel(LOG_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)
        embed.set_footer(text="VOID Security Logs")
        
        await channel.send(embed=embed)

    # 1. دخول عضو
    @commands.Cog.listener()
    async def on_member_join(self, member):
        desc = f"👤 **Member**\n{member.mention}\n\n🕒 **Time**\n<t:{int(datetime.now().timestamp())}:f>"
        await self.send_log(member.guild, "🟢 MEMBER JOINED", 0x00FF00, desc, member.display_avatar.url)

    # 2. خروج عضو
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        desc = f"👤 **Member**\n{member.name} ({member.id})\n\n🕒 **Time**\n<t:{int(datetime.now().timestamp())}:f>"
        await self.send_log(member.guild, "🔴 MEMBER LEFT", 0xFF0000, desc, member.display_avatar.url)

    # 3. حذف رول (اختياري)
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        desc = f"🛡️ **Role Deleted**\n{role.name}\n\n🕒 **Time**\n<t:{int(datetime.now().timestamp())}:f>"
        await self.send_log(role.guild, "🟡 ROLE DELETED", 0xFFD700, desc)

async def setup(bot):
    await bot.add_cog(Logs(bot))
