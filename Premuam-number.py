# bot.py — RGX NUMBER BOT (Complete Final Version)

import asyncio, json, os, re, sqlite3, threading
from datetime import datetime, timedelta

import requests
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, Update, CopyTextButton,
)
from telegram.constants import KeyboardButtonStyle as KBS
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters,
)

from emoji import CUSTOM_EMOJIS

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8208003630:AAE9PGWAetvkB2SDcOigYS5Yjfo7UzqUvN4"
ADMIN_IDS = [8744359777]

OTP_GROUP_URL = "https://t.me/RgxOtp"

API_URL = "put your panel api url"
API_TOKEN = "Put your panel api token"

# ==================== DATABASE SETUP ====================
conn = sqlite3.connect('mrisbrand_master.db', check_same_thread=False)
db_lock = threading.Lock()
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
              joined_date TEXT, last_active TEXT,
              current_number_id INTEGER DEFAULT NULL,
              current_number TEXT DEFAULT NULL, current_country TEXT DEFAULT NULL,
              current_service TEXT DEFAULT NULL, number_expiry TEXT DEFAULT NULL,
              last_menu_message_id INTEGER DEFAULT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS numbers
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, number TEXT,
              country TEXT, service TEXT, assigned_date TEXT, status TEXT DEFAULT 'active',
              expiry_time TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS otps
             (id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, otp TEXT,
              message TEXT, timestamp TEXT, forwarded INTEGER DEFAULT 0, user_id INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS countries
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, service TEXT,
              flag TEXT, active INTEGER DEFAULT 1, stock INTEGER DEFAULT 0)''')

c.execute('''CREATE TABLE IF NOT EXISTS available_numbers
             (id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, service TEXT,
              number TEXT, used INTEGER DEFAULT 0)''')

c.execute('''CREATE TABLE IF NOT EXISTS used_numbers
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, number TEXT,
              country TEXT, service TEXT, assigned_date TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS services
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE,
              display_name TEXT, active INTEGER DEFAULT 1, emoji_id TEXT DEFAULT '')''')

try:
    c.execute("ALTER TABLE services ADD COLUMN emoji_id TEXT DEFAULT ''")
except sqlite3.OperationalError:
    pass

default_services = ["WhatsApp", "Telegram", "Facebook", "IMO", "Google", "Tinder", "Uber", "Instagram", "Twitter", "Snapchat"]
for service in default_services:
    c.execute("INSERT OR IGNORE INTO services (name, display_name, active, emoji_id) VALUES (?, ?, 1, '')", (service, service))

conn.commit()
print("✅ Database setup completed")

# ==================== STATE TRACKING ====================
admin_mode = {}
admin_panel_state = {}
admin_temp_data = {}

def safe_url(url: str) -> str | None:
    if url and isinstance(url, str) and (url.startswith("http://") or url.startswith("https://") or url.startswith("tg://")):
        return url
    return None

# ==================== LOAD COUNTRIES FROM JSON ====================
def load_countries_db():
    try:
        with open('countries.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for name, info in data.items():
                if "emoji_id" not in info:
                    info["emoji_id"] = ""
            return data
    except FileNotFoundError:
        default = {
            "Pakistan": {"code": "+92", "iso": "PK", "emoji_id": ""},
            "India": {"code": "+91", "iso": "IN", "emoji_id": ""},
            "Venezuela": {"code": "+58", "iso": "VE", "emoji_id": ""},
            "Nigeria": {"code": "+234", "iso": "NG", "emoji_id": ""},
        }
        with open('countries.json', 'w', encoding='utf-8') as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        return default

def save_countries_db(data):
    with open('countries.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

COUNTRIES_DATA = load_countries_db()

def get_country_info(country_name):
    return COUNTRIES_DATA.get(country_name, {"emoji_id": ""})

# ==================== CUSTOM EMOJI HTML HELPER ====================
def emoji_tag(emoji_id: str, fallback: str = " ") -> str:
    if not emoji_id or not emoji_id.isdigit() or len(emoji_id) < 10:
        return fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

def country_flag_emoji(country_name: str) -> str:
    eid = get_country_info(country_name).get("emoji_id") or CUSTOM_EMOJIS["DEFAULT_FLAG"]
    return emoji_tag(eid, "🏁")

def service_emoji_tag(service_name: str) -> str:
    row = db_fetch_one("SELECT emoji_id FROM services WHERE name = ?", (service_name,))
    eid = row[0] if row and row[0] else CUSTOM_EMOJIS["DEFAULT_SERVICE"]
    return emoji_tag(eid, "⚙️")

# ==================== KEYBOARD BUILDERS ====================
BTN_GET_NUMBER = "Get Number"
BTN_LIVE_STOCK = "Live Stock"
BTN_SUPPORT = "Support"
BTN_ADMIN = "Admin Panel"

def bottom_menu_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    rows = [
        [
            KeyboardButton(BTN_GET_NUMBER, style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["GET_NUMBER"]),
            KeyboardButton(BTN_LIVE_STOCK, style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["LIVE_STOCK"])
        ],
        [
            KeyboardButton(BTN_SUPPORT, style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["SUPPORT"])
        ],
    ]
    if user_id in ADMIN_IDS:
        rows.append([KeyboardButton(BTN_ADMIN, style=KBS.DANGER, icon_custom_emoji_id=CUSTOM_EMOJIS["ADMIN"])])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True,
                               input_field_placeholder="Choose an option...")

def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Get Number", callback_data="menu_get_number", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["GET_NUMBER"]),
            InlineKeyboardButton("Live Stock", callback_data="menu_live_stock", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["LIVE_STOCK"]),
        ],
        [
            InlineKeyboardButton("Support", callback_data="menu_support", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["SUPPORT"]),
        ],
    ] + ([
        [InlineKeyboardButton("Admin Panel", callback_data="menu_admin", style=KBS.DANGER, icon_custom_emoji_id=CUSTOM_EMOJIS["ADMIN"])],
    ] if user_id in ADMIN_IDS else []))

def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Back to Main Menu", callback_data="back_to_menu", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"]),
    ]])

def number_action_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("New Number", callback_data="next_number", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["NEW_NUMBER"]),
            InlineKeyboardButton("Change Country", callback_data="back_to_countries", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["CHANGE_COUNTRY"]),
        ],
        [
            InlineKeyboardButton("OTP Group", url=OTP_GROUP_URL, style=KBS.DANGER, icon_custom_emoji_id=CUSTOM_EMOJIS["JOIN_OTP_GROUP"]),
        ],
        [
            InlineKeyboardButton("Home", callback_data="back_to_menu", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["HOME"]),
        ],
    ])

def countries_keyboard(countries: list) -> InlineKeyboardMarkup:
    rows = []
    for name, service, stock in countries:
        label = f"{name} — {service} ({stock})"
        cb = f"sel|{name}|{service}"[:60]
        flag_eid = get_country_info(name).get("emoji_id") or CUSTOM_EMOJIS["DEFAULT_FLAG"]
        rows.append([InlineKeyboardButton(label, callback_data=cb, style=KBS.SUCCESS, icon_custom_emoji_id=flag_eid)])
    rows.append([InlineKeyboardButton("Back to Main Menu", callback_data="back_to_menu", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"])])
    return InlineKeyboardMarkup(rows)

def stock_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Refresh", callback_data="refresh_stock", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["REFRESH"])],
        [InlineKeyboardButton("Home", callback_data="back_to_menu", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["HOME"])]
    ])

def support_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Contact Admin Support", url="t.me/BloodyV0id", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["CONTACT_SUPPORT"])],
        [InlineKeyboardButton("Home", callback_data="back_to_menu", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["HOME"])]
    ])

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Statistics", callback_data="admin_stats", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["STATS"]),
            InlineKeyboardButton("Upload Stock", callback_data="admin_upload", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["UPLOAD"]),
        ],
        [
            InlineKeyboardButton("Delete Stock", callback_data="admin_delete", style=KBS.DANGER, icon_custom_emoji_id=CUSTOM_EMOJIS["DELETE"]),
            InlineKeyboardButton("Broadcast", callback_data="admin_broadcast", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BROADCAST"]),
        ],
        [
            InlineKeyboardButton("Give Account", callback_data="admin_giveaway", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["GIVEAWAY"]),
            InlineKeyboardButton("Country Manager", callback_data="admin_country_manager", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["COUNTRY_MANAGER"]),
        ],
        [
            InlineKeyboardButton("Service Manager", callback_data="admin_service_manager", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["SERVICE_MANAGER"]),
            InlineKeyboardButton("Exit Admin", callback_data="admin_exit", style=KBS.DANGER, icon_custom_emoji_id=CUSTOM_EMOJIS["EXIT"]),
        ],
        [
            InlineKeyboardButton("Back to Main Menu", callback_data="back_to_menu", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"]),
        ],
    ])

def admin_back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"]),
    ]])

def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Cancel", callback_data="admin_back", style=KBS.DANGER, icon_custom_emoji_id=CUSTOM_EMOJIS["CANCEL"]),
    ]])

# ==================== DATABASE HELPERS ====================
def db_exec(query, params=()):
    with db_lock:
        c.execute(query, params)
        conn.commit()

def db_fetch_one(query, params=()):
    with db_lock:
        c.execute(query, params)
        return c.fetchone()

def db_fetch_all(query, params=()):
    with db_lock:
        c.execute(query, params)
        return c.fetchall()

def extract_country_from_filename(filename):
    """Extract country name from filename - handles spaces, dashes, multiple words"""
    try:
        name = filename.replace('.txt', '')
        # Split by underscore to separate country from service
        if '_' in name:
            country_part = name.split('_')[0].strip()
        else:
            country_part = name.strip()
        
        # Try exact match first
        for country_name in COUNTRIES_DATA.keys():
            if country_name.lower() == country_part.lower():
                return country_name
        
        # Try partial match - check if country_part starts with any known country
        for country_name in COUNTRIES_DATA.keys():
            if country_part.lower().startswith(country_name.lower()) or country_name.lower().startswith(country_part.lower()):
                return country_name
        
        # Try contains match
        for country_name in COUNTRIES_DATA.keys():
            if country_name.lower() in country_part.lower() or country_part.lower() in country_name.lower():
                return country_name
        
        # If no match found, return the raw country part
        return country_part
    except Exception:
        return None

def extract_service_from_filename(filename):
    """Extract service name from filename - everything after underscore"""
    try:
        name = filename.replace('.txt', '').lower()
        if '_' in name:
            service_part = name.split('_', 1)[1].strip()
        else:
            return "Unknown"
        
        # Try to match with known services
        services = [row[0] for row in db_fetch_all("SELECT name FROM services WHERE active = 1")]
        for service in services:
            if service.lower() in service_part:
                return service
        
        # If no match, return the raw service part
        return service_part
    except Exception:
        return "Unknown"

def load_numbers_from_file(file_path, filename):
    try:
        country = extract_country_from_filename(filename)
        service = extract_service_from_filename(filename)
        if not country:
            return 0, None, None
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            numbers = file.read().strip().split('\n')
        valid_numbers = []
        for num in numbers:
            num = num.strip()
            if num:
                if not num.startswith('+'):
                    num = '+' + num
                valid_numbers.append(num)
        if not valid_numbers:
            return 0, None, None
        with db_lock:
            for number in valid_numbers:
                c.execute('''INSERT INTO available_numbers (country, service, number)
                             VALUES (?, ?, ?)''', (country, service, number))
            c.execute('''INSERT OR IGNORE INTO countries (name, service, flag, stock)
                         VALUES (?, ?, ?, 0)''', (country, service, country))
            c.execute("SELECT stock FROM countries WHERE name = ? AND service = ?", (country, service))
            current = c.fetchone()
            current_stock = current[0] if current else 0
            c.execute('''UPDATE countries SET stock = ?, active = 1
                         WHERE name = ? AND service = ?''',
                      (current_stock + len(valid_numbers), country, service))
            conn.commit()
        return len(valid_numbers), country, service
    except Exception as e:
        print(f"Error loading file: {e}")
        return 0, None, None

def delete_country_stock(country, service):
    try:
        db_exec("DELETE FROM available_numbers WHERE country = ? AND service = ?", (country, service))
        db_exec("DELETE FROM countries WHERE name = ? AND service = ?", (country, service))
        return True
    except Exception as e:
        print(f"Error deleting stock: {e}")
        return False

def get_numbers_from_stock(country, service, count=3):
    try:
        with db_lock:
            c.execute('''SELECT COUNT(*) FROM available_numbers
                         WHERE country = ? AND service = ? AND used = 0''', (country, service))
            available = c.fetchone()
            if not available or available[0] == 0:
                return []
            take = min(count, available[0])
            c.execute('''SELECT id, number FROM available_numbers
                         WHERE country = ? AND service = ? AND used = 0
                         ORDER BY RANDOM() LIMIT ?''', (country, service, take))
            results = c.fetchall()
            if not results:
                return []
            numbers = []
            for num_id, number in results:
                c.execute("UPDATE available_numbers SET used = 1 WHERE id = ?", (num_id,))
                numbers.append(number)
            c.execute('''UPDATE countries SET stock = (
                            SELECT COUNT(*) FROM available_numbers 
                            WHERE country = ? AND service = ? AND used = 0
                         ) WHERE name = ? AND service = ?''', 
                      (country, service, country, service))
            conn.commit()
            return numbers
    except Exception as e:
        print(f"Error getting numbers: {e}")
        return []

def extract_otp_from_message(message_text):
    try:
        patterns = [r'(\d{3}-\d{3})', r'(\d{6})', r'(\d{4,8})']
        for pattern in patterns:
            match = re.search(pattern, message_text)
            if match:
                return match.group(1)
        return None
    except Exception:
        return None

def format_numbers_message(country, service, numbers, first_name=None):
    if first_name is None:
        first_name = "User"
    flag_eid = get_country_info(country).get("emoji_id") or CUSTOM_EMOJIS["DEFAULT_FLAG"]
    message = f"This Is your Activated Number {emoji_tag(CUSTOM_EMOJIS['GET_NUMBER'], '📱')}\n\n"
    rows = []
    for number in numbers:
        if not number.startswith('+'):
            number = '+' + number
        rows.append([InlineKeyboardButton(
            text=number,
            copy_text=CopyTextButton(text=number),
            style=KBS.PRIMARY,
            icon_custom_emoji_id=flag_eid
        )])
    rows.append([
        InlineKeyboardButton("New Number", callback_data="next_number", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["NEW_NUMBER"]),
        InlineKeyboardButton("Change Country", callback_data="back_to_countries", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["CHANGE_COUNTRY"]),
    ])
    rows.append([
        InlineKeyboardButton("OTP Group", url=OTP_GROUP_URL, style=KBS.DANGER, icon_custom_emoji_id=CUSTOM_EMOJIS["JOIN_OTP_GROUP"]),
    ])
    rows.append([
        InlineKeyboardButton("Home", callback_data="back_to_menu", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["HOME"]),
    ])
    return message, InlineKeyboardMarkup(rows)

def stock_added_message(country, service, count):
    """New format - shown to admin first"""
    flag_eid = get_country_info(country).get("emoji_id") or CUSTOM_EMOJIS["DEFAULT_FLAG"]
    svc_eid_row = db_fetch_one("SELECT emoji_id FROM services WHERE name = ?", (service,))
    svc_eid = svc_eid_row[0] if svc_eid_row and svc_eid_row[0] else CUSTOM_EMOJIS["DEFAULT_SERVICE"]
    
    return (
        f'{emoji_tag("4958617898751886363", "📊")} <b>STOCK</b> {emoji_tag("5463412319948148591", "📦")} <b>ADDED SUCCESSFULLY</b> {emoji_tag("4956721670690702265", "✅")}\n\n'
        f'<b>NUMBER</b> {emoji_tag("6204108584381322968", "📱")} : <b>{count}</b>\n'
        f'<b>COUNTRY</b> {emoji_tag("5188540541922480562", "🌍")} : {emoji_tag(flag_eid, "🏁")}\n'
        f'<b>SERVICE</b> {emoji_tag("5465590345108589516", "🔧")} : {emoji_tag(svc_eid, "⚙️")}'
    )

def stock_added_broadcast(country, service, count):
    """Broadcast message for all users"""
    flag_eid = get_country_info(country).get("emoji_id") or CUSTOM_EMOJIS["DEFAULT_FLAG"]
    svc_eid_row = db_fetch_one("SELECT emoji_id FROM services WHERE name = ?", (service,))
    svc_eid = svc_eid_row[0] if svc_eid_row and svc_eid_row[0] else CUSTOM_EMOJIS["DEFAULT_SERVICE"]
    
    return (
        f'{emoji_tag("4958617898751886363", "📊")} <b>STOCK</b> {emoji_tag("5463412319948148591", "📦")} <b>ADDED SUCCESSFULLY</b> {emoji_tag("4956721670690702265", "✅")}\n\n'
        f'<b>NUMBER</b> {emoji_tag("6204108584381322968", "📱")} : <b>{count}</b>\n'
        f'<b>COUNTRY</b> {emoji_tag("5188540541922480562", "🌍")} : {emoji_tag(flag_eid, "🏁")}\n'
        f'<b>SERVICE</b> {emoji_tag("5465590345108589516", "🔧")} : {emoji_tag(svc_eid, "⚙️")}'
    )

# ==================== WELCOME HTML ====================
def welcome_html(user_id, first_name):
    spark = CUSTOM_EMOJIS["WELCOME_SPARKLE"]
    rocket = CUSTOM_EMOJIS["ROCKET"]
    id_icon = CUSTOM_EMOJIS["ID_ICON"]
    check = CUSTOM_EMOJIS["CHECK_MARK"]
    gamepad = CUSTOM_EMOJIS["GAMEPAD"]
    return (
        f'{emoji_tag(spark, "✨")} Welcome to Developer RGX NUMBER BOT Bot, {first_name}! {emoji_tag(spark, "✨")}\n\n'
        f'{emoji_tag(rocket, "🚀")} Your Premium Platform for Virtual Numbers.\n\n'
        f'{emoji_tag(id_icon, "🆔")} Your ID: <code>{user_id}</code>\n'
        f'{emoji_tag(check, "✅")} You are a Verified Member!\n\n'
        f'{emoji_tag(gamepad, "🎮")} Tap a button below to navigate.\n\n'
        '━━━━━━━━━━━━━━━━━━━━\n'
        '👨‍💻 Developer: RGX NUMBER BOT'
    )

# ==================== /start COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name or "User"
    db_exec('''INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date, last_active)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, username, first_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    db_exec("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    await update.message.reply_text(welcome_html(user_id, first_name), reply_markup=bottom_menu_keyboard(user_id), parse_mode='HTML')

# ==================== MAIN MENU CALLBACKS ====================
async def show_main_menu(query, user_id, first_name):
    try:
        await query.edit_message_text(welcome_html(user_id, first_name), reply_markup=main_menu_keyboard(user_id), parse_mode='HTML')
    except Exception:
        try:
            await query.message.reply_text(welcome_html(user_id, first_name), reply_markup=main_menu_keyboard(user_id), parse_mode='HTML')
        except Exception:
            pass

async def show_get_number(query, context, user_id, first_name):
    db_exec("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    countries = db_fetch_all("SELECT name, service, stock FROM countries WHERE active = 1 AND stock > 0 ORDER BY name")
    if not countries:
        try:
            await query.edit_message_text("No numbers available at the moment.\n\nPlease check back later or contact admin.", reply_markup=back_to_main_keyboard())
        except Exception:
            pass
        return
    try:
        await query.edit_message_text("Select a Country & Service:\n\nChoose from the list below to get your virtual number.", reply_markup=countries_keyboard(countries))
    except Exception:
        pass

async def show_live_stock(query):
    try:
        await query.edit_message_text(stock_text(), reply_markup=stock_keyboard(), parse_mode='HTML')
    except Exception:
        pass

async def show_support(query):
    try:
        await query.edit_message_text("CONTACT SUPPORT\n\n━━━━━━━━━━━━━━━━━━━━\nFor any issues, questions, or requests — contact admin directly.\n\nDeveloper: RGX NUMBER BOT", reply_markup=support_keyboard())
    except Exception:
        pass

async def show_admin_panel_menu(query, user_id):
    if user_id not in ADMIN_IDS:
        await query.answer("Unauthorized!", show_alert=True)
        return
    admin_mode[user_id] = True
    admin_panel_state[user_id] = "main"
    try:
        await query.edit_message_text("ADMIN PANEL\n\nDeveloper: RGX NUMBER BOT\n\nSelect an action below:", reply_markup=admin_panel_keyboard())
    except Exception:
        pass

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    data = query.data
    await query.answer()
    action = data[len("menu_"):]
    if action == "get_number": await show_get_number(query, context, user_id, first_name)
    elif action == "live_stock": await show_live_stock(query)
    elif action == "support": await show_support(query)
    elif action == "admin": await show_admin_panel_menu(query, user_id)

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    await query.answer()
    await show_main_menu(query, user_id, first_name)

# ==================== NUMBER FLOW ====================
async def refresh_stock_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Refreshed!")
    try:
        await query.edit_message_text(stock_text(), reply_markup=stock_keyboard(), parse_mode='HTML')
    except Exception:
        pass

async def select_country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    await query.answer("Allocating 3 numbers...")
    try:
        parts = query.data.split('|', 2)
        if len(parts) < 3: 
            await query.answer("Invalid selection.", show_alert=True)
            return
        country = parts[1]
        service = parts[2]
    except Exception:
        await query.answer("Error parsing selection.", show_alert=True)
        return

    stock_result = db_fetch_one("SELECT stock FROM countries WHERE name = ? AND service = ? AND active = 1", (country, service))
    if not stock_result:
        await query.answer("This service is not available!", show_alert=True)
        return
    if stock_result[0] <= 0:
        await query.answer("No numbers left for this service! Try another.", show_alert=True)
        countries = db_fetch_all("SELECT name, service, stock FROM countries WHERE active = 1 AND stock > 0 ORDER BY name")
        if countries:
            await query.edit_message_text("Select a Country & Service:\n\nChoose from the list below.", reply_markup=countries_keyboard(countries))
        else:
            await query.edit_message_text("No numbers available.", reply_markup=back_to_main_keyboard())
        return

    numbers = get_numbers_from_stock(country, service, 3)
    if not numbers:
        await query.answer("Failed to allocate numbers! Please try again.", show_alert=True)
        return

    expiry = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for number in numbers:
        db_exec('''INSERT INTO numbers (user_id, number, country, service, assigned_date, status, expiry_time)
                   VALUES (?, ?, ?, ?, ?, 'active', ?)''',
                (user_id, number, country, service, now_str, expiry))
    db_exec('''UPDATE users SET current_number = ?, current_country = ?, current_service = ?, number_expiry = ?
               WHERE user_id = ?''', (numbers[0], country, service, expiry, user_id))

    msg, kb = format_numbers_message(country, service, numbers, first_name)
    try:
        await query.edit_message_text(msg, reply_markup=kb, parse_mode='HTML')
    except Exception as e:
        await context.bot.send_message(user_id, msg, reply_markup=kb, parse_mode='HTML')

async def next_number_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    await query.answer("Getting next 3 numbers...")
    result = db_fetch_one("SELECT current_country, current_service FROM users WHERE user_id = ?", (user_id,))
    country = service = None
    if result and result[0]:
        country, service = result
    else:
        fallback = db_fetch_one("SELECT country, service FROM numbers WHERE user_id = ? ORDER BY assigned_date DESC LIMIT 1", (user_id,))
        if fallback: country, service = fallback
    if not country:
        countries = db_fetch_all("SELECT name, service, stock FROM countries WHERE active = 1 AND stock > 0 ORDER BY name")
        await query.edit_message_text("Select a Country & Service:" if countries else "No numbers available.",
                                      reply_markup=countries_keyboard(countries) if countries else back_to_main_keyboard())
        return
    stock = db_fetch_one("SELECT stock FROM countries WHERE name = ? AND service = ? AND active = 1", (country, service))
    if not stock or stock[0] <= 0:
        await query.answer(f"No more {country} {service} numbers!", show_alert=True)
        countries = db_fetch_all("SELECT name, service, stock FROM countries WHERE active = 1 AND stock > 0 ORDER BY name")
        await query.edit_message_text("Select a Country & Service:" if countries else "No numbers available.",
                                      reply_markup=countries_keyboard(countries) if countries else back_to_main_keyboard())
        return
    numbers = get_numbers_from_stock(country, service, 3)
    if not numbers:
        await query.answer("Failed to get numbers!", show_alert=True)
        return
    expiry = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for number in numbers:
        db_exec('''INSERT INTO numbers (user_id, number, country, service, assigned_date, status, expiry_time)
                   VALUES (?, ?, ?, ?, ?, 'active', ?)''',
                (user_id, number, country, service, now_str, expiry))
    db_exec('''UPDATE users SET current_number = ?, current_country = ?, current_service = ?, number_expiry = ?
               WHERE user_id = ?''', (numbers[0], country, service, expiry, user_id))
    msg, kb = format_numbers_message(country, service, numbers, first_name)
    try:
        await query.edit_message_text(msg, reply_markup=kb, parse_mode='HTML')
    except Exception as e:
        await context.bot.send_message(user_id, msg, reply_markup=kb, parse_mode='HTML')

async def back_to_countries_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    db_exec('''UPDATE users SET current_number = NULL, current_country = NULL, current_service = NULL, number_expiry = NULL
               WHERE user_id = ?''', (user_id,))
    countries = db_fetch_all("SELECT name, service, stock FROM countries WHERE active = 1 AND stock > 0 ORDER BY name")
    await query.edit_message_text("Select a Country & Service:\n\nChoose from the list below." if countries else "No numbers available.",
                                  reply_markup=countries_keyboard(countries) if countries else back_to_main_keyboard())

# ==================== ADMIN SECTION ====================
async def enter_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        admin_mode[user_id] = True
        admin_panel_state[user_id] = "main"
        await update.message.reply_text("ADMIN PANEL\n\nDeveloper: RGX NUMBER BOT\n\nSelect an action below:", reply_markup=admin_panel_keyboard())
    else:
        await update.message.reply_text("Unauthorized access!")

async def exit_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in admin_mode:
        admin_mode.pop(user_id, None)
        admin_panel_state.pop(user_id, None)
        await update.message.reply_text("Admin mode deactivated!", reply_markup=main_menu_keyboard(user_id))
    else:
        await update.message.reply_text("You're not in admin mode!")

async def show_admin_stats(query, user_id):
    total_users = db_fetch_one("SELECT COUNT(*) FROM users")[0]
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    active_users = db_fetch_one("SELECT COUNT(*) FROM users WHERE last_active > ?", (yesterday,))[0]
    active_numbers = db_fetch_one("SELECT COUNT(*) FROM numbers WHERE status = 'active'")[0]
    total_stock = db_fetch_one("SELECT SUM(stock) FROM countries")[0] or 0
    available_numbers = db_fetch_one("SELECT COUNT(*) FROM available_numbers WHERE used = 0")[0]
    active_countries = db_fetch_one("SELECT COUNT(*) FROM countries WHERE active = 1")[0]
    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["STATS"], "📊")} BOT STATISTICS {emoji_tag(CUSTOM_EMOJIS["STATS"], "📊")}\n\n'
        f'{emoji_tag(CUSTOM_EMOJIS["GIVEAWAY"], "👥")} USERS {emoji_tag(CUSTOM_EMOJIS["GIVEAWAY"], "👥")}\n\n'
        f'Total Users: {total_users}\n'
        f'Active {emoji_tag(CUSTOM_EMOJIS["GREEN_CIRCLE"], "🟢")}: {active_users}\n'
        f'Inactive {emoji_tag(CUSTOM_EMOJIS["RED_CIRCLE"], "🔴")}: {total_users - active_users}\n\n'
        f'{emoji_tag(CUSTOM_EMOJIS["GET_NUMBER"], "📱")} NUMBERS {emoji_tag(CUSTOM_EMOJIS["GET_NUMBER"], "📱")}\n\n'
        f'Active {emoji_tag(CUSTOM_EMOJIS["GREEN_CIRCLE"], "🟢")}: {active_numbers}\n'
        f'Total Stock {emoji_tag(CUSTOM_EMOJIS["PACKAGE"], "📦")}: {total_stock}\n'
        f'Available {emoji_tag(CUSTOM_EMOJIS["GEAR"], "⚙️")}: {available_numbers}\n\n'
        f'{emoji_tag(CUSTOM_EMOJIS["CHANGE_COUNTRY"], "🌍")} COUNTRIES {emoji_tag(CUSTOM_EMOJIS["CHANGE_COUNTRY"], "🌍")}\n'
        f'{emoji_tag(CUSTOM_EMOJIS["GREEN_CIRCLE"], "🟢")} Active Services {emoji_tag(CUSTOM_EMOJIS["SERVICE_MANAGER"], "🔧")}: {active_countries}\n\n'
        f'{datetime.now().strftime("%I:%M %p | %d %b %Y")} {emoji_tag(CUSTOM_EMOJIS["CLOCK"], "🕐")}'
    )
    countries = db_fetch_all("SELECT name, service, stock FROM countries WHERE active = 1 ORDER BY name")
    if countries:
        text += f'\n\n{emoji_tag(CUSTOM_EMOJIS["PACKAGE"], "📦")} STOCK DETAILS {emoji_tag(CUSTOM_EMOJIS["PACKAGE"], "📦")}:\n'
        for name, service, stock_count in countries:
            text += f'In stock {country_flag_emoji(name)} {name} — {service_emoji_tag(service)}: {stock_count}\n'
    await query.edit_message_text(text, reply_markup=admin_back_button(), parse_mode='HTML')
