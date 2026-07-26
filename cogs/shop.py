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
DB_PATH = "streaks.db"  # قاعدة بيانات الستريك المشتركة

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
    "shield": {"name": "درع حماية الستريك", "price": 500, "max_daily": 2}
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

# --- قائمة الشراء التفاعلية داخل التذكرة ---
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
                desc += " (حد أقصى درعين يومياً)"
            options.append(
                discord.SelectOption(
                    label=item["name"],
                    description=desc,
                    value=key
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

        # فحص الحد اليومي للدروع في جدول قاعدة البيانات المشتركة
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        today = str(date.today())
        
        if self.shop_type == "needs":
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
                    bought_today = 0 # تصفير العداد إذا بدأ يوم جديد

            if bought_today >= item["max_daily"]:
                conn.close()
                await interaction.response.send_message(
                    f"❌ لقد وصلت إلى الحد الأقصى لشراء الدروع اليوم (**{item['max_daily']} دروع** كحد أقصى يومياً). عُد غداً!",
                    ephemeral=True
                )
                return

        # خصم الكوينز
        deduct_user_coins(interaction.user.id, price)

        role_given = False
        msg = f"🎉 مبروك! لقد اشتريت **{item['name']}** بنجاح مقابل **{price:,} كوينز**."

        if self.shop_type in ["roles", "titles"]:
            if item["role_id"] != 0:
                role = interaction.guild.get_role(item["role_id"])
                if role:
                    try:
                        await interaction.user.add_roles(role)
                        role_given = True
                    except Exception as e:
                        print(f"❌ خطأ في إعطاء الرتبة: {e}")
            if role_given:
                msg += "\n✨ تم منحك الرتبة تلقائياً وسيتم حذف التذكرة..."
            else:
                msg += "\n📌 تم خصم المبلغ، وسيتم حذف هذه التذكرة تلقائياً..."
        else:
            # إضافة درع وتحديث سجل الشراء اليومي في قاعدة بيانات الستريك
            if result is None:
                cursor.execute(
                    "INSERT INTO streaks (user_id, guild_id, streak_count, last_date, shields, last_shield_date, shield_bought_today) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (interaction.user.id, interaction.guild.id, 0, "", 1, today, 1)
                )
            else:
                new_shields = result[2] + 1
                new_bought = (bought_today + 1)
                cursor.execute(
                    "UPDATE streaks SET shields = ?, last_shield_date = ?, shield_bought_today = ? WHERE user_id = ? AND guild_id = ?",
                    (new_shields, today, new_bought, interaction.user.id, interaction.guild.id)
                )
            conn.commit()
            msg += "\n🛡️ تمت إضافة الدرع إلى ملف الستريك الخاص بك بنجاح وسيتم حذف التذكرة..."

        conn.close()

        # الرد على المستخدم
        await interaction.response.send_message(msg, ephemeral=False)

        # الانتظار لمدة 5 ثوانٍ ثم حذف روم التذكرة تلقائياً
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"❌ خطأ في حذف روم التذكرة: {e}")

class PurchaseView(discord.ui.View):
    def __init__(self, shop_type: str):
        super().__init__(timeout=None)
        self.add_item(PurchaseSelect(shop_type))

class StoreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # timeout=None لتبقى الأزرار تعمل للأبد

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
        custom_id="needs_store"
    )
    async def needs_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_store_ticket(interaction, "إحتياجات-الأعضاء", "needs")

    async def create_store_ticket(self, interaction: discord.Interaction, store_name: str, shop_type: str):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        user = interaction.user

        # آي دي الروم المخصص لاستخراج الفئة تلقائياً
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

        await interaction.followup.send(f"تم فتح تذكرتك بنجاح: {channel.mention}", ephemeral=True)

        view = PurchaseView(shop_type)

        if shop_type == "roles":
            await channel.send(
                f"أهلاً بك يا {user.mention} في **متجر الرتب**!\n"
                "إليك قائمة الرتب المتاحة للشراء:\n\n"
                "🔥 **Ultra** - السعر: 75,000 كوينز\n"
                "💎 **Premio** - السعر: 55,000 كوينز\n"
                "🔹 **Prime** - السعر: 45,000 كوينز\n"
                "🌟 **Plus** - السعر: 25,000 كوينز\n"
                "⭐ **Basic** - السعر: 10,000 كوينز\n\n"
                "👇 **يمكنك الشراء مباشرة عبر القائمة أدناه:**",
                view=view
            )
        elif shop_type == "titles":
            await channel.send(
                f"أهلاً بك يا {user.mention} في **متجر الألقاب**!\n"
                "إليك قائمة الألقاب المتاحة للشراء:\n\n"
                "👑 **King** - السعر: 60,000 كوينز\n"
                "👑 **Queen** - السعر: 60,000 كوينز\n\n"
                "👇 **يمكنك الشراء مباشرة عبر القائمة أدناه:**",
                view=view
            )
        else:
            await channel.send(
                f"أهلاً بك يا {user.mention} في قسم **إحتياجات الأعضاء**!\n"
                "إليك المنتجات المتاحة:\n\n"
                "🛡️ **درع حماية الستريك** - السعر: 500 كوينز *(حد أقصى درعين يومياً)*\n\n"
                "👇 **يمكنك الشراء مباشرة عبر القائمة أدناه:**",
                view=view
            )

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="store", description="إرسال لوحة متجر السيرفر")
    @app_commands.default_permissions(administrator=True)
    async def store_panel(self, interaction: discord.Interaction):
        view = StoreView()
        await interaction.response.send_message(
            "**مرحباً بك في متجر السيرفر!**\nاختر المتجر الذي ترغب في فتحه من الأزرار بالأسفل:", 
            view=view
        )

async def setup(bot):
    await bot.add_cog(Shop(bot))
