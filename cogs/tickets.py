import discord
from discord.ext import commands

TICKET_CATEGORY = 1525952823156801576
STAFF_ROLE = None  # حط ID رتبة الإدارة هنا
# الرابط المباشر لشعار VOID البنفسجي اللي أرسلته
TICKET_IMAGE_URL = "https://i.ibb.co/3mN68wM/VOID-Logo.png" 

class TicketReason(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="إبلاغ إداري",
                emoji="👮"
            ),
            discord.SelectOption(
                label="إبلاغ عضو",
                emoji="👤"
            ),
            discord.SelectOption(
                label="استفسار",
                emoji="❓"
            )
        ]

        super().__init__(
            placeholder="اختر سبب التكت",
            options=options
        )

    async def callback(self, interaction):
        reason = self.values[0]
        await interaction.response.send_modal(
            TicketModal(reason)
        )


class TicketMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketReason())


class TicketModal(discord.ui.Modal):
    def __init__(self, reason):
        super().__init__(
            title="بيانات التكت"
        )

        self.reason = reason

        self.user = discord.ui.TextInput(
            label="يوزر العضو",
            placeholder="اكتب اليوزر"
        )

        self.problem = discord.ui.TextInput(
            label="السبب",
            placeholder="اكتب سبب المشكلة"
        )

        self.proof = discord.ui.TextInput(
            label="الدليل",
            placeholder="ضع الرابط أو اكتب لا يوجد",
            required=False
        )

        self.add_item(self.user)
        self.add_item(self.problem)
        self.add_item(self.proof)

    async def on_submit(self, interaction):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY)

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category
        )

        await channel.set_permissions(
            interaction.user,
            view_channel=True,
            send_messages=True
        )

        embed = discord.Embed(
            title="🎫 تكت جديد",
            description="افتح تكت وإن شاء الله تنحل مشكلتك 🖤",
            color=0x8000FF
        )

        embed.add_field(name="النوع", value=self.reason, inline=False)
        embed.add_field(name="العضو", value=str(self.user), inline=False)
        embed.add_field(name="السبب", value=str(self.problem), inline=False)
        embed.add_field(name="الدليل", value=str(self.proof), inline=False)

        await channel.send(
            interaction.user.mention,
            embed=embed,
            view=TicketControl()
        )

        await interaction.response.send_message(
            f"✅ تم فتح التكت: {channel.mention}",
            ephemeral=True
        )


class TicketControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✅ استلام تكت",
        style=discord.ButtonStyle.success
    )
    async def claim(self, interaction, button):
        await interaction.response.send_message(
            f"✅ تم استلام التكت بواسطة {interaction.user.mention}"
        )

    @discord.ui.button(
        label="🔒 إغلاق تكت",
        style=discord.ButtonStyle.danger
    )
    async def close(self, interaction, button):
        await interaction.channel.delete()


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ارسل(self, ctx, arg=None):
        if arg == "تكت":
            embed = discord.Embed(
                title="🎫 نظام التذاكر",
                description="**افتح تكت وإن شاء الله تنحل مشكلتك** 🖤",
                color=0x8000FF
            )
            
            # عرض الصورة كبنر داخل الإمبيد الأساسي لفتح التكت
            embed.set_image(url=TICKET_IMAGE_URL)

            await ctx.send(
                embed=embed,
                view=OpenTicket()
            )


class OpenTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎫 افتح تكت",
        style=discord.ButtonStyle.primary
    )
    async def open(self, interaction, button):
        await interaction.response.send_message(
            "اختر سبب التكت:",
            view=TicketMenu(),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))
