import discord
from discord.ext import commands


TICKET_CATEGORY = 1525952823156801576
TICKET_STAFF = 1526284655584743465
TICKET_LOG = 1527750890952462408


class TicketModal(discord.ui.Modal):

    def __init__(self, ticket_type):
        super().__init__(title=ticket_type)
        self.ticket_type = ticket_type

        self.username = discord.ui.TextInput(
            label="يوزر الشخص",
            placeholder="اكتب اليوزر هنا",
            required=True
        )

        self.reason = discord.ui.TextInput(
            label="السبب",
            placeholder="اكتب سبب فتح التكت",
            style=discord.TextStyle.paragraph,
            required=True
        )

        self.proof = discord.ui.TextInput(
            label="الدليل",
            placeholder="ضع الدليل أو الرابط",
            required=False
        )

        self.add_item(self.username)
        self.add_item(self.reason)
        self.add_item(self.proof)


    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY)
        staff = guild.get_role(TICKET_STAFF)


        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category
        )


        await channel.set_permissions(
            guild.default_role,
            view_channel=False
        )

        await channel.set_permissions(
            interaction.user,
            view_channel=True,
            send_messages=True
        )

        await channel.set_permissions(
            staff,
            view_channel=True,
            send_messages=True
        )


        embed = discord.Embed(
            title="🎫 VOID TICKET",
            description=(
                f"نوع الطلب: **{self.ticket_type}**\n\n"
                f"صاحب التكت: {interaction.user.mention}\n\n"
                f"👤 اليوزر:\n{self.username.value}\n\n"
                f"📝 السبب:\n{self.reason.value}\n\n"
                f"📎 الدليل:\n{self.proof.value}"
            ),
            color=0x800080
        )


        await channel.send(
            embed=embed,
            view=TicketControl()
        )


        await interaction.response.send_message(
            f"✅ تم فتح تكتك: {channel.mention}",
            ephemeral=True
        )



class TicketSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label="إبلاغ عن إداري",
                emoji="🚨"
            ),
            discord.SelectOption(
                label="إبلاغ عن عضو",
                emoji="👤"
            ),
            discord.SelectOption(
                label="استفسار",
                emoji="❓"
            )
        ]

        super().__init__(
            placeholder="اختر نوع التكت",
            options=options
        )


    async def callback(self, interaction):

        await interaction.response.send_modal(
            TicketModal(self.values[0])
        )



class TicketMenu(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())



class TicketControl(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="📌 استلام التكت",
        style=discord.ButtonStyle.green
    )
    async def claim(self, interaction, button):

        role = interaction.guild.get_role(
            TICKET_STAFF
        )

        if role in interaction.user.roles:

            await interaction.response.send_message(
                f"📌 تم استلام التكت بواسطة {interaction.user.mention}"
            )

        else:

            await interaction.response.send_message(
                "❌ هذا الزر لمسؤولين التكت فقط",
                ephemeral=True
            )


    @discord.ui.button(
        label="🔒 إغلاق التكت",
        style=discord.ButtonStyle.red
    )
    async def close(self, interaction, button):

        log = interaction.guild.get_channel(
            TICKET_LOG
        )

        if log:

            await log.send(
                f"🔒 تم إغلاق تكت بواسطة {interaction.user.mention}"
            )

        await interaction.response.send_message(
            "🔒 سيتم إغلاق التكت"
        )

        await interaction.channel.delete()



class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="ارسل")
    @commands.has_permissions(administrator=True)
    async def send_ticket(self, ctx):

        embed = discord.Embed(
            title="🎫 افتح تكت",
            description=(
                "اضغط الزر لفتح تكت\n"
                "وإن شاء الله تنحل مشكلتك 🖤"
            ),
            color=0x800080
        )

        await ctx.send(
            embed=embed,
            view=TicketMenu()
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))
