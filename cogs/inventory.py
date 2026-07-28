import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random
from datetime import date

DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")

# نسب الرتب لكل صندوق
CHEST_RATES = {
    "الشائع": {"Tempest": 2.0, "Nebula": 0.5, "Obsidian": 0.1},
    "غير الشائع": {"Tempest": 7.0, "Nebula": 2.0, "Obsidian": 0.5},
    "النادر": {"Tempest": 15.0, "Nebula": 5.0, "Obsidian": 1.0},
    "الإيبك": {"Tempest": 25.0, "Nebula": 10.0, "Obsidian": 3.0},
    "الميثك": {"Tempest": 40.0, "Nebula": 20.0, "Obsidian": 5.0}
}

def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    try:
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_inventory(data):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_user_inventory(user_id):
    data = load_inventory()
    uid = str(user_id)
    today = str(date.today())
    
    if uid not in data:
        data[uid] = {
            "boxes": {"الشائع": 0, "غير الشائع": 0, "النادر": 0, "الإيبك": 0, "الميثك": 0},
            "ranks": [],
            "titles": [],
            "active_rank": None,
            "active_title": None,
            "coins": 0,
            "xp": 0,
            "daily_chests": {"date": today, "الشائع": False, "غير الشائع": False, "النادر": False, "الإيبك": False, "الميثك": False}
        }
        save_inventory(data)
    else:
        user_data = data[uid]
        if "daily_chests" not in user_data or user_data["daily_chests"].get("date") != today:
            user_data["daily_chests"] = {"date": today, "الشائع": False, "غير الشائع": False, "النادر": False, "الإيبك": False, "الميثك": False}
            save_inventory(data)
            
    return data[uid]

def update_user_inventory(user_id, user_data):
    data = load_inventory()
    data[str(user_id)] = user_data
    save_inventory(data)

def add_box_to_inventory(user_id, chest_name, count=1):
    user_data = get_user_inventory(user_id)
    if "boxes" not in user_data:
        user_data["boxes"] = {"الشائع": 0, "غير الشائع": 0, "النادر": 0, "الإيبك": 0, "الميثك": 0}
    user_data["boxes"][chest_name] = user_data["boxes"].get(chest_name, 0) + count
    update_user_inventory(user_id, user_data)

def add_rank_to_inventory(user_id, rank_name):
    user_data = get_user_inventory(user_id)
    if "ranks" not in user_data:
        user_data["ranks"] = []
    if rank_name not in user_data["ranks"]:
        user_data["ranks"].append(rank_name)
        update_user_inventory(user_id, user_data)

def add_title_to_inventory(user_id, title_name):
    user_data = get_user_inventory(user_id)
    if "titles" not in user_data:
        user_data["titles"] = []
    if title_name not in user_data["titles"]:
        user_data["titles"].append(title_name)
        update_user_inventory(user_id, user_data)

# --- منطق فتح الصناديق ---
async def open_chest_logic(interaction: discord.Interaction, chest_name: str):
    user_id = interaction.user.id
    user_data = get_user_inventory(user_id)
    
    if user_data["boxes"].get(chest_name, 0) <= 0:
        await interaction.response.send_message(f"❌ توكل بس! ما معك صندوق **{chest_name}** 😂", ephemeral=True)
        return

    user_data["boxes"][chest_name] -= 1
    
    roll = random.uniform(0, 100)
    rates = CHEST_RATES.get(chest_name, {})
    
    reward_text = ""
    current_prob = 0.0
    matched_rank = None
    
    for rank_name, chance in rates.items():
        current_prob += chance
        if roll <= current_prob:
            matched_rank = rank_name
            break

    if matched_rank:
        if matched_rank in user_data.get("ranks", []):
            reward_text = f"🏷️ الرتبة: **{matched_rank}**\n⚠️ توكل الرتبة معك يلا روح 😂 *(كنت تمتلكها مسبقاً ولم تحصل على تعويض)*"
        else:
            user_data["ranks"].append(matched_rank)
            reward_text = f"🎉 مبروك! حصلت على رتبة جديدة: **{matched_rank}** 🏷️"
    else:
        reward_type = random.choice(["coins", "xp"])
        if reward_type == "coins":
            multiplier = {"الشائع": 1, "غير الشائع": 3, "النادر": 8, "الإيبك": 20, "الميثك": 50}.get(chest_name, 1)
            won_coins = random.randint(500, 2000) * multiplier
            user_data["coins"] = user_data.get("coins", 0) + won_coins
            reward_text = f"💰 كوينز: **+{won_coins:,}** كوينز"
        else:
            multiplier = {"الشائع": 1, "غير الشائع": 2, "النادر": 5, "الإيبك": 12, "الميثك": 30}.get(chest_name, 1)
            won_xp = random.randint(100, 500) * multiplier
            user_data["xp"] = user_data.get("xp", 0) + won_xp
            reward_text = f"⭐ نقاط خبرة XP: **+{won_xp:,}** XP"

    update_user_inventory(user_id, user_data)

    embed = discord.Embed(
        title=f"🎁 نتيجة فتح صندوق [{chest_name}]",
        description=f"لقد قمت بفتح صندوق **{chest_name}** بنجاح!\n\n**الجائزة المحصول عليها:**\n{reward_text}",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed, ephemeral=False)