async def show_delete_options(query, user_id):
    countries = db_fetch_all("SELECT name, service, stock FROM countries WHERE active = 1 ORDER BY name")
    if not countries:
        await query.edit_message_text("No countries to delete!", reply_markup=admin_back_button())
        return
    rows = []
    for name, service, stock_count in countries:
        rows.append([InlineKeyboardButton(f"Delete {name} — {service} (Stock: {stock_count})", callback_data=f"admin_del|{name}|{service}", style=KBS.DANGER, icon_custom_emoji_id=CUSTOM_EMOJIS["DELETE"])])
    rows.append([InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"])])
    await query.edit_message_text("DELETE STOCK\n\nSelect a country/service to delete all its numbers:", reply_markup=InlineKeyboardMarkup(rows))

async def request_upload(query, user_id):
    admin_panel_state[user_id] = "waiting_file"
    await query.edit_message_text("UPLOAD STOCK\n\nSend a .txt file with phone numbers.\nFilename must contain country & service name.\nOne number per line.", reply_markup=admin_cancel_keyboard())

async def request_broadcast(query, user_id):
    admin_panel_state[user_id] = "waiting_broadcast"
    await query.edit_message_text("BROADCAST MESSAGE\n\nSend the message you want to broadcast to ALL users.", reply_markup=admin_cancel_keyboard())

async def request_giveaway(query, user_id):
    admin_panel_state[user_id] = "waiting_giveaway"
    await query.edit_message_text("GIVE FREE ACCOUNT\n\nSend: user_id count\nExample: 123456789 5", reply_markup=admin_cancel_keyboard())

async def exit_admin_callback_query(query, user_id, bot):
    admin_mode.pop(user_id, None)
    admin_panel_state.pop(user_id, None)
    try:
        await query.edit_message_text(welcome_html(user_id, query.from_user.first_name or "User"), reply_markup=main_menu_keyboard(user_id), parse_mode='HTML')
    except Exception:
        await bot.send_message(user_id, "Returned to main menu.", reply_markup=main_menu_keyboard(user_id))

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id in ADMIN_IDS and user_id not in admin_mode:
        admin_mode[user_id] = True
        admin_panel_state[user_id] = "main"
    if user_id not in admin_mode:
        await query.answer("Admin mode required!", show_alert=True)
        return
    await query.answer()
    data = query.data
    if data.startswith("admin_del|"):
        parts = data.split('|', 2)
        if len(parts) == 3:
            if delete_country_stock(parts[1], parts[2]):
                await query.answer(f"{parts[1]} — {parts[2]} deleted!")
            else:
                await query.answer(f"Error deleting {parts[1]} — {parts[2]}!", show_alert=True)
            await show_delete_options(query, user_id)
        return
    action = data[len("admin_"):]
    if action == "stats": await show_admin_stats(query, user_id)
    elif action == "upload": await request_upload(query, user_id)
    elif action == "delete": await show_delete_options(query, user_id)
    elif action == "broadcast": await request_broadcast(query, user_id)
    elif action == "giveaway": await request_giveaway(query, user_id)
    elif action == "country_manager": await country_manager_menu(query, user_id)
    elif action == "service_manager": await service_manager_menu(query, user_id)
    elif action == "exit": await exit_admin_callback_query(query, user_id, context.bot)
    elif action == "back":
        admin_panel_state[user_id] = "main"
        await query.edit_message_text("ADMIN PANEL\n\nDeveloper: RGX NUMBER BOT\n\nSelect an action below:", reply_markup=admin_panel_keyboard())

# ==================== COUNTRY MANAGER ====================
async def country_manager_menu(query, user_id):
    if user_id not in admin_mode: await query.answer("Admin mode required!", show_alert=True); return
    admin_panel_state[user_id] = "country_manager"
    rows = [
        [InlineKeyboardButton("Add New Country", callback_data="country_add", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["COUNTRY_MANAGER"])],
        [InlineKeyboardButton("List All Countries", callback_data="country_list", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["COUNTRY_MANAGER"])],
        [InlineKeyboardButton("Edit Country", callback_data="country_edit_select", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["COUNTRY_MANAGER"])],
        [InlineKeyboardButton("Delete Country", callback_data="country_delete_select", style=KBS.DANGER, icon_custom_emoji_id=CUSTOM_EMOJIS["DELETE"])],
        [InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"])],
    ]
    await query.edit_message_text("COUNTRY MANAGER\n\nSelect an option:", reply_markup=InlineKeyboardMarkup(rows))

async def country_add_start(query, user_id):
    admin_panel_state[user_id] = "waiting_country_add"
    await query.edit_message_text("ADD NEW COUNTRY\n\nFormat: CountryName | Code | ISO | emoji_id\n\nExample: Pakistan | +92 | PK | 6204108584381322968", reply_markup=admin_cancel_keyboard())

async def country_list_show(query):
    lines = [f'ALL COUNTRIES {emoji_tag(CUSTOM_EMOJIS["CHANGE_COUNTRY"], "🌍")}', '']
    for name, info in COUNTRIES_DATA.items():
        lines.append(f'• {country_flag_emoji(name)} {name}')
        lines.append(f'  Code: {info["code"]} | ISO: {info["iso"]} | Emoji ID: {info.get("emoji_id") or "Not set"}')
        lines.append('')
    await query.edit_message_text('\n'.join(lines), reply_markup=admin_back_button(), parse_mode='HTML')

async def country_edit_select(query):
    rows = []
    for name, info in COUNTRIES_DATA.items():
        icon = info.get("emoji_id") or CUSTOM_EMOJIS["DEFAULT_FLAG"]
        rows.append([InlineKeyboardButton(f"{name} (ID: {info.get('emoji_id') or 'none'})", callback_data=f"country_edit|{name}", style=KBS.PRIMARY, icon_custom_emoji_id=icon)])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_country_manager", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"])])
    await query.edit_message_text("Select country to edit:", reply_markup=InlineKeyboardMarkup(rows))

