import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
import sqlite3
from datetime import date

# --- إعدادات مسار التخزين الدائم (Volume) لضمان عدم حذف البيانات ---
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "economy.json")
DB_PATH = os.path.join(DATA_DIR, "streaks.db")

INVENTORY_CHANNEL_ID = 1530408124958244975  # روم مقتنياتك

# --- أسعار وأتمتة المنتجات ---
ROLES_SHOP = {
    "ultra": {"name": "Ultra", "price": 75000, "role_id": 1530402702914490420},
    "premio": {"name": "Premio", "price": 55000, "role_id": 1530404996451930153},
    "prime": {"name": "Prime", "price": 45000, "role_id": 1530398293732102286},
    "plus": {"name": "Plus", "price": 25000, "role_id": 1530397307206631605},
    "basic": {"name": "Basic", "price": 10000, "role_id": 1530396937587523595}
}

TITLES_SHOP = {
    "king": {"name": "King", "price": 60000, "role_id": 1530407131507986554},
    "queen": {"name": "Queen", "price": 60000, "role_id": 1530407411335172188}
}

NEEDS_SHOP = {
    "shield": {"name": "درع حماية الستريك", "price": 500, "max_daily": 2},
    "common_box": {"name": "📦 صندوق شائع", "price": 2000, "is_box": True},
    "uncommon_box": {"name": "📦 صندوق غير شائع", "price": 7500, "is_box": True},
    "rare_box": {"name": "📦 صندوق نادر", "price": 20000, "is_box": True},
    "epic_box": {"name": "📦 صندوق إيبك", "price": 50000, "is_box": True},
    "mythic_box": {"name": "📦 صندوق ميثك", "price": 150000, "is_box": True}
}

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user_coins(user_id):
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        return 0
    user_data = data[user_id]
    if isinstance(user_data, int):
        return user_data
    return user_data.get("coins", 0)

