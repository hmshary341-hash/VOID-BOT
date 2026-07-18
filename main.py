import os
import discord
from discord.ext import commands
from datetime import timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# الفاصل
CHANNEL_ID = 1526823698089119784
SEPARATOR_IMAGE = "https://files.catbox.moe/7q1g3v.png"


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# إرسال الفاصل في روم محدد
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == CHANNEL_ID:
        embed = discord.Embed()
        embed.set_image(url=SEPARATOR_IMAGE)
        await message.channel.send(embed=embed)

    await bot.process_commands(message)


# تايم
@bot.command()
@commands.has_permissions(moderate_members=True)
async def سدها(ctx, member: discord.Member):
    await member.timeout(discord.utils.utcnow() + timedelta(minutes=1))
    await ctx.send(f"⏳ تم إعطاء {member.mention} تايم دقيقة")


# فك التايم
@bot.command()
@commands.has_permissions(moderate_members=True)
async def فكها(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔓 تم فك التايم عن {member.mention}")


# كيك
@bot.command()
@commands.has_permissions(kick_members=True)
async def سقها(ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f"🚪 تم طرد {member.mention}")


# باند
@bot.command()
@commands.has_permissions(ban_members=True)
async def القمها(ctx, member: discord.Member):
    await member.ban()
    await ctx.send(f"🔨 تم تبنيد {member.mention}")


# حذف رسائل
@bot.command()
@commands.has_permissions(manage_messages=True)
async def حذف(ctx, amount: int):
    await ctx.channel.purge(limit=amount)


# قفل روم
@bot.command()
@commands.has_permissions(manage_channels=True)
async def قفل(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم قفل الروم")


# فتح روم
@bot.command()
@commands.has_permissions(manage_channels=True)
async def فتح(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح الروم")


# تحذير
@bot.command()
@commands.has_permissions(moderate_members=True)
async def انتبه_لنفسك(ctx, member: discord.Member):
    await ctx.send(f"⚠️ انتبه لنفسك {member.mention}")


# لون رول
@bot.command()
@commands.has_permissions(manage_roles=True)
async def لون_رول(ctx, role: discord.Role, color: str):
    await role.edit(color=discord.Color.from_str(color))
    await ctx.send("🎨 تم تغيير لون الرتبة")


# فل
@bot.command()
async def الفل(ctx, *, text):
    await ctx.send(text)


# بنق
@bot.command()
async def بنق(ctx):
    await ctx.send(f"🏓 {round(bot.latency * 1000)}ms")


# مساعدة
@bot.command()
async def مساعدة(ctx):
    await ctx.send("""
📋 أوامر VOID:
!سدها
!فكها
!سقها
!القمها
!حذف
!قفل
!فتح
!انتبه_لنفسك
!لون_رول
!الفل
!بنق
""")


TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
