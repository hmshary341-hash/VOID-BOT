import discord
from discord.ext import commands
import random
import json
import os
import asyncio

DATA_FILE = "economy.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user_data(data, user_id):
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "coins": 0, "daily_transferred": 0, "last_date": "", 
            "last_daily_date": "", "last_work_date": "", "nerd_count": 0, 
            "last_nerd_date": "", "mafia_wins": 0, "citizen_wins": 0
        }
    elif isinstance(data[user_id], int):
        old = data[user_id]
        data[user_id] = {
            "coins": old, "daily_transferred": 0, "last_date": "", 
            "last_daily_date": "", "last_work_date": "", "nerd_count": 0, 
            "last_nerd_date": "", "mafia_wins": 0, "citizen_wins": 0
        }
    else:
        if "mafia_wins" not in data[user_id]:
            data[user_id]["mafia_wins"] = 0
        if "citizen_wins" not in data[user_id]:
            data[user_id]["citizen_wins"] = 0
    return data[user_id]

def normalize_arabic(text):
    if not text:
        return ""
    text = text.strip()
    for char in ['أ', 'إ', 'آ']:
        text = text.replace(char, 'ا')
    return text

async def reward_winner(channel, winner, game_name):
    data = load_data()
    u_data = get_user_data(data, winner.id)
    u_data["coins"] += 550
    save_data(data)

    embed = discord.Embed(
        title=f"🏆 نهاية لعبة {game_name}",
        description=f"الفائز: {winner.mention}\n💰 الجائزة المضافة: **550 كوينز**",
        color=discord.Color.gold()
    )
    embed.set_image(url=winner.display_avatar.url)
    await channel.send(f"فوز مستحق مبروك {winner.mention}! 🏆", embed=embed)

# ==========================================
# نظام لعبة المافيا
# ==========================================
class PlayerSelect(discord.ui.Select):
    def __init__(self, players, placeholder, callback_func):
        options = [discord.SelectOption(label=p.name, value=str(p.id)) for p in players]
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)
        self.custom_callback = callback_func

    async def callback(self, interaction: discord.Interaction):
        await self.custom_callback(interaction, self.values[0])

class PlayerSelectView(discord.ui.View):
    def __init__(self, players, placeholder, callback_func):
        super().__init__(timeout=30)
        self.add_item(PlayerSelect(players, placeholder, callback_func))

