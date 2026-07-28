import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
import sqlite3
from datetime import date

from cogs.inventory import add_title_to_inventory, add_rank_to_inventory, add_box_to_inventory

DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "economy.json")
DB_PATH = os.path.join(DATA_DIR, "streaks.db")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")

ROLES_SHOP = {
    "ultra": {"name": "Ultra", "price": 75000},
    "premio": {"name": "Premio", "price": 55000},
    "prime": {"name": "Prime", "price": 45000},
    "plus": {"name": "Plus", "price": 25000},
    "basic": {"name": "Basic", "price": 10000}
}

TITLES_SHOP = {
    "king": {"name": "King", "price": 60000},
    "queen": {"name": "Queen", "price": 60000}
}

NEEDS_SHOP = {
    "shield": {"name": "درع حماية الستريك", "price": 500, "type": "shield", "max_daily": 2},
    "mythic_box": {"name": "الميثك", "price": 150000, "type": "chest", "chest_key": "الميثك"},
    "epic_box": {"name": "الإيبك", "price": 50000, "type": "chest", "chest_key": "الإيبك"},
    "rare_box": {"name": "النادر", "price": 20000, "type": "chest", "chest_key": "النادر"},
    "uncommon_box": {"name": "غير الشائع", "price": 7500, "type": "chest", "chest_key": "غير الشائع"},
    "common_box": {"name": "الشائع", "price": 2000, "type": "chest", "chest_key": "الشائع"}
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

def load_inventory_json():
    if not os.path.exists(INVENTORY_FILE):
        return {}
    try:
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_inventory_json(data):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
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
            if shop_type == "needs":
                if item.get("type") == "shield":
                    desc += " (حد أقصى درعين يومياً)"
                else:
                    desc += " (صندوق واحد يومياً)"
            
            emoji = "📦" if shop_type == "needs" and item.get("type") == "chest" else None

            options.append(
                discord.SelectOption(
                    label=item["name"],
                    description=desc,
                    value=key,
                    emoji=emoji
                )
            )
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
            await interaction.response.send_message(
                f"❌ ليس لديك رصيد كافٍ! رصيدك الحالي: **{user_coins:,} كوينز** وأنت بحاجة إلى **{price:,} كوينز** لشراء {item['name']}.", 
                ephemeral=True
            )
            return

        today = str(date.today())

        if self.shop_type == "needs":
            if item.get("type") == "chest":
                inv_data = load_inventory_json()
                uid = str(interaction.user.id)
                if uid not in inv_data:
                    inv_data[uid] = {"boxes": {}, "daily_chests": {}}
                
                user_inv = inv_data[uid]
                if "daily_chests" not in user_inv or user_inv["daily_chests"].get("date") != today:
                    user_inv["daily_chests"] = {"date": today, "الشائع": False, "غير الشائع": False, "النادر": False, "الإيبك": False, "الميثك": False}
                
                chest_k = item["chest_key"]
                if user_inv["daily_chests"].get(chest_k, False):
                    await interaction.response.send_message(
                        f"❌ لقد وصلت إلى الحد الأقصى لشراء صندوق **({item['name']})** اليوم (صندوق واحد يومياً). عُد غداً!",
                        ephemeral=True
                    )
                    return
                
                deduct_user_coins(interaction.user.id, price)
                user_inv["daily_chests"][chest_k] = True
                save_inventory_json(inv_data)
                
                add_box_to_inventory(interaction.user.id, item["name"], 1)
                
                await interaction.response.send_message(
                    f"🎉 مبروك! لقد اشتريت صندوق **{item['name']}** بنجاح مقابل **{price:,} كوينز** وتمت إضافته إلى حقيبتك 📦.",
                    ephemeral=False
                )
                return

            elif item.get("type") == "shield":
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
                conn.commit()

                cursor.execute(
                    "SELECT streak_count, last_date, shields, last_shield_date, shield_bought_today FROM streaks WHERE user_id = ? AND guild_id = ?",
                    (interaction.user.id, interaction.guild.id)
                )
                result = cursor.fetchone()
                bought_today = 0
                if result:
                    last_s_date = result[3]
                    bought_today = result[4] if result[4] is not None else 0
                    if last_s_date != today:
                        bought_today = 0

                if bought_today >= item["max_daily"]:
                    conn.close()
                    await interaction.response.send_message(
                        f"❌ لقد وصلت إلى الحد الأقصى لشراء الدروع اليوم (**{item['max_daily']} دروع** كحد أقصى يومياً). عُد غداً!",
                        ephemeral=True
                    )
                    return

                deduct_user_coins(interaction.user.id, price)

                if result is None:
                    cursor.execute(
                        "INSERT INTO streaks (user_id, guild_id, streak_count, last_date, shields, last_shield_date, shield_bought_today) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (interaction.user.id, interaction.guild.id, 0, "", 1, today, 1)
                    )
                else:
                    new_shields = result[2] + 1
                    new_bought = bought_today + 1
                    cursor.execute(
                        "UPDATE streaks SET shields = ?, last_shield_date = ?, shield_bought_today = ? WHERE user_id = ? AND guild_id = ?",
                        (new_shields, today, new_bought, interaction.user.id, interaction.guild.id)
                    )
                conn.commit()
                conn.close()

                await interaction.response.send_message(
                    f"🎉 مبروك! لقد اشتريت **{item['name']}** بنجاح مقابل **{price:,} كوينز** وتمت إضافته إلى ملف الستريك الخاص بك 🛡️.",
                    ephemeral=False
                )
                return

        deduct_user_coins(interaction.user.id, price)
        msg = f"🎉 مبروك! لقد اشتريت **{item['name']}** بنجاح مقابل **{price:,} كوينز**."

        if self.shop_type == "roles":
            add_rank_to_inventory(interaction.user.id, item["name"])
            msg += "\n📌 تم إضافة الرتبة إلى حقيبتك بنجاح (يمكنك تفعيلها من الانفنتوري)."

        elif self.shop_type == "titles":
            add_title_to_inventory(interaction.user.id, item["name"])
            msg += "\n🪪 تمت إضافة اللقب إلى حقيبتك بنجاح (يمكنك تفعيله من الانفنتوري)."

        await interaction.response.send_message(msg, ephemeral=False)

class PurchaseView(discord.ui.View):
    def __init__(self, shop_type: str):
        super().__init__(timeout=None)
        self.add_item(PurchaseSelect(shop_type))

    @discord.ui.button(
        label="قفل المتجر", 
        style=discord.ButtonStyle.danger, 
        custom_id="close_store_button"
    )
    async def close_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 جاري قفل المتجر...", ephemeral=True)
        await asyncio.sleep(2)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"❌ خطأ في قفل روم المتجر: {e}")

class StoreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="افتح متجر الرتب", 
        style=discord.ButtonStyle.primary, 
        custom_id="roles_store"
    )
    async def roles_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_store_ticket(interaction, "متجر-الرتب", "roles")

    @discord.ui.button(
        label="افتح متجر الألقاب", 
        style=discord.ButtonStyle.success, 
        custom_id="titles_store"
    )
    async def titles_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_store_ticket(interaction, "متجر-الألقاب", "titles")

    @discord.ui.button(
        label="إحتياجات الأعضاء", 
        style=discord.ButtonStyle.secondary, 
        custom_id="needs_store",
        emoji="🛒"
    )
    async def needs_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_store_ticket(interaction, "إحتياجات-الأعضاء", "needs")

    async def create_store_ticket(self, interaction: discord.Interaction, store_name: str, shop_type: str):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        user = interaction.user

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
            name=store_name,
            category=category,
            overwrites=overwrites
        )

        await interaction.followup.send(f"تم فتح متجرك بنجاح: {channel.mention}", ephemeral=True)
        view = PurchaseView(shop_type)

        if shop_type == "roles":
            await channel.send(f"أهلاً بك يا {user.mention} في **متجر الرتب**!\nاختر الرتبة التي تريد إضافتها لحقيبتك:", view=view)
        elif shop_type == "titles":
            await channel.send(f"أهلاً بك يا {user.mention} في **متجر الألقاب**!\nاختر اللقب الذي تريد إضافته لحقيبتك:", view=view)
        else:
            await channel.send(f"أهلاً بك يا {user.mention} في **إحتياجات الأعضاء**!\nاختر ما ترغب بشرائه:", view=view)

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="store", description="إرسال لوحة متجر السيرفر")
    @app_commands.default_permissions(administrator=True)
    async def store_panel(self, interaction: discord.Interaction):
        view = StoreView()
        await interaction.response.send_message("**مرحباً بك في متجر السيرفر!**\nاختر المتجر الذي ترغب في فتحه من الأزرار بالأسفل:", view=view)

async def setup(bot):
    await bot.add_cog(Shop(bot))
