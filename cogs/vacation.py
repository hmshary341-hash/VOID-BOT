import discord
from discord.ext import commands
from discord import app_commands

# --- إعدادات الآي ديَات ---
VACATION_CHANNEL_ID = 1530060027434500146  # روم تقديم الطلبات
ADMIN_CHANNEL_ID = 1530511919709032458     # روم استقبال الطلبات للإدارة
ADMIN_ROLE_IDS = [                         # رتب الإدارة المخولة بالقبول والرفض
    1529995977203777566,
    1529996765825335306
]

class VacationModal(discord.ui.Modal, title="نموذج طلب إجازة"):
    reason = discord.ui.TextInput(
        label="سبب الإجازة",
        style=discord.TextStyle.paragraph,
        placeholder="اكتب سبب طلب الإجازة باختصار...",
        required=True,
        max_length=300
    )
    duration = discord.ui.TextInput(
        label="مدة الإجازة (أو التاريخ)",
        style=discord.TextStyle.short,
        placeholder="مثال: 3 أيام أو من تاريخ كذا إلى كذا",
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(ADMIN_CHANNEL_ID)
        
        embed = discord.Embed(
            title="📋 طلب إجازة جديد",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="👤 العضو", value=interaction.user.mention, inline=False)
        embed.add_field(name="⏳ مدة الإجازة", value=self.duration.value, inline=False)
        embed.add_field(name="📝 السبب", value=self.reason.value, inline=False)
        
        view = VacationAdminView(interaction.user.id)

        if channel:
            await channel.send(embed=embed, view=view)
            await interaction.response.send_message("✅ تم إرسال طلب إجازتك بنجاح إلى الإدارة بانتظار الرد!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ عذراً، لم يتم العثور على روم استقبال الطلبات!", ephemeral=True)

class VacationAdminView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    def check_permissions(self, interaction: discord.Interaction):
        # السماح لمن يمتلك إحدى رتب الإدارة المحددة أو صلاحية إدارة السيرفر
        if interaction.user.guild_permissions.manage_guild:
            return True
        return any(role.id in ADMIN_ROLE_IDS for role in interaction.user.roles)

    @discord.ui.button(label="قبول", style=discord.ButtonStyle.success, custom_id="accept_vacation")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_permissions(interaction):
            await interaction.response.send_message("❌ ليس لديك الصلاحية للرد على الطلبات!", ephemeral=True)
            return

        for child in self.children:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.add_field(name="📌 الحالة", value=f"✅ تم القبول بواسطة {interaction.user.mention}", inline=False)

        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("تم قبول الطلب بنجاح.", ephemeral=True)

        try:
            member = interaction.guild.get_member(self.user_id)
            if member:
                await member.send(f"🎉 تم **قبول** طلب إجازتك في سيرفر **{interaction.guild.name}**!")
        except:
            pass

    @discord.ui.button(label="رفض", style=discord.ButtonStyle.danger, custom_id="reject_vacation")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_permissions(interaction):
            await interaction.response.send_message("❌ ليس لديك الصلاحية للرد على الطلبات!", ephemeral=True)
            return

        for child in self.children:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.add_field(name="📌 الحالة", value=f"❌ تم الرفض بواسطة {interaction.user.mention}", inline=False)

        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("تم رفض الطلب.", ephemeral=True)

        try:
            member = interaction.guild.get_member(self.user_id)
            if member:
                await member.send(f"❌ للأسف، تم **رفض** طلب إجازتك في سيرفر **{interaction.guild.name}**.")
        except:
            pass

class Vacation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vacation", description="تقديم طلب إجازة جديد للإدارة")
    async def vacation(self, interaction: discord.Interaction):
        # التحقق من استخدام الأمر في الروم المخصص فقط
        if interaction.channel.id != VACATION_CHANNEL_ID:
            await interaction.response.send_message("❌ يمكنك استخدام هذا الأمر فقط في روم طلبات الإجازة المخصص!", ephemeral=True)
            return
            
        await interaction.response.send_modal(VacationModal())

async def setup(bot):
    await bot.add_cog(Vacation(bot))