class MafiaView(discord.ui.View):
    def __init__(self, host_id):
        super().__init__(timeout=300)
        self.host_id = host_id
        self.players = []
        self.roles = {}
        self.game_started = False
        self.mafia_users = []
        self.non_mafia_users = []
        self.doctor_user = None
        self.detective_user = None

    @discord.ui.button(label="دخول اللعبة 🎮", style=discord.ButtonStyle.green, custom_id="mafia_join")
    async def join_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game_started:
            await interaction.response.send_message("❌ لقد بدأت اللعبة بالفعل!", ephemeral=True)
            return
        if interaction.user in self.players:
            await interaction.response.send_message("⚠️ أنت منضم بالفعل في اللعبة!", ephemeral=True)
            return

        self.players.append(interaction.user)
        player_list = "\n".join([p.mention for p in self.players])
        embed = interaction.message.embeds[0]
        embed.description = f"**اللاعبون المنضمون ({len(self.players)}):**\n{player_list}"
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("✅ تم انضمامك إلى لعبة المافيا بنجاح!", ephemeral=True)

    @discord.ui.button(label="خروج من اللعبة 🚪", style=discord.ButtonStyle.danger, custom_id="mafia_leave")
    async def leave_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game_started:
            await interaction.response.send_message("❌ لا يمكنك الخروج بعد بدء اللعبة!", ephemeral=True)
            return
        if interaction.user not in self.players:
            await interaction.response.send_message("⚠️ أنت لست منضماً في اللعبة أساساً!", ephemeral=True)
            return

        self.players.remove(interaction.user)
        player_list = "\n".join([p.mention for p in self.players]) if self.players else "لا يوجد لاعبون منضمون حالياً."
        embed = interaction.message.embeds[0]
        embed.description = f"**اللاعبون المنضمون ({len(self.players)}):**\n{player_list}"
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("✅ تم خروجك من لعبة المافيا بنجاح.", ephemeral=True)

    @discord.ui.button(label="بدء اللعبة 🚀", style=discord.ButtonStyle.primary, custom_id="mafia_start")
    async def start_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ فقط من بدأ الأمر أو الإدارة يستطيع بدء اللعبة!", ephemeral=True)
            return
        if self.game_started:
            await interaction.response.send_message("❌ اللعبة بدأت بالفعل!", ephemeral=True)
            return
        if len(self.players) <= 3:
            await interaction.response.send_message("❌ ممنوع لعب المافيا إذا كان عدد اللاعبين 3 أو أقل!", ephemeral=True)
            return

        self.game_started = True
        shuffled_players = self.players.copy()
        random.shuffle(shuffled_players)
        num_players = len(shuffled_players)
        
        if num_players >= 8:
            mafia_count = 2
            doctor_count = 1
            detective_count = 1
        else:
            mafia_count = 1
            doctor_count = 1
            detective_count = 0

        self.mafia_users = []
        self.non_mafia_users = []
        
        for _ in range(mafia_count):
            user = shuffled_players.pop()
            self.roles[user.id] = "مافيا 🦹‍♂️"
            self.mafia_users.append(user)
        
        for _ in range(doctor_count):
            if shuffled_players:
                user = shuffled_players.pop()
                self.roles[user.id] = "طبيب 🩺"
                self.doctor_user = user
                self.non_mafia_users.append(user)
                
        if detective_count > 0 and shuffled_players:
            user = shuffled_players.pop()
            self.roles[user.id] = "محقق 🔍"
            self.detective_user = user
            self.non_mafia_users.append(user)

        while shuffled_players:
            user = shuffled_players.pop()
            self.roles[user.id] = "مواطن 👤"
            self.non_mafia_users.append(user)

        reveal_view = MafiaControlView(self.roles, self.mafia_users, self.non_mafia_users, self.doctor_user, self.detective_user, self.players, self.host_id)
        
        embed = discord.Embed(
            title="🎮 بدأت لعبة المافيا بنجاح!",
            description="تم توزيع الأدوار.\n- اضغط على زر **اكشف دورك السري** لمعرفة دورك.\n- زر **ابدأ الليل 🌙** لبدء جولة الأفعال الليلية.\n- زر **تصويت طرد 🗳️** لطرد المشكوك فيهم بالنهار.",
            color=discord.Color.dark_red()
        )
        await interaction.message.edit(embed=embed, view=reveal_view)
        await interaction.response.send_message("🚀 بدأت اللعبة وتم إرسال الأدوار للأعضاء عبر الأزرار!", ephemeral=True)

