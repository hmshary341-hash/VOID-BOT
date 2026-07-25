import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3
from datetime import datetime, date

# --- الإعدادات ---
STREAK_ROLE_ID = 1530367528046694500     # آي دي رتبة الستريك
REMINDER_CHANNEL_ID = 1530050831636762839 # آي دي روم الستريك والتذكير

class Streak(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_setup()
        self.daily_reminder.start()

    def cog_unload(self):
        self.daily_reminder.cancel()

    def db_setup(self):
        self.conn = sqlite3.connect("streaks.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS streaks (
                user_id INTEGER,
                guild_id INTEGER,
                streak_count INTEGER,
                last_date TEXT,
                shields INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id)
            )
        """)
        self.conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # التحكد أن الرسالة في روم الستريك فقط
        if message.channel.id != REMINDER_CHANNEL_ID:
            return

        # التحقق من أن الرسالة تحتوي على صورة (مرفقات صور)
        has_image = any(
            (att.content_type and 'image' in att.content_type) or 
            att.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'webp')) 
            for att in message.attachments
        )

        if not has_image:
            return  # إذا أرسل كلاماً بدون صورة في روم الستريك، لا يتم احتسابه كستريك

        user_id = message.author.id
        guild_id = message.guild.id
        today = str(date.today())

        self.cursor.execute(
            "SELECT streak_count, last_date, shields FROM streaks WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
        )
        result = self.cursor.fetchone()

        status_text = ""

        if result is None:
            streak_count = 1
            shields = 0
            self.cursor.execute(
                "INSERT INTO streaks VALUES (?, ?, ?, ?, ?)",
                (user_id, guild_id, streak_count, today, shields)
            )
        else:
            streak_count, last_date, shields = result
            if last_date == today:
                # إذا أرسل صورة أخرى في نفس اليوم، نلغي التكرار أو نكتفي بتنبيهه
                await message.reply("⚠️ لقد قمت بتسجيل ستريك اليوم مسبقاً!", delete_after=5)
                return

            last_date_obj = datetime.strptime(last_date, "%Y-%m-%d").date()
            today_obj = date.today()
            diff = (today_obj - last_date_obj).days

            if diff == 1:
                streak_count += 1
            elif diff > 1:
                missed_days = diff - 1
                if shields >= missed_days:
                    shields -= missed_days
                    streak_count += 1
                    status_text = f"\n🛡️ تم استهلاك **{missed_days} درع** لحماية ستريكك بسبب الغياب!"
                else:
                    streak_count = 1
                    shields = 0
                    status_text = f"\n💔 انقطع ستريكك لعدم كفاية الدروع وتمت إعادته إلى 1!"

            if streak_count == 5:
                shields += 2
                status_text += f"\n🎉 مبروك! وصل ستريكك إلى 5 أيام وحصلت على **2 درع 🛡️**!"

            self.cursor.execute(
                "UPDATE streaks SET streak_count = ?, last_date = ?, shields = ? WHERE user_id = ? AND guild_id = ?",
                (streak_count, today, shields, user_id, guild_id)
            )
        self.conn.commit()

        # إعطاء رتبة الستريك
        role = message.guild.get_role(STREAK_ROLE_ID)
        if role and role not in message.author.roles:
            try:
                await message.author.add_roles(role)
            except Exception as e:
                print(f"❌ خطأ في إعطاء رتبة الستريك: {e}")

        # إرسال رسالة عامة في الروم تؤكد تسجيل الستريك
        await message.reply(
            f"🔥 | {message.author.mention}\n"
            f"• عدد أيام الستريك: **{streak_count}** يوم\n"
            f"• عدد الدروع الحالية: **{shields} 🛡️**"
            f"{status_text}"
        )

    @tasks.loop(hours=24)
    async def daily_reminder(self):
        if REMINDER_CHANNEL_ID == 0:
            return
        
        channel = self.bot.get_channel(REMINDER_CHANNEL_ID)
        if not channel:
            return
        
        today = str(date.today())
        self.cursor.execute("SELECT user_id FROM streaks WHERE guild_id = ? AND last_date != ?", (channel.guild.id, today))
        rows = self.cursor.fetchall()
        
        if rows:
            mentions = []
            for row in rows:
                user_id = row[0]
                member = channel.guild.get_member(user_id)
                if member and not member.bot:
                    mentions.append(member.mention)
            
            if mentions:
                chunks = [mentions[i:i + 10] for i in range(0, len(mentions), 10)]
                for chunk in chunks:
                    try:
                        await channel.send(f"⚠️ **تنبيه الستريك اليومي!** لم تسجلوا تفاعلكم اليوم يا أبطال، الحقوا عليكم قبل أن ينقطع الستريك: {' '.join(chunk)}")
                    except:
                        pass

    @daily_reminder.before_loop
    async def before_daily_reminder(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="streak", description="عرض عدد أيام الستريك الخاص بك وعدد الدروع المحمية")
    async def streak(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer(ephemeral=True)
        target = member or interaction.user

        self.cursor.execute(
            "SELECT streak_count, shields FROM streaks WHERE user_id = ? AND guild_id = ?",
            (target.id, interaction.guild.id)
        )
        result = self.cursor.fetchone()

        if result is None:
            streak_count, shields = 0, 0
        else:
            streak_count, shields = result

        await interaction.followup.send(
            f"🔥 | **{target.display_name}**\n"
            f"• عدد أيام الستريك: **{streak_count}** يوم\n"
            f"• عدد الدروع الحالية: **{shields} 🛡️**",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Streak(bot))
