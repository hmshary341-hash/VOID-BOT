import discord
from discord.ext import commands

# إنشاء كلاس الأزرار للاقتراح
class SuggestionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # timeout=None عشان الأزرار ما تنتهي صلاحيتها إذا طوّل الاقتراح

    # زر القبول
    @discord.ui.button(label="قبول", style=discord.ButtonStyle.success, emoji="✅", custom_id="approve_btn")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        # تأكد إن اللي ضغط الزر عنده صلاحية إدارة الرسائل (إدمن/موديريتور)
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌ عذراً، هذا الزر مخصص للإدارة فقط!", ephemeral=True)

        # تعديل الإمبيد الحالي ليصبح مقبولاً
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green() # تغيير اللون للأخضر
        embed.title = "💡 اقتراح مقبول"
        
        # إضافة حقل يوضح مين الإدمن اللي قبل الاقتراح
        embed.add_field(name="الوضعية", value=f"🟢 تم القبول بواسطة: {interaction.user.mention}", inline=False)

        # تعطيل الأزرار بعد الضغط
        for child in self.children:
            child.disabled = True

        # تحديث الرسالة
        await interaction.response.edit_message(embed=embed, view=self)

    # زر الرفض
    @discord.ui.button(label="رفض", style=discord.ButtonStyle.danger, emoji="❌", custom_id="deny_btn")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        # تأكد من الصلاحيات
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌ عذراً، هذا الزر مخصص للإدارة فقط!", ephemeral=True)

        # تعديل الإمبيد الحالي ليصبح مرفوضاً
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red() # تغيير اللون للأحمر
        embed.title = "💡 اقتراح مرفوض"
        
        # إضافة حقل يوضح مين الإدمن اللي رفض الاقتراح
        embed.add_field(name="الوضعية", value=f"🔴 تم الرفض بواسطة: {interaction.user.mention}", inline=False)

        # تعطيل الأزرار بعد الضغط
        for child in self.children:
            child.disabled = True

        # تحديث الرسالة
        await interaction.response.edit_message(embed=embed, view=self)


class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.suggestion_channel_id = 1527099799038595192 # الآيدي الخاص بك

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ كوج الاقتراحات بالأزرار جاهز ويعمل بنجاح!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == self.suggestion_channel_id:
            try:
                await message.delete()

                embed = discord.Embed(
                    title="💡 اقتراح جديد!",
                    description=message.content,
                    color=discord.Color.blurple()
                )
                
                avatar_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
                embed.set_author(name=message.author.display_name, icon_url=avatar_url)
                embed.set_footer(text=f"بواسطة: {message.author.name} • معرف المستخدم: {message.author.id}")

                # إرسال الإمبيد مع الأزرار (View)
                view = SuggestionView()
                await message.channel.send(embed=embed, view=view)

            except discord.Forbidden:
                print(f"❌ خطأ: البوت يفتقر إلى صلاحيات حذف الرسائل أو إرسالها.")
            except Exception as e:
                print(f"❌ حدث خطأ غير متوقع: {e}")

async def setup(bot):
    await bot.add_cog(Suggestions(bot))