class MafiaControlView(discord.ui.View):
    def __init__(self, roles, mafia_users, non_mafia_users, doctor_user, detective_user, players, host_id):
        super().__init__(timeout=None)
        self.roles = roles
        self.mafia_users = mafia_users
        self.non_mafia_users = non_mafia_users
        self.doctor_user = doctor_user
        self.detective_user = detective_user
        self.players = players
        self.host_id = host_id
        
        self.mafia_choices = {}
        self.doctor_choice = None
        self.total_mafia_count = len(self.mafia_users)
        self.eliminated_mafia_count = 0

    @discord.ui.button(label="اكشف دورك السري 🕵️‍♂️", style=discord.ButtonStyle.secondary, custom_id="mafia_reveal")
    async def reveal_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        if user_id not in self.roles:
            await interaction.response.send_message("❌ أنت لست مشاركاً في هذه اللعبة!", ephemeral=True)
            return
        role = self.roles[user_id]
        await interaction.response.send_message(f"🔒 دورك السري في اللعبة هو: **{role}**", ephemeral=True)

    @discord.ui.button(label="ابدأ الليل 🌙", style=discord.ButtonStyle.danger, custom_id="start_night_btn")
    async def start_night_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ هذا الزر مخصص لمنشئ اللعبة أو الإدارة فقط!", ephemeral=True)
            return

        await interaction.response.send_message("🌙 بدأ الليل! تم إرسال الأوامر الخاصة لكل دور بشكل سري.", ephemeral=True)

        for player in self.players:
            role = self.roles.get(player.id)
            if "مافيا" in role:
                async def mafia_action(inter, target_id):
                    self.mafia_choices[inter.user.id] = int(target_id)
                    target_name = discord.utils.get(self.players, id=int(target_id)).name
                    await inter.response.send_message(f"🔪 لقد اخترت قتل: **{target_name}**", ephemeral=True)

                view = PlayerSelectView(self.players, "اختر من تقتل (خاص بالمافيا)", mafia_action)
                try:
                    await player.send("🔪 **الليل وصل:** بصفتك مافيا، اختر من تقتل هذه الليلة (أمامك 30 ثانية):", view=view)
                except:
                    pass

            elif "طبيب" in role:
                async def doctor_action(inter, target_id):
                    self.doctor_choice = int(target_id)
                    target_name = discord.utils.get(self.players, id=int(target_id)).name
                    await inter.response.send_message(f"🩺 لقد اخترت حماية: **{target_name}**", ephemeral=True)

                view = PlayerSelectView(self.players, "اختر من تحمي (نفسك أو غيرك)", doctor_action)
                try:
                    await player.send("🩺 **الليل وصل:** بصفتك طبيب، اختر من تحمي هذه الليلة:", view=view)
                except:
                    pass

            elif "محقق" in role:
                async def detective_action(inter, target_id):
                    target_id_int = int(target_id)
                    target_member = discord.utils.get(self.players, id=target_id_int)
                    target_role = self.roles.get(target_id_int, "مواطن")
                    if "مافيا" in target_role:
                        msg = f"🔍 كشفت **{target_member.name}**...\nأبك أبك هذا مافيا 🦹‍♂️🔥!"
                    else:
                        msg = f"🔍 كشفت **{target_member.name}**...\nهذا مو مافيا، الدكتور الحلو 🩺✨."
                    await inter.response.send_message(msg, ephemeral=True)

                view = PlayerSelectView(self.players, "اختر من تريد الكشف عنه", detective_action)
                try:
                    await player.send("🔍 **الليل وصل:** بصفتك محقق، اختر شخصاً لتكشف هويته:", view=view)
                except:
                    pass

        await asyncio.sleep(30)

        target_to_kill = None
        if self.mafia_choices:
            choices_list = list(self.mafia_choices.values())
            target_to_kill = random.choice(choices_list)
        else:
            target_to_kill = random.choice(self.players).id

        if target_to_kill == self.doctor_choice:
            await interaction.channel.send("🛡️ **شقكم الدكتور وما قتلتوه!** (لم يمت أحد هذه الليلة بفضل حماية الطبيب).")
        else:
            dead_player = discord.utils.get(self.players, id=target_to_kill)
            if dead_player:
                await interaction.channel.send(f"💀 **عسير!** لقد تم قتل اللاعب **{dead_player.mention}** هذه الليلة من قِبل المافيا!")

    @discord.ui.button(label="تصويت طرد 🗳️", style=discord.ButtonStyle.primary, custom_id="vote_kick_btn")
    async def vote_kick_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ هذا الزر مخصص لمنشئ اللعبة أو الإدارة فقط!", ephemeral=True)
            return

        async def kick_action(inter, target_id):
            target_id_int = int(target_id)
            target_member = discord.utils.get(self.players, id=target_id_int)
            target_role = self.roles.get(target_id_int, "مواطن")

            if "مافيا" in target_role:
                self.eliminated_mafia_count += 1
                count_str = f" {self.eliminated_mafia_count}/{self.total_mafia_count}" if self.total_mafia_count > 1 else ""
                await inter.response.send_message(f"القم واعععععععععع تم طرد مافيا{count_str} 👞💥")
            else:
                await inter.response.send_message(f"😢 للأسف تم طرد اللاعب **{target_member.name}** لكنه طلع بريء ومو مافيا!")

        view = PlayerSelectView(self.players, "اختر اللاعب المراد التصويت لطرده", kick_action)
        await interaction.response.send_message("🗳️ **بدأ التصويت النهاري!** اختر الشخص المشكوك فيه لطرده:", view=view, ephemeral=True)

    @discord.ui.button(label="🏆 إعلان فوز المافيا", style=discord.ButtonStyle.danger, custom_id="mafia_win_btn")
    async def mafia_win_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ هذا الزر مخصص لمنشئ اللعبة أو الإدارة فقط!", ephemeral=True)
            return

        data = load_data()
        description = "🎉 **فاز فريق المافيا بالسيطرة على المدينة!**\n\n**أعضاء المافيا الفائزون:**\n"
        first_mafia = self.mafia_users[0] if self.mafia_users else None
        for mafia in self.mafia_users:
            u_data = get_user_data(data, mafia.id)
            u_data["coins"] += 550
            u_data["mafia_wins"] += 1
            description += f"👤 **{mafia.name}** ({mafia.mention})\n📊 عدد مرات الفوز بالمافيا: **{u_data['mafia_wins']}**\n💰 الجائزة المضافة: **550 كوينز**\n\n"
        save_data(data)

        embed = discord.Embed(title="🏆 نهاية اللعبة - انتصار المافيا!", description=description, color=discord.Color.dark_red())
        if first_mafia:
            embed.set_image(url=first_mafia.display_avatar.url)
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(embed=embed, view=self)
        
        win_text = f"فوز مستحق مبروك للمافيا! 🏆\n" + (f"{first_mafia.mention}" if first_mafia else "")
        await interaction.response.send_message(win_text, ephemeral=False)

    @discord.ui.button(label="🏆 إعلان فوز المواطنين", style=discord.ButtonStyle.success, custom_id="citizen_win_btn")
    async def citizen_win_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ هذا الزر مخصص لمنشئ اللعبة أو الإدارة فقط!", ephemeral=True)
            return

        data = load_data()
        description = "🎉 **فاز فريق المواطنين والعدالة في المدينة!**\n\n**المواطنون الفائزون:**\n"
        first_citizen = self.non_mafia_users[0] if self.non_mafia_users else None
        for citizen in self.non_mafia_users:
            u_data = get_user_data(data, citizen.id)
            u_data["coins"] += 550
            u_data["citizen_wins"] += 1
            role_name = self.roles.get(citizen.id, "مواطن 👤")
            description += f"👤 **{citizen.name}** ({citizen.mention}) - [{role_name}]\n📊 عدد مرات فوز المواطنين: **{u_data['citizen_wins']}**\n💰 الجائزة المضافة: **550 كوينز**\n\n"
        save_data(data)

        embed = discord.Embed(title="🏆 نهاية اللعبة - انتصار المواطنين!", description=description, color=discord.Color.green())
        if first_citizen:
            embed.set_image(url=first_citizen.display_avatar.url)
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(embed=embed, view=self)
        
        win_text = f"فوز مستحق مبروك للمواطنين! 🏆\n" + (f"{first_citizen.mention}" if first_citizen else "")
        await interaction.response.send_message(win_text, ephemeral=False)