def deduct_user_coins(user_id, amount):
    data = load_data()
    user_id = str(user_id)
    if user_id in data:
        if isinstance(data[user_id], int):
            data[user_id] = {"coins": max(0, data[user_id] - amount)}
        else:
            data[user_id]["coins"] = max(0, data[user_id].get("coins", 0) - amount)
        save_data(data)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS streaks (
            user_id INTEGER,
            guild_id INTEGER,
            streak_count INTEGER,
            last_date TEXT,
            shields INTEGER DEFAULT 0,
            last_shield_date TEXT DEFAULT '',
            shield_bought_today INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_inventory (
            user_id INTEGER,
            guild_id INTEGER,
            item_key TEXT,
            item_name TEXT,
            item_type TEXT,
            quantity INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, guild_id, item_key)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- متجر الشراء ---
class PurchaseSelect(discord.ui.Select):
    def __init__(self, shop_type: str):
        self.shop_type = shop_type
        if shop_type == "roles":
            items = ROLES_SHOP
        elif shop_type == "titles":
            items = TITLES_SHOP
        else:
            items = NEEDS_SHOP
        
        options = []
        for key, item in items.items():
            desc = f"السعر: {item['price']:,} كوينز"
            options.append(discord.SelectOption(label=item["name"], description=desc, value=key))
        super().__init__(placeholder="اختر الغرض الذي تريد شراءه...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        item_key = self.values[0]
        
        if self.shop_type == "roles":
            item = ROLES_SHOP[item_key]
        elif self.shop_type == "titles":
            item = TITLES_SHOP[item_key]
        else:
            item = NEEDS_SHOP[item_key]
        
        user_coins = get_user_coins(interaction.user.id)
        price = item["price"]

        if user_coins < price:
            await interaction.response.send_message(f"❌ ليس لديك رصيد كافٍ! رصيدك: **{user_coins:,} كوينز**.", ephemeral=True)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        today = str(date.today())
        
        # إذا كان شراء درع، يذهب مباشرة للستريك وليس الحقيبة
        if self.shop_type == "needs" and item_key == "shield":
            cursor.execute("SELECT shield_bought_today, last_shield_date FROM streaks WHERE user_id = ? AND guild_id = ?", (interaction.user.id, interaction.guild.id))
            res = cursor.fetchone()
            bought_today = res[0] if res and res[1] == today else 0
            if bought_today >= item.get("max_daily", 2):
                conn.close()
                await interaction.response.send_message("❌ لقد وصلت للحد الأقصى اليومي لشراء الدروع!", ephemeral=True)
                return
            
            new_bought = bought_today + 1
            if not res:
                cursor.execute("INSERT INTO streaks (user_id, guild_id, streak_count, last_date, shields, last_shield_date, shield_bought_today) VALUES (?, ?, 0, '', 1, ?, ?)", (interaction.user.id, interaction.guild.id, today, new_bought))
            else:
                cursor.execute("UPDATE streaks SET shields = shields + 1, last_shield_date = ?, shield_bought_today = ? WHERE user_id = ? AND guild_id = ?", (today, new_bought, interaction.user.id, interaction.guild.id))
            conn.commit()
            conn.close()
            deduct_user_coins(interaction.user.id, price)
            await interaction.response.send_message("🛡️ تم شراء الدرع وإضافته إلى الستريك الخاص بك بنجاح!", ephemeral=True)
            return

        # خصم الكوينز وإرسال الصناديق أو المنتجات العادية للحقيبة
        deduct_user_coins(interaction.user.id, price)

        cursor.execute("SELECT quantity FROM user_inventory WHERE user_id = ? AND guild_id = ? AND item_key = ?", (interaction.user.id, interaction.guild.id, item_key))
        inv_row = cursor.fetchone()

        if inv_row:
            cursor.execute("UPDATE user_inventory SET quantity = quantity + 1 WHERE user_id = ? AND guild_id = ? AND item_key = ?", (interaction.user.id, interaction.guild.id, item_key))
        else:
            cursor.execute("INSERT INTO user_inventory (user_id, guild_id, item_key, item_name, item_type, quantity) VALUES (?, ?, ?, ?, ?, 1)", (interaction.user.id, interaction.guild.id, item_key, item["name"], self.shop_type))

        conn.commit()
        conn.close()

        await interaction.response.send_message(f"يلا روح طلبك وصل في روم <#{INVENTORY_CHANNEL_ID}>", ephemeral=False)

class PurchaseView(discord.ui.View):
    def __init__(self, shop_type: str):
        super().__init__(timeout=None)
        self.add_item(PurchaseSelect(shop_type))

    @discord.ui.button(label="قفل المتجر", style=discord.ButtonStyle.danger, custom_id="close_store_button")
    async def close_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 جاري قفل المتجر...", ephemeral=True)
        await asyncio.sleep(2)
        try:
            await interaction.channel.delete()
        except:
            pass

class StoreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="افتح متجر الرتب", style=discord.ButtonStyle.primary, custom_id="roles_store")
    async def roles_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_store_ticket(interaction, "متجر-الرتب", "roles")

    @discord.ui.button(label="افتح متجر الألقاب", style=discord.ButtonStyle.success, custom_id="titles_store")
    async def titles_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_store_ticket(interaction, "متجر-الألقاب", "titles")

    @discord.ui.button(label="إحتياجات الأعضاء", style=discord.ButtonStyle.secondary, custom_id="needs_store")
    async def needs_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_store_ticket(interaction, "إحتياجات-الأعضاء", "needs")

    async def create_store_ticket(self, interaction: discord.Interaction, store_name: str, shop_type: str):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        user = interaction.user
        base_channel = guild.get_channel(INVENTORY_CHANNEL_ID)
        category = base_channel.category if base_channel else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        channel = await guild.create_text_channel(name=store_name, category=category, overwrites=overwrites)
        await interaction.followup.send(f"تم فتح متجرك بنجاح: {channel.mention}", ephemeral=True)
        
        if shop_type == "needs":
            desc = (
                f"أهلاً بك يا {user.mention} في قسم **إحتياجات الأعضاء والصناديق**!\n\n"
                "🛡️ **درع حماية الستريك** - السعر: 500 كوينز\n"
                "📦 **صندوق شائع** - السعر: 2,000 كوينز\n"
                "📦 **صندوق غير شائع** - السعر: 7,500 كوينز\n"
                "📦 **صندوق نادر** - السعر: 20,000 كوينز\n"
                "📦 **صندوق إيبك** - السعر: 50,000 كوينز\n"
                "📦 **صندوق ميثك** - السعر: 150,000 كوينز\n\n"
                "👇 **اختر من القائمة أدناه للشراء:**"
            )
        else:
            desc = f"أهلاً بك يا {user.mention} في المتجر! اختر العنصر للشراء:"

        await channel.send(desc, view=PurchaseView(shop_type))


# --- نظام لوحة الحقيبة الدائمة (بدون وقت انتهاء) ---
class InventoryPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح الحقيبة", style=discord.ButtonStyle.green, custom_id="persistent_open_inventory")
    async def open_inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📦 اختر القسم الذي تريد عرضه من حقيبتك:", view=InventoryCategoriesView(), ephemeral=True)

class InventoryCategoriesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="الألقاب", style=discord.ButtonStyle.primary, custom_id="inv_cat_titles")
    async def titles_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_item_selector(interaction, "titles")

    @discord.ui.button(label="الرتب", style=discord.ButtonStyle.primary, custom_id="inv_cat_roles")
    async def roles_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_item_selector(interaction, "roles")

    @discord.ui.button(label="مقتنياتك", style=discord.ButtonStyle.secondary, custom_id="inv_cat_belongings")
    async def belongings_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_belongings_selector(interaction)

    async def send_item_selector(self, interaction: discord.Interaction, item_type: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT item_key, item_name, quantity FROM user_inventory WHERE user_id = ? AND guild_id = ? AND item_type = ?", (interaction.user.id, interaction.guild.id, item_type))
        items = cursor.fetchall()
        conn.close()

        if not items:
            await interaction.response.send_message(f"❌ ليس لديك أي {item_type} في حقيبتك.", ephemeral=True)
            return

        view = discord.ui.View(timeout=None)
        select = discord.ui.Select(placeholder=f"اختر {item_type}...", min_values=1, max_values=1)
        for key, name, qty in items:
            select.add_option(label=name, description=f"الكمية: {qty}", value=key)

        async def select_callback(inter: discord.Interaction):
            selected_key = select.values[0]
            await inter.response.send_message("ماذا تفعل بهذا العنصر؟", view=RoleTitleActionView(selected_key, item_type), ephemeral=True)

        select.callback = select_callback
        view.add_item(select)
        await interaction.response.send_message("اختر العنصر للتفاعل معه:", view=view, ephemeral=True)

    async def send_belongings_selector(self, interaction: discord.Interaction):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # استبعاد الدرع لأنه مخصص للستريك فقط
        cursor.execute("SELECT item_key, item_name, quantity FROM user_inventory WHERE user_id = ? AND guild_id = ? AND item_type = 'needs' AND item_key != 'shield'", (interaction.user.id, interaction.guild.id))
        items = cursor.fetchall()
        conn.close()

        if not items:
            await interaction.response.send_message("❌ ليس لديك أي مقتنيات أو صناديق في حقيبتك.", ephemeral=True)
            return

        view = discord.ui.View(timeout=None)
        select = discord.ui.Select(placeholder="اختر مقتنى أو صندوق...", min_values=1, max_values=1)
        for key, name, qty in items:
            select.add_option(label=name, description=f"الكمية: {qty}", value=key)

        async def select_callback(inter: discord.Interaction):
            selected_key = select.values[0]
            if "box" in selected_key:
                await inter.response.send_message("🎁 صندوق محظوظ:", view=BoxActionView(selected_key), ephemeral=True)
            else:
                await inter.response.send_message("هذا عنصر عادي.", ephemeral=True)

        select.callback = select_callback
        view.add_item(select)
        await interaction.response.send_message("اختر من مقتنياتك:", view=view, ephemeral=True)

# --- أزرار استخدام أو إزالة الرتبة واللقب (بدون حذف من الحقيبة) ---
class RoleTitleActionView(discord.ui.View):
    def __init__(self, item_key: str, item_type: str):
        super().__init__(timeout=None)
        self.item_key = item_key
        self.item_type = item_type

    @discord.ui.button(label="استخدام", style=discord.ButtonStyle.green, custom_id="action_use_item")
    async def use_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = ROLES_SHOP.get(self.item_key, {}).get("role_id") or TITLES_SHOP.get(self.item_key, {}).get("role_id")
        if role_id:
            role = interaction.guild.get_role(role_id)
            if role:
                try:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message("✅ تم تفعيل العنصر ومنحك الرتبة/اللقب بنجاح!", ephemeral=True)
                    return
                except:
                    pass
        await interaction.response.send_message("❌ حدث خطأ أثناء منح الرتبة (تأكد من صلاحيات البوت والـ Role ID).", ephemeral=True)

    @discord.ui.button(label="إزالة", style=discord.ButtonStyle.danger, custom_id="action_remove_item")
    async def remove_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = ROLES_SHOP.get(self.item_key, {}).get("role_id") or TITLES_SHOP.get(self.item_key, {}).get("role_id")
        if role_id:
            role = interaction.guild.get_role(role_id)
            if role:
                try:
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message("🗑️ تم إزالة الرتبة/اللقب منك، وما زال محفوظاً في حقيبتك!", ephemeral=True)
                    return
                except:
                    pass
        await interaction.response.send_message("❌ حدث خطأ أو لم تكن تمتلك الرتبة فعلياً.", ephemeral=True)

# --- زر فتح الصندوق ---
class BoxActionView(discord.ui.View):
    def __init__(self, box_key: str):
        super().__init__(timeout=None)
        self.box_key = box_key

    @discord.ui.button(label="فتح الصندوق", style=discord.ButtonStyle.blurple, custom_id="action_open_box")
    async def open_box(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM user_inventory WHERE user_id = ? AND guild_id = ? AND item_key = ?", (interaction.user.id, interaction.guild.id, self.box_key))
        row = cursor.fetchone()

        if not row or row[0] <= 0:
            conn.close()
            await interaction.response.send_message("❌ ليس لديك هذا الصندوق في حقيبتك!", ephemeral=True)
            return

        new_qty = row[0] - 1
        if new_qty > 0:
            cursor.execute("UPDATE user_inventory SET quantity = ? WHERE user_id = ? AND guild_id = ? AND item_key = ?", (new_qty, interaction.user.id, interaction.guild.id, self.box_key))
        else:
            cursor.execute("DELETE FROM user_inventory WHERE user_id = ? AND guild_id = ? AND item_key = ?", (interaction.user.id, interaction.guild.id, self.box_key))
        conn.commit()
        conn.close()

        # يمكنك تعديل الجائزة هنا حسب رغبتك
        await interaction.response.send_message("🎉 مبروك! فتحت الصندوق وحصلت على جوائز مميزة (تم خصم الصندوق من حقيبتك).", ephemeral=True)


# --- الكوج الرئيسي ---
class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="store", description="إرسال لوحة متجر السيرفر")
    @app_commands.default_permissions(administrator=True)
    async def store_panel(self, interaction: discord.Interaction):
        await interaction.response.send_message("**مرحباً بك في متجر السيرفر!** اختر المتجر:", view=StoreView())

    @app_commands.command(name="inventory_panel", description="إرسال لوحة فتح الحقيبة الدائمة في الروم")
    @app_commands.default_permissions(administrator=True)
    async def inventory_panel_command(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "🎒 **حقيبة مقتنياتك الشخصية**\nاضغط على الزر أدناه لفتح حقيبتك وإدارة مقتنياتك والصناديق والرتب والألقاب:",
            view=InventoryPanelView()
        )

async def setup(bot):
    await bot.add_cog(Shop(bot))