async def country_edit_start(query, user_id, country_name):
    admin_temp_data[user_id] = {"edit_country": country_name}
    admin_panel_state[user_id] = "waiting_country_edit"
    info = COUNTRIES_DATA[country_name]
    await query.edit_message_text(f"EDIT COUNTRY: {country_name}\n\nCurrent:\nCode: {info['code']}\nISO: {info['iso']}\nEmoji ID: {info.get('emoji_id', 'Not set')}\n\nSend new details: Code | ISO | emoji_id\nSend /skip to keep.", reply_markup=admin_cancel_keyboard())

async def country_delete_select(query):
    rows = []
    for name in COUNTRIES_DATA:
        rows.append([InlineKeyboardButton(f"Delete {name}", callback_data=f"country_delete|{name}", style=KBS.DANGER, icon_custom_emoji_id=CUSTOM_EMOJIS["DELETE"])])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_country_manager", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"])])
    await query.edit_message_text("Select country to delete:", reply_markup=InlineKeyboardMarkup(rows))

async def country_delete_direct(query, user_id, country_name):
    if user_id not in admin_mode: await query.answer("Admin mode required!", show_alert=True); return
    if country_name in COUNTRIES_DATA:
        del COUNTRIES_DATA[country_name]
        save_countries_db(COUNTRIES_DATA)
        db_exec("DELETE FROM available_numbers WHERE country = ?", (country_name,))
        db_exec("DELETE FROM countries WHERE name = ?", (country_name,))
        await query.answer(f"{country_name} deleted!")
    else:
        await query.answer("Country not found!", show_alert=True)
    await country_delete_select(query)