# ==========================================
# نظام لعبة ربيكا (إنسان حيوان الجماعية)
# ==========================================
class RebeccaModal(discord.ui.Modal, title="لعبة إنسان حيوان مع ربيكا 💅"):
    def __init__(self, letter, game_view):
        super().__init__()
        self.letter = letter
        self.game_view = game_view

        self.human = discord.ui.TextInput(label=f"إنسان بحرف ({letter})", placeholder="مثال: محمد", required=True, max_length=50)
        self.animal = discord.ui.TextInput(label=f"حيوان بحرف ({letter})", placeholder="مثال: بطريق", required=True, max_length=50)
        self.plant = discord.ui.TextInput(label=f"نبات بحرف ({letter})", placeholder="مثال: برتقال", required=True, max_length=50)
        self.jamad = discord.ui.TextInput(label=f"جماد بحرف ({letter})", placeholder="مثال: باب", required=True, max_length=50)
        self.country = discord.ui.TextInput(label=f"بلاد بحرف ({letter})", placeholder="مثال: بحرين", required=True, max_length=50)

        self.add_item(self.human)
        self.add_item(self.animal)
        self.add_item(self.plant)
        self.add_item(self.jamad)
        self.add_item(self.country)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in self.game_view.submitted_users:
            await interaction.response.send_message("❌ لقد قمت بالمشاركة مسبقاً في هذه الجولة!", ephemeral=True)
            return

        h = self.human.value.strip()
        a = self.animal.value.strip()
        p = self.plant.value.strip()
        j = self.jamad.value.strip()
        c = self.country.value.strip()

        norm_letter = normalize_arabic(self.letter)
        score = 0
        fields = [("إنسان", h), ("حيوان", a), ("نبات", p), ("جماد", j), ("بلاد", c)]

        for name, val in fields:
            norm_val = normalize_arabic(val)
            if norm_val.startswith(norm_letter):
                score += 10

        reward = score * 20
        if reward > 0:
            data = load_data()
            u_data = get_user_data(data, user_id)
            u_data["coins"] = u_data.get("coins", 0) + reward
            save_data(data)

        self.game_view.scores[user_id] = {"name": interaction.user.name, "score": score, "reward": reward}
        self.game_view.submitted_users.add(user_id)

        await interaction.response.send_message(f"✅ تم تسجيل إجاباتك بنجاح!\nالنقاط: **{score}/50**\nالكوينز المكتسبة: **+{reward}** 💰", ephemeral=True)

