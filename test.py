# bot.py — SR NUMBER HUB (Final with custom balance emojis, persistent menu, no inline auto-delete, KBS for all buttons)

import asyncio, json, os, re, sqlite3, threading, tempfile, zipfile, shutil
from datetime import datetime, timedelta

import requests
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, Update, CopyTextButton,
    CallbackQuery
)
from telegram.constants import KeyboardButtonStyle as KBS
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters,
)
from telegram.error import BadRequest

from emoji import CUSTOM_EMOJIS

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8666689980:AAGju2ULiLUA0oCrEdaqsh2Mi6zVNU4ZAL4"
SUPER_ADMIN_IDS = [8744359777]

AUTO_DELETE_DELAY = 2   # seconds (only for plain messages)

OTP_GROUP_URL = "https://t.me/SRotpHub"
MIN_WITHDRAW = 0.1

ADMIN_WHATSAPP = "https://wa.me/8801962636806"
ADMIN_TELEGRAM = "t.me/SR_ADMIN_RAKESH"
ADMIN2_WHATSAPP = ""
ADMIN2_TELEGRAM = ""

GROUP_ID = -1004380384761
CHANNEL_URL = "https://t.me/your_channel"
BOT_URL = "https://t.me/your_bot"

# Emoji constants for group OTP
EMOJI_PREFIX = "4958725487682650920"
EMOJI_SEPARATOR = "6307542847251814164"
EMOJI_OTP_BUTTON = "6206420230269310869"
EMOJI_CHANNEL_BUTTON = "6204010762206189094"
EMOJI_BOT_BUTTON = "5339267587337370029"

# Emoji for expandable SMS
LEFT_ARROW_EMOJI = "6068830682359010545"   # 👈
SEND_EMOJI = "5433614747381538714"         # 📤

# ==================== CUSTOM EMOJIS ADDITIONS ====================
CUSTOM_EMOJIS["USER_MANAGER"] = "6307777408300753473"
CUSTOM_EMOJIS["SEARCH_USER"] = "6206446249181189526"
CUSTOM_EMOJIS["DOWNLOAD_LIST"] = "6203886371363364022"
CUSTOM_EMOJIS["EDIT_BALANCE"] = "6204162490515855272"
CUSTOM_EMOJIS["BAN_USER"] = "6203761490894264678"
CUSTOM_EMOJIS["MANAGE_API"] = "6206188632747808299"
CUSTOM_EMOJIS["ADD_API_KEY"] = "6206375377925839184"
CUSTOM_EMOJIS["REMOVE_API_KEY"] = "6206108815075579644"
CUSTOM_EMOJIS["LIST_API_KEY"] = "6307686831735444755"
CUSTOM_EMOJIS["SUPPORT"] = "5208573502046610594"
CUSTOM_EMOJIS["SELECT_SERVICE_PREFIX"] = "6206236607532504295"
CUSTOM_EMOJIS["SELECT_SERVICE_SUFFIX"] = "5197474438970363734"
CUSTOM_EMOJIS["SELECT_COUNTRY_PREFIX"] = "5309748255637118475"
CUSTOM_EMOJIS["PROFILE_ICON"] = "5818715087237549366"

# ==================== DATABASE FOLDER ====================
DB_DIR = "NUMBER-PANEL-DATA"
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "mrisbrand_master.db")
USER_DATA_FILE = os.path.join(DB_DIR, "user_data.json")

# ==================== DATABASE SETUP ====================
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
db_lock = threading.Lock()
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
              joined_date TEXT, last_active TEXT,
              current_number_id INTEGER DEFAULT NULL,
              current_number TEXT DEFAULT NULL, current_country TEXT DEFAULT NULL,
              current_service TEXT DEFAULT NULL, number_expiry TEXT DEFAULT NULL,
              last_menu_message_id INTEGER DEFAULT NULL,
              last_bot_message_id INTEGER DEFAULT NULL,
              remove_cc INTEGER DEFAULT 0,
              banned INTEGER DEFAULT 0)''')

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

c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_countries_name_service ON countries(name, service)")

c.execute('''CREATE TABLE IF NOT EXISTS available_numbers
             (id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, service TEXT,
              number TEXT, used INTEGER DEFAULT 0)''')

c.execute('''CREATE TABLE IF NOT EXISTS used_numbers
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, number TEXT,
              country TEXT, service TEXT, assigned_date TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS services
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE,
              display_name TEXT, active INTEGER DEFAULT 1, emoji_id TEXT DEFAULT '')''')

c.execute('''CREATE TABLE IF NOT EXISTS admins
             (user_id INTEGER PRIMARY KEY)''')
c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (8744359777)")

c.execute('''CREATE TABLE IF NOT EXISTS group_emojis
             (type TEXT, key TEXT, emoji_id TEXT, PRIMARY KEY(type, key))''')

c.execute('''CREATE TABLE IF NOT EXISTS api_keys
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              panel_name TEXT,
              base_url TEXT,
              token TEXT,
              interval_sec INTEGER,
              active INTEGER DEFAULT 1)''')

# Add missing columns
try:
    c.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0")
except sqlite3.OperationalError: pass
try:
    c.execute("ALTER TABLE users ADD COLUMN withdrawn REAL DEFAULT 0")
except sqlite3.OperationalError: pass
try:
    c.execute("ALTER TABLE users ADD COLUMN total_otp INTEGER DEFAULT 0")
except sqlite3.OperationalError: pass
try:
    c.execute("ALTER TABLE users ADD COLUMN remove_cc INTEGER DEFAULT 0")
except sqlite3.OperationalError: pass
try:
    c.execute("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0")
except sqlite3.OperationalError: pass
try:
    c.execute("ALTER TABLE users ADD COLUMN last_bot_message_id INTEGER DEFAULT NULL")
except sqlite3.OperationalError: pass
try:
    c.execute("ALTER TABLE services ADD COLUMN emoji_id TEXT DEFAULT ''")
except sqlite3.OperationalError: pass
try:
    c.execute("ALTER TABLE users ADD COLUMN keyboard_message_id INTEGER DEFAULT NULL")
except sqlite3.OperationalError: pass

default_services = ["WhatsApp", "Telegram", "Facebook", "IMO", "Google", "Tinder", "Uber", "Instagram", "Twitter", "Snapchat"]
for service in default_services:
    c.execute("INSERT OR IGNORE INTO services (name, display_name, active, emoji_id) VALUES (?, ?, 1, '')", (service, service))

conn.commit()
print("✅ Database setup completed")

# ==================== STATE TRACKING ====================
admin_mode = {}
admin_panel_state = {}
admin_temp_data = {}
last_activation_data = {}

def safe_url(url: str) -> str | None:
    if url and isinstance(url, str) and (url.startswith("http://") or url.startswith("https://") or url.startswith("tg://")):
        return url
    return None

def safe_icon(emoji_id: str) -> str | None:
    if emoji_id and isinstance(emoji_id, str) and emoji_id.isdigit() and len(emoji_id) > 9:
        return emoji_id
    return None

def parse_payout(payout_str: str) -> float:
    if not payout_str:
        return 0.001
    return float(payout_str.replace('$', '').strip())

# ==================== LOAD COUNTRIES FROM JSON ====================
def load_countries_db():
    try:
        with open('countries.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for name, info in data.items():
                if "emoji_id" not in info:
                    info["emoji_id"] = ""
                if "payout" not in info:
                    info["payout"] = "0.001$"
                if "iso" not in info:
                    info["iso"] = name[:2].upper()
            return data
    except FileNotFoundError:
        default = {
            "Pakistan": {"code": "+92", "iso": "PK", "payout": "0.001$", "emoji_id": ""},
            "India": {"code": "+91", "iso": "IN", "payout": "0.001$", "emoji_id": ""},
            "Venezuela": {"code": "+58", "iso": "VE", "payout": "0.001$", "emoji_id": ""},
            "Nigeria": {"code": "+234", "iso": "NG", "payout": "0.001$", "emoji_id": ""},
        }
        with open('countries.json', 'w', encoding='utf-8') as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        return default

def save_countries_db(data):
    with open('countries.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

COUNTRIES_DATA = load_countries_db()

def get_country_info(country_name):
    return COUNTRIES_DATA.get(country_name, {"emoji_id": "", "payout": "0.001$", "iso": country_name[:2].upper()})

# ==================== DEFAULT EMOJIS ====================
DEFAULT_EMOJIS = {
    "services": {
        "uber": "5298715455316303708",
        "bolt": "5343587658717219067",
        "whatsapp": "5298715455316303708",
        "telegram": "5339267587337370029",
        "casushi": "5346008706012169915",
    },
    "countries": {
        "gb": "5293993521026453119",
        "af": "5292108962391414885",
    }
}

# ==================== CUSTOM EMOJI HTML HELPER ====================
def emoji_tag(emoji_id: str, fallback: str = " ") -> str:
    if not emoji_id or not emoji_id.isdigit() or len(emoji_id) < 10:
        return fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

def country_flag_emoji(country_name: str) -> str:
    eid = get_country_info(country_name).get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
    return emoji_tag(eid, "🏁")

def service_emoji_tag(service_name: str) -> str:
    row = db_fetch_one("SELECT emoji_id FROM services WHERE LOWER(name) = LOWER(?)", (service_name,))
    eid = row[0] if row and row[0] else CUSTOM_EMOJIS.get("DEFAULT_SERVICE", "")
    return emoji_tag(eid, "⚙️")

# ==================== KEYBOARD BUILDERS ====================
BTN_GET_NUMBER = "Get Number"
BTN_BALANCE = "Balance"
BTN_SUPPORT = "Support"
BTN_ADMIN = "Admin Panel"

def bottom_menu_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    rows = [
        [
            KeyboardButton(BTN_GET_NUMBER, style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("GET_NUMBER", ""))),
            KeyboardButton(BTN_BALANCE, style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon("5312123810638483121")),
        ],
        [
            KeyboardButton(BTN_SUPPORT, style=KBS.SUCCESS, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("SUPPORT", "")))
        ],
    ]
    if is_admin(user_id):
        rows.append([KeyboardButton(BTN_ADMIN, style=KBS.DANGER, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADMIN", "")))])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True,
                               input_field_placeholder="Choose an option...")

def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Back to Main Menu", callback_data="back_to_menu", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))),
    ]])

def services_keyboard() -> InlineKeyboardMarkup:
    services = db_fetch_all("SELECT name, display_name, emoji_id FROM services WHERE active = 1 ORDER BY name")
    if not services:
        return back_to_main_keyboard()
    rows = []
    row = []
    for s in services:
        btn = InlineKeyboardButton(
            text=s[1],
            callback_data=f"svc_sel|{s[0]}",
            style=KBS.PRIMARY,
            icon_custom_emoji_id=safe_icon(s[2]) if s[2] else None
        )
        row.append(btn)
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("Back to Main Menu", callback_data="back_to_menu", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    return InlineKeyboardMarkup(rows)

def countries_for_service_keyboard(service: str) -> InlineKeyboardMarkup:
    countries = db_fetch_all(
        "SELECT name, stock FROM countries WHERE service = ? AND active = 1 AND stock > 0 ORDER BY name",
        (service,)
    )
    if not countries:
        return back_to_main_keyboard()
    rows = []
    for name, stock in countries:
        info = get_country_info(name)
        flag_eid = info.get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
        payout = info.get("payout", "0.001$")
        label = f"{name} — {payout} — ({stock})"
        rows.append([InlineKeyboardButton(
            label,
            callback_data=f"cnt_sel|{name}|{service}",
            style=KBS.SUCCESS,
            icon_custom_emoji_id=safe_icon(flag_eid)
        )])
    rows.append([InlineKeyboardButton("Back to Services", callback_data="menu_get_number", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    return InlineKeyboardMarkup(rows)

def support_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    if ADMIN_WHATSAPP:
        buttons.append(InlineKeyboardButton("Admin WH", url=ADMIN_WHATSAPP, style=KBS.SUCCESS,
                                            icon_custom_emoji_id=safe_icon("5334998226636390258")))
    if ADMIN_TELEGRAM:
        buttons.append(InlineKeyboardButton("Admin TG", url=ADMIN_TELEGRAM, style=KBS.PRIMARY,
                                            icon_custom_emoji_id=safe_icon("5330237710655306682")))
    if ADMIN2_WHATSAPP:
        buttons.append(InlineKeyboardButton("Admin2 WH", url=ADMIN2_WHATSAPP, style=KBS.SUCCESS,
                                            icon_custom_emoji_id=safe_icon("5334998226636390258")))
    if ADMIN2_TELEGRAM:
        buttons.append(InlineKeyboardButton("Admin2 TG", url=ADMIN2_TELEGRAM, style=KBS.PRIMARY,
                                            icon_custom_emoji_id=safe_icon("5330237710655306682")))
    if not buttons:
        buttons = [InlineKeyboardButton("No support available", callback_data="noop")]
    return InlineKeyboardMarkup([buttons])

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    # Removed: Delete Stock, Give Account, Exit Admin
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("User Manager", callback_data="admin_user_manager", style=KBS.PRIMARY,
                                 icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("USER_MANAGER", ""))),
            InlineKeyboardButton("Upload Stock", callback_data="admin_upload", style=KBS.SUCCESS,
                                 icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("UPLOAD", ""))),
        ],
        [
            InlineKeyboardButton("Broadcast", callback_data="admin_broadcast", style=KBS.PRIMARY,
                                 icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BROADCAST", ""))),
            InlineKeyboardButton("Country Manager", callback_data="admin_country_manager", style=KBS.PRIMARY,
                                 icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("COUNTRY_MANAGER", ""))),
        ],
        [
            InlineKeyboardButton("Service Manager", callback_data="admin_service_manager", style=KBS.PRIMARY,
                                 icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("SERVICE_MANAGER", ""))),
            InlineKeyboardButton("Manage API", callback_data="admin_manage_api", style=KBS.SUCCESS,
                                 icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("MANAGE_API", ""))),
        ],
        [
            InlineKeyboardButton("Database", callback_data="admin_database", style=KBS.SUCCESS,
                                 icon_custom_emoji_id=safe_icon("6206236607532504295")),
        ],
        [
            InlineKeyboardButton("Back to Main Menu", callback_data="back_to_menu", style=KBS.PRIMARY,
                                 icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))),
        ],
    ])

def admin_back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.PRIMARY,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))),
    ]])

def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Cancel", callback_data="admin_back", style=KBS.DANGER,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CANCEL", ""))),
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

def ensure_user(user_id, username, first_name):
    db_exec('''INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date, last_active)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, username, first_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def extract_country_from_filename(filename):
    try:
        name = filename.replace('.txt', '')
        if '_' in name:
            country_part = name.split('_')[0].strip()
        else:
            country_part = name.strip()
        for country_name in COUNTRIES_DATA.keys():
            if country_name.lower() == country_part.lower():
                return country_name
        for country_name in COUNTRIES_DATA.keys():
            if country_part.lower().startswith(country_name.lower()) or country_name.lower().startswith(country_part.lower()):
                return country_name
        for country_name in COUNTRIES_DATA.keys():
            if country_name.lower() in country_part.lower() or country_part.lower() in country_name.lower():
                return country_name
        return country_part
    except Exception:
        return None

