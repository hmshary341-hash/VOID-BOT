import discord
from discord import app_commands
from discord.ext import commands

# --- الإعدادات والآي ديـات المحددة ---
PANEL_CHANNEL_ID = 1530455860285935697      # روم التقديم (اللي يقدمون منه)
APPLICATION_CHANNEL_ID = 1530456596138819626  # روم استقبال طلبات التقديم للإدارة

ADMIN_ROLE_IDS = [
    1529995977203777566,
    1529996765825335306
]  # الرتب المسموح لها بقبول/رفض التقديمات

# 🔹 الرتب الإدارية (تُعطى عند القبول فقط)
SUPPORT_ROLE_ID = 1529999244155420763       # رتبة إداري دعم
EVENT_ROLE_ID = 1530001664675811370         # رتبة إداري ايفنت
GENERAL_ADMIN_ROLE_ID = 1530623673143267469 # الرتبة المشتركة (تجيهم الاثنين عند القبول)

class ApplicationModal(discord.ui.Modal):
    def __init__(self, admin_type: str):
        super().__init__(title=f"📋 تقديم {admin_type}")
        self.admin_type = admin_type

    q1_q2 = discord.ui.TextInput(
        label="1 & 2. الاسم داخل ديسكورد + العمر",
        placeholder="مثال: Feras | العمر: 19 سنة",
        max_length=100
    )
    
    q3_q4 = discord.ui.TextInput(
        label="3 & 4. التواجد + الخبرات السابقة",
        placeholder="التواجد: 6 ساعات | الخبرات: كنت مشرف في سيرفر...",
        max_length=200
    )
    
    q5 = discord.ui.TextInput(
        label="5. ليش تبي تنضم للإدارة؟",
        placeholder="اكتب أسبابك ورغبتك في مساعدة السيرفر...",
        style=discord.TextStyle.paragraph,
        max_length=300
    )
    
    q6_q7 = discord.ui.TextInput(
        label="6. عضو سب؟ | 7. إداري خالف القوانين؟",
        placeholder="عضو: أعطيه تنبيه ثم ميوت... / إداري: أصوّر وأبلغ الإدارة العليا",
        style=discord.TextStyle.paragraph,
        max_length=300
    )
    
    q8_q9 = discord.ui.TextInput(
        label="8. البوتات + 9. هل قرأت القوانين (نعم/لا)",
        placeholder="البوتات: ميراك، بروتك, الخ... / قرأت القوانين: نعم وألتزم بها",
        style=discord.TextStyle.paragraph,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(APPLICATION_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("❌ روم استقبال التقديمات غير موجود أو أخطأت في الآي دي الخاص به!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📥 تقديم جديد لـ ({self.admin_type})",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="📌 نوع التقديم", value=f"**{self.admin_type}**", inline=False)
        embed.add_field(name="👤 المتقدم", value=interaction.user.mention, inline=False)
        embed.add_field(name="1 & 2. الاسم والعمر", value=self.q1_q2.value, inline=False)
        embed.add_field(name="3 & 4. ساعات التواجد والخبرات", value=self.q3_q4.value, inline=False)
        embed.add_field(name="5. ليش تبي تنضم؟", value=self.q5.value, inline=False)
        embed.add_field(name="6 & 7. التصرف مع المخالفين", value=self.q6_q7.value, inline=False)
        embed.add_field(name="8 & 9. البوتات وقراءة القوانين", value=self.q8_q9.value, inline=False)
        embed.set_footer(text=f"ID: {interaction.user.id}")

        view = ReviewView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message("✨ تم إرسال تقديمك بنجاح! انتظر الرد قريباً.", ephemeral=True)

class ApplyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إداري دعم 🛠️", style=discord.ButtonStyle.green, custom_id="apply_support_btn_v6")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationModal("إداري دعم"))

    @discord.ui.button(label="إداري ايفنت 🎉", style=discord.ButtonStyle.blurple, custom_id="apply_event_btn_v6")
    async def event_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationModal("إداري ايفنت"))

class ReviewView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="قبول ✅", style=discord.ButtonStyle.success, custom_id="accept_apply_v6")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(r.id in ADMIN_ROLE_IDS for r in interaction.user.roles):
            await interaction.response.send_message("❌ هذا الزر للإدارة فقط!", ephemeral=True)
            return
        
        for child in self.children:
            child.disabled = True
        
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.add_field(name="حالة التقديم", value=f"✅ **تم القبول بواسطة** {interaction.user.mention}", inline=False)
        
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"تم قبول التقديم بنجاح وإعطاء الرتب المطلوبة للعضو.", ephemeral=True)
        
        applicant = None
        try:
            footer_text = embed.footer.text
            user_id = int(footer_text.split(": ")[1])
            applicant = interaction.guild.get_member(user_id)
        except:
            pass

        # معرفة نوع التقديم من الـ Embed
        app_type = ""
        for field in embed.fields:
            if field.name == "📌 نوع التقديم":
                app_type = field.value
                break

        if applicant:
            try:
                roles_to_add = []
                role_name = ""
                
                # جلب الرتبة المشتركة للجميع عند القبول
                general_role = interaction.guild.get_role(GENERAL_ADMIN_ROLE_ID)
                if general_role:
                    roles_to_add.append(general_role)

                # تحديد الرتبة الخاصة حسب اختيار المتقدم
                if "إداري دعم" in app_type:
                    support_role = interaction.guild.get_role(SUPPORT_ROLE_ID)
                    if support_role:
                        roles_to_add.append(support_role)
                    role_name = "إداري دعم"
                elif "إداري ايفنت" in app_type:
                    event_role = interaction.guild.get_role(EVENT_ROLE_ID)
                    if event_role:
                        roles_to_add.append(event_role)
                    role_name = "إداري ايفنت"

                # إعطاء الرتب دفعة واحدة للعضو
                if roles_to_add:
                    await applicant.add_roles(*roles_to_add)
                    await applicant.send(f"🎉 مبارك! تم قبول تقديمك كـ **({role_name})** وتم إعطاؤك الرتب الإدارية في السيرفر بنجاح.")
                else:
                    await applicant.send(f"🎉 مبارك! تم قبول تقديمك الإداري في السيرفر.")
            except Exception as e:
                print(f"Error giving roles: {e}")

    @discord.ui.button(label="رفض ❌", style=discord.ButtonStyle.danger, custom_id="reject_apply_v6")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(r.id in ADMIN_ROLE_IDS for r in interaction.user.roles):
            await interaction.response.send_message("❌ هذا الزر للإدارة فقط!", ephemeral=True)
            return

        for child in self.children:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.add_field(name="حالة التقديم", value=f"❌ **تم الرفض بواسطة** {interaction.user.mention}", inline=False)

        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"تم رفض التقديم.", ephemeral=True)

        applicant = None
        try:
            footer_text = embed.footer.text
            user_id = int(footer_text.split(": ")[1])
            applicant = interaction.guild.get_member(user_id)
        except:
            pass

        if applicant:
            try:
                await applicant.send(f"عذراً، لم يتم قبول تقديمك الإداري هذه المرة. نتمنى لك حظاً أوفر في المرات القادمة.")
            except:
                pass

class ApplicationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(ApplyView())
        self.bot.add_view(ReviewView())

    @app_commands.command(name="apply_panel", description="إرسال لوحة التقديم الإداري في الروم المخصص")
    async def apply_panel(self, interaction: discord.Interaction):
        if not any(r.id in ADMIN_ROLE_IDS for r in interaction.user.roles):
            await interaction.response.send_message("❌ هذا الأمر خاص بالإدارة فقط!", ephemeral=True)
            return

        target_channel = interaction.guild.get_channel(PANEL_CHANNEL_ID)
        if not target_channel:
            await interaction.response.send_message("❌ روم التقديم غير موجود، تأكد من صحة الآي دي!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🌟 نظام التقديم الإداري الرسمي",
            description="هل تملك الكفاءة لتكون جزءاً من طاقم الإدارة لدينا؟\nاختر أحد الأزرار بالأسفل لفتح استمارة التقديم (إداري دعم أو إداري ايفنت) والإجابة على الأسئلة بكل وضوح.",
            color=discord.Color.from_rgb(100, 100, 255)
        )
        embed.set_footer(text="نظام التقديم الفخم - سيرفرك")
        
        await target_channel.send(embed=embed, view=ApplyView())
        await interaction.response.send_message(f"✅ تم إرسال لوحة التقديم بنجاح إلى روم {target_channel.mention}!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ApplicationCog(bot))