# --- إدارة الصناديق ---
class ChestSelect(discord.ui.Select):
    def __init__(self, user_boxes):
        options = []
        for chest_name, count in user_boxes.items():
            options.append(
                discord.SelectOption(
                    label=f"صندوق {chest_name}",
                    description=f"المتوفر: {count}",
                    value=chest_name,
                    emoji="📦"
                )
            )
        super().__init__(placeholder="اختر الصندوق الذي تريد فتحه...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_chest = self.values[0]
        await open_chest_logic(interaction, selected_chest)

class ChestsOpenView(discord.ui.View):
    def __init__(self, user_boxes):
        super().__init__(timeout=180)
        self.add_item(ChestSelect(user_boxes))

    @discord.ui.button(label="رجوع للصناديق", style=discord.ButtonStyle.secondary, custom_id="back_to_boxes")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data = get_user_inventory(interaction.user.id)
        user_boxes = user_data.get("boxes", {})
        box_text = "\n".join([f"📦 **{name}**: {count}x" for name, count in user_boxes.items()])
        await interaction.response.edit_message(content=f"🎁 **صناديقك:**\n\n{box_text}", view=self)

# --- واجهة إدارة الرتب (تفعيل أو إلغاء تفعيل دون حذف من الحقيبة) ---
class RanksManageView(discord.ui.View):
    def __init__(self, user_id, ranks):
        super().__init__(timeout=180)
        self.user_id = user_id
        options = [discord.SelectOption(label=r, value=r, emoji="🏷️") for r in ranks[:25]]
        self.add_item(RanksSelect(options, user_id))

    @discord.ui.button(label="إزالة / إلغاء تفعيل الرتبة الحالية", style=discord.ButtonStyle.danger, custom_id="unequip_rank", emoji="🛑")
    async def unequip_rank_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا ليس انفنتوري الخاص بك!", ephemeral=True)
            return
        
        user_data = get_user_inventory(self.user_id)
        active_rank = user_data.get("active_rank")
        
        if not active_rank:
            await interaction.response.send_message("❌ ليس لديك أي رتبة مفعلة حالياً!", ephemeral=True)
            return

        role = discord.utils.get(interaction.guild.roles, name=active_rank)
        if role and role in interaction.user.roles:
            try:
                await interaction.user.remove_roles(role)
            except Exception:
                pass

        user_data["active_rank"] = None
        update_user_inventory(self.user_id, user_data)
        await interaction.response.send_message(f"🛑 تم إزالة (إلغاء تفعيل) رتبة **{active_rank}** من عليك بنجاح! **ولا زالت محفوظة في حقيبتك**.", ephemeral=True)

class RanksSelect(discord.ui.Select):
    def __init__(self, options, user_id):
        self.user_id = user_id
        super().__init__(placeholder="اختر رتبة لتفعيلها على ديسكورد...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_rank = self.values[0]
        user_data = get_user_inventory(self.user_id)
        
        role = discord.utils.get(interaction.guild.roles, name=selected_rank)
        if not role:
            await interaction.response.send_message(f"❌ الرتبة **{selected_rank}** غير موجودة في رتب السيرفر حالياً!", ephemeral=True)
            return
        
        try:
            await interaction.user.add_roles(role)
        except Exception:
            await interaction.response.send_message("❌ حدث خطأ أثناء منحك الرتبة، تأكد من صلاحيات البوت.", ephemeral=True)
            return

        user_data["active_rank"] = selected_rank
        update_user_inventory(self.user_id, user_data)
        await interaction.response.send_message(f"✨ تم تفعيل رتبة **{selected_rank}** بنجاح! *(وهي محفوظة دائماً في حقيبتك)*", ephemeral=True)

# --- واجهة الانفنتوري الرئيسية للأزرار ---
class InventoryOptionsView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id

    @discord.ui.button(label="ألقابك النصية", style=discord.ButtonStyle.secondary, custom_id="inv_titles_btn", emoji="🪪")
    async def titles_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا ليس انفنتوري الخاص بك!", ephemeral=True)
            return
        user_data = get_user_inventory(self.user_id)
        titles = user_data.get("titles", [])
        if not titles:
            await interaction.response.send_message("❌ لا تمتلك أي ألقاب في حقيبتك!", ephemeral=True)
            return
        titles_text = "\n".join([f"• {t}" for t in titles])
        await interaction.response.send_message(f"🪪 **ألقابك النصية المحفوظة في الحقيبة:**\n{titles_text}", ephemeral=True)

    @discord.ui.button(label="رتبك", style=discord.ButtonStyle.secondary, custom_id="inv_ranks_btn", emoji="🏷️")
    async def ranks_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا ليس انفنتوري الخاص بك!", ephemeral=True)
            return
        user_data = get_user_inventory(self.user_id)
        ranks = user_data.get("ranks", [])
        if not ranks:
            await interaction.response.send_message("❌ لا تمتلك أي رتب في حقيبتك!", ephemeral=True)
            return
        
        view = RanksManageView(self.user_id, ranks)
        ranks_text = "\n".join([f"• {r}" for r in ranks])
        active = user_data.get("active_rank", "لا يوجد")
        await interaction.response.send_message(f"🏷️ **رتبك في الحقيبة:**\n{ranks_text}\n\n📌 الرتبة المفعلة حالياً: **{active}**\nاختر من القائمة لتفعيل الرتبة، أو اضغط زر الإزالة لإلغاء تفعيلها مع بقائها بالحقيبة:", view=view, ephemeral=True)

    @discord.ui.button(label="صناديقي", style=discord.ButtonStyle.primary, custom_id="inv_boxes_btn", emoji="🎁")
    async def boxes_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا ليس انفنتوري الخاص بك!", ephemeral=True)
            return
        user_data = get_user_inventory(self.user_id)
        user_boxes = user_data.get("boxes", {})
        
        box_text = "\n".join([f"📦 **{name}** ×{count}" for name, count in user_boxes.items()])
        view = ChestsOpenView(user_boxes)
        await interaction.response.send_message(f"🎁 **صناديقك:**\n\n{box_text}", view=view, ephemeral=True)

# --- اللوحة الدائمة التي لا تنتهي (لإرسالها عبر أمر الإدارة) ---
class InventorySetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # timeout=None لكي لا تنتهي أبداً

    @discord.ui.button(label="📂 فتح الانفنتوري", style=discord.ButtonStyle.primary, custom_id="persistent_inventory_button")
    async def open_inventory_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data = get_user_inventory(interaction.user.id)
        embed = discord.Embed(
            title="🎒 نظام الحقيبة",
            description=f"أهلاً بك يا {interaction.user.mention} في حقيبتك الخاصة ✨\n\nمن هنا يمكنك إدارة ممتلكاتك:\n\n🪪 ألقابك النصية\n🏷️ رتبك\n🎁 صناديقي",
            color=discord.Color.blue()
        )
        view = InventoryOptionsView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class InventoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # أمر إداري لإرسال اللوحة الدائمة في الروم الحالي (لا تنتهي أبداً)
    @app_commands.command(name="setup_inventory", description="إرسال لوحة الحقيبة الدائمة للسيرفر")
    @app_commands.default_permissions(administrator=True)
    async def setup_inventory(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎒 لوحة الحقيبة (Inventory)",
            description="اضغط على الزر بالأسفل لفتح حقيبتك وإدارة رتبك وألقابك وصناديقك بكل سهولة ✨",
            color=discord.Color.blue()
        )
        view = InventorySetupView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ تم إرسال لوحة الحقيبة الدائمة في الروم بنجاح!", ephemeral=True)

    @app_commands.command(name="inventory", description="فتح حقيبتك الشخصية")
    async def inventory_cmd(self, interaction: discord.Interaction):
        user_data = get_user_inventory(interaction.user.id)
        embed = discord.Embed(
            title="🎒 نظام الحقيبة",
            description=f"أهلاً بك يا {interaction.user.mention} في حقيبتك الخاصة ✨\n\nمن هنا يمكنك إدارة ممتلكاتك:\n\n🪪 ألقابك النصية\n🏷️ رتبك\n🎁 صناديقي",
            color=discord.Color.blue()
        )
        view = InventoryOptionsView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(InventoryCog(bot))