def extract_service_from_filename(filename):
    try:
        name = filename.replace('.txt', '').lower()
        if '_' in name:
            service_part = name.split('_', 1)[1].strip()
        else:
            return "Unknown"
        services = db_fetch_all("SELECT name FROM services WHERE active = 1")
        for service in services:
            if service[0].lower() in service_part:
                return service[0]
        return service_part
    except Exception:
        return "Unknown"

def load_numbers_from_file(file_path, filename, force_country=None, force_service=None):
    try:
        if force_country and force_service:
            country = force_country
            service = force_service
        else:
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
                         ORDER BY id ASC LIMIT ?''', (country, service, take))
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

def format_numbers_message(country, service, numbers, user_id=None, first_name=None):
    if first_name is None:
        first_name = "User"
    remove_cc = 0
    if user_id:
        row = db_fetch_one("SELECT remove_cc FROM users WHERE user_id = ?", (user_id,))
        if row:
            remove_cc = row[0] or 0

    flag_eid = get_country_info(country).get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
    country_code = get_country_info(country).get("code", "")
    service_eid_row = db_fetch_one("SELECT emoji_id FROM services WHERE LOWER(name) = LOWER(?)", (service,))
    service_eid = service_eid_row[0] if service_eid_row and service_eid_row[0] else CUSTOM_EMOJIS.get("DEFAULT_SERVICE", "")

    phone_icon_id = "5197474438970363734"

    header = (
        f'{emoji_tag(phone_icon_id, "📱")} <b>THIS IS YOUR</b> <b>{country}</b> '
        f'{country_flag_emoji(country)} <b>NUMBERS</b> {emoji_tag(phone_icon_id, "📱")}\n\n'
    )
    rows = []
    flag_unicode = ISO_TO_INFO.get(get_country_code(country), ("🏳", ""))[0] if get_country_code(country) else "🏳"
    for number in numbers:
        display_num = number
        copy_num = number
        if remove_cc == 1 and country_code and number.startswith(country_code):
            display_num = number[len(country_code):]
            copy_num = display_num
        btn_text = f'{flag_unicode} | {display_num}'
        rows.append([InlineKeyboardButton(
            text=btn_text,
            copy_text=CopyTextButton(text=copy_num),
            style=KBS.PRIMARY,
            icon_custom_emoji_id=safe_icon(service_eid)
        )])

    if remove_cc == 1:
        cc_button = InlineKeyboardButton("ADD CC", callback_data="toggle_cc",
                                         style=KBS.SUCCESS,
                                         icon_custom_emoji_id=safe_icon("4956507094124594921"))
    else:
        cc_button = InlineKeyboardButton("REMOVE CC", callback_data="toggle_cc",
                                         style=KBS.DANGER,
                                         icon_custom_emoji_id=safe_icon("4956337889593000947"))
    rows.append([cc_button])

    rows.append([
        InlineKeyboardButton("New Number", callback_data="next_number", style=KBS.SUCCESS,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("NEW_NUMBER", ""))),
        InlineKeyboardButton("Change Service", callback_data="back_to_services", style=KBS.SUCCESS,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CHANGE_COUNTRY", ""))),
    ])
    rows.append([
        InlineKeyboardButton("OTP Group", url=OTP_GROUP_URL, style=KBS.DANGER,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("JOIN_OTP_GROUP", ""))),
    ])
    return header, InlineKeyboardMarkup(rows)

def stock_added_message(country, service, count):
    flag_eid = get_country_info(country).get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
    svc_eid_row = db_fetch_one("SELECT emoji_id FROM services WHERE name = ?", (service,))
    svc_eid = svc_eid_row[0] if svc_eid_row and svc_eid_row[0] else CUSTOM_EMOJIS.get("DEFAULT_SERVICE", "")
    return (
        f'{emoji_tag("4958617898751886363", "📊")} <b>STOCK</b> {emoji_tag("5463412319948148591", "📦")} <b>ADDED SUCCESSFULLY</b> {emoji_tag("4956721670690702265", "✅")}\n\n'
        f'<b>NUMBER</b> {emoji_tag("6204108584381322968", "📱")} : <b>{count}</b>\n'
        f'<b>COUNTRY</b> {emoji_tag("5188540541922480562", "🌍")} : {emoji_tag(flag_eid, "🏁")}\n'
        f'<b>SERVICE</b> {emoji_tag("5465590345108589516", "🔧")} : {emoji_tag(svc_eid, "⚙️")}'
    )

def stock_added_broadcast(country, service, count):
    flag_eid = get_country_info(country).get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
    svc_eid_row = db_fetch_one("SELECT emoji_id FROM services WHERE name = ?", (service,))
    svc_eid = svc_eid_row[0] if svc_eid_row and svc_eid_row[0] else CUSTOM_EMOJIS.get("DEFAULT_SERVICE", "")
    return (
        f'{emoji_tag("4958617898751886363", "📊")} <b>STOCK</b> {emoji_tag("5463412319948148591", "📦")} <b>ADDED SUCCESSFULLY</b> {emoji_tag("4956721670690702265", "✅")}\n\n'
        f'<b>NUMBER</b> {emoji_tag("6204108584381322968", "📱")} : <b>{count}</b>\n'
        f'<b>COUNTRY</b> {emoji_tag("5188540541922480562", "🌍")} : {emoji_tag(flag_eid, "🏁")}\n'
        f'<b>SERVICE</b> {emoji_tag("5465590345108589516", "🔧")} : {emoji_tag(svc_eid, "⚙️")}'
    )

# ==================== WELCOME HTML ====================
def welcome_html(user_id, first_name):
    spark = CUSTOM_EMOJIS.get("WELCOME_SPARKLE", "")
    rocket = CUSTOM_EMOJIS.get("ROCKET", "")
    id_icon = CUSTOM_EMOJIS.get("ID_ICON", "")
    check = CUSTOM_EMOJIS.get("CHECK_MARK", "")
    gamepad = CUSTOM_EMOJIS.get("GAMEPAD", "")
    return (
        f'{emoji_tag(spark, "✨")} Welcome to SR NUMBER HUB, {first_name}! {emoji_tag(spark, "✨")}\n\n'
        f'{emoji_tag(rocket, "🚀")} Your Premium Platform for Virtual Numbers.\n\n'
        f'{emoji_tag(id_icon, "🆔")} Your ID: <code>{user_id}</code>\n'
        f'{emoji_tag(check, "✅")} You are a Verified Member!\n\n'
        f'{emoji_tag(gamepad, "🎮")} Tap a button below to navigate.\n\n'
        '━━━━━━━━━━━━━━━━━━━━\n'
        '👨‍💻 Developer: SR NUMBER HUB'
    )

# ==================== AUTO-CLEAN HELPERS ====================
async def delete_previous_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        if update.message:
            await update.message.delete()
    except:
        pass
    row = db_fetch_one("SELECT last_bot_message_id FROM users WHERE user_id=?", (user_id,))
    if row and row[0]:
        kb_id_row = db_fetch_one("SELECT keyboard_message_id FROM users WHERE user_id=?", (user_id,))
        kb_id = kb_id_row[0] if kb_id_row else None
        if row[0] != kb_id:
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=row[0])
            except:
                pass
        db_exec("UPDATE users SET last_bot_message_id=NULL WHERE user_id=?", (user_id,))

async def schedule_delete(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int = AUTO_DELETE_DELAY):
    if context.job_queue:
        context.job_queue.run_once(
            lambda ctx: ctx.bot.delete_message(chat_id=chat_id, message_id=message_id),
            when=delay
        )

async def send_clean_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None, parse_mode=None, auto_delete: bool = True, persistent_menu: bool = True):
    user_id = update.effective_user.id
    await delete_previous_messages(update, context)
    
    if persistent_menu and not isinstance(reply_markup, InlineKeyboardMarkup):
        reply_markup = bottom_menu_keyboard(user_id)
    
    sent = await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?", (sent.message_id, user_id))
    
    if isinstance(reply_markup, ReplyKeyboardMarkup):
        old_kb_id_row = db_fetch_one("SELECT keyboard_message_id FROM users WHERE user_id=?", (user_id,))
        old_kb_id = old_kb_id_row[0] if old_kb_id_row else None
        if old_kb_id and old_kb_id != sent.message_id:
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=old_kb_id)
            except:
                pass
        db_exec("UPDATE users SET keyboard_message_id=? WHERE user_id=?", (sent.message_id, user_id))
    
    # Only auto-delete if reply_markup is None (no inline, no reply keyboard)
    if auto_delete and reply_markup is None:
        await schedule_delete(context, user_id, sent.message_id)
    return sent

# ==================== SAFE EDIT / SEND FALLBACK ====================
async def edit_or_send(query: CallbackQuery, text: str, reply_markup=None, parse_mode=None, context: ContextTypes.DEFAULT_TYPE = None, auto_delete: bool = True, persistent_menu: bool = False):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        if auto_delete and context and reply_markup is None:
            await schedule_delete(context, query.message.chat_id, query.message.message_id)
        return None
    except BadRequest as e:
        if "Message is not modified" in str(e):
            return None
        if context and context.bot:
            user_id = query.from_user.id
            try:
                await query.message.delete()
            except:
                pass
            
            if persistent_menu and not isinstance(reply_markup, InlineKeyboardMarkup):
                reply_markup = bottom_menu_keyboard(user_id)
            
            sent = await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?",
                    (sent.message_id, user_id))
            
            if isinstance(reply_markup, ReplyKeyboardMarkup):
                old_kb_id_row = db_fetch_one("SELECT keyboard_message_id FROM users WHERE user_id=?", (user_id,))
                old_kb_id = old_kb_id_row[0] if old_kb_id_row else None
                if old_kb_id and old_kb_id != sent.message_id:
                    try:
                        await context.bot.delete_message(chat_id=user_id, message_id=old_kb_id)
                    except:
                        pass
                db_exec("UPDATE users SET keyboard_message_id=? WHERE user_id=?", (sent.message_id, user_id))
            
            if auto_delete and reply_markup is None:
                await schedule_delete(context, query.message.chat_id, sent.message_id)
            return sent
        return None

async def safe_edit_message(query, text, **kwargs):
    try:
        await query.edit_message_text(text, **kwargs)
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            raise

# ==================== REPLY OR EDIT ====================
async def reply_or_edit(target, text: str, reply_markup=None, parse_mode=None, context: ContextTypes.DEFAULT_TYPE = None, auto_delete: bool = True, persistent_menu: bool = False):
    if isinstance(target, CallbackQuery):
        await edit_or_send(target, text, reply_markup=reply_markup, parse_mode=parse_mode, context=context, auto_delete=auto_delete, persistent_menu=persistent_menu)
    elif hasattr(target, 'callback_query') and target.callback_query:
        await edit_or_send(target.callback_query, text, reply_markup=reply_markup, parse_mode=parse_mode, context=context, auto_delete=auto_delete, persistent_menu=persistent_menu)
    else:
        if context:
            await send_clean_message(target, context, text, reply_markup=reply_markup, parse_mode=parse_mode, auto_delete=auto_delete, persistent_menu=persistent_menu)
        else:
            if hasattr(target, 'message') and target.message:
                await target.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)

# ==================== START COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await ban_check(update, context):
        return
    username = update.effective_user.username
    first_name = update.effective_user.first_name or "User"
    ensure_user(user_id, username, first_name)
    db_exec("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    await delete_previous_messages(update, context)
    sent = await update.message.reply_text(welcome_html(user_id, first_name), reply_markup=bottom_menu_keyboard(user_id), parse_mode='HTML')
    db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?", (sent.message_id, user_id))
    db_exec("UPDATE users SET keyboard_message_id=? WHERE user_id=?", (sent.message_id, user_id))

# ==================== BAN CHECK ====================
async def ban_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    banned = db_fetch_one("SELECT banned FROM users WHERE user_id=?", (user_id,))
    if banned and banned[0]:
        text = (
            f'{emoji_tag("6206077285720659346", "🚫")} <b>Now You Can\'t Use Me</b> {emoji_tag("6206003549722122915", "😢")}\n'
            f'{emoji_tag("6206267591426578467", "📞")} <b>CONTACT TO SUPPORT ADMINS</b> {emoji_tag("6206319341487527808", "👨‍💼")}'
        )
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text, reply_markup=support_keyboard(), parse_mode='HTML')
        else:
            await update.message.reply_text(text, reply_markup=support_keyboard(), parse_mode='HTML')
        return True
    return False

# ==================== ADMIN CHECKS ====================
def is_admin(user_id):
    return db_fetch_one("SELECT user_id FROM admins WHERE user_id=?", (user_id,)) is not None

def is_super_admin(user_id):
    return user_id in SUPER_ADMIN_IDS

# ==================== MAIN MENU CALLBACKS ====================
async def show_main_menu(update: Update, user_id, first_name, context: ContextTypes.DEFAULT_TYPE = None):
    ensure_user(user_id, update.effective_user.username, first_name)
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, welcome_html(user_id, first_name), reply_markup=None, parse_mode='HTML', context=context, persistent_menu=True)
    else:
        if context:
            await send_clean_message(update, context, welcome_html(user_id, first_name), reply_markup=None, parse_mode='HTML', persistent_menu=True)

async def show_get_number(update: Update, context, user_id, first_name):
    ensure_user(user_id, update.effective_user.username, first_name)
    db_exec("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_PREFIX"], "🔧")} <b>Select service</b> '
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_SUFFIX"], "📱")}'
    )
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, text, reply_markup=services_keyboard(), parse_mode='HTML', context=context)
    else:
        await send_clean_message(update, context, text, reply_markup=services_keyboard(), parse_mode='HTML')

async def show_balance(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE = None):
    ensure_user(user_id, update.effective_user.username, update.effective_user.first_name)
    user = db_fetch_one("SELECT first_name, balance, withdrawn, total_otp FROM users WHERE user_id = ?", (user_id,))
    if not user:
        return
    first_name, balance, withdrawn, total_otp = user
    balance = balance or 0.0
    withdrawn = withdrawn or 0.0
    total_otp = total_otp or 0

    # Custom emoji IDs for balance
    emoji_clipboard = "4958506272551863292"   # 📋
    emoji_id = "5197269100878907942"          # 🆔
    emoji_money = "4958926882994127612"       # 💰
    emoji_withdraw = "5445221832074483553"    # 💸
    emoji_warning = "4958534696645428119"     # ⚠️
    emoji_inbox = "5197288647275071607"       # 📨

    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["PROFILE_ICON"], "👤")} '
        f'<a href="tg://user?id={user_id}">{first_name}</a> YOUR DETAILS {emoji_tag(emoji_clipboard, "📋")}\n'
        f'------------------------------------------------\n'
        f'<blockquote><b>{emoji_tag(emoji_id, "🆔")} USER ID: <code>{user_id}</code></b></blockquote>\n'
        f'<blockquote><b>{emoji_tag(emoji_money, "💰")} BALANCE: <code>${balance:.3f}</code></b></blockquote>\n'
        f'<blockquote><b>{emoji_tag(emoji_withdraw, "💸")} WITHDRAWED: <code>${withdrawn:.3f}</code></b></blockquote>\n'
        f'<blockquote><b>{emoji_tag(emoji_warning, "⚠️")} MINIMUM WITHDRAW: <code>$0.1</code></b></blockquote>\n'
        f'<blockquote><b>{emoji_tag(emoji_inbox, "📨")} TOTAL OTP: <code>{total_otp}</code></b></blockquote>'
    )
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"WITHDRAW", callback_data="withdraw", style=KBS.SUCCESS,
                             icon_custom_emoji_id=safe_icon("5445353829304387411"))
    ]])
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, text, reply_markup=kb, parse_mode='HTML', context=context)
    else:
        if context:
            await send_clean_message(update, context, text, reply_markup=kb, parse_mode='HTML')

async def show_withdraw(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE = None):
    ensure_user(user_id, update.effective_user.username, update.effective_user.first_name)
    balance = db_fetch_one("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    if not balance:
        return
    balance = balance[0] or 0.0
    if balance >= MIN_WITHDRAW:
        text = (
            f'{emoji_tag("4956290155326473271", "📞")} PLEASE CONTACT TO ADMIN {emoji_tag("4956420911310832630", "👨‍💼")}\n\n'
            f'{emoji_tag("4958926882994127612", "💰")} BALANCE: ${balance:.3f}\n'
        )
        kb_buttons = []
        if ADMIN_WHATSAPP:
            kb_buttons.append([InlineKeyboardButton("ADMIN WH", url=ADMIN_WHATSAPP, style=KBS.SUCCESS,
                                                    icon_custom_emoji_id=safe_icon("5334998226636390258"))])
        if ADMIN_TELEGRAM:
            kb_buttons.append([InlineKeyboardButton("ADMIN TG", url=ADMIN_TELEGRAM, style=KBS.PRIMARY,
                                                    icon_custom_emoji_id=safe_icon("5330237710655306682"))])
        if ADMIN2_WHATSAPP:
            kb_buttons.append([InlineKeyboardButton("ADMIN2 WH", url=ADMIN2_WHATSAPP, style=KBS.SUCCESS,
                                                    icon_custom_emoji_id=safe_icon("5334998226636390258"))])
        if ADMIN2_TELEGRAM:
            kb_buttons.append([InlineKeyboardButton("ADMIN2 TG", url=ADMIN2_TELEGRAM, style=KBS.PRIMARY,
                                                    icon_custom_emoji_id=safe_icon("5330237710655306682"))])
        kb = InlineKeyboardMarkup(kb_buttons) if kb_buttons else None
    else:
        need = round(MIN_WITHDRAW - balance, 3)
        text = (
            f'{emoji_tag("4956611513369494230", "🔻")} YOUR MAIN BALANCE IS LOW{emoji_tag("4956387556594811916", "😞")}\n\n'
            f'{emoji_tag("4958534696645428119", "⚠️")} MINIMUM WITHDRAW: $0.1\n'
            f'{emoji_tag("4958926882994127612", "💰")} YOUR CURRENT BALANCE: ${balance:.3f}\n'
            f'{emoji_tag("4958642964181025908", "🧾")} NEED: ${need:.3f}\n\n'
            f'{emoji_tag("4958503072801228000", "📢")} KINDLY GRAB SOME OTP TO WITHDRAW YOU BALANCE {emoji_tag("4956721670690702265", "✅")}'
        )
        kb = None
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, text, reply_markup=kb, parse_mode='HTML', context=context)
    else:
        if context:
            await send_clean_message(update, context, text, reply_markup=kb, parse_mode='HTML')

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    text = "CONTACT SUPPORT\n\n━━━━━━━━━━━━━━━━━━━━\nFor any issues, contact admin directly.\n\nDeveloper: SR NUMBER HUB"
    if isinstance(update, CallbackQuery):
        user_id = update.effective_user.id
        # Send inline support message
        await edit_or_send(update, text, reply_markup=support_keyboard(), context=context, auto_delete=False)
        # Ensure reply keyboard anchor exists
        kb_id_row = db_fetch_one("SELECT keyboard_message_id FROM users WHERE user_id=?", (user_id,))
        if not kb_id_row or not kb_id_row[0]:
            anchor = await context.bot.send_message(chat_id=user_id, text="Main Menu", reply_markup=bottom_menu_keyboard(user_id))
            db_exec("UPDATE users SET keyboard_message_id=? WHERE user_id=?", (anchor.message_id, user_id))
    else:
        if context:
            await send_clean_message(update, context, text, reply_markup=None, persistent_menu=True)

async def send_support_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = "CONTACT SUPPORT\n\n━━━━━━━━━━━━━━━━━━━━\nFor any issues, contact admin directly.\n\nDeveloper: SR NUMBER HUB"
    # First ensure reply keyboard anchor
    kb_id_row = db_fetch_one("SELECT keyboard_message_id FROM users WHERE user_id=?", (user_id,))
    if kb_id_row and kb_id_row[0]:
        anchor_id = kb_id_row[0]
    else:
        anchor = await context.bot.send_message(chat_id=user_id, text="Main Menu", reply_markup=bottom_menu_keyboard(user_id))
        anchor_id = anchor.message_id
        db_exec("UPDATE users SET keyboard_message_id=? WHERE user_id=?", (anchor_id, user_id))
    # Now send inline support message
    sent_inline = await context.bot.send_message(chat_id=user_id, text=text, reply_markup=support_keyboard())
    db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?", (sent_inline.message_id, user_id))

# ==================== ADMIN COMMANDS ====================
async def enter_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_admin(user_id):
        admin_mode[user_id] = True
        admin_panel_state[user_id] = "main"
        await send_clean_message(update, context, "ADMIN PANEL\n\nDeveloper: SR NUMBER HUB\n\nSelect an action below:", reply_markup=admin_panel_keyboard(), auto_delete=False)
    else:
        await update.message.reply_text("Unauthorized access!")

async def exit_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in admin_mode:
        admin_mode.pop(user_id, None)
        admin_panel_state.pop(user_id, None)
        await send_clean_message(update, context, "Admin mode deactivated!", reply_markup=bottom_menu_keyboard(user_id))
    else:
        await update.message.reply_text("You're not in admin mode!")

async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_super_admin(user_id):
        await update.message.reply_text("⛔ Only super admins can add new admins.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /addadmin <user_id>")
        return
    try:
        target_uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return
    db_exec("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (target_uid,))
    await update.message.reply_text(f"✅ User {target_uid} has been added as an admin.")

async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_super_admin(user_id):
        await update.message.reply_text("⛔ Only super admins can remove admins.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeadmin <user_id>")
        return
    try:
        target_uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return
    if target_uid in SUPER_ADMIN_IDS:
        await update.message.reply_text("⛔ Cannot remove a super admin.")
        return
    db_exec("DELETE FROM admins WHERE user_id = ?", (target_uid,))
    admin_mode.pop(target_uid, None)
    admin_panel_state.pop(target_uid, None)
    await update.message.reply_text(f"❌ User {target_uid} has been removed from admin list.")

async def admin_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Unauthorized.")
        return
    admins = db_fetch_all("SELECT user_id FROM admins")
    if not admins:
        await update.message.reply_text("No admins found.")
        return
    lines = ["**📋 Admin List:**\n"]
    for (uid,) in admins:
        super_label = " (Super)" if uid in SUPER_ADMIN_IDS else ""
        lines.append(f"• {uid}{super_label}")
    await update.message.reply_text("\n".join(lines))

# ==================== ADMIN PANEL MENU ====================
async def admin_panel_menu(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE = None):
    if not is_admin(user_id):
        if isinstance(update, CallbackQuery):
            await update.answer("Unauthorized!", show_alert=True)
        else:
            await update.message.reply_text("Unauthorized!")
        return
    admin_mode[user_id] = True
    admin_panel_state[user_id] = "main"
    text = "ADMIN PANEL\n\nDeveloper: SR NUMBER HUB\n\nSelect an action below:"
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, text, reply_markup=admin_panel_keyboard(), context=context, auto_delete=False)
    else:
        if context:
            await send_clean_message(update, context, text, reply_markup=admin_panel_keyboard(), auto_delete=False)

# ==================== USER DATA JSON SAVE/LOAD ====================
def save_user_data_json():
    users = db_fetch_all("SELECT user_id, username, first_name, joined_date, last_active, balance, withdrawn, total_otp, banned FROM users")
    data = {"users": {}, "total_users": 0}
    for u in users:
        uid, username, first_name, joined, last, bal, wd, tot, banned = u
        data["users"][str(uid)] = {
            "username": username or "",
            "first_name": first_name or "",
            "joined_date": joined or "",
            "last_active": last or "",
            "balance": round(bal or 0.0, 3),
            "withdrawn": round(wd or 0.0, 3),
            "total_otp": tot or 0,
            "banned": banned or 0,
            "status": "banned" if banned else "active"
        }
    data["total_users"] = len(data["users"])
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving user_data.json: {e}")

async def periodic_json_save(context: ContextTypes.DEFAULT_TYPE):
    save_user_data_json()

# ==================== USER MANAGER ====================
def generate_user_list_text():
    users = db_fetch_all("SELECT user_id, first_name, balance, withdrawn, total_otp, banned FROM users ORDER BY user_id")
    lines = []
    for u in users:
        uid, first_name, balance, withdrawn, total_otp, banned = u
        balance = balance or 0.0
        withdrawn = withdrawn or 0.0
        total_otp = total_otp or 0
        status = "Banned" if banned else "Active"
        lines.append(f"{first_name} | {uid} | ${balance:.3f} | ${withdrawn:.3f} | {total_otp} | {status}")
    return '\n'.join(lines)

async def send_user_list_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = generate_user_list_text()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text)
        f.flush()
        await update.callback_query.message.reply_document(document=open(f.name, 'rb'), filename="USER_DATA.txt")
    os.unlink(f.name)

# Async wrappers
async def _user_manager_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await user_manager_menu(update, context, update.callback_query.from_user.id)

async def _database_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await database_menu(update, context, update.callback_query.from_user.id)

async def _manage_api_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await manage_api_menu(update, context, update.callback_query.from_user.id)

async def _um_edit_balance_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await um_edit_balance_prompt(query, query.from_user.id, context)

async def _um_ban_toggle_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await um_ban_toggle(query, query.from_user.id, context)

async def _api_add_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await api_add_start(update, context, update.callback_query.from_user.id)

async def _api_remove_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await api_remove_list(update, context, update.callback_query.from_user.id)

async def _api_list_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await api_list(update, context, update.callback_query.from_user.id)

async def _um_search_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await um_search_prompt(update, context, update.callback_query.from_user.id)

async def user_manager_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.callback_query.answer("Admin mode required!", show_alert=True)
        return
    admin_panel_state[user_id] = "user_manager"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Search User", callback_data="um_search", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("SEARCH_USER", "")))],
        [InlineKeyboardButton("Download User List", callback_data="um_download", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DOWNLOAD_LIST", "")))],
        [InlineKeyboardButton("Stats Overview", callback_data="um_stats", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("STATS", "")))],
        [InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))],
    ])
    await reply_or_edit(update, "USER MANAGER\n\nSelect an option:", reply_markup=kb, context=context, auto_delete=False)

async def um_search_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    admin_panel_state[user_id] = "um_searching"
    await reply_or_edit(update, "Send the user ID or username to search.", reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def show_user_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data):
    uid, first_name, username, balance, withdrawn, total_otp, banned, joined, last_active = user_data
    balance = balance or 0.0
    withdrawn = withdrawn or 0.0
    total_otp = total_otp or 0
    status = "Banned" if banned else "Active"
    since = (datetime.now() - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
    recent = db_fetch_all("SELECT number, service FROM numbers WHERE user_id=? AND assigned_date > ? ORDER BY assigned_date DESC LIMIT 10", (uid, since))
    recent_str = "\n".join([f"  • {num} ({svc})" for num, svc in recent]) if recent else "  None"
    text = (
        f"Name: {first_name}\n"
        f"ID: {uid}\n"
        f"Username: @{username or 'N/A'}\n"
        f"Balance: ${balance:.3f}\n"
        f"Withdrawn: ${withdrawn:.3f}\n"
        f"Total OTP: {total_otp}\n"
        f"Status: {status}\n"
        f"Joined: {joined}\n"
        f"Last Active: {last_active}\n\n"
        f"📱 Recent Numbers (20 min):\n{recent_str}"
    )
    ban_text = "Ban" if not banned else "Unban"
    ban_style = KBS.DANGER if not banned else KBS.SUCCESS
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Edit Balance", callback_data=f"um_editbal|{uid}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("EDIT_BALANCE", "")))],
        [InlineKeyboardButton(ban_text, callback_data=f"um_ban|{uid}", style=ban_style,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BAN_USER", "")))],
        [InlineKeyboardButton("Back", callback_data="um_back", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))],
    ])
    await reply_or_edit(update, text, reply_markup=kb, context=context, auto_delete=False)

async def um_edit_balance_prompt(query, user_id, context: ContextTypes.DEFAULT_TYPE):
    target_uid = query.data.split('|')[1]
    admin_panel_state[user_id] = "um_editbal"
    admin_temp_data[user_id] = {"target_uid": target_uid}
    await edit_or_send(query, "Send amount to add/subtract (e.g., +0.5 or -0.2) and optional reason.",
                       reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def um_ban_toggle(query, user_id, context: ContextTypes.DEFAULT_TYPE):
    target_uid = query.data.split('|')[1]
    if not is_admin(user_id): return
    user = db_fetch_one("SELECT banned FROM users WHERE user_id=?", (target_uid,))
    if not user:
        await query.answer("User not found.")
        return
    new_ban = 0 if user[0] else 1
    db_exec("UPDATE users SET banned = ? WHERE user_id = ?", (new_ban, target_uid))
    save_user_data_json()
    await query.answer(f"User {'banned' if new_ban else 'unbanned'}!")
    if new_ban:
        try:
            ban_text = (
                f'{emoji_tag("6206077285720659346", "🚫")} <b>Now You Can\'t Use Me</b> {emoji_tag("6206003549722122915", "😢")}\n'
                f'{emoji_tag("6206267591426578467", "📞")} <b>CONTACT TO SUPPORT ADMINS</b> {emoji_tag("6206319341487527808", "👨‍💼")}'
            )
            await context.bot.send_message(target_uid, ban_text, reply_markup=support_keyboard(), parse_mode='HTML')
        except:
            pass
    else:
        try:
            unban_text = (
                f'{emoji_tag("6206508629286196237", "🎉")} <b>Congratulation Now You Can Use The Bot</b> {emoji_tag("6206479140040743133", "🥳")}\n'
                f'{emoji_tag("6206503415195899956", "🔓")} <b>You Are Unbanned</b> {emoji_tag("6204251568137574946", "✅")}'
            )
            await context.bot.send_message(target_uid, unban_text, parse_mode='HTML')
        except:
            pass
    user_data = db_fetch_one("SELECT user_id, first_name, username, balance, withdrawn, total_otp, banned, joined_date, last_active FROM users WHERE user_id=?", (target_uid,))
    if user_data:
        await show_user_detail(query, context, user_data)

async def um_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = db_fetch_one("SELECT COUNT(*) FROM users")[0]
    banned = db_fetch_one("SELECT COUNT(*) FROM users WHERE banned=1")[0]
    active = total - banned
    today = datetime.now().strftime("%Y-%m-%d")
    today_otp = db_fetch_one("SELECT COUNT(*) FROM otps WHERE timestamp LIKE ?", (f"{today}%",))[0] or 0
    text = (
        f"📊 User Statistics\n"
        f"Total Users: {total}\n"
        f"Active: {active}\n"
        f"Banned: {banned}\n"
        f"Today's OTP: {today_otp}\n"
    )
    await reply_or_edit(update, text, reply_markup=admin_back_button(), context=context, auto_delete=False)

# ==================== DATABASE DOWNLOAD/UPLOAD ====================
async def database_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id): await update.callback_query.answer("Admin mode required!", show_alert=True); return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("DOWNLOAD", callback_data="db_download", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon("6203886371363364022"))],
        [InlineKeyboardButton("UPLOAD", callback_data="db_upload", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon("6206046503690048595"))],
        [InlineKeyboardButton("Back", callback_data="admin_back", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))],
    ])
    await reply_or_edit(update, "DATABASE MANAGEMENT\n\nSelect an option:", reply_markup=kb, context=context, auto_delete=False)

async def db_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id): return
    await query.answer("Preparing database download...")
    save_user_data_json()
    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copy2(DB_PATH, os.path.join(tmpdir, "mrisbrand_master.db"))
        if os.path.exists("countries.json"):
            shutil.copy2("countries.json", os.path.join(tmpdir, "countries.json"))
        if os.path.exists(USER_DATA_FILE):
            shutil.copy2(USER_DATA_FILE, os.path.join(tmpdir, "user_data.json"))
        if os.path.exists("emoji.py"):
            shutil.copy2("emoji.py", os.path.join(tmpdir, "emoji.py"))
        zip_path = os.path.join(tmpdir, "sr-number-data.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    if file == "sr-number-data.zip":
                        continue
                    full = os.path.join(root, file)
                    arcname = os.path.relpath(full, tmpdir)
                    zf.write(full, arcname)
        await context.bot.send_document(chat_id=query.message.chat_id, document=open(zip_path, 'rb'))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

async def db_upload_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id): return
    admin_panel_state[user_id] = "waiting_db_upload"
    await edit_or_send(query, "Upload the sr-number-data.zip file to restore the database.",
                       reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

# ==================== SINGLE DOCUMENT HANDLER ====================
async def handle_all_documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.document:
        return
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    document = update.message.document
    state = admin_panel_state.get(user_id)
    
    if state == "waiting_file":
        if not document.file_name.endswith('.txt'):
            await update.message.reply_text("Please upload a .txt file!")
            return
        file = await context.bot.get_file(document.file_id)
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{document.file_name}"
        await file.download_to_drive(file_path)
        
        count, country, service = load_numbers_from_file(file_path, document.file_name)
        if count > 0:
            emoji_row = db_fetch_one("SELECT emoji_id FROM services WHERE name = ?", (service,))
            if not emoji_row:
                admin_temp_data[user_id] = {"pending_service_emoji": service, "country": country, "count": count}
                admin_panel_state[user_id] = "waiting_service_emoji_upload"
                await update.message.reply_text(
                    f"✅ {count} numbers loaded for {country}.\n"
                    f"New service '{service}' detected.\n"
                    "Send the custom emoji ID (or /skip).",
                    reply_markup=admin_cancel_keyboard())
                return
            msg = stock_added_message(country, service, count)
            await update.message.reply_text(msg, parse_mode='HTML', reply_markup=admin_panel_keyboard())
            broadcast_msg = stock_added_broadcast(country, service, count)
            users = db_fetch_all("SELECT user_id FROM users")
            for u in users:
                try:
                    await context.bot.send_message(u[0], broadcast_msg, parse_mode='HTML')
                    await asyncio.sleep(0.05)
                except Exception:
                    continue
            admin_panel_state[user_id] = "main"
        else:
            admin_temp_data[user_id] = {
                "pending_file_path": file_path,
                "pending_filename": document.file_name
            }
            countries = db_fetch_all("SELECT name FROM countries GROUP BY name ORDER BY name")
            if not countries:
                await update.message.reply_text("No countries defined. Add a country first.", reply_markup=admin_panel_keyboard())
                return
            keyboard = []
            for (cname,) in countries:
                keyboard.append([InlineKeyboardButton(cname, callback_data=f"fu_country|{cname}")])
            keyboard.append([InlineKeyboardButton("Cancel", callback_data="admin_back")])
            await update.message.reply_text(
                "❌ Could not detect country from filename.\nSelect the correct country:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            admin_panel_state[user_id] = "waiting_fu_country"
        return

    elif state == "waiting_db_upload":
        if not document.file_name.endswith('.zip'):
            await update.message.reply_text("Please upload the correct sr-number-data.zip file.")
            return
        file = await context.bot.get_file(document.file_id)
        tmpdir = tempfile.mkdtemp()
        zip_path = os.path.join(tmpdir, "upload.zip")
        await file.download_to_drive(zip_path)
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmpdir)
            for root, dirs, files in os.walk(tmpdir):
                for fname in files:
                    full = os.path.join(root, fname)
                    if fname == "mrisbrand_master.db":
                        global conn, c
                        conn.close()
                        shutil.copy2(full, DB_PATH)
                        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                        c = conn.cursor()
                    elif fname == "countries.json":
                        shutil.copy2(full, "countries.json")
                        global COUNTRIES_DATA
                        COUNTRIES_DATA = load_countries_db()
                    elif fname == "user_data.json":
                        shutil.copy2(full, USER_DATA_FILE)
                    elif fname == "emoji.py":
                        shutil.copy2(full, "emoji.py")
        except Exception as e:
            await update.message.reply_text(f"Error restoring database: {e}")
            return
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
        admin_panel_state[user_id] = "main"
        await update.message.reply_text("✅ Database restored successfully!", reply_markup=admin_panel_keyboard())
        return

    else:
        await update.message.reply_text("No action taken – please use the admin panel.")

# ==================== FORCE UPLOAD CALLBACKS ====================
async def fu_country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    country = query.data.split("|")[1]
    admin_temp_data[user_id]["fu_country"] = country

    services = db_fetch_all("SELECT name, display_name FROM services WHERE active=1 ORDER BY name")
    keyboard = []
    for svc, dname in services:
        keyboard.append([InlineKeyboardButton(dname, callback_data=f"fu_service|{svc}")])
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="admin_back")])
    await edit_or_send(query,
        f"Country: {country}\nSelect the service for this file:",
        reply_markup=InlineKeyboardMarkup(keyboard), context=context, auto_delete=False)
    admin_panel_state[user_id] = "waiting_fu_service"

async def fu_service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    service = query.data.split("|")[1]
    data = admin_temp_data.pop(user_id)
    file_path = data["pending_file_path"]
    country = data["fu_country"]

    count, _, _ = load_numbers_from_file(file_path, "force.txt", force_country=country, force_service=service)

    if count > 0:
        emoji_row = db_fetch_one("SELECT emoji_id FROM services WHERE name = ?", (service,))
        if not emoji_row:
            admin_temp_data[user_id] = {"pending_service_emoji": service, "country": country, "count": count}
            admin_panel_state[user_id] = "waiting_service_emoji_upload"
            await edit_or_send(query,
                f"✅ {count} numbers loaded.\nNew service '{service}' detected.\nSend emoji ID or /skip.",
                reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)
            return
        msg = stock_added_message(country, service, count)
        await edit_or_send(query, msg, parse_mode='HTML', reply_markup=admin_panel_keyboard(), context=context, auto_delete=False)
        broadcast_msg = stock_added_broadcast(country, service, count)
        users = db_fetch_all("SELECT user_id FROM users")
        for u in users:
            try:
                await context.bot.send_message(u[0], broadcast_msg, parse_mode='HTML')
            except:
                pass
    else:
        await edit_or_send(query, "No valid numbers found in the file.",
                           reply_markup=admin_panel_keyboard(), context=context, auto_delete=False)

    admin_panel_state[user_id] = "main"

# ==================== ADMIN TEXT HANDLER ====================
async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = admin_panel_state.get(user_id)
    if not is_admin(user_id):
        return False

    if state == "waiting_broadcast":
        msg = update.message
        users = db_fetch_all("SELECT user_id FROM users WHERE banned=0")
        user_ids = [u[0] for u in users]

        semaphore = asyncio.Semaphore(20)
        sent_counter = 0

        async def send_to_user(uid):
            nonlocal sent_counter
            async with semaphore:
                try:
                    await msg.copy(chat_id=uid)
                    sent_counter += 1
                except Exception:
                    pass

        tasks = [asyncio.create_task(send_to_user(uid)) for uid in user_ids]
        await asyncio.gather(*tasks)

        admin_panel_state[user_id] = "main"
        await msg.reply_text(f"Broadcast sent to {sent_counter} users!", reply_markup=admin_panel_keyboard())
        return True

    if state == "waiting_db_upload":
        return False

    if not update.message or not update.message.text:
        return False

    text = update.message.text.strip()

    if state == "um_searching":
        user = db_fetch_one("SELECT user_id, first_name, username, balance, withdrawn, total_otp, banned, joined_date, last_active FROM users WHERE user_id=? OR username=?", (text, text))
        if not user and text.isdigit():
            user = db_fetch_one("SELECT user_id, first_name, username, balance, withdrawn, total_otp, banned, joined_date, last_active FROM users WHERE user_id=?", (int(text),))
        if not user:
            await update.message.reply_text("User not found.")
            return True
        admin_panel_state[user_id] = "user_manager"
        await show_user_detail(update, context, user)
        return True

    if state == "um_editbal":
        data = admin_temp_data.pop(user_id, {})
        target_uid = data.get("target_uid")
        if not target_uid:
            await update.message.reply_text("Session expired.")
            return True
        try:
            amount = float(text.split()[0])
        except ValueError:
            await update.message.reply_text("Invalid amount. Use format: +0.5 or -0.2")
            return True
        current = db_fetch_one("SELECT balance FROM users WHERE user_id=?", (target_uid,))
        if not current:
            await update.message.reply_text("User not found.")
            return True
        new_balance = (current[0] or 0.0) + amount
        db_exec("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, target_uid))
        save_user_data_json()
        await update.message.reply_text(f"Balance updated for {target_uid}. New balance: ${new_balance:.3f}")
        admin_panel_state[user_id] = "main"
        await admin_panel_menu(update, user_id, context)
        return True

    if state == "waiting_giveaway":
        parts = text.split()
        try:
            target, count = int(parts[0]), int(parts[1]) if len(parts) > 1 else 1
            await update.message.reply_text(f"Given {count} free account(s) to {target}.", reply_markup=admin_panel_keyboard())
            admin_panel_state[user_id] = "main"
        except:
            await update.message.reply_text("Invalid format!")
        return True

    elif state == "waiting_country_add":
        try:
            parts = [p.strip() for p in text.split('|')]
            if len(parts) < 4: await update.message.reply_text("Format: CountryName | Code | ISO | payout | emoji_id"); return True
            name, code, iso, payout = parts[0], parts[1], parts[2].upper(), parts[3]
            emoji_id = parts[4] if len(parts) >= 5 else ""
            COUNTRIES_DATA[name] = {"code": code, "iso": iso, "payout": payout, "emoji_id": emoji_id}
            save_countries_db(COUNTRIES_DATA)
            await country_add_service_selection(update, user_id, name, context)
            return True
        except Exception as e: await update.message.reply_text(f"Error: {e}")
        return True

    elif state == "waiting_country_edit":
        if text.strip() == "/skip":
            admin_panel_state[user_id] = "country_manager"
            await update.message.reply_text("No changes.")
            await country_manager_menu(update, user_id, context)
            return True
        try:
            parts = [p.strip() for p in text.split('|')]
            if len(parts) < 3: await update.message.reply_text("At least Code | ISO | payout required."); return True
            code, iso, payout = parts[0], parts[1].upper(), parts[2]
            emoji_id = parts[3] if len(parts) >= 4 else ""
            country_name = admin_temp_data.get(user_id, {}).get("edit_country")
            COUNTRIES_DATA[country_name].update({"code": code, "iso": iso, "payout": payout, "emoji_id": emoji_id})
            save_countries_db(COUNTRIES_DATA)
            admin_panel_state[user_id] = "country_manager"
            await update.message.reply_text(f"Country {country_name} updated!")
            await country_manager_menu(update, user_id, context)
        except Exception as e: await update.message.reply_text(f"Error: {e}")
        return True

    elif state == "waiting_service_name":
        try:
            db_exec("INSERT INTO services (name, display_name, active, emoji_id) VALUES (?, ?, 1, '')", (text, text))
            await update.message.reply_text(f"Service {text} added!")
        except sqlite3.IntegrityError: await update.message.reply_text(f"Service {text} already exists!")
        admin_panel_state[user_id] = "service_manager"
        await service_manager_menu(update, user_id, context)
        return True

    elif state == "waiting_service_emoji":
        return await handle_service_emoji_set(update, context)

    elif state == "waiting_service_emoji_upload":
        if text.strip() == "/skip": text = ""
        data = admin_temp_data.get(user_id, {})
        service = data.get("pending_service_emoji")
        country = data.get("country")
        count = data.get("count")
        db_exec("INSERT OR IGNORE INTO services (name, display_name, active, emoji_id) VALUES (?, ?, 1, ?)", (service, service, text))
        if text:
            db_exec("UPDATE services SET emoji_id = ? WHERE name = ?", (text, service))
        msg = stock_added_message(country, service, count)
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=admin_panel_keyboard())
        broadcast_msg = stock_added_broadcast(country, service, count)
        users = db_fetch_all("SELECT user_id FROM users")
        for u in users:
            try:
                await context.bot.send_message(u[0], broadcast_msg, parse_mode='HTML')
                await asyncio.sleep(0.05)
            except Exception:
                continue
        admin_panel_state[user_id] = "main"
        admin_temp_data.pop(user_id, None)
        return True

    return False

# ==================== CALLBACK HANDLERS ====================
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if await ban_check(update, context):
        return
    first_name = query.from_user.first_name or "User"
    data = query.data
    await query.answer()
    action = data[len("menu_"):]
    if action == "get_number": await show_get_number(update, context, user_id, first_name)
    elif action == "balance": await show_balance(update, user_id, context)
    elif action == "support": await show_support(update, context)
    elif action == "admin": await admin_panel_menu(update, user_id, context)

async def balance_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context): return
    await query.answer()
    await show_balance(update, query.from_user.id, context)

async def withdraw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context): return
    await query.answer()
    await show_withdraw(update, query.from_user.id, context)

async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context): return
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    await query.answer()
    await show_main_menu(query, user_id, first_name, context)

# ==================== TOGGLE CC CALLBACK ====================
async def toggle_cc_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context): return
    user_id = query.from_user.id
    await query.answer()
    row = db_fetch_one("SELECT remove_cc FROM users WHERE user_id = ?", (user_id,))
    if row:
        new_val = 0 if row[0] == 1 else 1
        db_exec("UPDATE users SET remove_cc = ? WHERE user_id = ?", (new_val, user_id))
    else:
        new_val = 0
    data = last_activation_data.get(user_id)
    if not data:
        await edit_or_send(query, "No active numbers to display.", reply_markup=back_to_main_keyboard(), context=context)
        return
    country, service, numbers, msg_id = data
    msg, kb = format_numbers_message(country, service, numbers, user_id=user_id)
    await edit_or_send(query, msg, reply_markup=kb, parse_mode='HTML', context=context)

# ==================== SERVICE→COUNTRY FLOW ====================
async def service_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context): return
    user_id = query.from_user.id
    await query.answer()
    service = query.data.split('|', 1)[1]
    db_exec("UPDATE users SET current_service = ? WHERE user_id = ?", (service, user_id))
    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_COUNTRY_PREFIX"], "🌍")} '
        f'<b>Select country for {service.upper()}</b> {service_emoji_tag(service)}'
    )
    await edit_or_send(query, text, reply_markup=countries_for_service_keyboard(service), parse_mode='HTML', context=context)

async def country_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context): return
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    await query.answer("Allocating 3 numbers...")
    parts = query.data.split('|')
    if len(parts) < 3:
        await query.answer("Invalid selection.", show_alert=True)
        return
    country = parts[1]
    service = parts[2]

    await edit_or_send(query, f'{emoji_tag("5976826804931928647", "⏳")}', parse_mode='HTML', context=context)
    await asyncio.sleep(1)

    numbers = get_numbers_from_stock(country, service, 3)
    if not numbers:
        await query.answer("No numbers available for this country/service!", show_alert=True)
        await edit_or_send(query, "Select a Country:", reply_markup=countries_for_service_keyboard(service), context=context)
        return

    expiry = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for number in numbers:
        db_exec('''INSERT INTO numbers (user_id, number, country, service, assigned_date, status, expiry_time)
                   VALUES (?, ?, ?, ?, ?, 'active', ?)''',
                (user_id, number, country, service, now_str, expiry))
    db_exec('''UPDATE users SET current_number = ?, current_country = ?, current_service = ?, number_expiry = ?
               WHERE user_id = ?''', (numbers[0], country, service, expiry, user_id))

    msg, kb = format_numbers_message(country, service, numbers, user_id=user_id)
    sent_msg = await query.message.reply_text(msg, reply_markup=kb, parse_mode='HTML')
    last_activation_data[user_id] = (country, service, numbers, sent_msg.message_id)
    # No schedule_delete for inline; it will remain until next action
    try:
        await query.delete_message()
    except:
        pass

async def back_to_services_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context): return
    user_id = query.from_user.id
    await query.answer()
    db_exec("UPDATE users SET current_service = NULL, current_country = NULL, current_number = NULL, number_expiry = NULL WHERE user_id = ?", (user_id,))
    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_PREFIX"], "🔧")} <b>Select service</b> '
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_SUFFIX"], "📱")}'
    )
    await edit_or_send(query, text, reply_markup=services_keyboard(), parse_mode='HTML', context=context)

async def next_number_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context): return
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    await query.answer("Getting next 3 numbers...")
    
    await edit_or_send(query, f'{emoji_tag("5976826804931928647", "⏳")}', parse_mode='HTML', context=context)
    await asyncio.sleep(1)

    result = db_fetch_one("SELECT current_country, current_service FROM users WHERE user_id = ?", (user_id,))
    country = service = None
    if result and result[0]:
        country, service = result
    else:
        fallback = db_fetch_one("SELECT country, service FROM numbers WHERE user_id = ? ORDER BY assigned_date DESC LIMIT 1", (user_id,))
        if fallback: country, service = fallback
    if not country or not service:
        await query.answer("Please select a service and country first!", show_alert=True)
        await edit_or_send(query, "Select a Service:", reply_markup=services_keyboard(), context=context)
        return
    numbers = get_numbers_from_stock(country, service, 3)
    if not numbers:
        await query.answer(f"No more {country} {service} numbers!", show_alert=True)
        await edit_or_send(query, f"Select a Country for {service}:", reply_markup=countries_for_service_keyboard(service), context=context)
        return
    expiry = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for number in numbers:
        db_exec('''INSERT INTO numbers (user_id, number, country, service, assigned_date, status, expiry_time)
                   VALUES (?, ?, ?, ?, ?, 'active', ?)''',
                (user_id, number, country, service, now_str, expiry))
    db_exec('''UPDATE users SET current_number = ?, current_country = ?, current_service = ?, number_expiry = ?
               WHERE user_id = ?''', (numbers[0], country, service, expiry, user_id))
    msg, kb = format_numbers_message(country, service, numbers, user_id=user_id)
    sent_msg = await query.message.reply_text(msg, reply_markup=kb, parse_mode='HTML')
    last_activation_data[user_id] = (country, service, numbers, sent_msg.message_id)
    try:
        await query.delete_message()
    except:
        pass

# ==================== ADMIN CALLBACKS ====================
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
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
            await show_delete_options(query, user_id, context)
        return
    action = data[len("admin_"):]
    if action == "stats": await show_admin_stats(update, user_id, context)
    elif action == "upload": await request_upload(update, user_id, context)
    elif action == "delete": await show_delete_options(query, user_id, context)
    elif action == "broadcast": await request_broadcast(update, user_id, context)
    elif action == "giveaway": await request_giveaway(update, user_id, context)
    elif action == "country_manager": await country_manager_menu(update, user_id, context)
    elif action == "service_manager": await service_manager_menu(update, user_id, context)
    elif action == "user_manager": await _user_manager_wrapper(update, context)
    elif action == "database": await _database_wrapper(update, context)
    elif action == "manage_api": await _manage_api_wrapper(update, context)
    elif action == "exit": await exit_admin_callback_query(query, user_id, context.bot)
    elif action == "back":
        admin_panel_state[user_id] = "main"
        await edit_or_send(query, "ADMIN PANEL\n\nDeveloper: SR NUMBER HUB\n\nSelect an action below:",
                           reply_markup=admin_panel_keyboard(), context=context, auto_delete=False)

async def show_admin_stats(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
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
    await reply_or_edit(update, text, reply_markup=admin_back_button(), parse_mode='HTML', context=context, auto_delete=False)

async def show_delete_options(query, user_id, context: ContextTypes.DEFAULT_TYPE):
    countries = db_fetch_all("SELECT name, service, stock FROM countries WHERE active = 1 ORDER BY name")
    if not countries:
        await edit_or_send(query, "No countries to delete!", reply_markup=admin_back_button(), context=context, auto_delete=False)
        return
    rows = []
    for name, service, stock_count in countries:
        rows.append([InlineKeyboardButton(f"Delete {name} — {service} (Stock: {stock_count})",
                                          callback_data=f"admin_del|{name}|{service}",
                                          style=KBS.DANGER,
                                          icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DELETE", "")))])
    rows.append([InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await edit_or_send(query, "DELETE STOCK\n\nSelect a country/service to delete all its numbers:",
                       reply_markup=InlineKeyboardMarkup(rows), context=context, auto_delete=False)

async def request_upload(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    admin_panel_state[user_id] = "waiting_file"
    await reply_or_edit(update, "UPLOAD STOCK\n\nSend a .txt file with phone numbers.\nFilename must contain country & service name.\nOne number per line.",
                        reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def request_broadcast(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    admin_panel_state[user_id] = "waiting_broadcast"
    await reply_or_edit(update, "BROADCAST MESSAGE\n\nSend the message you want to broadcast to ALL users (any media or text).",
                        reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def request_giveaway(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    admin_panel_state[user_id] = "waiting_giveaway"
    await reply_or_edit(update, "GIVE FREE ACCOUNT\n\nSend: user_id count\nExample: 123456789 5",
                        reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def exit_admin_callback_query(query, user_id, bot):
    admin_mode.pop(user_id, None)
    admin_panel_state.pop(user_id, None)
    try:
        await edit_or_send(query, welcome_html(user_id, query.from_user.first_name or "User"),
                           reply_markup=None, parse_mode='HTML', context=None, auto_delete=False)
    except Exception:
        await bot.send_message(user_id, "Returned to main menu.", reply_markup=bottom_menu_keyboard(user_id))

# ==================== COUNTRY & SERVICE CALLBACKS ====================
async def country_manager_menu(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(user_id): await update.callback_query.answer("Admin mode required!", show_alert=True); return
    admin_panel_state[user_id] = "country_manager"
    rows = [
        [InlineKeyboardButton("Add New Country", callback_data="country_add", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("COUNTRY_MANAGER", "")))],
        [InlineKeyboardButton("List All Countries", callback_data="country_list", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("COUNTRY_MANAGER", "")))],
        [InlineKeyboardButton("Edit Country", callback_data="country_edit_select", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("COUNTRY_MANAGER", "")))],
        [InlineKeyboardButton("Delete Country", callback_data="country_delete_select", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DELETE", "")))],
        [InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))],
    ]
    await reply_or_edit(update, "COUNTRY MANAGER\n\nSelect an option:", reply_markup=InlineKeyboardMarkup(rows), context=context, auto_delete=False)

async def country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id): await query.answer("Admin mode required!", show_alert=True); return
    await query.answer()
    data = query.data
    if data == "country_add":
        await country_add_start(update, user_id, context)
    elif data == "country_list":
        await country_list_show(update, user_id, context)
    elif data == "country_edit_select":
        await country_edit_select(update, user_id, context)
    elif data == "country_delete_select":
        await country_delete_select(update, user_id, context)
    elif data.startswith("country_edit|"):
        await country_edit_start(update, user_id, data.split('|', 1)[1], context)
    elif data.startswith("country_delete|"):
        await country_delete_direct(query, user_id, data.split('|', 1)[1], context)

async def country_add_start(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    admin_panel_state[user_id] = "waiting_country_add"
    await reply_or_edit(update,
        "ADD NEW COUNTRY\n\nFormat: CountryName | Code | ISO | payout | emoji_id\n"
        "Example: Bangladesh | +880 | BD | 0.001$ | 5911365056594973179",
        reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def country_list_show(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    lines = [f'ALL COUNTRIES {emoji_tag(CUSTOM_EMOJIS["CHANGE_COUNTRY"], "🌍")}', '']
    for name, info in COUNTRIES_DATA.items():
        lines.append(f'• {country_flag_emoji(name)} {name}')
        lines.append(f'  Code: {info["code"]} | ISO: {info["iso"]} | Payout: {info.get("payout", "0.001$")} | Emoji ID: {info.get("emoji_id") or "Not set"}')
        lines.append('')
    await reply_or_edit(update, '\n'.join(lines), reply_markup=admin_back_button(), parse_mode='HTML', context=context, auto_delete=False)

async def country_edit_select(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    rows = []
    for name, info in COUNTRIES_DATA.items():
        icon = info.get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
        rows.append([InlineKeyboardButton(f"{name} (Payout: {info.get('payout','0.001$')})",
                                          callback_data=f"country_edit|{name}",
                                          style=KBS.PRIMARY,
                                          icon_custom_emoji_id=safe_icon(icon))])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_country_manager", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await reply_or_edit(update, "Select country to edit:", reply_markup=InlineKeyboardMarkup(rows), context=context, auto_delete=False)

async def country_edit_start(update: Update, user_id, country_name, context: ContextTypes.DEFAULT_TYPE):
    admin_temp_data[user_id] = {"edit_country": country_name}
    admin_panel_state[user_id] = "waiting_country_edit"
    info = COUNTRIES_DATA[country_name]
    await reply_or_edit(update,
        f"EDIT COUNTRY: {country_name}\n\nCurrent:\nCode: {info['code']}\nISO: {info['iso']}\nPayout: {info.get('payout','0.001$')}\nEmoji ID: {info.get('emoji_id', 'Not set')}\n\nSend new details: Code | ISO | payout | emoji_id\nSend /skip to keep.",
        reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def country_delete_select(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    rows = []
    for name in COUNTRIES_DATA:
        rows.append([InlineKeyboardButton(f"Delete {name}", callback_data=f"country_delete|{name}",
                                          style=KBS.DANGER,
                                          icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DELETE", "")))])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_country_manager", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await reply_or_edit(update, "Select country to delete:", reply_markup=InlineKeyboardMarkup(rows), context=context, auto_delete=False)

async def country_delete_direct(query, user_id, country_name, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(user_id): await query.answer("Admin mode required!", show_alert=True); return
    if country_name in COUNTRIES_DATA:
        del COUNTRIES_DATA[country_name]
        save_countries_db(COUNTRIES_DATA)
        db_exec("DELETE FROM available_numbers WHERE country = ?", (country_name,))
        db_exec("DELETE FROM countries WHERE name = ?", (country_name,))
        await query.answer(f"{country_name} deleted!")
    else:
        await query.answer("Country not found!", show_alert=True)
    await country_delete_select(query, user_id, context)

# SINGLE-COLUMN service list after country add
async def country_add_service_selection(update: Update, user_id, country_name, context: ContextTypes.DEFAULT_TYPE):
    services = db_fetch_all("SELECT name, display_name, emoji_id FROM services WHERE active = 1 ORDER BY name")
    rows = []
    for s in services:
        rows.append([InlineKeyboardButton(
            s[1],
            callback_data=f"cnt_add_svc|{country_name}|{s[0]}",
            style=KBS.PRIMARY,
            icon_custom_emoji_id=safe_icon(s[2]) if s[2] else None
        )])
    rows.append([InlineKeyboardButton("Skip", callback_data="admin_back", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    kb = InlineKeyboardMarkup(rows)
    text = f"Country '{country_name}' added. Select a service to link (or Skip):"
    await reply_or_edit(update, text, reply_markup=kb, context=context, auto_delete=False)

async def country_add_service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    parts = query.data.split('|')
    if len(parts) != 3: await query.answer("Invalid.", show_alert=True); return
    country_name = parts[1]
    service_name = parts[2]
    db_exec("INSERT OR IGNORE INTO countries (name, service, flag, stock) VALUES (?, ?, ?, 0)", (country_name, service_name, country_name))
    await query.answer(f"{country_name} now available for {service_name}!")
    admin_panel_state[user_id] = "main"
    await edit_or_send(query, "Country linked successfully.", reply_markup=admin_panel_keyboard(), context=context, auto_delete=False)

# ==================== SERVICE MANAGER ====================
async def service_manager_menu(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(user_id):
        await update.callback_query.answer("Admin mode required!", show_alert=True)
        return
    admin_panel_state[user_id] = "service_manager"
    rows = [
        [InlineKeyboardButton("Add New Service", callback_data="service_add", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADD", "")))],
        [InlineKeyboardButton("Remove Service", callback_data="service_remove", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DELETE", "")))],
        [InlineKeyboardButton("Toggle Service Active", callback_data="service_toggle", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon("4956583802240500602"))],
        [InlineKeyboardButton("Set Service Emoji", callback_data="service_set_emoji", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon("4956214413578207998"))],
        [InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))],
    ]
    await reply_or_edit(update, "SERVICE MANAGER\n\nSelect an option:", reply_markup=InlineKeyboardMarkup(rows), context=context, auto_delete=False)

async def service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin mode required!", show_alert=True)
        return
    await query.answer()
    data = query.data
    if data == "service_add":
        await service_add_start(update, user_id, context)
    elif data == "service_remove":
        await service_remove_select(query, user_id, context)
    elif data.startswith("service_remove|"):
        await service_remove_execute(query, data.split('|', 1)[1], context)
    elif data == "service_toggle":
        await service_toggle_select(query, user_id, context)
    elif data == "service_set_emoji":
        await service_set_emoji_select(update, user_id, context)
    elif data.startswith("service_toggle|"):
        await service_toggle_execute(query, data.split('|', 1)[1], context)
    elif data.startswith("service_emoji_set|"):
        await service_set_emoji_start(update, user_id, data.split('|', 1)[1], context)

async def service_add_start(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    admin_panel_state[user_id] = "waiting_service_name"
    await reply_or_edit(update, "Send the service name.", reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def service_remove_select(target, user_id, context: ContextTypes.DEFAULT_TYPE):
    services = db_fetch_all("SELECT name, display_name FROM services ORDER BY name")
    rows = []
    for s in services:
        rows.append([InlineKeyboardButton(f"Remove {s[1]}",
                                          callback_data=f"service_remove|{s[0]}",
                                          style=KBS.DANGER,
                                          icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DELETE", "")))])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_service_manager", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await reply_or_edit(target, "Select service to remove:", reply_markup=InlineKeyboardMarkup(rows), context=context, auto_delete=False)

async def service_remove_execute(query, service_name, context: ContextTypes.DEFAULT_TYPE):
    db_exec("DELETE FROM services WHERE name = ?", (service_name,))
    db_exec("DELETE FROM countries WHERE service = ?", (service_name,))
    await query.answer(f"Service '{service_name}' removed!")
    await service_remove_select(query, query.from_user.id, context)

async def service_toggle_select(target, user_id, context: ContextTypes.DEFAULT_TYPE):
    services = db_fetch_all("SELECT name, display_name, active FROM services ORDER BY name")
    rows = []
    for s in services:
        status = "Active" if s[2] else "Inactive"
        style = KBS.SUCCESS if s[2] else KBS.DANGER
        rows.append([InlineKeyboardButton(f"{s[1]} ({status})",
                                          callback_data=f"service_toggle|{s[0]}",
                                          style=style,
                                          icon_custom_emoji_id=safe_icon("4956583802240500602"))])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_service_manager", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await reply_or_edit(target, "Select service to toggle:", reply_markup=InlineKeyboardMarkup(rows), context=context, auto_delete=False)

async def service_toggle_execute(query, service_name, context: ContextTypes.DEFAULT_TYPE):
    result = db_fetch_one("SELECT active FROM services WHERE name = ?", (service_name,))
    if result:
        new_status = 0 if result[0] else 1
        db_exec("UPDATE services SET active = ? WHERE name = ?", (new_status, service_name))
        await query.answer(f"Service {'activated' if new_status else 'deactivated'}!")
    await service_toggle_select(query, query.from_user.id, context)

async def service_set_emoji_select(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(user_id): await update.callback_query.answer("Admin mode required!", show_alert=True); return
    services = db_fetch_all("SELECT name, display_name FROM services WHERE active = 1 ORDER BY name")
    rows = []
    for s in services:
        rows.append([InlineKeyboardButton(f"{s[1]} ({s[0]})",
                                          callback_data=f"service_emoji_set|{s[0]}",
                                          style=KBS.PRIMARY,
                                          icon_custom_emoji_id=safe_icon("4956214413578207998"))])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_service_manager", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await reply_or_edit(update, "Select service to set emoji:", reply_markup=InlineKeyboardMarkup(rows), context=context, auto_delete=False)

async def service_set_emoji_start(update: Update, user_id, service_name, context: ContextTypes.DEFAULT_TYPE):
    admin_temp_data[user_id] = {"set_emoji_service": service_name}
    admin_panel_state[user_id] = "waiting_service_emoji"
    await reply_or_edit(update, f"Send custom emoji ID for '{service_name}'.\nSend /skip to keep.", reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def handle_service_emoji_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    service_name = admin_temp_data.get(user_id, {}).get("set_emoji_service")
    if not service_name: await update.message.reply_text("Session expired."); return True
    if text == "/skip": text = ""
    db_exec("UPDATE services SET emoji_id = ? WHERE name = ?", (text, service_name))
    await update.message.reply_text(f"Emoji for {service_name} updated!")
    admin_panel_state[user_id] = "service_manager"
    await service_manager_menu(update, user_id, context)
    return True

# ==================== /country & /service COMMANDS ====================
async def group_country_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Admin only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /country ISO|EMOJI_ID\nExample: /country GB|123456789")
        return
    parts = " ".join(context.args).split("|")
    if len(parts) != 2:
        await update.message.reply_text("Invalid format. Use ISO|EMOJI_ID")
        return
    iso = parts[0].strip().upper()
    eid = parts[1].strip()
    db_exec("INSERT OR REPLACE INTO group_emojis (type, key, emoji_id) VALUES ('country', ?, ?)", (iso, eid))
    DEFAULT_EMOJIS["countries"][iso.lower()] = eid
    await update.message.reply_text(f"✅ Group country emoji for {iso} set to <code>{eid}</code>", parse_mode="HTML")

async def group_service_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Admin only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /service NAME|EMOJI_ID\nExample: /service PayPal|123456789")
        return
    parts = " ".join(context.args).split("|")
    if len(parts) != 2:
        await update.message.reply_text("Invalid format. Use NAME|EMOJI_ID")
        return
    name = parts[0].strip().lower()
    eid = parts[1].strip()
    db_exec("INSERT OR REPLACE INTO group_emojis (type, key, emoji_id) VALUES ('service', ?, ?)", (name, eid))
    DEFAULT_EMOJIS["services"][name.lower()] = eid
    await update.message.reply_text(f"✅ Group service emoji for {name} set to <code>{eid}</code>", parse_mode="HTML")

# ==================== BOTTOM MENU TEXT ROUTERS ====================
async def send_get_number_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await ban_check(update, context): return
    ensure_user(user_id, update.effective_user.username, update.effective_user.first_name)
    db_exec("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_PREFIX"], "🔧")} <b>Select service</b> '
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_SUFFIX"], "📱")}'
    )
    await send_clean_message(update, context, text, reply_markup=services_keyboard(), parse_mode='HTML')

async def send_balance_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await ban_check(update, context): return
    ensure_user(user_id, update.effective_user.username, update.effective_user.first_name)
    user = db_fetch_one("SELECT first_name, balance, withdrawn, total_otp FROM users WHERE user_id = ?", (user_id,))
    if not user:
        return
    first_name, balance, withdrawn, total_otp = user
    balance = balance or 0.0
    withdrawn = withdrawn or 0.0
    total_otp = total_otp or 0

    # Custom emoji IDs for balance
    emoji_clipboard = "4958506272551863292"   # 📋
    emoji_id = "5197269100878907942"          # 🆔
    emoji_money = "4958926882994127612"       # 💰
    emoji_withdraw = "5445221832074483553"    # 💸
    emoji_warning = "4958534696645428119"     # ⚠️
    emoji_inbox = "5197288647275071607"       # 📨

    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["PROFILE_ICON"], "👤")} '
        f'<a href="tg://user?id={user_id}">{first_name}</a> YOUR DETAILS {emoji_tag(emoji_clipboard, "📋")}\n'
        f'------------------------------------------------\n'
        f'<blockquote><b>{emoji_tag(emoji_id, "🆔")} USER ID: <code>{user_id}</code></b></blockquote>\n'
        f'<blockquote><b>{emoji_tag(emoji_money, "💰")} BALANCE: <code>${balance:.3f}</code></b></blockquote>\n'
        f'<blockquote><b>{emoji_tag(emoji_withdraw, "💸")} WITHDRAWED: <code>${withdrawn:.3f}</code></b></blockquote>\n'
        f'<blockquote><b>{emoji_tag(emoji_warning, "⚠️")} MINIMUM WITHDRAW: <code>$0.1</code></b></blockquote>\n'
        f'<blockquote><b>{emoji_tag(emoji_inbox, "📨")} TOTAL OTP: <code>{total_otp}</code></b></blockquote>'
    )
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"WITHDRAW", callback_data="withdraw", style=KBS.SUCCESS,
                             icon_custom_emoji_id=safe_icon("5445353829304387411"))
    ]])
    await send_clean_message(update, context, text, reply_markup=kb, parse_mode='HTML')

async def send_support_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = "CONTACT SUPPORT\n\n━━━━━━━━━━━━━━━━━━━━\nFor any issues, contact admin directly.\n\nDeveloper: SR NUMBER HUB"
    # First ensure reply keyboard anchor
    kb_id_row = db_fetch_one("SELECT keyboard_message_id FROM users WHERE user_id=?", (user_id,))
    if kb_id_row and kb_id_row[0]:
        anchor_id = kb_id_row[0]
    else:
        anchor = await context.bot.send_message(chat_id=user_id, text="Main Menu", reply_markup=bottom_menu_keyboard(user_id))
        anchor_id = anchor.message_id
        db_exec("UPDATE users SET keyboard_message_id=? WHERE user_id=?", (anchor_id, user_id))
    # Now send inline support message
    sent_inline = await context.bot.send_message(chat_id=user_id, text=text, reply_markup=support_keyboard())
    db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?", (sent_inline.message_id, user_id))

# ==================== MANAGE API FUNCTIONS ====================
async def manage_api_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id): return
    admin_panel_state[user_id] = "manage_api"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("ADD API KEY", callback_data="api_add", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADD_API_KEY", "")))],
        [InlineKeyboardButton("REMOVE API KEY", callback_data="api_remove", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("REMOVE_API_KEY", "")))],
        [InlineKeyboardButton("LIST API KEY", callback_data="api_list", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("LIST_API_KEY", "")))],
        [InlineKeyboardButton("Back", callback_data="admin_back", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))],
    ])
    await reply_or_edit(update, "MANAGE API\n\nSelect an option:", reply_markup=kb, context=context, auto_delete=False)

async def api_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    admin_panel_state[user_id] = "api_add_name"
    await reply_or_edit(update, "Send the panel name:", reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def handle_api_add_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = admin_panel_state.get(user_id)
    if not state or not state.startswith("api_add_"):
        return False
    text = update.message.text.strip()
    if state == "api_add_name":
        admin_temp_data[user_id] = {"panel_name": text}
        admin_panel_state[user_id] = "api_add_url"
        await update.message.reply_text("Send the API base URL:", reply_markup=admin_cancel_keyboard())
        return True
    elif state == "api_add_url":
        admin_temp_data[user_id]["base_url"] = text
        admin_panel_state[user_id] = "api_add_token"
        await update.message.reply_text("Send the API token:", reply_markup=admin_cancel_keyboard())
        return True
    elif state == "api_add_token":
        admin_temp_data[user_id]["token"] = text
        admin_panel_state[user_id] = "api_add_interval"
        await update.message.reply_text("Send the polling interval (seconds):", reply_markup=admin_cancel_keyboard())
        return True
    elif state == "api_add_interval":
        try:
            interval = int(text)
        except ValueError:
            await update.message.reply_text("Invalid number. Try again.")
            return True
        data = admin_temp_data.pop(user_id)
        db_exec("INSERT INTO api_keys (panel_name, base_url, token, interval_sec, active) VALUES (?,?,?,?,1)",
                (data["panel_name"], data["base_url"], data["token"], interval))
        api_id = db_fetch_one("SELECT last_insert_rowid()")[0]
        asyncio.create_task(poll_api(api_id))
        admin_panel_state[user_id] = "main"
        await update.message.reply_text("✅ API key added and polling started!", reply_markup=admin_panel_keyboard())
        return True
    return False

async def api_remove_list(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id): return
    keys = db_fetch_all("SELECT id, panel_name, token FROM api_keys WHERE active=1")
    rows = []
    for k in keys:
        short = k[2][:5] if len(k[2]) > 5 else k[2]
        rows.append([InlineKeyboardButton(f"❌ {k[1]} ({short}...)", callback_data=f"api_rem_{k[0]}",
                                          style=KBS.DANGER,
                                          icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DELETE", "")))])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await reply_or_edit(update, "Select API key to remove:", reply_markup=InlineKeyboardMarkup(rows), context=context, auto_delete=False)

async def api_remove_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id): return
    api_id = int(query.data.split("_")[-1])
    db_exec("UPDATE api_keys SET active=0 WHERE id=?", (api_id,))
    await query.answer("API key removed!")
    await api_remove_list(update, context, user_id)

async def api_list(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id): return
    keys = db_fetch_all("SELECT id, panel_name, base_url, token, interval_sec FROM api_keys WHERE active=1")
    if not keys:
        text = "No active API keys."
    else:
        lines = ["**Active API Keys:**\n"]
        for k in keys:
            lines.append(f"• {k[1]} | {k[3][:12]}... | Interval: {k[4]}s")
        text = "\n".join(lines)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
    await reply_or_edit(update, text, reply_markup=kb, context=context, auto_delete=False)

# ==================== FULL COUNTRY CODE MAP ====================
COUNTRY_CODE_MAP = {
    "1": ("US", "🇺🇸", "United States"),
    "7": ("RU", "🇷🇺", "Russia"),
    "20": ("EG", "🇪🇬", "Egypt"),
    "27": ("ZA", "🇿🇦", "South Africa"),
    "30": ("GR", "🇬🇷", "Greece"),
    "31": ("NL", "🇳🇱", "Netherlands"),
    "32": ("BE", "🇧🇪", "Belgium"),
    "33": ("FR", "🇫🇷", "France"),
    "34": ("ES", "🇪🇸", "Spain"),
    "36": ("HU", "🇭🇺", "Hungary"),
    "39": ("IT", "🇮🇹", "Italy"),
    "40": ("RO", "🇷🇴", "Romania"),
    "41": ("CH", "🇨🇭", "Switzerland"),
    "43": ("AT", "🇦🇹", "Austria"),
    "44": ("GB", "🇬🇧", "United Kingdom"),
    "45": ("DK", "🇩🇰", "Denmark"),
    "46": ("SE", "🇸🇪", "Sweden"),
    "47": ("NO", "🇳🇴", "Norway"),
    "48": ("PL", "🇵🇱", "Poland"),
    "49": ("DE", "🇩🇪", "Germany"),
    "51": ("PE", "🇵🇪", "Peru"),
    "52": ("MX", "🇲🇽", "Mexico"),
    "53": ("CU", "🇨🇺", "Cuba"),
    "54": ("AR", "🇦🇷", "Argentina"),
    "55": ("BR", "🇧🇷", "Brazil"),
    "56": ("CL", "🇨🇱", "Chile"),
    "57": ("CO", "🇨🇴", "Colombia"),
    "58": ("VE", "🇻🇪", "Venezuela"),
    "60": ("MY", "🇲🇾", "Malaysia"),
    "61": ("AU", "🇦🇺", "Australia"),
    "62": ("ID", "🇮🇩", "Indonesia"),
    "63": ("PH", "🇵🇭", "Philippines"),
    "64": ("NZ", "🇳🇿", "New Zealand"),
    "65": ("SG", "🇸🇬", "Singapore"),
    "66": ("TH", "🇹🇭", "Thailand"),
    "81": ("JP", "🇯🇵", "Japan"),
    "82": ("KR", "🇰🇷", "South Korea"),
    "84": ("VN", "🇻🇳", "Vietnam"),
    "86": ("CN", "🇨🇳", "China"),
    "90": ("TR", "🇹🇷", "Turkey"),
    "91": ("IN", "🇮🇳", "India"),
    "92": ("PK", "🇵🇰", "Pakistan"),
    "93": ("AF", "🇦🇫", "Afghanistan"),
    "94": ("LK", "🇱🇰", "Sri Lanka"),
    "95": ("MM", "🇲🇲", "Myanmar"),
    "98": ("IR", "🇮🇷", "Iran"),
    "211": ("SS", "🇸🇸", "South Sudan"),
    "212": ("MA", "🇲🇦", "Morocco"),
    "213": ("DZ", "🇩🇿", "Algeria"),
    "216": ("TN", "🇹🇳", "Tunisia"),
    "218": ("LY", "🇱🇾", "Libya"),
    "220": ("GM", "🇬🇲", "Gambia"),
    "221": ("SN", "🇸🇳", "Senegal"),
    "222": ("MR", "🇲🇷", "Mauritania"),
    "223": ("ML", "🇲🇱", "Mali"),
    "224": ("GN", "🇬🇳", "Guinea"),
    "225": ("CI", "🇨🇮", "Ivory Coast"),
    "226": ("BF", "🇧🇫", "Burkina Faso"),
    "227": ("NE", "🇳🇪", "Niger"),
    "228": ("TG", "🇹🇬", "Togo"),
    "229": ("BJ", "🇧🇯", "Benin"),
    "230": ("MU", "🇲🇺", "Mauritius"),
    "231": ("LR", "🇱🇷", "Liberia"),
    "232": ("SL", "🇸🇱", "Sierra Leone"),
    "233": ("GH", "🇬🇭", "Ghana"),
    "234": ("NG", "🇳🇬", "Nigeria"),
    "235": ("TD", "🇹🇩", "Chad"),
    "236": ("CF", "🇨🇫", "Central African Republic"),
    "237": ("CM", "🇨🇲", "Cameroon"),
    "238": ("CV", "🇨🇻", "Cape Verde"),
    "239": ("ST", "🇸🇹", "Sao Tome and Principe"),
    "240": ("GQ", "🇬🇶", "Equatorial Guinea"),
    "241": ("GA", "🇬🇦", "Gabon"),
    "242": ("CG", "🇨🇬", "Congo"),
    "243": ("CD", "🇨🇩", "DR Congo"),
    "244": ("AO", "🇦🇴", "Angola"),
    "245": ("GW", "🇬🇼", "Guinea-Bissau"),
    "246": ("IO", "🇮🇴", "British Indian Ocean Territory"),
    "248": ("SC", "🇸🇨", "Seychelles"),
    "249": ("SD", "🇸🇩", "Sudan"),
    "250": ("RW", "🇷🇼", "Rwanda"),
    "251": ("ET", "🇪🇹", "Ethiopia"),
    "252": ("SO", "🇸🇴", "Somalia"),
    "253": ("DJ", "🇩🇯", "Djibouti"),
    "254": ("KE", "🇰🇪", "Kenya"),
    "255": ("TZ", "🇹🇿", "Tanzania"),
    "256": ("UG", "🇺🇬", "Uganda"),
    "257": ("BI", "🇧🇮", "Burundi"),
    "258": ("MZ", "🇲🇿", "Mozambique"),
    "260": ("ZM", "🇿🇲", "Zambia"),
    "261": ("MG", "🇲🇬", "Madagascar"),
    "262": ("RE", "🇷🇪", "Reunion"),
    "263": ("ZW", "🇿🇼", "Zimbabwe"),
    "264": ("NA", "🇳🇦", "Namibia"),
    "265": ("MW", "🇲🇼", "Malawi"),
    "266": ("LS", "🇱🇸", "Lesotho"),
    "267": ("BW", "🇧🇼", "Botswana"),
    "268": ("SZ", "🇸🇿", "Eswatini"),
    "269": ("KM", "🇰🇲", "Comoros"),
    "290": ("SH", "🇸🇭", "Saint Helena"),
    "291": ("ER", "🇪🇷", "Eritrea"),
    "297": ("AW", "🇦🇼", "Aruba"),
    "298": ("FO", "🇫🇴", "Faroe Islands"),
    "299": ("GL", "🇬🇱", "Greenland"),
    "350": ("GI", "🇬🇮", "Gibraltar"),
    "351": ("PT", "🇵🇹", "Portugal"),
    "352": ("LU", "🇱🇺", "Luxembourg"),
    "353": ("IE", "🇮🇪", "Ireland"),
    "354": ("IS", "🇮🇸", "Iceland"),
    "355": ("AL", "🇦🇱", "Albania"),
    "356": ("MT", "🇲🇹", "Malta"),
    "357": ("CY", "🇨🇾", "Cyprus"),
    "358": ("FI", "🇫🇮", "Finland"),
    "359": ("BG", "🇧🇬", "Bulgaria"),
    "370": ("LT", "🇱🇹", "Lithuania"),
    "371": ("LV", "🇱🇻", "Latvia"),
    "372": ("EE", "🇪🇪", "Estonia"),
    "373": ("MD", "🇲🇩", "Moldova"),
    "374": ("AM", "🇦🇲", "Armenia"),
    "375": ("BY", "🇧🇾", "Belarus"),
    "376": ("AD", "🇦🇩", "Andorra"),
    "377": ("MC", "🇲🇨", "Monaco"),
    "378": ("SM", "🇸🇲", "San Marino"),
    "380": ("UA", "🇺🇦", "Ukraine"),
    "381": ("RS", "🇷🇸", "Serbia"),
    "382": ("ME", "🇲🇪", "Montenegro"),
    "383": ("XK", "🇽🇰", "Kosovo"),
    "385": ("HR", "🇭🇷", "Croatia"),
    "386": ("SI", "🇸🇮", "Slovenia"),
    "387": ("BA", "🇧🇦", "Bosnia and Herzegovina"),
    "389": ("MK", "🇲🇰", "North Macedonia"),
    "420": ("CZ", "🇨🇿", "Czech Republic"),
    "421": ("SK", "🇸🇰", "Slovakia"),
    "423": ("LI", "🇱🇮", "Liechtenstein"),
    "500": ("FK", "🇫🇰", "Falkland Islands"),
    "501": ("BZ", "🇧🇿", "Belize"),
    "502": ("GT", "🇬🇹", "Guatemala"),
    "503": ("SV", "🇸🇻", "El Salvador"),
    "504": ("HN", "🇭🇳", "Honduras"),
    "505": ("NI", "🇳🇮", "Nicaragua"),
    "506": ("CR", "🇨🇷", "Costa Rica"),
    "507": ("PA", "🇵🇦", "Panama"),
    "509": ("HT", "🇭🇹", "Haiti"),
    "590": ("GP", "🇬🇵", "Guadeloupe"),
    "591": ("BO", "🇧🇴", "Bolivia"),
    "592": ("GY", "🇬🇾", "Guyana"),
    "593": ("EC", "🇪🇨", "Ecuador"),
    "594": ("GF", "🇬🇫", "French Guiana"),
    "595": ("PY", "🇵🇾", "Paraguay"),
    "596": ("MQ", "🇲🇶", "Martinique"),
    "597": ("SR", "🇸🇷", "Suriname"),
    "598": ("UY", "🇺🇾", "Uruguay"),
    "599": ("BQ", "🇧🇶", "Caribbean Netherlands"),
    "880": ("BD", "🇧🇩", "Bangladesh"),
    "960": ("MV", "🇲🇻", "Maldives"),
    "961": ("LB", "🇱🇧", "Lebanon"),
    "962": ("JO", "🇯🇴", "Jordan"),
    "963": ("SY", "🇸🇾", "Syria"),
    "964": ("IQ", "🇮🇶", "Iraq"),
    "965": ("KW", "🇰🇼", "Kuwait"),
    "966": ("SA", "🇸🇦", "Saudi Arabia"),
    "967": ("YE", "🇾🇪", "Yemen"),
    "968": ("OM", "🇴🇲", "Oman"),
    "970": ("PS", "🇵🇸", "Palestine"),
    "971": ("AE", "🇦🇪", "UAE"),
    "972": ("IL", "🇮🇱", "Israel"),
    "973": ("BH", "🇧🇭", "Bahrain"),
    "974": ("QA", "🇶🇦", "Qatar"),
    "975": ("BT", "🇧🇹", "Bhutan"),
    "976": ("MN", "🇲🇳", "Mongolia"),
    "977": ("NP", "🇳🇵", "Nepal"),
    "992": ("TJ", "🇹🇯", "Tajikistan"),
    "993": ("TM", "🇹🇲", "Turkmenistan"),
    "994": ("AZ", "🇦🇿", "Azerbaijan"),
    "995": ("GE", "🇬🇪", "Georgia"),
    "996": ("KG", "🇰🇬", "Kyrgyzstan"),
    "998": ("UZ", "🇺🇿", "Uzbekistan"),
}
ISO_TO_INFO = {v[0]: (v[1], v[2]) for v in COUNTRY_CODE_MAP.values()}

def get_country_code(country_name):
    if not country_name:
        return ""
    lower = country_name.lower()
    for code, (iso, flag, name) in COUNTRY_CODE_MAP.items():
        if lower == name.lower() or lower == iso.lower() or lower == code:
            return iso
    for code, (iso, flag, name) in COUNTRY_CODE_MAP.items():
        if lower in name.lower() or name.lower() in lower:
            return iso
    return country_name.upper()[:2]

# ==================== RICH MESSAGE GROUP OTP ====================
def format_group_otp_rich(entry):
    number = entry.get("number", "")
    otp_code = entry.get("otp", "")
    service_name = entry.get("service", "Unknown")
    country_raw = entry.get("country", entry.get("country_code", "?"))
    country_iso = entry.get("country_code", "")
    if not country_iso and country_raw:
        country_iso = get_country_code(country_raw) or "??"
    
    country_emoji_id = None
    if country_iso:
        row = db_fetch_one("SELECT emoji_id FROM group_emojis WHERE type='country' AND key=?", (country_iso.upper(),))
        if not row:
            row = db_fetch_one("SELECT emoji_id FROM group_emojis WHERE type='country' AND key=?", (country_iso.lower(),))
        if row and row[0]:
            country_emoji_id = row[0]
    if not country_emoji_id and country_iso and country_iso.lower() in DEFAULT_EMOJIS["countries"]:
        country_emoji_id = DEFAULT_EMOJIS["countries"][country_iso.lower()]
    
    flag_fallback = ISO_TO_INFO.get(country_iso, ("🏳", ""))[0] if country_iso else "🏳"
    if country_emoji_id:
        country_display = f'<tg-emoji emoji-id="{country_emoji_id}">{flag_fallback}</tg-emoji><b>{country_iso}</b>'
    else:
        country_display = f'{flag_fallback}<b>{country_iso}</b>'
    
    service_emoji_id = None
    svc_row = db_fetch_one("SELECT emoji_id FROM services WHERE LOWER(name) = LOWER(?)", (service_name,))
    if svc_row and svc_row[0]:
        service_emoji_id = svc_row[0]
    if not service_emoji_id:
        service_emoji_id = CUSTOM_EMOJIS.get("DEFAULT_SERVICE", "6204108584381322968")
    
    clean = number.replace('+', '').replace(' ', '').strip()
    if len(clean) >= 9:
        prefix, suffix = clean[:5], clean[-4:]
    else:
        prefix, suffix = clean, ""
    sep_tag = f'<tg-emoji emoji-id="{EMOJI_SEPARATOR}">➖</tg-emoji>'
    masked = f"<b>+{prefix}{sep_tag}{suffix}</b>" if suffix else f"<b>+{clean}</b>"
    
    top_line = (
        f'<tg-emoji emoji-id="{EMOJI_PREFIX}">🤖</tg-emoji> '
        f'{country_display} | '
        f'<tg-emoji emoji-id="{service_emoji_id}">🔧</tg-emoji> {masked}'
    )
    
    message_text = entry.get("message", "")[:500]
    sms_safe = message_text.replace("<", "&lt;").replace(">", "&gt;")
    summary = (
        f'<tg-emoji emoji-id="{LEFT_ARROW_EMOJI}">👈</tg-emoji> '
        f'<b>View Full SMS</b> '
        f'<tg-emoji emoji-id="{SEND_EMOJI}">📤</tg-emoji>'
    )
    details_block = (
        f'<details>'
        f'<summary>{summary}</summary>'
        f'<blockquote><b>{sms_safe}</b></blockquote>'
        f'</details>'
    )
    
    html = f'<p>{top_line}</p>\n{details_block}'
    
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": otp_code,
                    "icon_custom_emoji_id": EMOJI_OTP_BUTTON,
                    "style": "success",
                    "copy_text": {"text": otp_code}
                }
            ],
            [
                {
                    "text": "𝐂𝐇𝐀𝐍𝐍𝐄𝐋",
                    "icon_custom_emoji_id": EMOJI_CHANNEL_BUTTON,
                    "style": "primary",
                    "url": CHANNEL_URL
                },
                {
                    "text": "𝐁𝐎𝐓",
                    "icon_custom_emoji_id": EMOJI_BOT_BUTTON,
                    "style": "primary",
                    "url": BOT_URL
                }
            ]
        ]
    }
    return html, keyboard

# ==================== OTP PROCESSING ====================
def is_duplicate_otp_dm(number, otp_code, current_ts_str):
    try:
        current_ts = datetime.strptime(current_ts_str, "%Y-%m-%d %H:%M:%S")
    except:
        return False
    rows = db_fetch_all("SELECT timestamp FROM otps WHERE number=? AND otp=? AND user_id!=0 ORDER BY timestamp DESC LIMIT 1", (number, otp_code))
    if not rows:
        return False
    last_ts_str = rows[0][0]
    try:
        last_ts = datetime.strptime(last_ts_str, "%Y-%m-%d %H:%M:%S")
    except:
        return False
    diff = abs((current_ts - last_ts).total_seconds())
    return diff <= 0.5

async def process_otps(otps_list, context: ContextTypes.DEFAULT_TYPE = None, bot=None):
    if context:
        bot = context.bot
    if not bot:
        if application and application.bot:
            bot = application.bot
        else:
            print("❌ process_otps: No bot instance!")
            return
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    active_rows = db_fetch_all(
        "SELECT number, user_id, country, assigned_date FROM numbers WHERE status='active' AND expiry_time > ?",
        (now_str,))
    num_map = {}
    for num, uid, country, assigned in active_rows:
        clean = num.replace('+', '')
        num_map.setdefault(clean, []).append((uid, country, assigned))
    
    for otp_entry in otps_list:
        number = otp_entry.get("number", "")
        otp_code = otp_entry.get("otp", "")
        service_name = otp_entry.get("service", "Unknown")
        otp_timestamp_str = otp_entry.get("timestamp", now_str)
        message = otp_entry.get("message", "")[:200]
        
        if not number or not otp_code:
            continue
        
        if GROUP_ID:
            already_sent = db_fetch_one("SELECT id FROM otps WHERE number=? AND otp=? AND user_id=0", (number, otp_code))
            if not already_sent:
                db_exec("INSERT INTO otps (number, otp, message, timestamp, forwarded, user_id) VALUES (?,?,?,?,1,0)",
                        (number, otp_code, message, otp_timestamp_str))
                try:
                    grp_html, grp_kb = format_group_otp_rich({
                        "number": number,
                        "otp": otp_code,
                        "service": service_name,
                        "country_code": otp_entry.get("country_code", ""),
                        "country": otp_entry.get("country", ""),
                        "message": message
                    })
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendRichMessage"
                    payload = {
                        "chat_id": GROUP_ID,
                        "rich_message": {"html": grp_html},
                        "reply_markup": grp_kb
                    }
                    requests.post(url, json=payload, timeout=10)
                except Exception as e:
                    print(f"Group Rich message failed: {e}")
        
        if number in num_map:
            try:
                otp_timestamp = datetime.strptime(otp_timestamp_str, "%Y-%m-%d %H:%M:%S")
            except:
                otp_timestamp = now
            for uid, country, assigned_date_str in num_map[number]:
                if db_fetch_one("SELECT banned FROM users WHERE user_id=? AND banned=1", (uid,)):
                    continue
                try:
                    assigned_date = datetime.strptime(assigned_date_str, "%Y-%m-%d %H:%M:%S")
                except:
                    assigned_date = now
                if otp_timestamp < assigned_date:
                    continue
                if is_duplicate_otp_dm(number, otp_code, otp_timestamp_str):
                    continue
                country_data = get_country_info(country)
                payout_str = country_data.get("payout", "0.001$")
                try:
                    reward = parse_payout(payout_str)
                except:
                    reward = 0.001
                db_exec("UPDATE users SET balance = balance + ?, total_otp = total_otp + 1 WHERE user_id = ?",
                        (reward, uid))
                db_exec("INSERT INTO otps (number, otp, message, timestamp, forwarded, user_id) VALUES (?,?,?,?,1,?)",
                        (number, otp_code, message, otp_timestamp_str, uid))
                flag_eid = country_data.get("emoji_id") or CUSTOM_EMOJIS["DEFAULT_FLAG"]
                country_iso = country_data.get("iso", "").upper()
                svc_row = db_fetch_one("SELECT emoji_id FROM services WHERE LOWER(name) = LOWER(?)", (service_name,))
                svc_eid = svc_row[0] if svc_row and svc_row[0] else CUSTOM_EMOJIS["DEFAULT_SERVICE"]
                header = (
                    f'{emoji_tag("5278576134622056695", "🆕")} <b>NEW</b> '
                    f'{emoji_tag(flag_eid, "🏁")}<b>{country_iso} OTP ARRIVED</b>\n'
                    f'{emoji_tag("6204108584381322968", "📱")} <b>NUMBER</b>: +{number}\n'
                    f'{emoji_tag("5976327845696251345", "📲")} <b>APP</b>: {emoji_tag(svc_eid, "⚙️")} <b>{service_name}</b>\n'
                    f'💰 <b>BALANCE ADDED</b>: <code>+${reward}</code>{emoji_tag("5976788549658221281", "💵")}'
                )
                button = InlineKeyboardMarkup([[
                    InlineKeyboardButton(text=otp_code, copy_text=CopyTextButton(text=otp_code),
                                         style=KBS.SUCCESS, icon_custom_emoji_id=safe_icon("5330115548900501467"))
                ]])
                try:
                    await bot.send_message(uid, header, reply_markup=button, parse_mode='HTML')
                except Exception as e:
                    print(f"DM OTP failed for {uid}: {e}")
    save_user_data_json()

async def poll_api(api_id):
    while not application or not application.bot:
        await asyncio.sleep(1)
    while True:
        key = db_fetch_one("SELECT base_url, token, interval_sec, active FROM api_keys WHERE id=? AND active=1", (api_id,))
        if not key:
            break
        base_url, token, interval, _ = key
        try:
            resp = requests.get(f"{base_url}/all_otp?token={token}", timeout=10)
            if resp.status_code == 200 and resp.json().get("status") == "success":
                otps = resp.json().get("data", {}).get("otps", [])
                await process_otps(otps, bot=application.bot)
        except Exception as e:
            print(f"API {api_id} error: {e}")
        await asyncio.sleep(interval)

# ==================== GENERIC TEXT HANDLER ====================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if await handle_admin_text(update, context): return
    if await handle_api_add_text(update, context): return
    user_id = update.effective_user.id
    if await ban_check(update, context): return
    text = update.message.text.strip()
    if text == BTN_GET_NUMBER: await send_get_number_panel(update, context)
    elif text == BTN_BALANCE: await send_balance_panel(update, context)
    elif text == BTN_SUPPORT: await send_support_panel(update, context)
    elif text == BTN_ADMIN: await send_admin_panel_msg(update, context)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

# ==================== MAIN ====================
application = None

def main():
    global application
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(MessageHandler(filters.Document.ALL & filters.ChatType.PRIVATE, handle_all_documents), group=0)
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_admin_text), group=1)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("enteradmin", enter_admin_command))
    application.add_handler(CommandHandler("exitadmin", exit_admin_command))
    application.add_handler(CommandHandler("addadmin", add_admin_command))
    application.add_handler(CommandHandler("removeadmin", remove_admin_command))
    application.add_handler(CommandHandler("adminlist", admin_list_command))
    application.add_handler(CommandHandler("country", group_country_command))
    application.add_handler(CommandHandler("service", group_service_command))

    application.add_handler(CallbackQueryHandler(service_selection_callback, pattern="^svc_sel\|"))
    application.add_handler(CallbackQueryHandler(country_selection_callback, pattern="^cnt_sel\|"))
    application.add_handler(CallbackQueryHandler(back_to_services_callback, pattern="^back_to_services$"))
    application.add_handler(CallbackQueryHandler(country_add_service_callback, pattern="^cnt_add_svc\|"))
    application.add_handler(CallbackQueryHandler(next_number_callback, pattern="^next_number$"))
    application.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^admin_del\|"))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    application.add_handler(CallbackQueryHandler(country_callback, pattern="^country_"))
    application.add_handler(CallbackQueryHandler(service_callback, pattern="^service_"))
    application.add_handler(CallbackQueryHandler(service_callback, pattern="^service_set_emoji$"))
    application.add_handler(CallbackQueryHandler(service_callback, pattern=r"^service_emoji_set\|"))
    application.add_handler(CallbackQueryHandler(balance_menu_callback, pattern="^menu_balance$"))
    application.add_handler(CallbackQueryHandler(withdraw_callback, pattern="^withdraw$"))
    application.add_handler(CallbackQueryHandler(noop_callback, pattern="^noop$"))
    application.add_handler(CallbackQueryHandler(toggle_cc_callback, pattern="^toggle_cc$"))
    application.add_handler(CallbackQueryHandler(fu_country_callback, pattern=r"^fu_country\|"))
    application.add_handler(CallbackQueryHandler(fu_service_callback, pattern=r"^fu_service\|"))
    application.add_handler(CallbackQueryHandler(_user_manager_wrapper, pattern="^admin_user_manager$"))
    application.add_handler(CallbackQueryHandler(_um_search_wrapper, pattern="^um_search$"))
    application.add_handler(CallbackQueryHandler(send_user_list_file, pattern="^um_download$"))
    application.add_handler(CallbackQueryHandler(um_stats, pattern="^um_stats$"))
    application.add_handler(CallbackQueryHandler(_um_edit_balance_wrapper, pattern=r"^um_editbal\|"))
    application.add_handler(CallbackQueryHandler(_um_ban_toggle_wrapper, pattern=r"^um_ban\|"))
    application.add_handler(CallbackQueryHandler(_user_manager_wrapper, pattern="^um_back$"))
    application.add_handler(CallbackQueryHandler(_database_wrapper, pattern="^admin_database$"))
    application.add_handler(CallbackQueryHandler(db_download, pattern="^db_download$"))
    application.add_handler(CallbackQueryHandler(db_upload_prompt, pattern="^db_upload$"))
    application.add_handler(CallbackQueryHandler(_manage_api_wrapper, pattern="^admin_manage_api$"))
    application.add_handler(CallbackQueryHandler(_api_add_wrapper, pattern="^api_add$"))
    application.add_handler(CallbackQueryHandler(_api_remove_wrapper, pattern="^api_remove$"))
    application.add_handler(CallbackQueryHandler(_api_list_wrapper, pattern="^api_list$"))
    application.add_handler(CallbackQueryHandler(api_remove_execute, pattern=r"^api_rem_\d+$"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    application.add_error_handler(error_handler)

    if application.job_queue:
        application.job_queue.run_repeating(periodic_json_save, interval=60, first=10)

    async def start_api_tasks(app):
        print("🚀 Starting added API polling tasks...")
        for (api_id,) in db_fetch_all("SELECT id FROM api_keys WHERE active=1"):
            asyncio.create_task(poll_api(api_id))
            print(f"   ➤ Started polling for API {api_id}")

    application.post_init = start_api_tasks

    save_user_data_json()
    print(f"✅ Super Admins: {SUPER_ADMIN_IDS}")
    print(f"✅ Multi-admin, User Manager, Multi-API, Rich Message Group OTP active")
    print(f"✅ User data JSON saved to {USER_DATA_FILE}")
    print("🔄 Starting polling...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
