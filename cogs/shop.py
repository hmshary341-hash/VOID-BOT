import discord
from discord.ext import commands
from discord import app_commands

class StoreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # timeout=None لتبقى الأزرار تعمل للأبد

    @discord.ui.button(
        label="افتح متجر الرتب", 
        style=discord.ButtonStyle.primary, 
        custom_id="roles_store"
    )
    async def roles_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_store_ticket(interaction, "متجر-الرتب", is_roles=True)

    @discord.ui.button(
        label="افتح متجر الألقاب", 
        style=discord.ButtonStyle.success, 
        custom_id="titles_store"
    )
    async def titles_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_store_ticket(interaction, "متجر-الألقاب", is_roles=False)

    async def create_store_ticket(self, interaction: discord.Interaction, store_name: str, is_roles: bool):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        user = interaction.user

        # آي دي الروم المخصص لاستخراج الفئة تلقائياً
        channel_id = 1530408124958244975 
        base_channel = guild.get_channel(channel_id)
        category = base_channel.category if base_channel else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True, 
                send_messages=True, 
                read_message_history=True
            )
        }

        channel = await guild.create_text_channel(
            name=f"{store_name}-{user.name}",
            category=category,
            overwrites=overwrites
        )

        await interaction.followup.send(f"تم فتح تذكرتك بنجاح: {channel.mention}", ephemeral=True)

        if is_roles:
            await channel.send(
                f"أهلاً بك يا {user.mention} في **متجر الرتب**!\n"
                "إليك قائمة الرتب المتاحة للشراء:\n\n"
                "🔥 **Ultra** - السعر: 75,000 كوينز\n"
                "🔹 **Prime** - السعر: 45,000 كوينز\n"
                "🌟 **Plus** - السعر: 25,000 كوينز\n"
                "⭐ **Basic** - السعر: 10,000 كوينز\n\n"
                "الرجاء إبلاغ الإدارة بالرتبة التي ترغب بشرائها وطريقة الدفع."
            )
        else:
            await channel.send(
                f"أهلاً بك يا {user.mention} في **متجر الألقاب**!\n"
                "إليك قائمة الألقاب المتاحة للشراء:\n\n"
                "👑 **King** - السعر: 60,000 كوينز\n"
                "👑 **Queen** - السعر: 60,000 كوينز\n\n"
                "الرجاء إبلاغ الإدارة باللقب الذي ترغب بشرائه وطريقة الدفع."
            )

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="store", description="إرسال لوحة متجر الرتب والألقاب")
    @app_commands.default_permissions(administrator=True)
    async def store_panel(self, interaction: discord.Interaction):
        view = StoreView()
        await interaction.response.send_message(
            "**مرحباً بك في متجر السيرفر!**\nاختر المتجر الذي ترغب في فتحه من الأزرار بالأسفل:", 
            view=view
        )

async def setup(bot):
    await bot.add_cog(Shop(bot))
