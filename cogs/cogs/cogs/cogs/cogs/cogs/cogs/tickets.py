import discord
from discord.ext import commands


TICKET_CATEGORY = 1525952823156801576
TICKET_STAFF = 1526284655584743465
TICKET_LOG = 1527750890952462408


class TicketButtons(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="📌 استلام",
        style=discord.ButtonStyle.success,
        custom_id="ticket_claim"
    )
    async def claim(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        role = interaction.guild.get_role(TICKET_STAFF)

        if role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ هذا الزر لمسؤولين التكت فقط",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"📌 تم استلام التذكرة بواسطة {interaction.user.mention}"
        )


    @discord.ui.button(
        label="🔒 إغلاق",
        style=discord.ButtonStyle.danger,
        custom_id="ticket_close"
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        log = interaction.guild.get_channel(TICKET_LOG)

        if log:

            await log.send(
                f"🔒 تم إغلاق تذكرة بواسطة {interaction.user.mention}\n"
                f"الروم: {interaction.channel.name}"
            )


        await interaction.response.send_message(
            "🔒 سيتم إغلاق التذكرة"
        )

        await interaction.channel.delete()



class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="تكت")
    async def ticket(self, ctx):

        category = self.bot.get_channel(
            TICKET_CATEGORY
        )

        staff_role = ctx.guild.get_role(
            TICKET_STAFF
        )


        if not category or not staff_role:

            await ctx.send(
                "❌ إعدادات التكت ناقصة"
            )
            return


        overwrites = {

            ctx.guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),

            ctx.author:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            ),

            staff_role:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )
        }


        channel = await ctx.guild.create_text_channel(
            name=f"ticket-{ctx.author.name}",
            category=category,
            overwrites=overwrites
        )


        embed = discord.Embed(
            title="🎫 VOID TICKET",
            description=(
                f"أهلاً {ctx.author.mention}\n\n"
                "انتظر مسؤول التكت للرد عليك."
            ),
            color=0x8000FF
        )


        await channel.send(
            embed=embed,
            view=TicketButtons()
        )


        await ctx.send(
            f"✅ تم فتح تذكرتك: {channel.mention}",
            delete_after=5
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))
