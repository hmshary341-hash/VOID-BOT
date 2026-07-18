class TicketActions(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="قفل التذكرة", style=discord.ButtonStyle.secondary, emoji="🔒", custom_id="lock_ticket")
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.set_permissions(interaction.user, send_messages=False)
        await interaction.response.send_message("🔒 تم قفل التذكرة.")

    @discord.ui.button(label="حذف التذكرة", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="delete_ticket")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🗑️ جاري حفظ المحادثة وحذف التذكرة...", ephemeral=True)
        
        # تجميع المحادثة
        transcript = []
        async for message in interaction.channel.history(limit=None, oldest_first=True):
            transcript.append(f"{message.author.name}: {message.content}")
        
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            # إنشاء الملف
            file = discord.File(io.StringIO("\n".join(transcript)), filename=f"transcript-{interaction.channel.name}.txt")
            
            # إنشاء الـ Embed الجمالي
            embed = discord.Embed(
                title="📋 سجل تذكرة محذوفة",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.add_field(name="اسم القناة:", value=interaction.channel.name, inline=True)
            embed.add_field(name="حُذفت بواسطة:", value=interaction.user.mention, inline=True)
            embed.set_footer(text="VOID APP | نظام الأرشفة")
            
            # إرسال الـ Embed مع الملف
            await log_channel.send(embed=embed, file=file)
            
        await interaction.channel.delete()