class RebeccaParticipateButton(discord.ui.Button):
    def __init__(self, game_view):
        super().__init__(label="شارك بكلماتك ✍️", style=discord.ButtonStyle.success, custom_id="rebecca_part")
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.game_view.players:
            await interaction.response.send_message("❌ أنت لست من المشاركين الأساسيين في هذه اللعبة!", ephemeral=True)
            return
        if interaction.user.id in self.game_view.submitted_users:
            await interaction.response.send_message("⚠️ لقد شاركت بالفعل في هذه الجولة!", ephemeral=True)
            return
        await interaction.response.send_modal(RebeccaModal(self.game_view.chosen_letter, self.game_view))

class RebeccaEndButton(discord.ui.Button):
    def __init__(self, game_view):
        super().__init__(label="إنهاء وإعلان النتائج 📊", style=discord.ButtonStyle.danger, custom_id="rebecca_end")
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.game_view.host_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ فقط منظم اللعبة يستطيع إنهاءها!", ephemeral=True)
            return

        desc = f"📊 **نتائج جولة ربيكا (الحرف: {self.game_view.chosen_letter})**\n\n"
        winner_member = None

        if self.game_view.scores:
            sorted_scores = sorted(self.game_view.scores.values(), key=lambda x: x["score"], reverse=True)
            top_score_data = sorted_scores[0]
            
            for p in self.game_view.players:
                if p.name == top_score_data["name"]:
                    winner_member = p
                    break

            if winner_member:
                data = load_data()
                u_data = get_user_data(data, winner_member.id)
                u_data["coins"] += 550
                save_data(data)

            for i, data_item in enumerate(sorted_scores, 1):
                desc += f"{i}. **{data_item['name']}** - النقاط: {data_item['score']}/50 | الكوينز: +{data_item['reward']} 💰\n"
        else:
            desc += "محد شارك يا كسالى! ربيكا زعلانة منكم 🙄💅"

        embed = discord.Embed(title="🏆 نهاية اللعبة - نتائج ربيكا", description=desc, color=discord.Color.gold())
        if winner_member:
            embed.set_image(url=winner_member.display_avatar.url)

        for item in self.view.children:
            item.disabled = True
        await interaction.message.edit(embed=embed, view=self.view)

        if winner_member:
            await interaction.response.send_message(f"فوز مستحق مبروك {winner_member.mention}! 🏆 حصلت على المركز الأول وجائزة 550 كوينز!", ephemeral=False)
        else:
            await interaction.response.send_message("✅ تم إنهاء اللعبة وإعلان النتائج بنجاح!", ephemeral=True)

