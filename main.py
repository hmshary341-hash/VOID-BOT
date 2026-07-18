import os
import discord
from discord.ext import commands
from datetime import timedelta


# =====================
# VOID CONFIG
# =====================

WELCOME_CHANNEL = 1525595451607486535
GOODBYE_CHANNEL = 1527103575946297415

RULES_CHANNEL = 1525592697069502596
THE_VOID_ROLE = 1526653269743767562

GIVEAWAY_START = 1526628744020754594
GIVEAWAY_END = 1526709276083490949

BOOST_CHANNEL = 1526828845762744320

STATS_CHANNEL = 1526712984531894292

SUGGEST_CHANNEL = 1527099799038595192

TICKET_LOG = 1527750890952462408

EVENT_CHANNEL = 1526824130391834644
KING_GAME_ROLE = 1527871033665654824


# =====================
# تشغيل البوت
# =====================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =====================
# عند تشغيل البوت
# =====================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# =====================
# الترحيب والمغادرة
# =====================

@bot.event
async def on_member_join(member):

    # إعطاء رتبة THE VOID
    role = member.guild.get_role(THE_VOID_ROLE)
    if role:
        await member.add_roles(role)

    # رسالة الترحيب
    channel = bot.get_channel(WELCOME_CHANNEL)

    if channel:
        embed = discord.Embed(
            title="🖤 WELCOME TO VOID",
            description=(
                f"أهلاً بك {member.mention} في سيرفر VOID 💜\n\n"
                "نتمنى لك وقت ممتع معنا.\n"
                "لا تنسى قراءة القوانين والالتزام بها 🖤"
            ),
            color=0x8000FF
        )

        embed.set_footer(text="VOID • Community")
        await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):

    # رسالة المغادرة
    channel = bot.get_channel(GOODBYE_CHANNEL)

    if channel:
        embed = discord.Embed(
            title="🖤 GOODBYE FROM VOID",
            description=(
                f"نأسف لمغادرتك {member.mention} 💜\n\n"
                "نتمنى أن نراك مرة أخرى قريباً."
            ),
            color=0x8000FF
        )

        embed.set_footer(text="VOID • Community")
        await channel.send(embed=embed)

# =====================
# نظام القوانين
# =====================

@bot.command()
@commands.has_permissions(administrator=True)
async def قوانين(ctx):

    if ctx.channel.id != RULES_CHANNEL:
        return

    embed = discord.Embed(
        title="📜 قوانين VOID",
        description=(
            "🖤 احترام جميع الأعضاء\n"
            "🖤 ممنوع السب والإساءة\n"
            "🖤 ممنوع الإزعاج والسبام\n"
            "🖤 الالتزام بقوانين ديسكورد\n\n"
            "اضغط الزر للموافقة على القوانين والحصول على رتبة 🖤 THE VOID"
        ),
        color=0x8000FF
    )

    view = RulesButton()
    await ctx.send(embed=embed, view=view)


class RulesButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="أوافق على القوانين",
        emoji="🖤",
        style=discord.ButtonStyle.success
    )
    async def agree(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = interaction.guild.get_role(THE_VOID_ROLE)

        if role:
            await interaction.user.add_roles(role)

            await interaction.response.send_message(
                "✅ تم إعطاؤك رتبة 🖤 THE VOID",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ لم يتم العثور على الرتبة",
                ephemeral=True
        )

# =====================
# نظام الاقتراحات
# =====================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    # اقتراحات بدون أمر
    if message.channel.id == SUGGEST_CHANNEL:

        embed = discord.Embed(
            title="💡 اقتراح جديد",
            description=message.content,
            color=0x8000FF
        )

        embed.set_author(
            name=str(message.author),
            icon_url=message.author.display_avatar.url
        )

        embed.set_footer(text="VOID • Suggestions")

        await message.delete()

        msg = await message.channel.send(embed=embed)

        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    await bot.process_commands(message)

# =====================
# نظام القيف أواي
# =====================

import random
import asyncio


@bot.command()
@commands.has_permissions(manage_guild=True)
async def قيف(ctx, time: int, winners: int, *, prize):

    if ctx.channel.id != GIVEAWAY_START:
        return

    embed = discord.Embed(
        title="🎉 GIVEAWAY",
        description=(
            f"🎁 الجائزة: {prize}\n\n"
            f"⏳ المدة: {time} ثانية\n"
            f"🏆 عدد الفائزين: {winners}\n\n"
            "اضغط 🎉 للمشاركة!"
        ),
        color=0x8000FF
    )

    embed.set_footer(text="VOID • Giveaway")

    giveaway_msg = await ctx.send(embed=embed)
    await giveaway_msg.add_reaction("🎉")

    await asyncio.sleep(time)

    giveaway_msg = await ctx.channel.fetch_message(giveaway_msg.id)

    users = []

    for reaction in giveaway_msg.reactions:
        if str(reaction.emoji) == "🎉":
            users = [
                user async for user in reaction.users()
                if not user.bot
            ]

    if users:

        winners_list = random.sample(
            users,
            min(winners, len(users))
        )

        mentions = " ".join(
            winner.mention for winner in winners_list
        )

        end_channel = bot.get_channel(GIVEAWAY_END)

        if end_channel:
            await end_channel.send(
                f"🎉 مبروك للفائزين {mentions}\n"
                f"🎁 الجائزة: {prize}"
            )
    else:
        await ctx.send("❌ لا يوجد مشاركين في القيف أواي")

# =====================
# نظام الفعاليات
# =====================

@bot.command()
@commands.has_permissions(manage_guild=True)
async def فعالية(ctx, member: discord.Member):

    if ctx.channel.id != EVENT_CHANNEL:
        return

    role = ctx.guild.get_role(KING_GAME_ROLE)

    if role:
        await member.add_roles(role)

        embed = discord.Embed(
            title="🏆 EVENT WINNER",
            description=(
                f"مبروك {member.mention} 🎉\n\n"
                "لقد حصلت على رتبة 👑 King Game"
            ),
            color=0x8000FF
        )

        embed.set_footer(text="VOID • Events")

        await ctx.send(embed=embed)

    else:
        await ctx.send("❌ رتبة King Game غير موجودة")

# =====================
# نظام البوست
# =====================

@bot.event
async def on_member_update(before, after):

    if before.premium_since != after.premium_since:

        if after.premium_since:

            channel = bot.get_channel(BOOST_CHANNEL)

            if channel:
                embed = discord.Embed(
                    title="🚀 NEW BOOST",
                    description=(
                        f"شكراً {after.mention} على دعمك للسيرفر 💜\n\n"
                        "تم إرسال بوست جديد لـ VOID 🖤"
                    ),
                    color=0x8000FF
                )

                embed.set_footer(text="VOID • Boost")
                await channel.send(embed=embed)


# =====================
# إحصائيات السيرفر
# =====================

@bot.command()
@commands.has_permissions(administrator=True)
async def تحديث_الإحصائيات(ctx):

    channel = bot.get_channel(STATS_CHANNEL)

    if channel:

        embed = discord.Embed(
            title="📊 VOID SERVER STATS",
            description=(
                f"👥 الأعضاء: {ctx.guild.member_count}\n"
                f"💬 الرومات: {len(ctx.guild.channels)}\n"
                f"🎭 الرتب: {len(ctx.guild.roles)}"
            ),
            color=0x8000FF
        )

        embed.set_footer(text="VOID • Statistics")

        await channel.send(embed=embed)

# =====================
# لوق التكت
# =====================

async def send_ticket_log(text):

    channel = bot.get_channel(TICKET_LOG)

    if channel:
        embed = discord.Embed(
            title="🎫 Ticket Log",
            description=text,
            color=0x8000FF
        )

        embed.set_footer(text="VOID • Logs")

        await channel.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_channels=True)
async def سجل_تكت(ctx, *, text):

    await send_ticket_log(
        f"📌 {ctx.author.mention}\n{text}"
    )

    await ctx.send("✅ تم تسجيل التكت في اللوق")


# =====================
# لوق الإدارة
# =====================

@bot.event
async def on_message_delete(message):

    if message.author.bot:
        return

    await send_ticket_log(
        f"🗑️ تم حذف رسالة\n"
        f"العضو: {message.author.mention}\n"
        f"الروم: {message.channel.mention}\n"
        f"الرسالة: {message.content}"
    )


@bot.event
async def on_message_edit(before, after):

    if before.author.bot:
        return

    if before.content != after.content:

        await send_ticket_log(
            f"✏️ تم تعديل رسالة\n"
            f"العضو: {before.author.mention}\n"
            f"قبل:\n{before.content}\n\n"
            f"بعد:\n{after.content}"
        )

# =====================
# أوامر الإدارة
# =====================

# تايم
@bot.command()
@commands.has_permissions(moderate_members=True)
async def سدها(ctx, member: discord.Member):
    await member.timeout(
        discord.utils.utcnow() + timedelta(minutes=1)
    )
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
    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=False
    )
    await ctx.send("🔒 تم قفل الروم")


# فتح روم
@bot.command()
@commands.has_permissions(manage_channels=True)
async def فتح(ctx):
    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=True
    )
    await ctx.send("🔓 تم فتح الروم")


# بنق
@bot.command()
async def بنق(ctx):
    await ctx.send(
        f"🏓 {round(bot.latency * 1000)}ms"
    )


# =====================
# المساعدة
# =====================

@bot.command()
async def مساعدة(ctx):

    embed = discord.Embed(
        title="🖤 VOID COMMANDS",
        description="""
🛡️ الإدارة:
!سدها
!فكها
!سقها
!القمها
!حذف
!قفل
!فتح

🎉 الأنظمة:
!قيف
!فعالية
!قوانين
!تحديث_الإحصائيات

⚙️ أخرى:
!بنق
""",
        color=0x8000FF
    )

    embed.set_footer(text="VOID • Bot")

    await ctx.send(embed=embed)

                          # =====================
# تشغيل البوت
# =====================

TOKEN = os.getenv("TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ لم يتم العثور على TOKEN")
