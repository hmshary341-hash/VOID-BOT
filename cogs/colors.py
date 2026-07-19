import discord
from discord import app_commands
from discord.ext import commands

class Colors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ربط كل رقم بالـ ID الخاص بالرتبة
        self.color_roles = {
            1: 1527015939697016882,
            2: 1527015992885252326,
            3: 1527016058001555486,
            4: 1527016123684622336,
            5: 1527016223248744650,
            6: 1527016301724307486,
            7: 1527016364559040573,
            8: 1527016418615365814,
            9: 1527016599612031147,
            10: 1527016689529524284,
            11: 1527016896942309587,
            12: 1527768986115244253,
        }

    @app_commands.command(name="color", description="اختر لونك الخاص برقم")
    @app_commands.describe(number="رقم اللون (من 1 إلى 12)")
    async def color(self, interaction: discord.Interaction, number: int):
        # التحقق إذا كان الرقم موجود
        if number not in self.color_roles:
            return await interaction.response.send_message(f"❌ لا يوجد لون بهذا الرقم: {number}", ephemeral=True)

        role_id = self.color_roles[number]
        role = interaction.guild.get_role(role_id)

        if not role:
            return await interaction.response.send_message("❌ الرتبة غير موجودة، تأكد من الـ ID في الكود.", ephemeral=True)

        # 1. إزالة جميع رتب الألوان القديمة من العضو
        all_color_roles_ids = list(self.color_roles.values())
        roles_to_remove = [r for r in interaction.user.roles if r.id in all_color_roles_ids]
        
        try:
            # إزالة الرتب القديمة
            if roles_to_remove:
                await interaction.user.remove_roles(*roles_to_remove)
            
            # 2. إضافة الرتبة الجديدة
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ تم تغيير لونك إلى الرقم: {number}", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ ليس لدي صلاحية لتعديل رتبك (تأكد أن رتبة البوت أعلى من رتبة اللون).", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ حدث خطأ غير متوقع: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Colors(bot))