async def country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if user_id not in admin_mode: await query.answer("Admin mode required!", show_alert=True); return
    await query.answer()
    if data == "country_add": await country_add_start(query, user_id)
    elif data == "country_list": await country_list_show(query)
    elif data == "country_edit_select": await country_edit_select(query)
    elif data == "country_delete_select": await country_delete_select(query)
    elif data.startswith("country_edit|"): await country_edit_start(query, user_id, data.split('|', 1)[1])
    elif data.startswith("country_delete|"): await country_delete_direct(query, user_id, data.split('|', 1)[1])

# ==================== SERVICE MANAGER ====================
async def service_manager_menu(query, user_id):
    if user_id not in admin_mode: await query.answer("Admin mode required!", show_alert=True); return
    admin_panel_state[user_id] = "service_manager"
    rows = [
        [InlineKeyboardButton("Add New Service", callback_data="service_add", style=KBS.SUCCESS, icon_custom_emoji_id=CUSTOM_EMOJIS["SERVICE_MANAGER"])],
        [InlineKeyboardButton("List All Services", callback_data="service_list", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["SERVICE_MANAGER"])],
        [InlineKeyboardButton("Toggle Service Active", callback_data="service_toggle", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["SERVICE_MANAGER"])],
        [InlineKeyboardButton("Set Service Emoji", callback_data="service_set_emoji", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["SERVICE_MANAGER"])],
        [InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"])],
    ]
    await query.edit_message_text("SERVICE MANAGER\n\nSelect an option:", reply_markup=InlineKeyboardMarkup(rows))

async def service_add_start(query, user_id):
    admin_panel_state[user_id] = "waiting_service_name"
    await query.edit_message_text("Send the service name.", reply_markup=admin_cancel_keyboard())

async def service_list_show(query):
    services = db_fetch_all("SELECT name, display_name, active, emoji_id FROM services ORDER BY name")
    text = "ALL SERVICES\n\n"
    for s in services:
        text += f"• {s[1]} (keyword: {s[0]}) - {'Active' if s[2] else 'Inactive'} | Emoji: {s[3] or 'Not set'}\n"
    await query.edit_message_text(text, reply_markup=admin_back_button())

async def service_toggle_select(query):
    services = db_fetch_all("SELECT name, display_name, active FROM services ORDER BY name")
    rows = []
    for s in services:
        rows.append([InlineKeyboardButton(f"{s[1]} ({'Active' if s[2] else 'Inactive'})", callback_data=f"service_toggle|{s[0]}", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["SERVICE_MANAGER"])])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_service_manager", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"])])
    await query.edit_message_text("Select service to toggle:", reply_markup=InlineKeyboardMarkup(rows))