class RebeccaGameView(discord.ui.View):
    def __init__(self, host_id):
        super().__init__(timeout=300)
        self.host_id = host_id
        self.players = []
        self.game_started = False
        self.chosen_letter = ""
        self.submitted_users = set()
        self.scores = {}

    @discord.ui.button(label="دخول اللعبة 🎮", style=discord.ButtonStyle.green, custom_id="rebecca_join")
    async def join_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game_started:
            await interaction.response.send_message("❌ لقد بدأت اللعبة بالفعل!", ephemeral=True)
            return
        if interaction.user in self.players:
            await interaction.response.send_message("⚠️ أنت منضم بالفعل!", ephemeral=True)
            return

        self.players.append(interaction.user)
        player_list = "\n".join([p.mention for p in self.players])
        embed = interaction.message.embeds[0]
        embed.description = f"**اللاعبون المنضمون ({len(self.players)}):**\n{player_list}\n\n*(ملاحظة: اللعبة تتطلب لاعبان على الأقل)*"
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("✅ انضممت إلى لعبة ربيكا بنجاح!", ephemeral=True)

    @discord.ui.button(label="خروج من اللعبة 🚪", style=discord.ButtonStyle.danger, custom_id="rebecca_leave")
    async def leave_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game_started:
            await interaction.response.send_message("❌ لا يمكنك الخروج بعد بدء اللعبة!", ephemeral=True)
            return
        if interaction.user not in self.players:
            await interaction.response.send_message("⚠️ أنت لست منضماً أساساً!", ephemeral=True)
            return

        self.players.remove(interaction.user)
        player_list = "\n".join([p.mention for p in self.players]) if self.players else "لا يوجد لاعبون منضمون حالياً."
        embed = interaction.message.embeds[0]
        embed.description = f"**اللاعبون المنضمون ({len(self.players)}):**\n{player_list}\n\n*(ملاحظة: اللعبة تتطلب لاعبان على الأقل)*"
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("✅ تم خروجك من اللعبة بنجاح.", ephemeral=True)

    @discord.ui.button(label="بدء اللعبة 🚀", style=discord.ButtonStyle.primary, custom_id="rebecca_start")
    async def start_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ فقط من بدأ الأمر أو الإدارة يستطيع بدء اللعبة!", ephemeral=True)
            return
        if self.game_started:
            await interaction.response.send_message("❌ اللعبة بدأت بالفعل!", ephemeral=True)
            return
        if len(self.players) < 2:
            await interaction.response.send_message("❌ ممنوع لعب ربيكا إذا كان عدد اللاعبين أقل من 2!", ephemeral=True)
            return

        self.game_started = True
        letters = ["أ", "ب", "ت", "ج", "ح", "خ", "د", "ر", "س", "ش", "ص", "ع", "ف", "ق", "ك", "ل", "م", "ن", "هـ", "و", "ي"]
        self.chosen_letter = random.choice(letters)

        self.clear_items()
        self.add_item(RebeccaParticipateButton(self))
        self.add_item(RebeccaEndButton(self))

        embed = discord.Embed(
            title="💅 ربيكا تدير لعبة إنسان حيوان الجماعية!",
            description=f"الحرف المطلوب لهذه الجولة هو: **{self.chosen_letter}**\n\nاضغط على زر **شارك بكلماتك ✍️** لإدخال إجاباتك!",
            color=discord.Color.magenta()
        )
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("🚀 بدأت الجولة! يمكن للمشاركين الضغط على زر المشاركة الآن.", ephemeral=True)

