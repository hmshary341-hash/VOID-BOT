import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio

# --- إعدادات مسار التخزين الدائم (Volume) لضمان عدم حذف البيانات ---
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "economy.json")

# --- أسعار وأتمتة المنتجات ---
ROLES_SHOP = {
    "ultra": {"name": "Ultra", "price": 75000, "role_id": 0},  # ضع آي دي رتبة Ultra هنا
    "prime": {"name": "Prime", "price": 45000, "role_id": 0},  # ضع آي دي رتبة Prime هنا
    "plus": {"name": "Plus", "price": 25000, "role_id": 0},    # ضع آي دي رتبة Plus هنا
    "basic": {"name": "Basic", "price": 10000, "role_id": 0}   # ضع آي دي رتبة Basic هنا
}

TITLES_SHOP = {
    "king": {"name": "King", "price": 60000, "role_id": 0},    # ضع آي دي رتبة King هنا
    "queen": {"name": "Queen", "price": 60000, "role_id": 0}   # ضع آي دي رتبة Queen هنا
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
        items = ROLES_SHOP if shop_type == "roles" else TITLES_SHOP
        
        options = []
        for key, item in items.items():
            options.append(
                discord.SelectOption(
                    label=item["name"],
                    description=f"السعر: {item['price']:,} كوينز",
                    value=key
                )
            )
        super().__init__(placeholder="اختر الغرض الذي تريد شراءه...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        item_key = self.values[0]
        items_dict = ROLES_SHOP if self.shop_type == "roles" else TITLES_SHOP
        item = items_dict[item_key]
        
        user_coins = get_user_coins(interaction.user.id)
        price = item["price"]

        if user_coins < price:
            await interaction.response.send_message(
                f"❌ ليس لديك رصيد كافٍ! رصيدك الحالي: **{user_coins:,} كوينز** وأنت بحاجة إلى **{price:,} كوينز** لشراء {item['name']}.", 
                ephemeral=True
            )
            return

        # خصم الكوينز وحفظها في الفوليوم
        deduct_user_coins(interaction.user.id, price)

        # محاولة إعطاء الرتبة إن وجد آي دي لها
        role_given = False
        if item["role_id"] != 0:
            role = interaction.guild.get_role(item["role_id"])
            if role:
                try:
                    await interaction.user.add_roles(role)
                    role_given = True
                except Exception as e:
                    print(f"❌ خطأ في إعطاء الرتبة: {e}")

        msg = f"🎉 مبروك! لقد اشتريت **{item['name']}** بنجاح مقابل **{price:,} كوينز**."
        if role_given:
            msg += "\n✨ تم منحك الرتبة تلقائياً!"
        else:
            msg += "\n📌 تم خصم المبلغ، وسيتم حذف هذه التذكرة تلقائياً..."

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
        await self.create_store_ticket(interaction, "متجر-الرتب", is_roles=True)

    @discord.ui.button(
        label="افتح متجر الألقاب", 
        style=discord.ButtonStyle.success, 
        custom_id="titles_store"
    )
    async def titles_store_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_store_ticket(interaction, "متجر-الألقاب", is_roles=False)

    async def create_store_ticket(self, interaction: discord.Interaction, store_name: str, is_roles: bool):
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

        # اسم الروم أصبح باسم المتجر فقط بدون اسم المستخدم
        channel = await guild.create_text_channel(
            name=store_name,
            category=category,
            overwrites=overwrites
        )

        await interaction.followup.send(f"تم فتح تذكرتك بنجاح: {channel.mention}", ephemeral=True)

        shop_type = "roles" if is_roles else "titles"
        view = PurchaseView(shop_type)

        if is_roles:
            await channel.send(
                f"أهلاً بك يا {user.mention} في **متجر الرتب**!\n"
                "إليك قائمة الرتب المتاحة للشراء:\n\n"
                "🔥 **Ultra** - السعر: 75,000 كوينز\n"
                "🔹 **Prime** - السعر: 45,000 كوينز\n"
                "🌟 **Plus** - السعر: 25,000 كوينز\n"
                "⭐ **Basic** - السعر: 10,000 كوينز\n\n"
                "👇 **يمكنك الشراء مباشرة عبر القائمة أدناه:**",
                view=view
            )
        else:
            await channel.send(
                f"أهلاً بك يا {user.mention} في **متجر الألقاب**!\n"
                "إليك قائمة الألقاب المتاحة للشراء:\n\n"
                "👑 **King** - السعر: 60,000 كوينز\n"
                "👑 **Queen** - السعر: 60,000 كوينز\n\n"
                "👇 **يمكنك الشراء مباشرة عبر القائمة أدناه:**",
                view=view
            )

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="store", description="إرسال لوحة متجر الرتب والألقاب")
    @app_commands.default_permissions(administrator=True)
    async def store_panel(self, interaction: discord.Interaction):
        view = StoreView()
        await interaction.response.send_message(
            "**مرحباً بك في متجر السيرفر!**\nاختر المتجر الذي ترغب في فتحه من الأزرار بالأسفل:", 
            view=view
        )

async def setup(bot):
    await bot.add_cog(Shop(bot))