async def service_toggle_execute(query, service_name):
    result = db_fetch_one("SELECT active FROM services WHERE name = ?", (service_name,))
    if result:
        new_status = 0 if result[0] else 1
        db_exec("UPDATE services SET active = ? WHERE name = ?", (new_status, service_name))
        await query.answer(f"Service {'activated' if new_status else 'deactivated'}!")
    await service_toggle_select(query)

async def service_set_emoji_select(query, user_id):
    if user_id not in admin_mode: await query.answer("Admin mode required!", show_alert=True); return
    services = db_fetch_all("SELECT name, display_name FROM services WHERE active = 1 ORDER BY name")
    rows = []
    for s in services:
        rows.append([InlineKeyboardButton(f"{s[1]} ({s[0]})", callback_data=f"service_emoji_set|{s[0]}", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["SERVICE_MANAGER"])])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_service_manager", style=KBS.PRIMARY, icon_custom_emoji_id=CUSTOM_EMOJIS["BACK"])])
    await query.edit_message_text("Select service to set emoji:", reply_markup=InlineKeyboardMarkup(rows))

async def service_set_emoji_start(query, user_id, service_name):
    admin_temp_data[user_id] = {"set_emoji_service": service_name}
    admin_panel_state[user_id] = "waiting_service_emoji"
    await query.edit_message_text(f"Send custom emoji ID for '{service_name}'.\nSend /skip to keep.", reply_markup=admin_cancel_keyboard())

