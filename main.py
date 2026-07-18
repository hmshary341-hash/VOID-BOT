import os
import discord
from discord.ext import commands
from datetime import timedelta
import random
import asyncio


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
# BOT
# =====================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =====================
# READY
# =====================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# =====================
# WELCOME / GOODBYE
# =====================

@bot.event
async def on_member_join(member):

    role = member.guild.get_role(THE_VOID_ROLE)

    if role:
        await member.add_roles(role)

    channel = bot.get_channel(WELCOME_CHANNEL)

    if channel:
        embed = discord.Embed(
            title="🖤 WELCOME TO VOID",
            description=(
                f"أهلاً بك {member.mention} في سيرفر VOID 💜\n\n"
                "نتمنى لك وقت ممتع معنا.\n"
                "لا تنسى قراءة القوانين 🖤"
            ),
            color=0x8000FF
        )

        embed.set_footer(text="VOID • Community")

        await channel.send(embed=embed)



@bot.event
async def on_member_remove(member):

    channel = bot.get_channel(GOODBYE_CHANNEL)

    if channel:
        embed = discord.Embed(
            title="🖤 GOODBYE FROM VOID",
            description=(
                f"غادر السيرفر {member.mention}\n\n"
                "نتمنى رؤيتك مرة أخرى 💜"
            ),
            color=0x8000FF
        )

        embed.set_footer(text="VOID • Community")

        await channel.send(embed=embed)

# =====================
# نظام القوانين بزر
# =====================

class RulesButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="أوافق على القوانين",
        emoji="🖤",
        style=discord.ButtonStyle.success
    )
    async def agree(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        role = interaction.guild.get_role(THE_VOID_ROLE)

        if role:
            await interaction.user.add_roles(role)

            await interaction.response.send_message(
                "✅ تم إعطاؤك رتبة 🖤 THE VOID",
                ephemeral=True
            )

        else:
            await interaction.response.send_message(
                "❌ الرتبة غير موجودة",
                ephemeral=True
            )


@bot.command()
@commands.has_permissions(administrator=True)
async def قوانين(ctx):

    if ctx.channel.id != RULES_CHANNEL:
        return

    embed = discord.Embed(
        title="📜 قوانين VOID",
        description=(
            "🖤 احترام الجميع\n"
            "🖤 ممنوع السبام\n"
            "🖤 ممنوع الإساءة\n"
            "🖤 الالتزام بقوانين ديسكورد\n\n"
            "اضغط الزر للموافقة والحصول على رتبة THE VOID"
        ),
        color=0x8000FF
    )

    await ctx.send(
        embed=embed,
        view=RulesButton()
    )



# =====================
# الاقتراحات
# =====================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

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

        embed.set_footer(
            text="VOID • Suggestions"
        )

        await message.delete()

        msg = await message.channel.send(
            embed=embed
        )

        await msg.add_reaction("👍")
        await msg.add_reaction("👎")


    await bot.process_commands(message)



# =====================
# القيف أواي
# =====================

@bot.command()
@commands.has_permissions(manage_guild=True)
async def قيف(ctx, time:int, winners:int, *, prize):

    if ctx.channel.id != GIVEAWAY_START:
        return


    embed = discord.Embed(
        title="🎉 GIVEAWAY",
        description=(
            f"🎁 الجائزة: {prize}\n\n"
            f"⏳ الوقت: {time} ثانية\n"
            f"🏆 الفائزين: {winners}\n\n"
            "اضغط 🎉 للمشاركة"
        ),
        color=0x8000FF
    )


    msg = await ctx.send(embed=embed)

    await msg.add_reaction("🎉")


    await asyncio.sleep(time)


    msg = await ctx.channel.fetch_message(msg.id)


    users = []

    for reaction in msg.reactions:

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


        channel = bot.get_channel(GIVEAWAY_END)

        if channel:

            await channel.send(
                "🎉 الفائزين:\n" +
                " ".join(
                    x.mention for x in winners_list

                
                )
        )
    else:
        await ctx.send("❌ لا يوجد مشاركين")
# =====================
# الفعاليات + رتبة King Game
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
                "حصلت على رتبة 👑 King Game"
            ),
            color=0x8000FF
        )

        await ctx.send(embed=embed)

    else:
        await ctx.send("❌ رتبة King Game غير موجودة")


# =====================
# البوست
# =====================

@bot.event
async def on_member_update(before, after):

    if before.premium_since != after.premium_since:

        if after.premium_since:

            channel = bot.get_channel(BOOST_CHANNEL)

            if channel:

                embed = discord.Embed(
                    title="🚀 BOOST",
                    description=(
                        f"شكراً {after.mention} على دعم VOID 💜"
                    ),
                    color=0x8000FF
                )

                await channel.send(embed=embed)



# =====================
# الإحصائيات
# =====================

@bot.command()
@commands.has_permissions(administrator=True)
async def تحديث_الإحصائيات(ctx):

    channel = bot.get_channel(STATS_CHANNEL)

    if channel:

        embed = discord.Embed(
            title="📊 VOID STATS",
            description=(
                f"👥 الأعضاء: {ctx.guild.member_count}\n"
                f"💬 الرومات: {len(ctx.guild.channels)}\n"
                f"🎭 الرتب: {len(ctx.guild.roles)}"
            ),
            color=0x8000FF
        )

        await channel.send(embed=embed)



# =====================
# لوق التكت
# =====================

async def send_log(text):

    channel = bot.get_channel(TICKET_LOG)

    if channel:

        embed = discord.Embed(
            title="📋 VOID LOG",
            description=text,
            color=0x8000FF
        )

        await channel.send(embed=embed)



@bot.command()
@commands.has_permissions(manage_channels=True)
async def سجل_تكت(ctx, *, text):

    await send_log(
        f"🎫 {ctx.author.mention}\n{text}"
    )

    await ctx.send("✅ تم إرسال اللوق")

# =====================
# أوامر الإدارة
# =====================

@bot.command()
@commands.has_permissions(moderate_members=True)
async def سدها(ctx, member: discord.Member):

    await member.timeout(
        discord.utils.utcnow() + timedelta(minutes=1)
    )

    await ctx.send(
        f"⏳ تم إعطاء {member.mention} تايم"
    )


@bot.command()
@commands.has_permissions(moderate_members=True)
async def فكها(ctx, member: discord.Member):

    await member.timeout(None)

    await ctx.send(
        f"🔓 تم فك التايم عن {member.mention}"
    )


@bot.command()
@commands.has_permissions(kick_members=True)
async def سقها(ctx, member: discord.Member):

    await member.kick()

    await ctx.send(
        f"🚪 تم طرد {member.mention}"
    )


@bot.command()
@commands.has_permissions(ban_members=True)
async def القمها(ctx, member: discord.Member):

    await member.ban()

    await ctx.send(
        f"🔨 تم تبنيد {member.mention}"
    )


@bot.command()
@commands.has_permissions(manage_messages=True)
async def حذف(ctx, amount:int):

    await ctx.channel.purge(
        limit=amount
    )


@bot.command()
@commands.has_permissions(manage_channels=True)
async def قفل(ctx):

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=False
    )

    await ctx.send("🔒 تم قفل الروم")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def فتح(ctx):

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=True
    )

    await ctx.send("🔓 تم فتح الروم")


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

⚙️:
!بنق
""",
        color=0x8000FF
    )

    await ctx.send(embed=embed)



# =====================
# تشغيل البوت
# =====================

TOKEN = os.getenv("TOKEN")

if TOKEN:
    bot.run(TOKEN)

else:
    print("❌ TOKEN غير موجود")