# ==========================================
# قالب عام للألعاب البسيطة (تعطي 550 كوينز عند الفوز)
# ==========================================
class QuickGameView(discord.ui.View):
    def __init__(self, game_name):
        super().__init__(timeout=60)
        self.game_name = game_name

    @discord.ui.button(label="الفوز باللعبة 🏆", style=discord.ButtonStyle.green, custom_id="quick_win")
    async def win_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await reward_winner(interaction.channel, interaction.user, self.game_name)
        await interaction.response.send_message("✅ تم احتساب الفوز!", ephemeral=True)

# ==========================================
# فئة الأوامر النصية التقليدية
# ==========================================
class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="العاب")
    async def games_menu(self, ctx):
        msg = (
            "العاب السيرفر\n"
            "- روليت\n"
            "- xo\n"
            "- مافيا\n"
            "- كراسي\n"
            "- حجرة\n"
            "- نرد\n"
            "- عجلة\n"
            "- hotxo\n"
            "- غميضة\n"
            "- ربيكا\n"
            "- خمن\n\n"
            "العاب فردية\n"
            "- زر\n"
            "- اسرع\n"
            "- فكك\n"
            "- ادمج\n"
            "- اعلام\n"
            "- اعكس\n"
            "- حرف\n"
            "- صحح\n"
            "- ترتيب\n"
            "- الوان\n"
            "- ايموجي\n"
            "- اكشف"
        )
        await ctx.send(msg)

    @commands.command(name="ايقاف")
    async def stop_game(self, ctx):
        await ctx.send("🛑 تم إيقاف جميع الألعاب النشطة في هذه الشات بنجاح.")

    @commands.command(name="مافيا")
    async def mafia_cmd(self, ctx):
        embed = discord.Embed(
            title="🕵️‍♂️ لعبة المافيا الجماعية",
            description="**اللاعبون المنضمون (0):**\nلا يوجد لاعبون منضمون حالياً.",
            color=discord.Color.red()
        )
        view = MafiaView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="ربيكا")
    async def rebecca_cmd(self, ctx):
        embed = discord.Embed(
            title="💅 لعبة ربيكا الجماعية (إنسان حيوان)",
            description="**اللاعبون المنضمون (0):**\nلا يوجد لاعبون منضمون حالياً.\n\n*(ملاحظة: اللعبة تتطلب لاعبان على الأقل)*",
            color=discord.Color.magenta()
        )
        view = RebeccaGameView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="روليت")
    async def roulette_cmd(self, ctx):
        embed = discord.Embed(title="🎡 لعبة روليت", description="اضغط على الزر أدناه لتجرب حظك وتفوز بالجائزة!", color=discord.Color.blurple())
        await ctx.send(embed=embed, view=QuickGameView("روليت"))

    @commands.command(name="xo")
    async def xo_cmd(self, ctx):
        embed = discord.Embed(title="❌ إكس أو (XO)", description="اضغط على الزر أدناه لإعلان فوزك في الجولة!", color=discord.Color.blurple())
        await ctx.send(embed=embed, view=QuickGameView("XO"))

    @commands.command(name="كراسي")
    async def chairs_cmd(self, ctx):
        embed = discord.Embed(title="🪑 لعبة الكراسي الموسيقية", description="اضغط على الزر لتلحق بالكرسي وتفوز!", color=discord.Color.blurple())
        await ctx.send(embed=embed, view=QuickGameView("الكراسي"))

    @commands.command(name="حجرة")
    async def rock_cmd(self, ctx):
        embed = discord.Embed(title="✊ حجرة ورقة مقص", description="اضغط على الزر لتسجيل فوزك بالجولة!", color=discord.Color.blurple())
        await ctx.send(embed=embed, view=QuickGameView("حجرة ورقة مقص"))

    @commands.command(name="نرد")
    async def dice_cmd(self, ctx):
        embed = discord.Embed(title="🎲 لعبة النرد", description="اضغط على الزر لاختبار حظك بالنرد!", color=discord.Color.blurple())
        await ctx.send(embed=embed, view=QuickGameView("النرد"))

    @commands.command(name="عجلة")
    async def wheel_cmd(self, ctx):
        embed = discord.Embed(title="🎡 عجلة الحظ", description="اضغط على الزر لتدوير العجلة والفوز!", color=discord.Color.blurple())
        await ctx.send(embed=embed, view=QuickGameView("عجلة الحظ"))

    @commands.command(name="hotxo")
    async def hotxo_cmd(self, ctx):
        embed = discord.Embed(title="🔥 لعبة HotXO", description="اضغط على الزر للفوز بالجولة الحماسية!", color=discord.Color.blurple())
        await ctx.send(embed=embed, view=QuickGameView("HotXO"))

    @commands.command(name="غميضة")
    async def hide_cmd(self, ctx):
        embed = discord.Embed(title="🫣 لعبة الغميضة", description="اضغط على الزر لإيجاد المكان والفوز!", color=discord.Color.blurple())
        await ctx.send(embed=embed, view=QuickGameView("الغميضة"))

    @commands.command(name="خمن")
    async def guess_cmd(self, ctx):
        embed = discord.Embed(title="🤔 لعبة خمن", description="اضغط على الزر لإعلان تخمينك الصحيح!", color=discord.Color.blurple())
        await ctx.send(embed=embed, view=QuickGameView("خمن"))

    @commands.command(name="زر")
    async def button_game_cmd(self, ctx):
        embed = discord.Embed(title="🔘 أسرع زر", description="أسرع شخص يضغط على الزر يفوز!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("زر"))

    @commands.command(name="اسرع")
    async def fast_cmd(self, ctx):
        embed = discord.Embed(title="⚡ لعبة أسرع", description="اضغط بسرعة لتسجيل فوزك!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("أسرع"))

    @commands.command(name="فكك")
    async def decode_cmd(self, ctx):
        embed = discord.Embed(title="🧩 لعبة فكك", description="قم بفك الكلمة واضغط الزر إذا فزت!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("فكك"))

    @commands.command(name="ادمج")
    async def merge_cmd(self, ctx):
        embed = discord.Embed(title="🔗 لعبة ادمج", description="قم بدمج الحروف واضغط الزر للفوز!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("ادمج"))

    @commands.command(name="اعلام")
    async def flags_cmd(self, ctx):
        embed = discord.Embed(title="🚩 لعبة الأعلام", description="اعرف العلم واضغط الزر إذا أجبت صح!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("الأعلام"))

    @commands.command(name="اعكس")
    async def reverse_cmd(self, ctx):
        embed = discord.Embed(title="🔄 لعبة اعكس", description="اعكس الكلمة واضغط الزر للفوز!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("اعكس"))

    @commands.command(name="حرف")
    async def letter_cmd(self, ctx):
        embed = discord.Embed(title="🔤 لعبة حرف", description="أجب بالحرف المناسب واضغط الفوز!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("حرف"))

    @commands.command(name="صحح")
    async def correct_cmd(self, ctx):
        embed = discord.Embed(title="✅ لعبة صحح", description="صحح الخطأ الإملائي واضغط الزر!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("صحح"))

    @commands.command(name="ترتيب")
    async def order_cmd(self, ctx):
        embed = discord.Embed(title="🔢 لعبة ترتيب", description="رتب الكلمات أو الأرقام واضغط الزر!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("ترتيب"))

    @commands.command(name="الوان")
    async def colors_cmd(self, ctx):
        embed = discord.Embed(title="🎨 لعبة الألوان", description="اختر اللون الصحيح واضغط الزر!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("الألوان"))

    @commands.command(name="ايموجي")
    async def emoji_cmd(self, ctx):
        embed = discord.Embed(title="😀 لعبة الإيموجي", description="احزر الإيموجي واضغط الفوز!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("الإيموجي"))

    @commands.command(name="اكشف")
    async def reveal_cmd(self, ctx):
        embed = discord.Embed(title="🔍 لعبة اكشف", description="اكشف المطلوب واضغط الزر!", color=discord.Color.green())
        await ctx.send(embed=embed, view=QuickGameView("اكشف"))

async def setup(bot):
    await bot.add_cog(Games(bot))