async def handle_service_emoji_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    service_name = admin_temp_data.get(user_id, {}).get("set_emoji_service")
    if not service_name: await update.message.reply_text("Session expired."); return True
    if text == "/skip": text = ""
    db_exec("UPDATE services SET emoji_id = ? WHERE name = ?", (text, service_name))
    await update.message.reply_text(f"Emoji for {service_name} updated!")
    admin_panel_state[user_id] = "service_manager"
    await service_manager_menu(update, user_id)
    return True

async def service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if user_id not in admin_mode: await query.answer("Admin mode required!", show_alert=True); return
    await query.answer()
    if data == "service_add": await service_add_start(query, user_id)
    elif data == "service_list": await service_list_show(query)
    elif data == "service_toggle": await service_toggle_select(query)
    elif data == "service_set_emoji": await service_set_emoji_select(query, user_id)
    elif data.startswith("service_toggle|"): await service_toggle_execute(query, data.split('|', 1)[1])
    elif data.startswith("service_emoji_set|"): await service_set_emoji_start(query, user_id, data.split('|', 1)[1])

# ==================== FILE UPLOAD ====================
async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in admin_mode or admin_panel_state.get(user_id) != "waiting_file": return
    try:
        document = update.message.document
        if not document.file_name.endswith('.txt'): 
            await update.message.reply_text("Please upload a .txt file!"); return
        file = await context.bot.get_file(document.file_id)
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{document.file_name}"
        await file.download_to_drive(file_path)
        
        count, country, service = load_numbers_from_file(file_path, document.file_name)
        if count > 0:
            emoji_row = db_fetch_one("SELECT emoji_id FROM services WHERE name = ?", (service,))
            if not emoji_row or not emoji_row[0]:
                admin_temp_data[user_id] = {"pending_service_emoji": service, "country": country, "count": count}
                admin_panel_state[user_id] = "waiting_service_emoji_upload"
                await update.message.reply_text(
                    f"✅ {count} numbers loaded for {country} - {service}.\n\n"
                    f"This service ({service}) has no custom emoji set yet.\n"
                    "Please send the custom emoji ID for this service (or /skip).",
                    reply_markup=admin_cancel_keyboard())
                return
            
            msg = stock_added_message(country, service, count)
            await update.message.reply_text(msg, parse_mode='HTML', reply_markup=admin_panel_keyboard())
            
            broadcast_msg = stock_added_broadcast(country, service, count)
            users = db_fetch_all("SELECT user_id FROM users")
            for user in users:
                try:
                    await context.bot.send_message(user[0], broadcast_msg, parse_mode='HTML')
                    await asyncio.sleep(0.05)
                except Exception:
                    continue
            
            admin_panel_state[user_id] = "main"
        else:
            await update.message.reply_text("No valid numbers found in file!", reply_markup=admin_panel_keyboard())
            admin_panel_state[user_id] = "main"
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        admin_panel_state[user_id] = "main"

