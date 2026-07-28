import discord
from discord import app_commands
from discord.ext import commands
import json
import os

DATA_FILE = "inventory.json"

# ==========================================
# 📂 دوال التحميل والحفظ (JSON Functions)
# ==========================================
def load_data():
    """تحميل البيانات من ملف inventory.json"""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    """حفظ البيانات إلى ملف inventory.json"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_user_data(user_id):
    """جلب بيانات العضو أو إنشاء بيانات فارغة نظيفة إن لم تكن موجودة"""
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "titles": [],          # تبدأ فارغة ليتم إضافتها من النظام/الإدارة
            "active_title": None,
            "ranks": [],           # الرتب المكتسبة من النظام
            "active_ranks": [],
            "boxes": {             # تبدأ جميعها بـ 0 لتأتي من المتجر لاحقاً
                "الشائع": 0,
                "غير الشائع": 0,
                "النادر": 0,
                "الإيبك": 0,
                "الميثك": 0
            }
        }
        save_data(data)
    return data[uid]

def update_user_data(user_id, user_data):
    """تحديث بيانات العضو في ملف الحفظ"""
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)


# ==========================================
# 🎒 الواجهة الأساسية (Persistent View للوحة)
# ==========================================
class InventorySetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎒 فتح الانفنتوري", style=discord.ButtonStyle.blurple, custom_id="persistent:open_inventory_main")
    async def open_inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            content="أهلاً بك في حقيبتك الخاصة ✨\nمن هنا يمكنك إدارة ممتلكاتك:",
            view=InventoryMainMenuView(),
            ephemeral=True
        )


# ==========================================
# 🗂️ قائمة الخيارات الرئيسية للانفنتوري
# ==========================================
class InventoryMainMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="🪪 ألقابي", style=discord.ButtonStyle.secondary, custom_id="menu:titles_btn")
    async def titles_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data = get_user_data(interaction.user.id)
        titles = user_data.get("titles", [])
        active_title = user_data.get("active_title")

        desc = "🪪 **ألقابك:**\n\n"
        if titles:
            for t in titles:
                status = " (مفعل ✨)" if t == active_title else ""
                desc += f"• {t}{status}\n"
        else:
            desc += "لا توجد ألقاب لديك حالياً.\n"

        view = TitlesView(user_data, interaction.user)
        await interaction.response.edit_message(content=desc, view=view)

    @discord.ui.button(label="🏷️ رتبي", style=discord.ButtonStyle.secondary, custom_id="menu:ranks_btn")
    async def ranks_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data = get_user_data(interaction.user.id)
        
        # قراءة رتب العضو الحالية من ديسكورد تلقائياً + الرتب من JSON
        discord_roles = [role.name for role in interaction.user.roles if role.name != "@everyone"] if isinstance(interaction.user, discord.Member) else []
        json_ranks = user_data.get("ranks", [])
        
        # دمج الرتب بدون تكرار
        all_ranks = list(set(json_ranks + discord_roles))

        desc = "🏷️ **رتبك:**\n\n"
        if all_ranks:
            for r in all_ranks:
                is_active = r in discord_roles
                status = " (مفعلة ✨)" if is_active else ""
                desc += f"• {r}{status}\n"
        else:
            desc += "لا توجد رتب لديك حالياً.\n"

        view = RanksView(user_data, interaction.user, all_ranks)
        await interaction.response.edit_message(content=desc, view=view)

    @discord.ui.button(label="🎁 صناديقي", style=discord.ButtonStyle.secondary, custom_id="menu:boxes_btn")
    async def boxes_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data = get_user_data(interaction.user.id)
        boxes = user_data.get("boxes", {})

        desc = "🎁 **صناديقك:**\n\n"
        for b_name, b_count in boxes.items():
            desc += f"📦 {b_name} ×{b_count}\n"

        view = BoxesView(user_data, interaction.user)
        await interaction.response.edit_message(content=desc, view=view)


# ==========================================
# 🪪 قائمة وإدارة الألقاب (JSON فقط بدون رتب سيرفر)
# ==========================================
class TitlesSelect(discord.ui.Select):
    def __init__(self, titles, active_title):
        options = []
        for t in titles:
            is_active = (t == active_title)
            options.append(discord.SelectOption(label=t, description="مفعل حالياً ✨" if is_active else "لقب ملكك", emoji="🪪"))
        if not options:
            options.append(discord.SelectOption(label="لا توجد ألقاب", value="none"))
        super().__init__(placeholder="اختر لقباً...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_title = self.values[0]
        await interaction.response.defer()

class TitlesView(discord.ui.View):
    def __init__(self, user_data, user):
        super().__init__(timeout=180)
        self.user_data = user_data
        self.user = user
        self.selected_title = None
        self.add_item(TitlesSelect(user_data.get("titles", []), user_data.get("active_title")))

    @discord.ui.button(label="✅ تفعيل اللقب", style=discord.ButtonStyle.success, row=1)
    async def activate_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_title or self.selected_title == "none":
            return await interaction.response.send_message("❌ الرجاء اختيار لقب من القائمة أولاً!", ephemeral=True)
        
        self.user_data["active_title"] = self.selected_title
        update_user_data(self.user.id, self.user_data)
        await interaction.response.send_message(f"✅ تم تفعيل اللقب: **{self.selected_title}** بنجاح!", ephemeral=True)

    @discord.ui.button(label="❌ إزالة اللقب", style=discord.ButtonStyle.danger, row=1)
    async def deactivate_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_title or self.selected_title == "none":
            return await interaction.response.send_message("❌ الرجاء اختيار لقب من القائمة أولاً!", ephemeral=True)
        
        if self.user_data.get("active_title") == self.selected_title:
            self.user_data["active_title"] = None
            update_user_data(self.user.id, self.user_data)
            await interaction.response.send_message(f"❌ تم إزالة تفعيل اللقب: **{self.selected_title}** (محفوظ في ملف البيانات).", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ هذا اللقب غير مفعل أساساً!", ephemeral=True)

    @discord.ui.button(label="🔙 رجوع", style=discord.ButtonStyle.secondary, row=2)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="أهلاً بك في حقيبتك الخاصة ✨\nمن هنا يمكنك إدارة ممتلكاتك:", view=InventoryMainMenuView())


# ==========================================
# 🏷️ قائمة وإدارة الرتب (Discord Roles)
# ==========================================
class RanksSelect(discord.ui.Select):
    def __init__(self, ranks, user_roles):
        options = []
        for r in ranks:
            is_active = r in user_roles
            options.append(discord.SelectOption(label=r, description="مفعلة حالياً ✨" if is_active else "رتبة ملكك", emoji="🏷️"))
        if not options:
            options.append(discord.SelectOption(label="لا توجد رتب", value="none"))
        super().__init__(placeholder="اختر رتبة...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_rank = self.values[0]
        await interaction.response.defer()

class RanksView(discord.ui.View):
    def __init__(self, user_data, user, all_ranks):
        super().__init__(timeout=180)
        self.user_data = user_data
        self.user = user
        self.selected_rank = None
        user_roles = [r.name for r in user.roles] if isinstance(user, discord.Member) else []
        self.add_item(RanksSelect(all_ranks, user_roles))

    @discord.ui.button(label="✅ تفعيل الرتبة", style=discord.ButtonStyle.success, row=1)
    async def activate_rank(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_rank or self.selected_rank == "none":
            return await interaction.response.send_message("❌ الرجاء اختيار رتبة من القائمة أولاً!", ephemeral=True)
        
        if isinstance(interaction.user, discord.Member):
            role = discord.utils.get(interaction.user.guild.roles, name=self.selected_rank)
            if role:
                if role not in interaction.user.roles:
                    try:
                        await interaction.user.add_roles(role)
                    except Exception as e:
                        return await interaction.response.send_message(f"❌ خطأ أثناء تفعيل الرتبة: {e}", ephemeral=True)
                
                # حفظ الرتبة في الـ JSON إن لم تكن موجودة
                if self.selected_rank not in self.user_data.get("ranks", []):
                    self.user_data["ranks"].append(self.selected_rank)
                    update_user_data(self.user.id, self.user_data)

                await interaction.response.send_message(f"✅ تم تفعيل الرتبة: **{self.selected_rank}** بنجاح!", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ الرتبة **{self.selected_rank}** غير موجودة في رتب السيرفر!", ephemeral=True)

    @discord.ui.button(label="❌ إزالة الرتبة", style=discord.ButtonStyle.danger, row=1)
    async def deactivate_rank(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_rank or self.selected_rank == "none":
            return await interaction.response.send_message("❌ الرجاء اختيار رتبة من القائمة أولاً!", ephemeral=True)
        
        if isinstance(interaction.user, discord.Member):
            role = discord.utils.get(interaction.user.guild.roles, name=self.selected_rank)
            if role:
                if role in interaction.user.roles:
                    try:
                        await interaction.user.remove_roles(role)
                    except Exception as e:
                        return await interaction.response.send_message(f"❌ خطأ أثناء إزالة الرتبة: {e}", ephemeral=True)

                await interaction.response.send_message(f"❌ تم إزالة الرتبة: **{self.selected_rank}** (محفوظة في بياناتك ويمكن إرجاعها).", ephemeral=True)
            else:
                await interaction.response.send_message(f"⚠️ الرتبة غير موجودة في السيرفر!", ephemeral=True)

    @discord.ui.button(label="🔙 رجوع", style=discord.ButtonStyle.secondary, row=2)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="أهلاً بك في حقيبتك الخاصة ✨\nمن هنا يمكنك إدارة ممتلكاتك:", view=InventoryMainMenuView())


# ==========================================
# 🎁 قائمة وعرض الصناديق
# ==========================================
class BoxButton(discord.ui.Button):
    def __init__(self, box_name, count):
        super().__init__(label=f"{box_name} ({count})", style=discord.ButtonStyle.secondary, emoji="📦")
        self.box_name = box_name

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        view.selected_box = self.box_name
        
        boxes = view.user_data.get("boxes", {})
        desc = "🎁 **صناديقك:**\n\n"
        for b_name, b_count in boxes.items():
            desc += f"📦 {b_name} ×{b_count}\n"
        desc += f"\n🎁 تم اختيار صندوق **({self.box_name})**"

        open_view = BoxSelectedView(view.user_data, view.user, self.box_name)
        await interaction.response.edit_message(content=desc, view=open_view)

class BoxesView(discord.ui.View):
    def __init__(self, user_data, user):
        super().__init__(timeout=180)
        self.user_data = user_data
        self.user = user
        self.selected_box = None

        boxes = user_data.get("boxes", {})
        for box_name, count in boxes.items():
            self.add_item(BoxButton(box_name, count))

    @discord.ui.button(label="🔙 رجوع", style=discord.ButtonStyle.secondary, row=2)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="أهلاً بك في حقيبتك الخاصة ✨\nمن هنا يمكنك إدارة ممتلكاتك:", view=InventoryMainMenuView())

class BoxSelectedView(discord.ui.View):
    def __init__(self, user_data, user, box_name):
        super().__init__(timeout=180)
        self.user_data = user_data
        self.user = user
        self.box_name = box_name

    @discord.ui.button(label="🔥 فتح الصندوق", style=discord.ButtonStyle.primary, row=1)
    async def open_box(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✨ تم النقر لفتح صندوق **({self.box_name})** (سيتم ربط نظام الصناديق لاحقاً)", ephemeral=True)

    @discord.ui.button(label="🔙 رجوع للصناديق", style=discord.ButtonStyle.secondary, row=1)
    async def back_to_boxes(self, interaction: discord.Interaction, button: discord.ui.Button):
        boxes = self.user_data.get("boxes", {})
        desc = "🎁 **صناديقك:**\n\n"
        for b_name, b_count in boxes.items():
            desc += f"📦 {b_name} ×{b_count}\n"
        await interaction.response.edit_message(content=desc, view=BoxesView(self.user_data, self.user))


# ==========================================
# ⚙️ الـ Cog الخاص بالنظام وأمر الإدارة
# ==========================================
class InventoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_inventory", description="إرسال لوحة نظام الحقيبة في الروم الحالي (للإدارة فقط)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_inventory(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎒 نظام الحقيبة",
            description="أهلاً بك في حقيبتك الخاصة ✨\n\nمن هنا يمكنك إدارة ممتلكاتك:\n\n🪪 ألقابك\n🏷️ رتبك\n🎁 صناديقي",
            color=discord.Color.blurple()
        )
        view = InventorySetupView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ تمت إرسال لوحة الانفنتوري بنجاح في هذا الروم.", ephemeral=True)

    @setup_inventory.error
    async def setup_inventory_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ عذراً، هذا الأمر مخصص للإدارة فقط!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ حدث خطأ: {error}", ephemeral=True)


async def setup(bot):
    bot.add_view(InventorySetupView())
    await bot.add_cog(InventoryCog(bot))