# ==================== ADMIN TEXT HANDLER ====================
async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = admin_panel_state.get(user_id)
    if user_id not in admin_mode: return False
    text = update.message.text.strip()
    
    if state == "waiting_broadcast":
        users = db_fetch_all("SELECT user_id FROM users")
        sent = 0
        for user in users:
            try:
                await context.bot.send_message(user[0], text, parse_mode='HTML')
                sent += 1
                await asyncio.sleep(0.05)
            except Exception: continue
        admin_panel_state[user_id] = "main"
        await update.message.reply_text(f"Broadcast sent to {sent} users!", reply_markup=admin_panel_keyboard())
        return True
    
    elif state == "waiting_giveaway":
        parts = text.split()
        try:
            target, count = int(parts[0]), int(parts[1]) if len(parts) > 1 else 1
            await update.message.reply_text(f"Given {count} free account(s) to {target}.", reply_markup=admin_panel_keyboard())
            admin_panel_state[user_id] = "main"
        except: await update.message.reply_text("Invalid format!")
        return True
    
    elif state == "waiting_country_add":
        try:
            parts = [p.strip() for p in text.split('|')]
            if len(parts) < 3: await update.message.reply_text("Format: CountryName | Code | ISO | emoji_id"); return True
            name, code, iso, emoji_id = parts[0], parts[1], parts[2].upper(), parts[3] if len(parts) >= 4 else ""
            COUNTRIES_DATA[name] = {"code": code, "iso": iso, "flag": "🏁", "emoji_id": emoji_id}
            save_countries_db(COUNTRIES_DATA)
            admin_panel_state[user_id] = "country_manager"
            flag_id = emoji_id or CUSTOM_EMOJIS["DEFAULT_FLAG"]
            await update.message.reply_text(f'{emoji_tag(flag_id, "🏁")} {name} ADDED SUCCESSFULLY {emoji_tag("4956721670690702265", "✅")}', parse_mode='HTML')
            await country_manager_menu(update, user_id)
        except Exception as e: await update.message.reply_text(f"Error: {e}")
        return True
    
    elif state == "waiting_country_edit":
        if text.strip() == "/skip":
            admin_panel_state[user_id] = "country_manager"
            await update.message.reply_text("No changes.")
            await country_manager_menu(update, user_id)
            return True
        try:
            parts = [p.strip() for p in text.split('|')]
            if len(parts) < 2: await update.message.reply_text("At least Code | ISO required."); return True
            code, iso, emoji_id = parts[0], parts[1].upper(), parts[2] if len(parts) >= 3 else ""
            country_name = admin_temp_data.get(user_id, {}).get("edit_country")
            COUNTRIES_DATA[country_name].update({"code": code, "iso": iso, "emoji_id": emoji_id})
            save_countries_db(COUNTRIES_DATA)
            admin_panel_state[user_id] = "country_manager"
            await update.message.reply_text(f"Country {country_name} updated!")
            await country_manager_menu(update, user_id)
        except Exception as e: await update.message.reply_text(f"Error: {e}")
        return True
    
    elif state == "waiting_service_name":
        try:
            db_exec("INSERT INTO services (name, display_name, active, emoji_id) VALUES (?, ?, 1, '')", (text, text))
            await update.message.reply_text(f"Service {text} added!")
        except sqlite3.IntegrityError: await update.message.reply_text(f"Service {text} already exists!")
        admin_panel_state[user_id] = "service_manager"
        await service_manager_menu(update, user_id)
        return True
    
    elif state == "waiting_service_emoji":
        return await handle_service_emoji_set(update, context)
    
    elif state == "waiting_service_emoji_upload":
        if text.strip() == "/skip": text = ""
        data = admin_temp_data.get(user_id, {})
        service = data.get("pending_service_emoji")
        country = data.get("country")
        count = data.get("count")
        if service:
            db_exec("UPDATE services SET emoji_id = ? WHERE name = ?", (text, service))
        
        msg = stock_added_message(country, service, count)
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=admin_panel_keyboard())
        
        broadcast_msg = stock_added_broadcast(country, service, count)
        users = db_fetch_all("SELECT user_id FROM users")
        for user in users:
            try:
                await context.bot.send_message(user[0], broadcast_msg, parse_mode='HTML')
                await asyncio.sleep(0.05)
            except Exception:
                continue
        
        admin_panel_state[user_id] = "main"
        admin_temp_data.pop(user_id, None)
        return True
    
    return False

# ==================== OTP & CLEANUP ====================
async def monitor_otp_job(context: ContextTypes.DEFAULT_TYPE):
    try:
        if "put your panel api url" in API_URL: return
        response = requests.get(f"{API_URL}?token={API_TOKEN}", timeout=15)
        if response.status_code != 200: return
        data = response.json()
        if not isinstance(data, list): return
        active_numbers = {row[0].replace('+', ''): row[1] for row in db_fetch_all("SELECT number, user_id FROM numbers WHERE status = 'active' AND expiry_time > ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))}
        for item in data:
            if isinstance(item, list) and len(item) >= 3:
                number_clean = item[1].replace('+', '')
                if number_clean in active_numbers:
                    otp = extract_otp_from_message(item[2])
                    if otp and not db_fetch_one('SELECT id FROM otps WHERE number = ? AND otp = ?', (item[1], otp)):
                        db_exec('''INSERT INTO otps (number, otp, message, timestamp, user_id) VALUES (?, ?, ?, ?, ?)''',
                                (item[1], otp, item[2][:200], item[3] if len(item) > 3 else datetime.now().strftime("%Y-%m-%d %H:%M:%S"), active_numbers[number_clean]))
                        try: await context.bot.send_message(active_numbers[number_clean], f"OTP RECEIVED\n\nNumber: {item[1]}\nOTP CODE: {otp}\nService: {item[0]}\nTime: {item[3]}")
                        except: pass
    except Exception as e: print(f"OTP Error: {e}")

async def cleanup_expired_job(context: ContextTypes.DEFAULT_TYPE):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db_exec("UPDATE numbers SET status = 'expired' WHERE expiry_time < ? AND status = 'active'", (now,))
        db_exec("UPDATE users SET current_number=NULL, current_country=NULL, current_service=NULL, number_expiry=NULL WHERE number_expiry < ?", (now,))
    except Exception as e: print(f"Cleanup Error: {e}")

def stock_text():
    data = db_fetch_all("SELECT name, service, stock FROM countries WHERE active = 1 ORDER BY name")
    live_emoji = emoji_tag(CUSTOM_EMOJIS["LIVE_STOCK"], "📊")
    lines = [f'{live_emoji} CURRENT LIVE STOCK {live_emoji}', '━━━━━━━━━━━━━━━━━━━━', '']
    if not data:
        lines.append('No stock available.')
    else:
        for name, service, stock_count in data:
            circle = CUSTOM_EMOJIS["GREEN_CIRCLE"] if stock_count > 0 else CUSTOM_EMOJIS["RED_CIRCLE"]
            lines.append(f'{emoji_tag(circle, "⚪")} {country_flag_emoji(name)} {name} — {service_emoji_tag(service)}: {stock_count}')
    clock_emoji = emoji_tag(CUSTOM_EMOJIS["CLOCK"], "🕐")
    lines.append('')
    lines.append(f'Updated {clock_emoji}: {datetime.now().strftime("%H:%M:%S | %d %B %Y")}')
    return '\n'.join(lines)

# ==================== BOTTOM MENU TEXT ROUTERS ====================
async def send_get_number_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_exec("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    countries = db_fetch_all("SELECT name, service, stock FROM countries WHERE active = 1 AND stock > 0 ORDER BY name")
    if not countries: await update.message.reply_text("No numbers available.", reply_markup=back_to_main_keyboard()); return
    await update.message.reply_text("Select a Country & Service:", reply_markup=countries_keyboard(countries))

async def send_live_stock_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(stock_text(), reply_markup=stock_keyboard(), parse_mode='HTML')

async def send_support_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("CONTACT SUPPORT\n\n━━━━━━━━━━━━━━━━━━━━\nContact admin directly.\n\nDeveloper: RGX NUMBER BOT", reply_markup=support_keyboard())

async def send_admin_panel_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: await update.message.reply_text("Unauthorized!"); return
    admin_mode[user_id] = True
    admin_panel_state[user_id] = "main"
    await update.message.reply_text("ADMIN PANEL\n\nDeveloper: RGX NUMBER BOT", reply_markup=admin_panel_keyboard())

# ==================== GENERIC TEXT HANDLER ====================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if await handle_admin_text(update, context): return
    text = update.message.text.strip()
    if text == BTN_GET_NUMBER: await send_get_number_panel(update, context)
    elif text == BTN_LIVE_STOCK: await send_live_stock_panel(update, context)
    elif text == BTN_SUPPORT: await send_support_panel(update, context)
    elif text == BTN_ADMIN: await send_admin_panel_msg(update, context)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

# ==================== MAIN ====================
def main():
    print("🔥 Developer RGX NUMBER BOT Bot STARTING...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("enteradmin", enter_admin_command))
    application.add_handler(CommandHandler("exitadmin", exit_admin_command))
    application.add_handler(CallbackQueryHandler(refresh_stock_callback, pattern="^refresh_stock$"))
    application.add_handler(CallbackQueryHandler(select_country_callback, pattern=r"^sel\|"))
    application.add_handler(CallbackQueryHandler(next_number_callback, pattern="^next_number$"))
    application.add_handler(CallbackQueryHandler(back_to_countries_callback, pattern="^back_to_countries$"))
    application.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^admin_del\|"))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    application.add_handler(CallbackQueryHandler(country_callback, pattern="^country_"))
    application.add_handler(CallbackQueryHandler(service_callback, pattern="^service_"))
    application.add_handler(CallbackQueryHandler(service_callback, pattern="^service_set_emoji$"))
    application.add_handler(CallbackQueryHandler(service_callback, pattern=r"^service_emoji_set\|"))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file_upload))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_error_handler(error_handler)
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(monitor_otp_job, interval=5, first=5)
        job_queue.run_repeating(cleanup_expired_job, interval=60, first=60)
    print(f"✅ Admin IDs: {ADMIN_IDS}")
    print(f"✅ Loaded {len(COUNTRIES_DATA)} countries")
    print("✅ Custom Emoji System Active")
    print("🔄 Starting polling...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()