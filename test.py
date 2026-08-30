# THIS PREMUAM BOT WAS MADE BY : RAKESH DEV 
#TG : @SR_ADMIN_RAKESH,  AND DON'T TRY TO CHANGR SNY CREDIT
import asyncio, json, os, re, sqlite3, threading, tempfile, zipfile, shutil
from datetime import datetime, timedelta
import random
import html  # for escaping

import aiohttp
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
BOT_TOKEN = "8769374062:AAHTIxugF2XHffjlg6p2Xrd4Br-OUezroro"
SUPER_ADMIN_IDS = [8744359777]

AUTO_DELETE_DELAY = 2          # seconds (for normal messages)
MAIN_MENU_DELETE = 120         # 2 minutes

OTP_GROUP_URL = "https://t.me/NumberFlexOTP"
MIN_WITHDRAW = 0.1

ADMIN_WHATSAPP = "https://wa.me/8801962636806"
ADMIN_TELEGRAM = "t.me/SR_ADMIN_RAKESH"
ADMIN2_WHATSAPP = ""
ADMIN2_TELEGRAM = "t.me/ABU_SAID_0_9"

# Multiple group IDs – you can define them as:
#   A) a tuple/list of strings: GROUP_ID = "-1003716770621","-1001234567890"
#   B) a comma-separated string: GROUP_ID = "-1003716770621,-1001234567890"
#   C) a single string: GROUP_ID = "-1003716770621"
GROUP_ID = "-1003716770621","-1004309109716"   # ← edit as needed
CHANNEL_URL = "https://t.me/A_S_COMMUNITY_9_x"
BOT_URL = "https://t.me/AIR_NUMBER_BOT?start=1"

# Parse GROUP_ID into a list of integers
GROUP_IDS = []
if GROUP_ID:
    if isinstance(GROUP_ID, (list, tuple)):
        # e.g. ("-1003716770621", "-1001234567890")
        GROUP_IDS = [int(str(gid).strip()) for gid in GROUP_ID if str(gid).strip()]
    elif isinstance(GROUP_ID, str):
        if ',' in GROUP_ID:
            # Comma‑separated string: "-1003716770621,-1001234567890"
            GROUP_IDS = [int(gid.strip()) for gid in GROUP_ID.split(',') if gid.strip()]
        else:
            # Single group ID as a string
            GROUP_IDS = [int(GROUP_ID.strip())] if GROUP_ID.strip() else []
    else:
        # Fallback: try converting directly (just in case)
        try:
            GROUP_IDS = [int(GROUP_ID)]
        except (ValueError, TypeError):
            GROUP_IDS = []
            
# ==================== EMOJI CONSTANTS ====================
WELCOME_WAVE = "5199885118214255386"      # 👋
WELCOME_THINK = "5314563983422798645"     # 🤔
INBOX_EMOJI = "5472239203590888751"       # 📩
MONEY_EMOJI = "5805602131176069048"       # 🤑

MAIN_MENU_EMOJI = "5438499684270238914"   # for main menu

HEADER_EMOJI_1 = "6282641460093260838"
HEADER_EMOJI_2 = "6267315814190290529"

SUPPORT_EMOJI = "6264853036993090338"     # new support emoji

EMOJI_SEPARATOR = "5213333270703387541"

# Group OTP constants
EMOJI_PREFIX = "4958725487682650920"
EMOJI_OTP_BUTTON = "6206420230269310869"
EMOJI_CHANNEL_BUTTON = "6204010762206189094"
EMOJI_BOT_BUTTON = "5339267587337370029"
LEFT_ARROW_EMOJI = "6068830682359010545"
SEND_EMOJI = "5433614747381538714"

# ==================== CUSTOM EMOJIS ADDITIONS ====================
# Updated with premium emoji IDs
CUSTOM_EMOJIS["USER_MANAGER"] = "6307777408300753473"
CUSTOM_EMOJIS["SEARCH_USER"] = "6206446249181189526"
CUSTOM_EMOJIS["DOWNLOAD_LIST"] = "6203886371363364022"
CUSTOM_EMOJIS["EDIT_BALANCE"] = "6204162490515855272"
CUSTOM_EMOJIS["BAN_USER"] = "6203761490894264678"
CUSTOM_EMOJIS["MANAGE_API"] = "6206188632747808299"
CUSTOM_EMOJIS["ADD_API_KEY"] = "6206375377925839184"
CUSTOM_EMOJIS["REMOVE_API_KEY"] = "6206108815075579644"
CUSTOM_EMOJIS["LIST_API_KEY"] = "6307686831735444755"
CUSTOM_EMOJIS["SUPPORT"] = SUPPORT_EMOJI
CUSTOM_EMOJIS["SELECT_SERVICE_PREFIX"] = "6206236607532504295"
CUSTOM_EMOJIS["SELECT_SERVICE_SUFFIX"] = "5197474438970363734"
CUSTOM_EMOJIS["SELECT_COUNTRY_PREFIX"] = "5309748255637118475"
CUSTOM_EMOJIS["PROFILE_ICON"] = "5818715087237549366"

# Stock Management
CUSTOM_EMOJIS["STOCK_MANAGER"] = "6206236607532504295"
CUSTOM_EMOJIS["REMOVE_STOCK"] = "6206108815075579644"  # updated to premium
CUSTOM_EMOJIS["STOCK_STATUS"] = "4958506272551863292"
CUSTOM_EMOJIS["TOGGLE_STOCK"] = "4956583802240500602"
CUSTOM_EMOJIS["YES"] = "4956721670690702265"
CUSTOM_EMOJIS["NO"] = "6206110936789423908"
CUSTOM_EMOJIS["GET_NUMBER"] = "5303449763406954093"
CUSTOM_EMOJIS["NEW_NUMBER"] = "5877410604225924969"

# API System
CUSTOM_EMOJIS["API_SYSTEM"] = "6271486270384378674"
CUSTOM_EMOJIS["API_STATUS_ACTIVE"] = "5339112148175959615"
CUSTOM_EMOJIS["API_STATUS_INACTIVE"] = "5337017423906226569"
CUSTOM_EMOJIS["API_START_POLL"] = "6267264360482084046"
CUSTOM_EMOJIS["API_STOP_POLL"] = "6266797059450347770"
CUSTOM_EMOJIS["API_FORCE_POLL"] = "6282893896796082998"
CUSTOM_EMOJIS["API_TEST"] = "5978568938156461643"
CUSTOM_EMOJIS["API_STATS"] = "6266936886405633043"
CUSTOM_EMOJIS["API_LOGS"] = "5818774589714468177"
CUSTOM_EMOJIS["API_FIELD_NAME"] = "5818775306974006843"
CUSTOM_EMOJIS["API_FIELD_URL"] = "6285048454255220485"
CUSTOM_EMOJIS["API_FIELD_ENDPOINT"] = "6267172559851099903"
CUSTOM_EMOJIS["API_FIELD_TOKEN"] = "5821453562680448557"
CUSTOM_EMOJIS["API_FIELD_METHOD"] = "5926860096008098405"
CUSTOM_EMOJIS["API_FIELD_INTERVAL"] = "6093456762113888541"
CUSTOM_EMOJIS["API_FIELD_RECORDS"] = "5868569066154757449"
CUSTOM_EMOJIS["API_FIELD_RETRY"] = "5978846612087114958"
CUSTOM_EMOJIS["API_FIELD_OTP_PATH"] = "5818955300463447293"
CUSTOM_EMOJIS["API_FIELD_NUMBER"] = "5877410604225924969"
CUSTOM_EMOJIS["API_FIELD_MESSAGE"] = "5980911993140284450"
CUSTOM_EMOJIS["API_FIELD_COUNTRY"] = "5188381825701021648"
CUSTOM_EMOJIS["API_FIELD_SERVICE"] = "5818967150278218011"
CUSTOM_EMOJIS["API_FIELD_TIMESTAMP"] = "6285240160120477644"
CUSTOM_EMOJIS["API_FIELD_SUCCESS_PATH"] = "6267008582294705964"
CUSTOM_EMOJIS["API_FIELD_SUCCESS_VALUE"] = "6267039884016358504"
CUSTOM_EMOJIS["API_TODAY_OTP"] = "6224129999633388168"
CUSTOM_EMOJIS["API_TOTAL_OTP"] = "6266794310671275367"
CUSTOM_EMOJIS["API_LAST_POLL"] = "6267229004311303657"
CUSTOM_EMOJIS["API_ERROR_COUNT"] = "6267039884016358504"
CUSTOM_EMOJIS["API_SUCCESS_RATE"] = "6267058648728474885"
CUSTOM_EMOJIS["API_OTP_COUNT"] = "5978854270013804830"
CUSTOM_EMOJIS["API_BLOCK_START"] = "5947029782121155470"
CUSTOM_EMOJIS["API_BLOCK_END"] = "5947216621788465862"
CUSTOM_EMOJIS["API_SEPARATOR"] = "5870818207383686839"
CUSTOM_EMOJIS["BACK"] = "6118297066247558366"   # updated to premium
CUSTOM_EMOJIS["DELETE"] = "6206108815075579644"   # updated to premium (same as remove stock)
CUSTOM_EMOJIS["ADMIN"] = "6206319341487527808"    # updated to premium
CUSTOM_EMOJIS["UPLOAD"] = "6206046503690048595"
CUSTOM_EMOJIS["CANCEL"] = "6267000941547885720"
CUSTOM_EMOJIS["BROADCAST"] = "6206080502651164081" # updated to premium
CUSTOM_EMOJIS["ADD"] = "6206375377925839184"
CUSTOM_EMOJIS["GIVEAWAY"] = "6282893896796082998"
CUSTOM_EMOJIS["STATS"] = "6266936886405633043"
CUSTOM_EMOJIS["PACKAGE"] = "5463412319948148591"
CUSTOM_EMOJIS["GEAR"] = "6206236607532504295"
CUSTOM_EMOJIS["CHANGE_COUNTRY"] = "5188540541922480562"
CUSTOM_EMOJIS["GREEN_CIRCLE"] = "5339112148175959615"
CUSTOM_EMOJIS["RED_CIRCLE"] = "5337017423906226569"
CUSTOM_EMOJIS["CLOCK"] = "6267229004311303657"
CUSTOM_EMOJIS["DEFAULT_FLAG"] = "5188540541922480562"
CUSTOM_EMOJIS["DEFAULT_SERVICE"] = "5465590345108589516"
CUSTOM_EMOJIS["JOIN_OTP_GROUP"] = "6204010762206189094"

# Custom emoji IDs for LIST API format
CUSTOM_EMOJIS["API_LIST_ICON"] = "5411225014148014586"
CUSTOM_EMOJIS["API_LIST_INTERVAL_ICON"] = "6235253239080555488"

# SKIP emoji (premium)
SKIP_EMOJI = "6267262260243076354"  # ⏭

# Database emoji (premium)
DATABASE_EMOJI = "5818955300463447293"

# ==================== DATABASE FOLDER ====================
DB_DIR = "NUMBER-PANEL-DATA"
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "mrisbrand_master.db")
USER_DATA_FILE = os.path.join(DB_DIR, "user_data.json")

# ==================== DATABASE SETUP ====================
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
db_lock = threading.Lock()
c = conn.cursor()

# ---- Users ----
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
              joined_date TEXT, last_active TEXT,
              current_number_id INTEGER DEFAULT NULL,
              current_number TEXT DEFAULT NULL, current_country TEXT DEFAULT NULL,
              current_service TEXT DEFAULT NULL, number_expiry TEXT DEFAULT NULL,
              last_menu_message_id INTEGER DEFAULT NULL,
              last_bot_message_id INTEGER DEFAULT NULL,
              remove_cc INTEGER DEFAULT 0,
              banned INTEGER DEFAULT 0,
              persistent_message_id INTEGER DEFAULT NULL)''')

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

# ---- Enhanced API Keys ----
c.execute('''CREATE TABLE IF NOT EXISTS api_keys
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              panel_name TEXT,
              base_url TEXT,
              token TEXT,
              interval_sec INTEGER,
              active INTEGER DEFAULT 1,
              endpoint TEXT DEFAULT '/',
              method TEXT DEFAULT 'GET',
              headers TEXT,
              body_template TEXT,
              response_type TEXT DEFAULT 'json',
              otp_list_path TEXT DEFAULT 'data',
              number_path TEXT DEFAULT 'num',
              message_path TEXT DEFAULT 'message',
              country_path TEXT DEFAULT 'country',
              service_path TEXT DEFAULT 'cli',
              timestamp_path TEXT DEFAULT 'dt',
              success_path TEXT DEFAULT 'status',
              success_value TEXT DEFAULT 'success',
              max_records INTEGER DEFAULT 200,
              retry_count INTEGER DEFAULT 3,
              retry_delay INTEGER DEFAULT 5,
              error_count INTEGER DEFAULT 0,
              last_poll_time TEXT,
              total_otps INTEGER DEFAULT 0,
              last_otp_time TEXT,
              created_by INTEGER,
              created_at TEXT,
              updated_at TEXT,
              placeholder_config TEXT DEFAULT '{}',
              curl_command TEXT)''')

# ---- API Logs ----
c.execute('''CREATE TABLE IF NOT EXISTS api_logs
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              api_id INTEGER,
              timestamp TEXT,
              status TEXT,
              message TEXT,
              otp_count INTEGER)''')

# ---- Add missing columns for older DB ----
for col in ['balance', 'withdrawn', 'total_otp', 'remove_cc', 'banned', 'last_bot_message_id', 'keyboard_message_id', 'persistent_message_id']:
    try:
        c.execute(f"ALTER TABLE users ADD COLUMN {col} {'REAL' if col in ['balance','withdrawn'] else 'INTEGER'} DEFAULT 0")
    except sqlite3.OperationalError:
        pass
try:
    c.execute("ALTER TABLE services ADD COLUMN emoji_id TEXT DEFAULT ''")
except sqlite3.OperationalError:
    pass

# ---- Default services ----
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
polling_tasks = {}

# ==================== HELPER FUNCTIONS ====================
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

def get_country_name_by_iso(iso2: str) -> str | None:
    iso2 = iso2.upper()
    for name, info in COUNTRIES_DATA.items():
        if info.get("iso", "").upper() == iso2:
            return name
    for code, (iso, flag, name) in COUNTRY_CODE_MAP.items():
        if iso.upper() == iso2:
            return name
    return None

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
BTN_GET_NUMBER = "GET NUMBER"
BTN_BALANCE = "BALANCE"
BTN_SUPPORT = "SUPPORT"
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
                               input_field_placeholder="")

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
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("User Manager", callback_data="admin_user_manager", style=KBS.PRIMARY,
                                 icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("USER_MANAGER", ""))),
            InlineKeyboardButton("Stock Management", callback_data="admin_stock_management", style=KBS.SUCCESS,
                                 icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("STOCK_MANAGER", ""))),
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
                                 icon_custom_emoji_id=safe_icon(DATABASE_EMOJI)),  # updated
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

# ==================== STOCK MANAGEMENT KEYBOARD ====================
def stock_management_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("Upload Stock", callback_data="stock_upload", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("UPLOAD", "")))],
        [InlineKeyboardButton("Remove Stock", callback_data="stock_remove", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("REMOVE_STOCK", "")))],
        [InlineKeyboardButton("Stock Status", callback_data="stock_status", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("STOCK_STATUS", "")))],
        [InlineKeyboardButton("Toggle Stock", callback_data="stock_toggle", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("TOGGLE_STOCK", "")))],
        [InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))],
    ]
    return InlineKeyboardMarkup(rows)

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

# ============================================================
# ==================== UPDATED OTP DETECTION ====================
# ============================================================

# Universal regex for OTP-like tokens (provided)
UNIVERSAL_OTP_REGEX = re.compile(
    r'(?i)(?<![A-Z0-9])(?:\d{3,10}|[A-Z0-9]{3,10}|[A-Z0-9]{1,10}(?:\s*[-–—]\s*[A-Z0-9]{1,10})+)(?![A-Z0-9])'
)

# Keywords that strongly indicate an OTP
OTP_KEYWORDS = [
    r'otp', r'code', r'pin', r'passcode', r'verification', r'auth',
    r'confirm', r'security', r'two[- ]factor', r'sms',
    r'ওটিপি', r'ভেরিফিকেশন', r'পিন', r'কোড',  # Bangla
    r'ओटीपी', r'कोड', r'पिन', r'सत्यापन',    # Hindi
    r'código', r'verificación', r'clave',      # Spanish
    r'رمز', r'التحقق', r'كلمة المرور'         # Arabic
]
OTP_KEYWORD_PATTERN = re.compile(r'(?i)(?:' + '|'.join(OTP_KEYWORDS) + r')')

# Patterns that commonly appear before the OTP value (e.g., "is:", ":", "=")
OTP_SEPARATORS = r'[:=]\s*'

def _clean_token(token: str) -> str:
    """Remove common separators (space, dash, underscore, etc.) and return cleaned token."""
    # Remove whitespace and common separators but keep dashes if they are part of format like AB-123
    # We'll keep the original token for display, but for matching we may need to clean.
    # Return token as is; we'll handle matching with original.
    return token.strip()

def _score_candidate(candidate: str, full_message: str) -> int:
    """
    Score a candidate OTP based on context and likelihood.
    Higher score = more likely to be the actual OTP.
    """
    score = 0
    # Prefer candidates that are near keywords
    # Find all keyword matches
    keyword_matches = list(OTP_KEYWORD_PATTERN.finditer(full_message))
    if keyword_matches:
        # Find distance from candidate to nearest keyword
        candidate_start = full_message.find(candidate)
        if candidate_start != -1:
            nearest_distance = min(abs(m.start() - candidate_start) for m in keyword_matches)
            # Closer = higher score
            if nearest_distance < 20:
                score += 50
            elif nearest_distance < 50:
                score += 30
            elif nearest_distance < 100:
                score += 10
    # Prefer candidates that are preceded by separator (like ':', '=', 'is')
    sep_match = re.search(OTP_SEPARATORS + re.escape(candidate), full_message)
    if sep_match:
        score += 40
    # Prefer candidates that have 4-6 digits (common OTP length)
    if re.match(r'^\d{4,6}$', candidate):
        score += 20
    elif re.match(r'^[A-Z0-9]{4,8}$', candidate):
        score += 15
    # Penalise very long or very short (but still allow)
    if len(candidate) < 4:
        score -= 10
    if len(candidate) > 10:
        score -= 5
    # Penalise if candidate looks like a phone number (starts with + or has length >10 and all digits)
    if re.match(r'^\+?\d{10,15}$', candidate):
        score -= 50
    # Penalise if candidate looks like a year (19xx or 20xx)
    if re.match(r'^(19|20)\d{2}$', candidate):
        score -= 30
    # Penalise if candidate is purely numeric and appears as part of a longer number
    # (e.g., "1234567890" might be phone; but we already penalised phone)
    return score

def extract_otp_from_message(message: str) -> str | None:
    """
    Intelligent OTP extractor using regex, scoring, and fallback.
    Returns the most likely OTP string, or None if nothing suitable found.
    """
    if not message:
        return None

    # 1. Use the universal regex to get all candidate tokens
    candidates = UNIVERSAL_OTP_REGEX.findall(message)
    if not candidates:
        # No tokens found; try to extract any 4-6 digit sequence as last resort
        fallback = re.findall(r'\b(\d{4,6})\b', message)
        if fallback:
            # Filter out obvious years
            filtered = [num for num in fallback if not (len(num)==4 and num.startswith(('19','20')))]
            if filtered:
                # Take the first one that appears near an OTP keyword or at the end
                candidates = filtered

    if not candidates:
        return None

    # Remove duplicates while preserving order
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique_candidates.append(c)
    candidates = unique_candidates

    # Score each candidate
    scored = [(c, _score_candidate(c, message)) for c in candidates]
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # Return the highest scoring candidate if score > 0, otherwise None
    best = scored[0]
    if best[1] > 0:
        return best[0]
    else:
        # If no positive score, but we have candidates, return the first one
        # Only if it's reasonably OTP-like (len between 3 and 10)
        for c, s in scored:
            if 3 <= len(c) <= 10:
                return c
    return None

def extract_all_otps_from_message(message: str) -> list[str]:
    """
    Return a list of all potential OTP tokens found in the message.
    This is used for debugging or other purposes, but main extraction uses the above.
    """
    if not message:
        return []
    candidates = UNIVERSAL_OTP_REGEX.findall(message)
    # Filter out obvious non-OTP patterns (phone numbers, years) but keep for now
    # We'll just return unique tokens
    return list(set(candidates))

# ============================================================
# ==================== END OF OTP DETECTION ====================
# ============================================================

# ==================== NUMBERS MESSAGE FORMATTER ====================
def format_numbers_message(country, service, numbers, user_id=None, first_name=None):
    if first_name is None:
        first_name = "User"
    remove_cc = 0
    if user_id:
        row = db_fetch_one("SELECT remove_cc FROM users WHERE user_id=?", (user_id,))
        if row:
            remove_cc = row[0] or 0

    flag_eid = get_country_info(country).get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
    country_code = get_country_info(country).get("code", "")
    service_eid_row = db_fetch_one("SELECT emoji_id FROM services WHERE LOWER(name) = LOWER(?)", (service,))
    service_eid = service_eid_row[0] if service_eid_row and service_eid_row[0] else CUSTOM_EMOJIS.get("DEFAULT_SERVICE", "")
    phone_icon_id = "5197474438970363734"

    header = (
        f'{emoji_tag(HEADER_EMOJI_1, "⚙️")} <b>THIS IS YOUR</b> '
        f'{emoji_tag(HEADER_EMOJI_2, "📱")} <b>{country.upper()}</b> '
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
                                         icon_custom_emoji_id=safe_icon("6267000941547885720"))
    rows.append([cc_button])

    rows.append([
        InlineKeyboardButton("New Number", callback_data="next_number", style=KBS.PRIMARY,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("NEW_NUMBER", ""))),
        InlineKeyboardButton("Change Service", callback_data="back_to_services", style=KBS.SUCCESS,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CHANGE_COUNTRY", ""))),
    ])
    rows.append([
        InlineKeyboardButton("OTP Group", url=OTP_GROUP_URL, style=None,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("JOIN_OTP_GROUP", ""))),
    ])
    return header, InlineKeyboardMarkup(rows)

# ==================== STOCK ADDED MESSAGES ====================
def stock_added_message(country, service, count):
    flag_eid = get_country_info(country).get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
    svc_eid_row = db_fetch_one("SELECT emoji_id FROM services WHERE name = ?", (service,))
    svc_eid = svc_eid_row[0] if svc_eid_row and svc_eid_row[0] else CUSTOM_EMOJIS.get("DEFAULT_SERVICE", "")
    payout = get_country_info(country).get("payout", "0.001$")

    EMOJI_EYE = "4958617898751886363"
    EMOJI_PACKAGE = "5463412319948148591"
    EMOJI_CHECK = "4956721670690702265"
    EMOJI_NUMBER = "6204108584381322968"
    EMOJI_COUNTRY = "5188540541922480562"
    EMOJI_SERVICE = "5465590345108589516"
    EMOJI_PAYOUT = "5445353829304387411"
    EMOJI_COIN = "6118207206941790766"

    return (
        f'<blockquote>{emoji_tag(EMOJI_EYE, "👁️")} <b>STOCK</b> '
        f'{emoji_tag(EMOJI_PACKAGE, "📦")} <b>ADDED SUCCESSFULLY</b> '
        f'{emoji_tag(EMOJI_CHECK, "✅")}</blockquote>\n\n'
        f'<b>NUMBER</b> {emoji_tag(EMOJI_NUMBER, "📱")} : <code>{count}</code>\n'
        f'<b>COUNTRY</b> {emoji_tag(EMOJI_COUNTRY, "🌍")} : {emoji_tag(flag_eid, "🏁")} <b>{country}</b>\n'
        f'<b>SERVICE</b> {emoji_tag(EMOJI_SERVICE, "🔧")} : {emoji_tag(svc_eid, "⚙️")} <b>{service}</b>\n'
        f'<b>PAYOUT</b> {emoji_tag(EMOJI_PAYOUT, "💰")} : <code>{payout}</code> {emoji_tag(EMOJI_COIN, "🪙")}'
    )

def stock_added_broadcast_with_button(country, service, count):
    msg = stock_added_message(country, service, count)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "Get Number",
            callback_data=f"stock_get_number|{country}|{service}",
            style=KBS.PRIMARY,
            icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("GET_NUMBER", ""))
        )
    ]])
    return msg, kb

# ==================== PERSISTENT WELCOME MESSAGE ====================
async def ensure_persistent_welcome(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Send or edit the persistent welcome message with keyboard."""
    welcome_html = start_welcome_html()
    row = db_fetch_one("SELECT persistent_message_id FROM users WHERE user_id=?", (user_id,))
    if row and row[0]:
        try:
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=row[0],
                text=welcome_html,
                reply_markup=bottom_menu_keyboard(user_id),
                parse_mode='HTML'
            )
            return
        except Exception:
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=row[0])
            except:
                pass
    sent = await context.bot.send_message(
        chat_id=user_id,
        text=welcome_html,
        reply_markup=bottom_menu_keyboard(user_id),
        parse_mode='HTML'
    )
    db_exec("UPDATE users SET persistent_message_id=? WHERE user_id=?", (sent.message_id, user_id))

# ==================== MESSAGE BUILDERS ====================
def start_welcome_html():
    wave = emoji_tag(WELCOME_WAVE, "👋")
    think = emoji_tag(WELCOME_THINK, "🤔")
    inbox = emoji_tag(INBOX_EMOJI, "📩")
    money = emoji_tag(MONEY_EMOJI, "🤑")
    blockquote = (
        f'<blockquote>{wave} <b>WELCOME TO OUR 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓</b> {think}</blockquote>'
    )
    sub = f'<b>{inbox} RECEIVE OTP\'S AND START EARNING MONEY {money}</b>'
    return f'{blockquote}\n{sub}'

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

async def send_clean_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None, parse_mode=None, auto_delete: bool = True, delete_after: int = None):
    user_id = update.effective_user.id
    await delete_previous_messages(update, context)
    sent = await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?", (sent.message_id, user_id))
    if auto_delete and delete_after is None:
        await schedule_delete(context, user_id, sent.message_id)
    elif delete_after:
        await schedule_delete(context, user_id, sent.message_id, delete_after)
    return sent

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Send a persistent Main Menu message with bottom keyboard."""
    main_text = f'{emoji_tag(MAIN_MENU_EMOJI, "📱")} <b>Main Menu</b>'
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, main_text, reply_markup=bottom_menu_keyboard(user_id), parse_mode='HTML', context=context, auto_delete=False, delete_after=None)
    else:
        await send_clean_message(update, context, main_text, reply_markup=bottom_menu_keyboard(user_id), parse_mode='HTML', auto_delete=False)

# ==================== SAFE EDIT / SEND FALLBACK ====================
async def edit_or_send(query: CallbackQuery, text: str, reply_markup=None, parse_mode=None, context: ContextTypes.DEFAULT_TYPE = None, auto_delete: bool = True, delete_after: int = None):
    user_id = query.from_user.id
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        if delete_after:
            await schedule_delete(context, query.message.chat_id, query.message.message_id, delete_after)
        return None
    except BadRequest as e:
        if "Message is not modified" in str(e):
            return None
        if context and context.bot:
            try:
                await query.message.delete()
            except:
                pass
            sent = await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?",
                    (sent.message_id, user_id))
            if auto_delete and delete_after is None:
                await schedule_delete(context, query.message.chat_id, sent.message_id)
            elif delete_after:
                await schedule_delete(context, query.message.chat_id, sent.message_id, delete_after)
            return sent
        return None

# ==================== REPLY OR EDIT (UNIVERSAL) ====================
async def reply_or_edit(target, text: str, reply_markup=None, parse_mode=None, context: ContextTypes.DEFAULT_TYPE = None, auto_delete: bool = True, delete_after: int = None):
    """Universal function to either edit an inline message or send a new one."""
    if isinstance(target, CallbackQuery):
        await edit_or_send(target, text, reply_markup=reply_markup, parse_mode=parse_mode, context=context, auto_delete=auto_delete, delete_after=delete_after)
    elif hasattr(target, 'callback_query') and target.callback_query:
        await edit_or_send(target.callback_query, text, reply_markup=reply_markup, parse_mode=parse_mode, context=context, auto_delete=auto_delete, delete_after=delete_after)
    else:
        if context:
            await send_clean_message(target, context, text, reply_markup=reply_markup, parse_mode=parse_mode, auto_delete=auto_delete, delete_after=delete_after)
        else:
            if hasattr(target, 'message'):
                await target.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            elif hasattr(target, 'edit_message_text'):
                await target.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)

# ==================== START COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await ban_check(update, context):
        return
    username = update.effective_user.username
    first_name = update.effective_user.first_name or "User"
    ensure_user(user_id, username, first_name)
    db_exec("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    admin_mode.pop(user_id, None)
    admin_panel_state.pop(user_id, None)
    admin_temp_data.pop(user_id, None)
    last_activation_data.pop(user_id, None)
    db_exec("UPDATE users SET current_number = NULL, current_country = NULL, current_service = NULL, number_expiry = NULL WHERE user_id = ?", (user_id,))
    await delete_previous_messages(update, context)
    await ensure_persistent_welcome(context, user_id)

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
    username = None
    if hasattr(update, 'effective_user') and update.effective_user:
        username = update.effective_user.username
    ensure_user(user_id, username, first_name)
    await send_main_menu(update, context, user_id)

async def show_get_number(update: Update, context, user_id, first_name):
    ensure_user(user_id, update.effective_user.username, first_name)
    db_exec("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_PREFIX"], "🔧")} <b>Select service</b> '
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_SUFFIX"], "📱")}'
    )
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, text, reply_markup=services_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    else:
        await send_clean_message(update, context, text, reply_markup=services_keyboard(), parse_mode='HTML', auto_delete=False)

async def show_balance(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE = None):
    ensure_user(user_id, update.effective_user.username, update.effective_user.first_name)
    user = db_fetch_one("SELECT first_name, balance, withdrawn, total_otp FROM users WHERE user_id = ?", (user_id,))
    if not user:
        return
    first_name, balance, withdrawn, total_otp = user
    balance = balance or 0.0
    withdrawn = withdrawn or 0.0
    total_otp = total_otp or 0

    emoji_clipboard = "4958506272551863292"
    emoji_id = "5197269100878907942"
    emoji_money = "4958926882994127612"
    emoji_withdraw = "5445221832074483553"
    emoji_warning = "4958534696645428119"
    emoji_inbox = "5197288647275071607"

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
        InlineKeyboardButton("WITHDRAW", callback_data="withdraw", style=KBS.SUCCESS,
                             icon_custom_emoji_id=safe_icon("5445353829304387411"))
    ]])
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)
    else:
        if context:
            await send_clean_message(update, context, text, reply_markup=kb, parse_mode='HTML', auto_delete=False)

async def show_withdraw(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE = None):
    ensure_user(user_id, update.effective_user.username, update.effective_user.first_name)
    balance = db_fetch_one("SELECT balance FROM users WHERE user_id=?", (user_id,))
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
        await edit_or_send(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)
    else:
        if context:
            await send_clean_message(update, context, text, reply_markup=kb, parse_mode='HTML', auto_delete=False)

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    text = "CONTACT SUPPORT\n\n━━━━━━━━━━━━━━━━━━━━\nFor any issues, contact admin directly.\n\nDeveloper: 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓"
    if isinstance(update, CallbackQuery):
        user_id = update.effective_user.id
        await edit_or_send(update, text, reply_markup=support_keyboard(), context=context, auto_delete=False)
    else:
        if context:
            await send_clean_message(update, context, text, reply_markup=None, auto_delete=False)

# ==================== ADMIN COMMANDS ====================
async def enter_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_admin(user_id):
        admin_mode[user_id] = True
        admin_panel_state[user_id] = "main"
        await send_clean_message(update, context, "ADMIN PANEL\n\nDeveloper: 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓\n\nSelect an action below:", reply_markup=admin_panel_keyboard(), auto_delete=False)
    else:
        await update.message.reply_text("Unauthorized access!")

async def exit_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in admin_mode:
        admin_mode.pop(user_id, None)
        admin_panel_state.pop(user_id, None)
        await update.message.reply_text("Admin mode deactivated!")
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
    text = "ADMIN PANEL\n\nDeveloper: 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓\n\nSelect an action below:"
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
            await update.message.reply_text(msg, parse_mode='HTML')
            
            broadcast_msg, broadcast_kb = stock_added_broadcast_with_button(country, service, count)
            users = db_fetch_all("SELECT user_id FROM users")
            for u in users:
                try:
                    await context.bot.send_message(
                        u[0],
                        broadcast_msg,
                        reply_markup=broadcast_kb,
                        parse_mode='HTML'
                    )
                    await asyncio.sleep(0.05)
                except Exception:
                    continue
            
            await send_stock_management_menu(update, context, user_id)
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
        await edit_or_send(query, msg, parse_mode='HTML', context=context, auto_delete=False)
        
        broadcast_msg, broadcast_kb = stock_added_broadcast_with_button(country, service, count)
        users = db_fetch_all("SELECT user_id FROM users")
        for u in users:
            try:
                await context.bot.send_message(u[0], broadcast_msg, reply_markup=broadcast_kb, parse_mode='HTML')
                await asyncio.sleep(0.05)
            except Exception:
                pass
        
        await send_stock_management_menu(query, context, user_id)
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
        await update.message.reply_text(msg, parse_mode='HTML')
        
        broadcast_msg, broadcast_kb = stock_added_broadcast_with_button(country, service, count)
        users = db_fetch_all("SELECT user_id FROM users")
        for u in users:
            try:
                await context.bot.send_message(u[0], broadcast_msg, reply_markup=broadcast_kb, parse_mode='HTML')
                await asyncio.sleep(0.05)
            except Exception:
                continue
        
        await send_stock_management_menu(update, context, user_id)
        admin_panel_state[user_id] = "main"
        admin_temp_data.pop(user_id, None)
        return True

    return False

# ==================== STOCK GET NUMBER CALLBACK ====================
async def stock_get_number_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if await ban_check(update, context):
        return
    
    await query.answer("Getting numbers...")
    
    parts = query.data.split('|')
    if len(parts) < 3:
        await query.answer("Invalid request.", show_alert=True)
        return
    country = parts[1]
    service = parts[2]
    
    numbers = get_numbers_from_stock(country, service, 3)
    if not numbers:
        await query.answer("No numbers available right now!", show_alert=True)
        return
    
    old_data = last_activation_data.get(user_id)
    if old_data:
        old_msg_id = old_data[3]
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=old_msg_id)
        except:
            pass
    
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

# ==================== /testgroup COMMAND (FIXED - SENDS TO ALL GROUPS WITH sendRichMessage) ====================
async def testgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Unauthorized. Admin only.")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: /testgroup <service> <iso2>\n"
            "Example: /testgroup WhatsApp BD"
        )
        return
    
    service = args[0]
    iso2 = args[1].upper()
    
    country_name = get_country_name_by_iso(iso2)
    if not country_name:
        await update.message.reply_text(f"❌ Country with ISO2 '{iso2}' not found.")
        return
    
    country_info = get_country_info(country_name)
    country_code = country_info.get("code", "")
    if not country_code:
        for code, (iso, flag, name) in COUNTRY_CODE_MAP.items():
            if iso.upper() == iso2:
                country_code = "+" + code
                break
    if not country_code:
        country_code = "+880"
    
    local_part = ''.join(random.choices('0123456789', k=10))
    test_number = country_code + local_part
    test_otp = ''.join(random.choices('0123456789', k=6))
    test_message = "Your verification code is: " + test_otp
    
    entry = {
        "number": test_number,
        "otp": test_otp,
        "service": service,
        "country_code": iso2,
        "country": country_name,
        "message": test_message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Generate rich message – this uses <p>, <details>, <summary> as in original
    grp_html, grp_kb_dict = format_group_otp_rich(entry)
    
    # Send to ALL groups using sendRichMessage (custom endpoint)
    success_count = 0
    failed_groups = []
    for gid in GROUP_IDS:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendRichMessage"
            payload = {
                "chat_id": gid,
                "rich_message": {"html": grp_html},
                "reply_markup": grp_kb_dict   # send the dictionary, not InlineKeyboardMarkup
            }
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                success_count += 1
            else:
                failed_groups.append(f"{gid} (HTTP {resp.status_code})")
        except Exception as e:
            failed_groups.append(f"{gid} ({str(e)})")
    
    # Build response message
    if success_count == 0:
        reply = f"❌ Test OTP sent to 0 group(s).\n"
        if failed_groups:
            reply += "Failed groups:\n" + "\n".join(f"• {g}" for g in failed_groups)
        else:
            reply += "No groups found in GROUP_IDS. Please check the configuration."
    else:
        reply = f"✅ Test OTP sent to {success_count} group(s) for {service} - {country_name} ({iso2}).\n"
        reply += f"📱 Number: {test_number}\n🔑 OTP: {test_otp}\n"
        if failed_groups:
            reply += "\n⚠️ Failed groups:\n" + "\n".join(f"• {g}" for g in failed_groups)
    
    await update.message.reply_text(reply)

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
    await send_main_menu(query, context, user_id)

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
        await edit_or_send(query, "No active numbers to display.", reply_markup=back_to_main_keyboard(), context=context, auto_delete=False)
        return
    country, service, numbers, msg_id = data
    msg, kb = format_numbers_message(country, service, numbers, user_id=user_id)
    await edit_or_send(query, msg, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

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
    await edit_or_send(query, text, reply_markup=countries_for_service_keyboard(service), parse_mode='HTML', context=context, auto_delete=False)

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

    await edit_or_send(query, f'{emoji_tag("5976826804931928647", "⏳")}', parse_mode='HTML', context=context, auto_delete=False)
    await asyncio.sleep(1)

    numbers = get_numbers_from_stock(country, service, 3)
    if not numbers:
        await query.answer("No numbers available for this country/service!", show_alert=True)
        await edit_or_send(query, "Select a Country:", reply_markup=countries_for_service_keyboard(service), context=context, auto_delete=False)
        return

    old_data = last_activation_data.get(user_id)
    if old_data:
        old_msg_id = old_data[3]
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=old_msg_id)
        except:
            pass

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
    await edit_or_send(query, text, reply_markup=services_keyboard(), parse_mode='HTML', context=context, auto_delete=False)

async def next_number_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context): return
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    await query.answer("Getting next 3 numbers...")
    
    await edit_or_send(query, f'{emoji_tag("5976826804931928647", "⏳")}', parse_mode='HTML', context=context, auto_delete=False)
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
        await edit_or_send(query, "Select a Service:", reply_markup=services_keyboard(), context=context, auto_delete=False)
        return
    numbers = get_numbers_from_stock(country, service, 3)
    if not numbers:
        await query.answer(f"No more {country} {service} numbers!", show_alert=True)
        await edit_or_send(query, f"Select a Country for {service}:", reply_markup=countries_for_service_keyboard(service), context=context, auto_delete=False)
        return

    old_data = last_activation_data.get(user_id)
    if old_data:
        old_msg_id = old_data[3]
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=old_msg_id)
        except:
            pass

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
        await edit_or_send(query, "ADMIN PANEL\n\nDeveloper: 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓\n\nSelect an action below:",
                           reply_markup=admin_panel_keyboard(), context=context, auto_delete=False)
    elif action == "stock_management":
        await stock_management_menu(query, context, user_id)

# ==================== STOCK MANAGEMENT FUNCTIONS ====================
async def send_stock_management_menu(target, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["STOCK_MANAGER"], "📦")} <b>STOCK MANAGEMENT</b>\n\n'
        f'Select an action below:'
    )
    kb = stock_management_menu_keyboard()
    if isinstance(target, CallbackQuery):
        await edit_or_send(target, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)
    else:
        await send_clean_message(target, context, text, reply_markup=kb, parse_mode='HTML', auto_delete=False)

async def stock_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    await send_stock_management_menu(update, context, user_id)

async def stock_upload_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    admin_panel_state[user_id] = "waiting_file"
    await edit_or_send(query, "UPLOAD STOCK\n\nSend a .txt file with phone numbers.\nFilename must contain country & service name.\nOne number per line.",
                       reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

async def stock_remove_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only.")
        return
    await query.answer()
    rows = db_fetch_all("SELECT name, service, stock FROM countries WHERE stock > 0 ORDER BY name, service")
    if not rows:
        await edit_or_send(query, "No stock available to remove.", reply_markup=stock_management_menu_keyboard(), context=context, auto_delete=False)
        return
    kb_buttons = []
    for country, service, stock in rows:
        country_eid = get_country_info(country).get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
        label = f"{country} — {service} (Stock: {stock})"
        cb_data = f"stock_remove_confirm|{country}|{service}"
        kb_buttons.append([InlineKeyboardButton(
            label,
            callback_data=cb_data,
            style=KBS.DANGER,
            icon_custom_emoji_id=safe_icon(country_eid)
        )])
    kb_buttons.append([InlineKeyboardButton("Back", callback_data="admin_stock_management", style=KBS.PRIMARY,
                                            icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await edit_or_send(query, "Select stock to remove:", reply_markup=InlineKeyboardMarkup(kb_buttons), parse_mode='HTML', context=context, auto_delete=False)

async def stock_remove_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only.")
        return
    await query.answer()
    _, country, service = query.data.split('|')
    text = (
        f'Do you want to remove all numbers for {country_flag_emoji(country)} <b>{country}</b> '
        f'with service {service_emoji_tag(service)}?'
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("YES", callback_data=f"stock_remove_yes|{country}|{service}", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("YES", "")))],
        [InlineKeyboardButton("NO", callback_data="stock_remove_no", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("NO", "")))],
    ])
    await edit_or_send(query, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

async def stock_remove_yes_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only.")
        return
    _, country, service = query.data.split('|')
    if delete_country_stock(country, service):
        await query.answer(f"✅ Stock for {country} — {service} removed.", show_alert=True)
    else:
        await query.answer(f"❌ Failed to remove stock.", show_alert=True)
    await stock_remove_callback(update, context)

async def stock_remove_no_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("Cancelled.")
    await send_stock_management_menu(query, context, user_id)

async def stock_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only.")
        return
    await query.answer()
    rows = db_fetch_all("SELECT name, service, stock FROM countries WHERE stock > 0 ORDER BY name, service")
    if not rows:
        text = "No stock available."
    else:
        lines = []
        for country, service, stock in rows:
            payout = get_country_info(country).get("payout", "0.001$")
            line = (
                f'<blockquote>'
                f'{service_emoji_tag(service)}|'
                f'{country_flag_emoji(country)}<b>{country}</b>|'
                f'<code>{payout}</code>|'
                f'{stock}'
                f'</blockquote>'
            )
            lines.append(line)
        text = "\n".join(lines)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("Back", callback_data="admin_stock_management", style=KBS.PRIMARY,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))
    ]])
    await edit_or_send(query, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

async def stock_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only.")
        return
    await query.answer()
    rows = db_fetch_all("SELECT name, service, active FROM countries ORDER BY name, service")
    if not rows:
        await edit_or_send(query, "No countries/services defined.", reply_markup=stock_management_menu_keyboard(), context=context, auto_delete=False)
        return
    kb_buttons = []
    for country, service, active in rows:
        country_eid = get_country_info(country).get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
        label = f"{country} — {service}"
        cb_data = f"stock_toggle_do|{country}|{service}"
        style = KBS.SUCCESS if active else KBS.DANGER
        kb_buttons.append([InlineKeyboardButton(
            label,
            callback_data=cb_data,
            style=style,
            icon_custom_emoji_id=safe_icon(country_eid)
        )])
    kb_buttons.append([InlineKeyboardButton("Back", callback_data="admin_stock_management", style=KBS.PRIMARY,
                                            icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await edit_or_send(query, "Select stock to toggle active status:", reply_markup=InlineKeyboardMarkup(kb_buttons), parse_mode='HTML', context=context, auto_delete=False)

async def stock_toggle_do_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only.")
        return
    _, country, service = query.data.split('|')
    row = db_fetch_one("SELECT active FROM countries WHERE name = ? AND service = ?", (country, service))
    if not row:
        await query.answer("Entry not found.", show_alert=True)
        return
    new_active = 0 if row[0] else 1
    db_exec("UPDATE countries SET active = ? WHERE name = ? AND service = ?", (new_active, country, service))
    await query.answer(f"Toggled {country} — {service} to {'Active' if new_active else 'Inactive'}.")
    await stock_toggle_callback(update, context)

# ==================== ADMIN STATS ====================
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
        await send_main_menu(query, None, user_id)
    except Exception:
        await bot.send_message(user_id, "Main Menu")

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

# ==================== /setcountry & /setservice COMMANDS ====================
async def set_country_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /setcountry ISO|EMOJI_ID\nExample: /setcountry BD|5911365056594973179")
        return
    parts = " ".join(context.args).split("|")
    if len(parts) != 2:
        await update.message.reply_text("Invalid format. Use ISO|EMOJI_ID")
        return
    iso = parts[0].strip().upper()
    eid = parts[1].strip()
    db_exec("INSERT OR REPLACE INTO group_emojis (type, key, emoji_id) VALUES ('country', ?, ?)", (iso, eid))
    DEFAULT_EMOJIS["countries"][iso.lower()] = eid
    await update.message.reply_text(f"✅ Country emoji for {iso} set to <code>{eid}</code>", parse_mode="HTML")

async def set_service_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /setservice NAME|EMOJI_ID\nExample: /setservice PayPal|123456789")
        return
    parts = " ".join(context.args).split("|")
    if len(parts) != 2:
        await update.message.reply_text("Invalid format. Use NAME|EMOJI_ID")
        return
    name = parts[0].strip().lower()
    eid = parts[1].strip()
    db_exec("INSERT OR REPLACE INTO group_emojis (type, key, emoji_id) VALUES ('service', ?, ?)", (name, eid))
    DEFAULT_EMOJIS["services"][name.lower()] = eid
    await update.message.reply_text(f"✅ Service emoji for {name} set to <code>{eid}</code>", parse_mode="HTML")

# ==================== /country & /service COMMANDS (legacy) ====================
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
    await send_clean_message(update, context, text, reply_markup=services_keyboard(), parse_mode='HTML', auto_delete=False)

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

    emoji_clipboard = "4958506272551863292"
    emoji_id = "5197269100878907942"
    emoji_money = "4958926882994127612"
    emoji_withdraw = "5445221832074483553"
    emoji_warning = "4958534696645428119"
    emoji_inbox = "5197288647275071607"

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
        InlineKeyboardButton("WITHDRAW", callback_data="withdraw", style=KBS.SUCCESS,
                             icon_custom_emoji_id=safe_icon("5445353829304387411"))
    ]])
    await send_clean_message(update, context, text, reply_markup=kb, parse_mode='HTML', auto_delete=False)

async def send_support_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = "CONTACT SUPPORT\n\n━━━━━━━━━━━━━━━━━━━━\nFor any issues, contact admin directly.\n\nDeveloper: 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓"
    sent_inline = await context.bot.send_message(chat_id=user_id, text=text, reply_markup=support_keyboard())
    db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?", (sent_inline.message_id, user_id))

async def send_admin_panel_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Unauthorized!")
        return
    admin_mode[user_id] = True
    admin_panel_state[user_id] = "main"
    await send_clean_message(
        update, context,
        "ADMIN PANEL\n\nDeveloper: 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓",
        reply_markup=admin_panel_keyboard(),
        auto_delete=False
    )

# ==================== CURL PARSER - UNLIMITED FORMAT SUPPORT ====================

import re
import json
from urllib.parse import urlparse, parse_qs

def parse_curl_complete(curl_string: str) -> dict:
    """
    Unlimited CURL parser - supports any format, any placeholders, backslashes, multiline, quotes, etc.
    """
    result = {
        "method": "GET",
        "url": "",
        "headers": {},
        "data": None,
        "raw_curl": curl_string,
        "placeholders": {},
        "base_url": "",
        "endpoint": "/",
        "original_url": ""
    }
    
    # Clean up: remove backslashes, newlines, extra spaces
    curl_string = curl_string.replace('\\', ' ').replace('\n', ' ').replace('\r', ' ')
    curl_string = re.sub(r'\s+', ' ', curl_string).strip()
    
    if curl_string.startswith("curl"):
        curl_string = curl_string[4:].strip()
    
    # ===== 1. URL Extraction (supports quoted, unquoted, placeholders) =====
    # Try quoted URL first
    url_match = re.search(r'["\']((?:https?://)?[^\s"\']+)["\']', curl_string)
    if url_match:
        result["url"] = url_match.group(1)
        result["original_url"] = result["url"]
        curl_string = curl_string.replace(url_match.group(0), "").strip()
    else:
        # Unquoted URL (including placeholders like {API_BASE})
        url_match = re.search(r'((?:https?://)?[^\s"\']+)', curl_string)
        if url_match:
            result["url"] = url_match.group(1)
            result["original_url"] = result["url"]
            curl_string = curl_string.replace(url_match.group(0), "").strip()
    
    # If still no URL, try to find a URL with placeholders like {API_BASE}/path
    if not result["url"]:
        placeholder_url_match = re.search(r'\{[A-Za-z_]+\}/[^\s"]+', curl_string)
        if placeholder_url_match:
            result["url"] = placeholder_url_match.group(0)
            result["original_url"] = result["url"]
            curl_string = curl_string.replace(placeholder_url_match.group(0), "").strip()
    
    # ===== 2. Method Extraction =====
    method_pattern = r'-[Xx]\s+["\']?([A-Z]+)["\']?'
    method_match = re.search(method_pattern, curl_string)
    if method_match:
        result["method"] = method_match.group(1).upper()
        curl_string = re.sub(method_pattern, "", curl_string).strip()
    
    # ===== 3. Headers Extraction =====
    header_pattern = r'-H\s+["\']([^"\']+)["\']'
    header_matches = re.findall(header_pattern, curl_string)
    for header in header_matches:
        if ": " in header:
            key, value = header.split(": ", 1)
            result["headers"][key.strip()] = value.strip()
    curl_string = re.sub(header_pattern, "", curl_string).strip()
    
    # Also handle --header
    header_long_pattern = r'--header\s+["\']([^"\']+)["\']'
    header_long_matches = re.findall(header_long_pattern, curl_string)
    for header in header_long_matches:
        if ": " in header:
            key, value = header.split(": ", 1)
            result["headers"][key.strip()] = value.strip()
    curl_string = re.sub(header_long_pattern, "", curl_string).strip()
    
    # ===== 4. Data Extraction =====
    data_pattern = r'-d\s+["\']([^"\']+)["\']'
    data_match = re.search(data_pattern, curl_string)
    if data_match:
        data_str = data_match.group(1)
        try:
            result["data"] = json.loads(data_str)
        except:
            result["data"] = data_str
        curl_string = re.sub(data_pattern, "", curl_string).strip()
    
    data_raw_pattern = r'--data-raw\s+["\']([^"\']+)["\']'
    data_raw_match = re.search(data_raw_pattern, curl_string)
    if data_raw_match:
        data_str = data_raw_match.group(1)
        try:
            result["data"] = json.loads(data_str)
        except:
            result["data"] = data_str
        curl_string = re.sub(data_raw_pattern, "", curl_string).strip()
    
    data_binary_pattern = r'--data-binary\s+["\']([^"\']+)["\']'
    data_binary_match = re.search(data_binary_pattern, curl_string)
    if data_binary_match:
        data_str = data_binary_match.group(1)
        try:
            result["data"] = json.loads(data_str)
        except:
            result["data"] = data_str
        curl_string = re.sub(data_binary_pattern, "", curl_string).strip()
    
    # ===== 5. Find ALL placeholders {something} =====
    placeholder_pattern = r'\{([^{}]+)\}'
    
    # URL placeholders
    if result["url"]:
        placeholders = re.findall(placeholder_pattern, result["url"])
        for ph in placeholders:
            result["placeholders"][ph] = ""
    
    # Headers placeholders
    for key, value in result["headers"].items():
        placeholders = re.findall(placeholder_pattern, value)
        for ph in placeholders:
            result["placeholders"][ph] = ""
    
    # Data placeholders
    if result["data"] and isinstance(result["data"], str):
        placeholders = re.findall(placeholder_pattern, result["data"])
        for ph in placeholders:
            result["placeholders"][ph] = ""
    elif result["data"] and isinstance(result["data"], (dict, list)):
        data_str = json.dumps(result["data"])
        placeholders = re.findall(placeholder_pattern, data_str)
        for ph in placeholders:
            result["placeholders"][ph] = ""
    
    # ===== 6. Extract base URL and endpoint =====
    if result["url"]:
        if result["url"].startswith(("http://", "https://")):
            parsed = urlparse(result["url"])
            result["base_url"] = f"{parsed.scheme}://{parsed.netloc}"
            result["endpoint"] = parsed.path or "/"
            if parsed.query:
                result["endpoint"] += "?" + parsed.query
        else:
            # URL with placeholder like {API_BASE}/path
            parts = result["url"].split('/', 1)
            if len(parts) > 1:
                result["base_url"] = parts[0]
                result["endpoint"] = "/" + parts[1]
            else:
                result["base_url"] = parts[0]
                result["endpoint"] = "/"
    
    return result

def replace_all_placeholders(text: str, placeholders: dict) -> str:
    """Replace all {placeholder} with values."""
    if not text:
        return text
    for key, value in placeholders.items():
        text = text.replace(f"{{{key}}}", str(value))
    return text

def build_request_from_curl(parsed: dict, placeholders: dict = None) -> dict:
    """Build request from parsed CURL."""
    if not placeholders:
        placeholders = parsed.get("placeholders", {})
    
    url = parsed.get("original_url", parsed.get("url", ""))
    url = replace_all_placeholders(url, placeholders)
    
    headers = {}
    for key, value in parsed.get("headers", {}).items():
        headers[key] = replace_all_placeholders(value, placeholders)
    
    data = parsed.get("data")
    if data and isinstance(data, (dict, list)):
        data_str = json.dumps(data)
        data_str = replace_all_placeholders(data_str, placeholders)
        try:
            data = json.loads(data_str)
        except:
            data = data_str
    elif data and isinstance(data, str):
        data = replace_all_placeholders(data, placeholders)
    
    return {
        "method": parsed.get("method", "GET"),
        "url": url,
        "headers": headers,
        "data": data,
        "base_url": parsed.get("base_url", ""),
        "endpoint": parsed.get("endpoint", ""),
        "placeholders": placeholders
    }

# ==================== API ADD STEPS ====================
# Updated steps: added OTP List Path as step 6, shifted others.

STEP_ORDER = [
    "api_add_name",          # 1
    "api_add_base_url",      # 2
    "api_add_endpoint",      # 3
    "api_add_token",         # 4
    "api_add_interval",      # 5
    "api_add_otp_list_path", # 6
    "api_add_number_path",   # 7
    "api_add_message_path",  # 8
    "api_add_timestamp_path",# 9
    "api_add_service_path",  # 10
    "api_add_curl",          # 11
    "api_add_confirm"        # 12
]

STEP_EXAMPLES = {
    "panel_name": "e.g., MyProvider",
    "base_url": "e.g., https://zebrasms.com/api/v1",
    "endpoint": "e.g., /publicapi/getupdate",
    "token": "e.g., SUEKjeiWiw",
    "interval_sec": "e.g., 30 (minimum 1 second)",
    "otp_list_path": "e.g., data.rows (path to list of OTPs)",
    "number_path": "e.g., number or phone",
    "message_path": "e.g., message or sms",
    "timestamp_path": "e.g., timestamp or time",
    "service_path": "e.g., service or cli",
    "curl_command": """
curl {API_BASE}/publicapi/getupdate -H "MAuth: {TOKEN}"
or
curl "http://147.135.212.197/crapi/had/viewstats?token={TOKEN}&records={RECORDS}"
    """
}

STEP_MESSAGES = {
    "api_add_name": ("Panel Name", "panel_name", "api_add_base_url"),
    "api_add_base_url": ("Base URL", "base_url", "api_add_endpoint"),
    "api_add_endpoint": ("Endpoint", "endpoint", "api_add_token"),
    "api_add_token": ("Token", "token", "api_add_interval"),
    "api_add_interval": ("Interval (seconds, >=1)", "interval_sec", "api_add_otp_list_path"),
    "api_add_otp_list_path": ("OTP List Path", "otp_list_path", "api_add_number_path"),
    "api_add_number_path": ("Number Field Path", "number_path", "api_add_message_path"),
    "api_add_message_path": ("Message Field Path", "message_path", "api_add_timestamp_path"),
    "api_add_timestamp_path": ("Timestamp Field Path", "timestamp_path", "api_add_service_path"),
    "api_add_service_path": ("Service Field Path", "service_path", "api_add_curl"),
    "api_add_curl": ("CURL Example (Optional)", "curl_command", "api_add_confirm"),
    "api_add_confirm": ("", "", "api_add_finish"),
}

# Which steps can be skipped
SKIPPABLE_STEPS = [
    "api_add_name",
    "api_add_endpoint",
    "api_add_token",
    "api_add_interval",
    "api_add_otp_list_path",
    "api_add_number_path",
    "api_add_message_path",
    "api_add_timestamp_path",
    "api_add_service_path",
    "api_add_curl",
]

NON_SKIPPABLE_STEPS = [
    "api_add_base_url",
    "api_add_confirm",
]

# ==================== KEYBOARD BUILDERS FOR API ADD ====================

def get_step_keyboard(step: str) -> InlineKeyboardMarkup:
    """Build keyboard for step - only premium emojis."""
    buttons = []
    if step in SKIPPABLE_STEPS:
        buttons.append(InlineKeyboardButton(
            "SKIP",
            callback_data="api_add_skip",
            style=KBS.PRIMARY,
            icon_custom_emoji_id=safe_icon(SKIP_EMOJI)
        ))
    buttons.append(InlineKeyboardButton(
        "CANCEL",
        callback_data="api_add_cancel",
        style=KBS.DANGER,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CANCEL", ""))
    ))
    return InlineKeyboardMarkup([buttons])

# ==================== API ADD STEP DISPLAY ====================

async def api_add_step(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, step: str):
    """Show any API ADD step."""
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    
    admin_panel_state[user_id] = step
    
    step_num = STEP_ORDER.index(step) + 1
    total_steps = len(STEP_ORDER)
    
    label, field, next_step = STEP_MESSAGES.get(step, ("", "", ""))
    
    if step == "api_add_confirm":
        await show_confirm_step(update, context, user_id)
        return
    
    data = admin_temp_data.get(user_id, {})
    current_value = data.get(field, "")
    
    # Example with proper formatting
    example_text = ""
    if field in STEP_EXAMPLES:
        example_text = f"\n\n<blockquote>{emoji_tag('5303449763406954093', '💡')} <b>EXAMPLE</b>:\n<code>{STEP_EXAMPLES[field]}</code></blockquote>"
    
    if step in NON_SKIPPABLE_STEPS:
        required_text = f"{emoji_tag('4958534696645428119', '⚠️')} <b>Required</b>"
    else:
        required_text = f"{emoji_tag('4956721670690702265', '✅')} <b>Optional</b> (Can SKIP)"
    
    text = f"""{emoji_tag(CUSTOM_EMOJIS['ADD_API_KEY'], '➕')} <b>ADD API – Step {step_num}/{total_steps}</b>

<b>{label}</b>
{required_text}

Current value: <code>{current_value or 'Not set'}</code>
{example_text}

Send the value or press SKIP:"""
    
    await reply_or_edit(
        update,
        text,
        reply_markup=get_step_keyboard(step),
        parse_mode='HTML',
        context=context,
        auto_delete=False
    )

# ==================== SHOW CONFIRM STEP (FIXED) ====================

import html
import re

def sanitize_text(text: str) -> str:
    """Remove non-printable characters and trim."""
    if not text:
        return ""
    # Remove control characters except newline and tab
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text

async def show_confirm_step(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Show confirmation step - HTML-safe, with fallback to plain text."""
    data = admin_temp_data.get(user_id, {})
    
    # Premium emoji mapping for fields (using unicode fallback)
    field_emojis = {
        "Panel Name": CUSTOM_EMOJIS.get("API_FIELD_NAME", "5818775306974006843"),
        "Base URL": CUSTOM_EMOJIS.get("API_FIELD_URL", "6285048454255220485"),
        "Endpoint": CUSTOM_EMOJIS.get("API_FIELD_ENDPOINT", "6267172559851099903"),
        "Token": CUSTOM_EMOJIS.get("API_FIELD_TOKEN", "5821453562680448557"),
        "Interval": CUSTOM_EMOJIS.get("API_FIELD_INTERVAL", "6093456762113888541"),
        "OTP List Path": CUSTOM_EMOJIS.get("API_FIELD_OTP_PATH", "5818955300463447293"),
        "Number Path": CUSTOM_EMOJIS.get("API_FIELD_NUMBER", "5877410604225924969"),
        "Message Path": CUSTOM_EMOJIS.get("API_FIELD_MESSAGE", "5980911993140284450"),
        "Timestamp Path": CUSTOM_EMOJIS.get("API_FIELD_TIMESTAMP", "6285240160120477644"),
        "Service Path": CUSTOM_EMOJIS.get("API_FIELD_SERVICE", "5818967150278218011"),
    }
    curl_icon = CUSTOM_EMOJIS.get("API_TEST", "5978568938156461643")
    
    # Build HTML part (safe)
    confirm_text = f"{emoji_tag(CUSTOM_EMOJIS['ADD_API_KEY'], '➕')} <b>Confirm API Details</b>\n\n"
    
    fields = [
        ("Panel Name", data.get("panel_name")),
        ("Base URL", data.get("base_url")),
        ("Endpoint", data.get("endpoint")),
        ("Token", data.get("token")),
        ("Interval", data.get("interval_sec")),
        ("OTP List Path", data.get("otp_list_path")),
        ("Number Path", data.get("number_path")),
        ("Message Path", data.get("message_path")),
        ("Timestamp Path", data.get("timestamp_path")),
        ("Service Path", data.get("service_path")),
    ]
    
    for label, value in fields:
        emoji_id = field_emojis.get(label, CUSTOM_EMOJIS.get("DEFAULT_SERVICE", "5465590345108589516"))
        if value is None:
            confirm_text += f"{emoji_tag(emoji_id, '•')} {label}: <i>Skipped (Not Used)</i>\n"
        elif value == "":
            confirm_text += f"{emoji_tag(emoji_id, '•')} {label}: <i>Not set</i>\n"
        else:
            # Sanitize and escape
            safe_val = sanitize_text(str(value))
            safe_val = html.escape(safe_val)
            if len(safe_val) > 30:
                safe_val = safe_val[:30] + "..."
            confirm_text += f"{emoji_tag(emoji_id, '•')} {label}: <code>{safe_val}</code>\n"
    
    if data.get("curl_command"):
        raw_curl = sanitize_text(data["curl_command"][:200])
        curl_cmd = html.escape(raw_curl)
        if len(data["curl_command"]) > 200:
            curl_cmd += "..."
        confirm_text += f"\n{emoji_tag(curl_icon, '📌')} <b>CURL Command</b>:\n<code>{curl_cmd}</code>\n"
        parsed = data.get("parsed_curl")
        if parsed and parsed.get("placeholders"):
            ph_list = [sanitize_text(ph) for ph in parsed["placeholders"].keys()]
            ph_str = ", ".join([f"<code>{{{html.escape(ph)}}}</code>" for ph in ph_list])
            confirm_text += f"{emoji_tag(CUSTOM_EMOJIS['API_FIELD_TOKEN'], '🔑')} <b>Placeholders</b>: {ph_str}\n"
    else:
        confirm_text += f"\n{emoji_tag(curl_icon, '📌')} <b>CURL</b>: <i>Skipped (Not Used)</i>\n"
    
    confirm_text += f"\n<blockquote>{emoji_tag('5303449763406954093', '💡')} <b>Is all correct?</b></blockquote>"
    
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "YES ADD",
                callback_data=f"api_add_confirm_yes|{user_id}",
                style=KBS.SUCCESS,
                icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("YES", "4956721670690702265"))
            ),
            InlineKeyboardButton(
                "CANCEL",
                callback_data=f"api_add_confirm_no|{user_id}",
                style=KBS.DANGER,
                icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("NO", "6206110936789423908"))
            )
        ],
        [
            InlineKeyboardButton(
                "EDIT VALUE",
                callback_data=f"api_add_edit|{user_id}",
                style=KBS.PRIMARY,
                icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("EDIT_BALANCE", "6204162490515855272"))
            )
        ]
    ])
    
    admin_panel_state[user_id] = "api_add_confirm"
    
    # Try to send HTML, fallback to plain text
    async def send_confirm(chat_id, message_id=None):
        try:
            if message_id:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=confirm_text,
                    reply_markup=kb,
                    parse_mode='HTML'
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=confirm_text,
                    reply_markup=kb,
                    parse_mode='HTML'
                )
        except BadRequest as e:
            if "Message is not modified" in str(e):
                return
            # Fallback to plain text (remove all HTML tags)
            plain_text = re.sub(r'<[^>]+>', '', confirm_text)
            plain_text = plain_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            try:
                if message_id:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=plain_text,
                        reply_markup=kb
                    )
                else:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=plain_text,
                        reply_markup=kb
                    )
            except Exception as fallback_err:
                print(f"Fallback also failed: {fallback_err}")

    chat_id = update.message.chat.id if hasattr(update, 'message') else update.message.chat.id
    message_id = update.message.message_id if hasattr(update, 'message') else None
    
    await send_confirm(chat_id, message_id)

# ==================== HANDLE API ADD SKIP ====================

async def handle_api_add_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SKIP button handler - means this step is not needed; field set to None."""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("⏭ Step skipped! This field will not be used.")
    
    current_step = admin_panel_state.get(user_id)
    if not current_step or not current_step.startswith("api_add_"):
        await query.edit_message_text("❌ No active API addition session.", reply_markup=admin_panel_keyboard())
        return
    
    data = admin_temp_data.get(user_id, {})
    label, field, next_step = STEP_MESSAGES.get(current_step, ("", "", ""))
    
    # SKIP = field set to None (meaning "not used")
    if field:
        data[field] = None
    
    admin_temp_data[user_id] = data
    
    if next_step:
        await api_add_step(update, context, user_id, next_step)
    else:
        await show_confirm_step(query, context, user_id)

# ==================== HANDLE API ADD CANCEL ====================

async def handle_api_add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("❌ Cancelled!")
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await query.edit_message_text("❌ API addition cancelled.", reply_markup=admin_panel_keyboard())

# ==================== API ADD START ====================

async def api_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    admin_temp_data[user_id] = {}
    admin_panel_state[user_id] = "api_add_name"
    await api_add_step(update, context, user_id, "api_add_name")

# ==================== CURL CONFIRMATION BUTTONS ====================

async def api_add_curl_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle CONTINUE button after CURL parsing."""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("Proceeding to confirmation...")
    # Proceed to confirm step
    await show_confirm_step(query, context, user_id)

async def api_add_curl_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle CANCEL button after CURL parsing."""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("Cancelled.")
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await query.edit_message_text("❌ API addition cancelled.", reply_markup=admin_panel_keyboard())

# ==================== HANDLE API ADD TEXT INPUT ====================

async def handle_api_add_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = admin_panel_state.get(user_id)
    
    if not state or not state.startswith("api_add_"):
        return False
    
    text = update.message.text.strip()
    
    if text == "/cancel":
        admin_temp_data.pop(user_id, None)
        admin_panel_state[user_id] = "main"
        await update.message.reply_text("❌ API addition cancelled.", reply_markup=admin_panel_keyboard())
        return True
    
    data = admin_temp_data.get(user_id, {})
    label, field, next_step = STEP_MESSAGES.get(state, ("", "", ""))
    
    # CURL special handling
    if state == "api_add_curl":
        if text == "/skip":
            data["curl_command"] = None
            data["parsed_curl"] = None
            admin_temp_data[user_id] = data
            await show_confirm_step(update, context, user_id)
            return True
        
        try:
            parsed = parse_curl_complete(text)
            if not parsed.get("url"):
                await update.message.reply_text(
                    "❌ <b>Invalid CURL Command</b>\n\n"
                    "Could not extract URL. Please check your CURL command.\n\n"
                    "Make sure your CURL has a URL like:\n"
                    "<code>curl https://example.com/api/endpoint</code>\n"
                    "or\n"
                    "<code>curl {API_BASE}/api/endpoint</code>\n\n"
                    "Or send <code>/skip</code> to skip this step.",
                    parse_mode='HTML'
                )
                return True
            
            data["curl_command"] = text
            data["parsed_curl"] = parsed
            admin_temp_data[user_id] = data
            
            placeholders = parsed.get("placeholders", {})
            ph_list = [sanitize_text(ph) for ph in placeholders.keys()]
            placeholders_list = ", ".join([f"<code>{{{html.escape(ph)}}}</code>" for ph in ph_list]) if ph_list else "None"
            
            # Premium emoji replacements
            check_icon = CUSTOM_EMOJIS.get("YES", "4956721670690702265")  # ✅
            url_icon = CUSTOM_EMOJIS.get("API_FIELD_URL", "6285048454255220485")  # 🌐
            method_icon = CUSTOM_EMOJIS.get("API_FIELD_METHOD", "5926860096008098405")  # 📌
            headers_icon = CUSTOM_EMOJIS.get("API_FIELD_HEADERS", "5926860096008098405")  # 📋 (we don't have one, reuse)
            data_icon = CUSTOM_EMOJIS.get("API_FIELD_MESSAGE", "5980911993140284450")  # 📦
            token_icon = CUSTOM_EMOJIS.get("API_FIELD_TOKEN", "5821453562680448557")  # 🔑
            
            # Escape URL and other dynamic content
            url_display = html.escape(sanitize_text(parsed.get('url', 'N/A')))
            method_display = html.escape(sanitize_text(parsed.get('method', 'GET')))
            headers_count = len(parsed.get('headers', {}))
            data_present = 'Yes' if parsed.get('data') else 'No'
            
            info_text = f"""
{emoji_tag(check_icon, '✅')} <b>CURL Parsed Successfully</b>

{emoji_tag(url_icon, '🌐')} <b>URL</b>: <code>{url_display}</code>
{emoji_tag(method_icon, '📌')} <b>Method</b>: <code>{method_display}</code>
{emoji_tag(headers_icon, '📋')} <b>Headers</b>: <code>{headers_count}</code>
{emoji_tag(data_icon, '📦')} <b>Data</b>: {data_present}
{emoji_tag(token_icon, '🔑')} <b>Placeholders</b>: {placeholders_list}

<blockquote>✅ Bot will use this exact format for polling</blockquote>
"""
            # Inline buttons: CONTINUE and CANCEL with premium emojis
            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "CONTINUE",
                        callback_data="api_add_curl_continue",
                        style=KBS.SUCCESS,
                        icon_custom_emoji_id=safe_icon("6266818250818983044")  # Provided CONTINUE emoji
                    ),
                    InlineKeyboardButton(
                        "CANCEL",
                        callback_data="api_add_curl_cancel",
                        style=KBS.DANGER,
                        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CANCEL", ""))
                    )
                ]
            ])
            admin_panel_state[user_id] = "api_add_curl_confirm"
            await update.message.reply_text(info_text, reply_markup=kb, parse_mode='HTML')
            return True
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ <b>Error parsing CURL</b>\n\n<code>{html.escape(str(e))}</code>\n\nPlease send a valid CURL command or <code>/skip</code>",
                parse_mode='HTML'
            )
            return True
    
    # Normal field handling
    if field:
        if field == "interval_sec":
            try:
                val = int(text)
                if val < 1:
                    await update.message.reply_text("⏱️ Interval must be at least 1 second. Try again.")
                    return True
                data[field] = val
            except ValueError:
                await update.message.reply_text("❌ Please enter a valid number.")
                return True
        else:
            data[field] = text
        
        admin_temp_data[user_id] = data
    
    if next_step:
        await api_add_step(update, context, user_id, next_step)
    else:
        await show_confirm_step(update, context, user_id)
    
    return True

# ==================== API ADD CONFIRM YES (UPDATED) ====================

async def api_add_confirm_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = admin_temp_data.get(user_id, {})
    
    if not data:
        await query.answer("Session expired.", show_alert=True)
        return
    
    parsed_curl = data.get("parsed_curl")
    curl_command = data.get("curl_command")
    
    # Get values - if None, use empty string or defaults
    panel_name = data.get("panel_name") or "API_" + str(user_id)[-4:]
    base_url = data.get("base_url") or ""
    endpoint = data.get("endpoint") or "/"
    token = data.get("token") or ""
    interval = data.get("interval_sec") or 30
    otp_list_path = data.get("otp_list_path") or "data"
    number_path = data.get("number_path")  # Can be None = not used
    message_path = data.get("message_path")  # Can be None = not used
    timestamp_path = data.get("timestamp_path")  # Can be None = not used
    service_path = data.get("service_path")  # Can be None = not used
    
    if parsed_curl:
        # Only use parsed_curl base_url if it's not a placeholder (i.e., contains no {})
        if parsed_curl.get("base_url") and "{" not in parsed_curl["base_url"]:
            base_url = parsed_curl["base_url"]
        elif not base_url and parsed_curl.get("base_url"):
            base_url = parsed_curl["base_url"]
        # Similarly for endpoint
        if parsed_curl.get("endpoint") and "{" not in parsed_curl["endpoint"]:
            endpoint = parsed_curl["endpoint"]
        elif not endpoint and parsed_curl.get("endpoint"):
            endpoint = parsed_curl["endpoint"]
        
        method = parsed_curl.get("method", "GET")
        headers = parsed_curl.get("headers", {})
        body_template = parsed_curl.get("data")
        placeholders = parsed_curl.get("placeholders", {})
        placeholder_config = json.dumps(placeholders) if placeholders else "{}"
    else:
        method = "GET"
        headers = {}
        body_template = None
        placeholder_config = "{}"
    
    # If number_path is None, response parser will try to find OTP from message
    number_path = number_path if number_path is not None else ""
    message_path = message_path if message_path is not None else ""
    timestamp_path = timestamp_path if timestamp_path is not None else ""
    service_path = service_path if service_path is not None else ""
    
    db_exec("""
        INSERT INTO api_keys (
            panel_name, base_url, endpoint, token,
            interval_sec, active,
            method, headers, body_template,
            otp_list_path, number_path, message_path, timestamp_path, service_path,
            created_by, created_at,
            success_path, success_value,
            placeholder_config, curl_command
        ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'status', 'success', ?, ?)
    """, (
        panel_name,
        base_url,
        endpoint,
        token,
        interval,
        method,
        json.dumps(headers) if headers else "{}",
        json.dumps(body_template) if body_template else None,
        otp_list_path,
        number_path,
        message_path,
        timestamp_path,
        service_path,
        user_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        placeholder_config,
        curl_command
    ))
    
    api_id = db_fetch_one("SELECT last_insert_rowid()")[0]
    await start_polling_for_api(api_id)
    
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    
    # Build success message with used fields only
    used_fields = []
    if panel_name: used_fields.append(f"📛 Panel: {panel_name}")
    if base_url: used_fields.append(f"🌐 Base URL: {base_url}")
    if endpoint and endpoint != "/": used_fields.append(f"📍 Endpoint: {endpoint}")
    if token: used_fields.append(f"🔑 Token: {token[:8]}...")
    used_fields.append(f"⏱️ Interval: {interval}s")
    if otp_list_path: used_fields.append(f"📋 OTP List Path: {otp_list_path}")
    if number_path: used_fields.append(f"📱 Number Path: {number_path}")
    if message_path: used_fields.append(f"💬 Message Path: {message_path}")
    if timestamp_path: used_fields.append(f"🕐 Timestamp Path: {timestamp_path}")
    if service_path: used_fields.append(f"🔧 Service Path: {service_path}")
    if curl_command: used_fields.append(f"📌 CURL: {curl_command[:50]}...")
    
    # Show which fields were skipped
    skipped_fields = []
    if not number_path: skipped_fields.append("Number Path")
    if not message_path: skipped_fields.append("Message Path")
    if not timestamp_path: skipped_fields.append("Timestamp Path")
    if not service_path: skipped_fields.append("Service Path")
    if not curl_command: skipped_fields.append("CURL")
    if not otp_list_path: skipped_fields.append("OTP List Path")
    
    success_text = f"""
✅ {emoji_tag(CUSTOM_EMOJIS['ADD_API_KEY'], '➕')} <b>API '{panel_name}' added successfully!</b>

🆔 <b>API ID</b>: <code>{api_id}</code>
"""
    if used_fields:
        success_text += "\n📋 <b>Configured:</b>\n" + "\n".join([f"  • {f}" for f in used_fields])
    
    if skipped_fields:
        success_text += f"\n\n⏭ <b>Skipped (Not Used):</b>\n" + "\n".join([f"  • {f}" for f in skipped_fields])
    
    success_text += f"""
    
<blockquote>{emoji_tag('5303449763406954093', '💡')} <b>Next Steps</b>:
1. Go to <b>API System</b> → {panel_name}
2. Click <b>TEST</b> to verify API works
3. Click <b>EDIT</b> to adjust any settings
4. Check <b>LOGS</b> for polling status</blockquote>
"""
    
    await query.edit_message_text(success_text, reply_markup=admin_panel_keyboard(), parse_mode='HTML')

# ==================== API ADD CONFIRM NO ====================

async def api_add_confirm_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await query.edit_message_text("❌ API addition cancelled.", reply_markup=admin_panel_keyboard())

# ==================== API ADD EDIT ====================

async def api_add_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = admin_temp_data.get(user_id, {})
    if not data:
        await query.answer("Session expired.", show_alert=True)
        return
    admin_panel_state[user_id] = "api_add_name"
    await query.edit_message_text(
        "✏️ Edit mode: You can re-enter each step. Press SKIP to keep current value.",
        reply_markup=admin_cancel_keyboard()
    )
    await api_add_step(update, context, user_id, "api_add_name")

# ==================== CURL BASED POLLING (FIXED - DECODING) ====================

async def poll_single_api_curl_based(api_id: int):
    """CURL based polling with automatic placeholder replacement for {API_BASE}, {TOKEN}, etc."""
    async with aiohttp.ClientSession() as session:
        while True:
            config = get_api_config(api_id)
            if not config or not config.get('active'):
                break
            
            interval = config.get('interval_sec', 30)
            
            try:
                method = config.get('method', 'GET')
                base_url = config.get('base_url', '')
                endpoint = config.get('endpoint', '/')
                headers = json.loads(config.get('headers', '{}')) if config.get('headers') else {}
                body_template = config.get('body_template')
                token = config.get('token', '')
                curl_command = config.get('curl_command')
                otp_list_path = config.get('otp_list_path', 'data')
                
                # Build placeholder dictionary
                placeholders = {}
                user_placeholders = json.loads(config.get('placeholder_config', '{}')) if config.get('placeholder_config') else {}
                placeholders.update(user_placeholders)
                
                # Add auto placeholders
                if base_url:
                    placeholders["API_BASE"] = base_url
                    placeholders["BASE_URL"] = base_url
                    placeholders["API_URL"] = base_url
                    placeholders["API"] = base_url
                    placeholders["URL"] = base_url
                if token:
                    placeholders["TOKEN"] = token
                    placeholders["YOUR_TOKEN"] = token
                    placeholders["API_TOKEN"] = token
                    placeholders["AUTH_TOKEN"] = token
                placeholders["RECORDS"] = str(config.get('max_records', 200))
                placeholders["records"] = str(config.get('max_records', 200))
                
                if curl_command:
                    parsed = parse_curl_complete(curl_command)
                    parsed["placeholders"].update(placeholders)
                    request = build_request_from_curl(parsed, placeholders)
                    url = request["url"]
                    method = request["method"]
                    headers = request["headers"]
                    data = request["data"]
                else:
                    # Build URL from base_url + endpoint
                    url = base_url.rstrip('/') + '/' + endpoint.lstrip('/')
                    # Replace placeholders in URL
                    for key, value in placeholders.items():
                        url = url.replace(f"{{{key}}}", str(value))
                    # Replace placeholders in headers
                    for key, value in headers.items():
                        if isinstance(value, str):
                            for ph_key, ph_value in placeholders.items():
                                value = value.replace(f"{{{ph_key}}}", str(ph_value))
                            headers[key] = value
                    # Build data
                    data = None
                    if body_template:
                        try:
                            data = json.loads(body_template)
                            if data:
                                data_str = json.dumps(data)
                                for ph_key, ph_value in placeholders.items():
                                    data_str = data_str.replace(f"{{{ph_key}}}", str(ph_value))
                                data = json.loads(data_str)
                        except:
                            data = body_template

                if method.upper() == 'GET':
                    async with session.get(url, headers=headers, timeout=30) as response:
                        raw_bytes = await response.read()
                        status = response.status
                elif method.upper() == 'POST':
                    async with session.post(url, headers=headers, json=data, timeout=30) as response:
                        raw_bytes = await response.read()
                        status = response.status
                elif method.upper() == 'PUT':
                    async with session.put(url, headers=headers, json=data, timeout=30) as response:
                        raw_bytes = await response.read()
                        status = response.status
                elif method.upper() == 'DELETE':
                    async with session.delete(url, headers=headers, timeout=30) as response:
                        raw_bytes = await response.read()
                        status = response.status
                else:
                    async with session.request(method, url, headers=headers, json=data, timeout=30) as response:
                        raw_bytes = await response.read()
                        status = response.status
                
                # Decode with fallback
                try:
                    text = raw_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text = raw_bytes.decode('latin-1')
                    except:
                        text = raw_bytes.decode('utf-8', errors='ignore')

                if status == 200:
                    # Pass otp_list_path to parser
                    config['otp_list_path'] = otp_list_path
                    otps = ResponseParser.parse_response(text, config)
                    if otps:
                        # process_otps returns new OTP count
                        new_count = await process_otps(otps, bot=application.bot)
                        if new_count > 0:
                            db_exec("UPDATE api_keys SET total_otps = total_otps + ?, last_otp_time = ? WHERE id = ?",
                                    (new_count, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), api_id))
                    else:
                        new_count = 0
                    db_exec("INSERT INTO api_logs (api_id, timestamp, status, message, otp_count) VALUES (?, ?, 'success', ?, ?)",
                            (api_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "OK", new_count))
                    db_exec("UPDATE api_keys SET error_count = 0, last_poll_time = ? WHERE id = ?",
                            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), api_id))
                else:
                    error_msg = f"HTTP {status}"
                    db_exec("INSERT INTO api_logs (api_id, timestamp, status, message, otp_count) VALUES (?, ?, 'error', ?, 0)",
                            (api_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error_msg))
                    db_exec("UPDATE api_keys SET error_count = error_count + 1 WHERE id = ?", (api_id,))
            except Exception as e:
                print(f"API {api_id} error: {e}")
                db_exec("INSERT INTO api_logs (api_id, timestamp, status, message, otp_count) VALUES (?, ?, 'error', ?, 0)",
                        (api_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(e)[:200]))
                db_exec("UPDATE api_keys SET error_count = error_count + 1 WHERE id = ?", (api_id,))
            await asyncio.sleep(interval)

# ==================== API SYSTEM MANAGEMENT ====================

async def start_polling_for_api(api_id: int):
    config = get_api_config(api_id)
    if not config or not config.get('active'):
        return
    if api_id not in polling_tasks or polling_tasks[api_id].done():
        task = asyncio.create_task(poll_single_api_curl_based(api_id))
        polling_tasks[api_id] = task

async def stop_polling_for_api(api_id: int):
    if api_id in polling_tasks:
        polling_tasks[api_id].cancel()
        del polling_tasks[api_id]
    db_exec("UPDATE api_keys SET active = 0 WHERE id = ?", (api_id,))

async def start_all_polling():
    apis = db_fetch_all("SELECT id FROM api_keys WHERE active = 1")
    for (api_id,) in apis:
        await start_polling_for_api(api_id)

# ==================== API SYSTEM GRID ====================

async def api_system_grid(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    if not is_admin(user_id):
        if isinstance(update, CallbackQuery):
            await update.answer("Admin only!", show_alert=True)
        return
    admin_panel_state[user_id] = "api_system"
    apis = db_fetch_all("SELECT id, panel_name, active FROM api_keys ORDER BY id")
    if not apis:
        text = f"{emoji_tag(CUSTOM_EMOJIS['API_SYSTEM'], '🖥️')} No APIs configured yet."
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add API", callback_data="api_add", style=KBS.SUCCESS,
                                  icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADD_API_KEY", "")))],
            [InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                  icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
        ])
        await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)
        return

    rows = []
    row = []
    for api_id, panel_name, active in apis:
        style = KBS.SUCCESS if active else KBS.DANGER
        icon_id = CUSTOM_EMOJIS.get("API_STATUS_ACTIVE" if active else "API_STATUS_INACTIVE", "")
        btn = InlineKeyboardButton(
            panel_name,
            callback_data=f"api_detail|{api_id}",
            style=style,
            icon_custom_emoji_id=safe_icon(icon_id)
        )
        row.append(btn)
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([
        InlineKeyboardButton("Add API", callback_data="api_add", style=KBS.SUCCESS,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADD_API_KEY", "")))
    ])
    rows.append([
        InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))
    ])

    text = f"{emoji_tag(CUSTOM_EMOJIS['API_SYSTEM'], '🖥️')} <b>API SYSTEM</b> ({len(apis)} configured)"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)

# ==================== API DETAIL PAGE ====================

async def api_detail_page(update: Update, context: ContextTypes.DEFAULT_TYPE, api_id: int, user_id: int):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    config = get_api_config(api_id)
    if not config:
        await update.answer("API not found!", show_alert=True)
        return

    admin_panel_state[user_id] = f"api_detail_{api_id}"

    header = f"{emoji_tag(CUSTOM_EMOJIS['MANAGE_API'], '🔧')} <b>Manage: {config['panel_name']}</b>"
    info = (
        f"{emoji_tag(CUSTOM_EMOJIS['API_STATUS_ACTIVE'] if config['active'] else CUSTOM_EMOJIS['API_STATUS_INACTIVE'], '🟢' if config['active'] else '🔴')} Status: <b>{'ACTIVE' if config['active'] else 'INACTIVE'}</b>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_TODAY_OTP'], '📈')} Today's OTP: <code>{config.get('total_otps', 0)}</code>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_LAST_POLL'], '⏰')} Last Poll: <code>{config.get('last_poll_time', 'Never')}</code>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_ERROR_COUNT'], '❌')} Errors: <code>{config.get('error_count', 0)}</code>"
    )

    btns = []
    if config['active']:
        btns.append(InlineKeyboardButton(
            "STOP POLLING",
            callback_data=f"api_toggle|{api_id}",
            style=KBS.DANGER,
            icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_STOP_POLL", ""))
        ))
    else:
        btns.append(InlineKeyboardButton(
            "START POLLING",
            callback_data=f"api_toggle|{api_id}",
            style=KBS.SUCCESS,
            icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_START_POLL", ""))
        ))

    btns.append(InlineKeyboardButton(
        "EDIT",
        callback_data=f"api_edit|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("EDIT_BALANCE", ""))
    ))
    btns.append(InlineKeyboardButton(
        "TEST",
        callback_data=f"api_test|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_TEST", ""))
    ))
    btns.append(InlineKeyboardButton(
        "STATS",
        callback_data=f"api_stats|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_STATS", ""))
    ))
    btns.append(InlineKeyboardButton(
        "LOGS",
        callback_data=f"api_logs|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_LOGS", ""))
    ))
    btns.append(InlineKeyboardButton(
        "DELETE",
        callback_data=f"api_delete|{api_id}",
        style=KBS.DANGER,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DELETE", ""))
    ))
    btns.append(InlineKeyboardButton(
        "FORCE POLL",
        callback_data=f"api_force|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_FORCE_POLL", ""))
    ))
    btns.append(InlineKeyboardButton(
        "BACK TO LIST",
        callback_data="api_system",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))
    ))

    rows = [[btn] for btn in btns]
    sep = emoji_tag(CUSTOM_EMOJIS["API_SEPARATOR"], "➖") * 20
    text = f"{header}\n\n{info}\n\n{sep}\n\n"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)

# ==================== API TOGGLE ====================

async def api_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    api_id = int(query.data.split('|')[1])
    config = get_api_config(api_id)
    if not config:
        await query.answer("API not found!", show_alert=True)
        return

    if config['active']:
        await stop_polling_for_api(api_id)
        await query.answer("Polling stopped.")
    else:
        db_exec("UPDATE api_keys SET active = 1 WHERE id = ?", (api_id,))
        await start_polling_for_api(api_id)
        await query.answer("Polling started.")

    await api_detail_page(update, context, api_id, user_id)

# ==================== API EDIT MENU ====================

async def api_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, api_id: int, user_id: int):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    config = get_api_config(api_id)
    if not config:
        await update.answer("API not found!", show_alert=True)
        return

    admin_panel_state[user_id] = f"api_edit_{api_id}"

    fields = [
        ("NAME", "API_FIELD_NAME", "panel_name", KBS.SUCCESS),
        ("BASE URL", "API_FIELD_URL", "base_url", KBS.SUCCESS),
        ("ENDPOINT", "API_FIELD_ENDPOINT", "endpoint", KBS.SUCCESS),
        ("TOKEN", "API_FIELD_TOKEN", "token", KBS.SUCCESS),
        ("METHOD", "API_FIELD_METHOD", "method", KBS.SUCCESS),
        ("INTERVAL", "API_FIELD_INTERVAL", "interval_sec", KBS.SUCCESS),
        ("MAX RECORDS", "API_FIELD_RECORDS", "max_records", KBS.PRIMARY),
        ("RETRY COUNT", "API_FIELD_RETRY", "retry_count", KBS.PRIMARY),
        ("OTP LIST PATH", "API_FIELD_OTP_PATH", "otp_list_path", KBS.PRIMARY),
        ("NUMBER PATH", "API_FIELD_NUMBER", "number_path", KBS.PRIMARY),
        ("MESSAGE PATH", "API_FIELD_MESSAGE", "message_path", KBS.PRIMARY),
        ("COUNTRY PATH", "API_FIELD_COUNTRY", "country_path", KBS.PRIMARY),
        ("SERVICE PATH", "API_FIELD_SERVICE", "service_path", KBS.PRIMARY),
        ("TIMESTAMP PATH", "API_FIELD_TIMESTAMP", "timestamp_path", KBS.PRIMARY),
        ("SUCCESS PATH", "API_FIELD_SUCCESS_PATH", "success_path", KBS.PRIMARY),
        ("SUCCESS VALUE", "API_FIELD_SUCCESS_VALUE", "success_value", KBS.PRIMARY),
        ("PLACEHOLDERS", "API_FIELD_PLACEHOLDERS", "placeholder_config", KBS.PRIMARY),
    ]

    rows = []
    for label, emoji_key, field, style in fields:
        value = config.get(field, "")
        if field == "placeholder_config":
            try:
                value = json.loads(value) if value else {}
                display_value = ", ".join([f"{k}={v}" for k, v in value.items()]) if value else "None"
            except:
                display_value = str(value)[:20]
        else:
            display_value = str(value)[:30] + "..." if len(str(value)) > 30 else value
        rows.append([InlineKeyboardButton(
            f"{label}: {display_value}",
            callback_data=f"api_edit_field|{api_id}|{field}",
            style=style,
            icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get(emoji_key, ""))
        )])

    rows.append([
        InlineKeyboardButton(
            "BACK TO DETAIL",
            callback_data=f"api_detail|{api_id}",
            style=KBS.DANGER,
            icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))
        )
    ])

    text = f"{emoji_tag(CUSTOM_EMOJIS['EDIT_BALANCE'], '✏️')} <b>Edit Configuration: {config['panel_name']}</b>\n\nSelect a field to edit:"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)

# ==================== API EDIT FIELD PROMPT ====================

async def api_edit_field_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    data = query.data.split('|')
    api_id = int(data[1])
    field = data[2]
    config = get_api_config(api_id)
    if not config:
        await query.answer("API not found!", show_alert=True)
        return

    admin_temp_data[user_id] = {"api_id": api_id, "field": field, "current": config.get(field)}
    admin_panel_state[user_id] = f"api_edit_value_{api_id}"

    current_val = config.get(field, "")
    if field == "placeholder_config":
        try:
            current_val = json.loads(current_val) if current_val else {}
            display_val = "\n".join([f"{k}: {v}" for k, v in current_val.items()]) if current_val else "None"
        except:
            display_val = str(current_val)
    else:
        display_val = str(current_val)

    await query.edit_message_text(
        f"{emoji_tag(CUSTOM_EMOJIS['EDIT_BALANCE'], '✏️')} Edit <b>{field}</b>\n\nCurrent value:\n<code>{display_val}</code>\n\nSend new value (or /cancel):",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel", callback_data=f"api_edit|{api_id}", style=KBS.DANGER,
                                  icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
        ]),
        parse_mode='HTML'
    )

# ==================== API TEST ====================

async def api_test_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    api_id = int(query.data.split('|')[1])
    config = get_api_config(api_id)
    if not config:
        await query.answer("API not found!", show_alert=True)
        return

    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['API_TEST'], '🧪')} Testing <b>{config['panel_name']}</b> ...", parse_mode='HTML')

    try:
        async with aiohttp.ClientSession() as session:
            method = config.get('method', 'GET')
            base_url = config.get('base_url', '')
            endpoint = config.get('endpoint', '/')
            headers = json.loads(config.get('headers', '{}')) if config.get('headers') else {}
            body_template = config.get('body_template')
            token = config.get('token', '')
            curl_command = config.get('curl_command')
            otp_list_path = config.get('otp_list_path', 'data')
            
            placeholders = {}
            user_placeholders = json.loads(config.get('placeholder_config', '{}')) if config.get('placeholder_config') else {}
            placeholders.update(user_placeholders)
            if base_url:
                placeholders["API_BASE"] = base_url
                placeholders["BASE_URL"] = base_url
                placeholders["API_URL"] = base_url
                placeholders["API"] = base_url
                placeholders["URL"] = base_url
            if token:
                placeholders["TOKEN"] = token
                placeholders["YOUR_TOKEN"] = token
                placeholders["API_TOKEN"] = token
                placeholders["AUTH_TOKEN"] = token
            placeholders["RECORDS"] = str(config.get('max_records', 200))
            
            if curl_command:
                parsed = parse_curl_complete(curl_command)
                parsed["placeholders"].update(placeholders)
                request = build_request_from_curl(parsed, placeholders)
                url = request["url"]
                method = request["method"]
                headers = request["headers"]
                data = request["data"]
            else:
                url = base_url.rstrip('/') + '/' + endpoint.lstrip('/')
                for key, value in placeholders.items():
                    url = url.replace(f"{{{key}}}", str(value))
                for key, value in headers.items():
                    if isinstance(value, str):
                        for ph_key, ph_value in placeholders.items():
                            value = value.replace(f"{{{ph_key}}}", str(ph_value))
                        headers[key] = value
                data = None
                if body_template:
                    try:
                        data = json.loads(body_template)
                        if data:
                            data_str = json.dumps(data)
                            for ph_key, ph_value in placeholders.items():
                                data_str = data_str.replace(f"{{{ph_key}}}", str(ph_value))
                            data = json.loads(data_str)
                    except:
                        data = body_template

            if method.upper() == 'GET':
                async with session.get(url, headers=headers, timeout=30) as response:
                    raw_bytes = await response.read()
                    status = response.status
            elif method.upper() == 'POST':
                async with session.post(url, headers=headers, json=data, timeout=30) as response:
                    raw_bytes = await response.read()
                    status = response.status
            else:
                async with session.request(method, url, headers=headers, json=data, timeout=30) as response:
                    raw_bytes = await response.read()
                    status = response.status

            # Decode with fallback
            try:
                text = raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text = raw_bytes.decode('latin-1')
                except:
                    text = raw_bytes.decode('utf-8', errors='ignore')

            if status == 200:
                config['otp_list_path'] = otp_list_path
                otps = ResponseParser.parse_response(text, config)
                if otps:
                    sample = "\n".join([
                        f"{emoji_tag(CUSTOM_EMOJIS['API_OTP_COUNT'], '📨')} {i+1}. {otp.get('number', 'N/A')} – OTP: {otp.get('otp', '?')}"
                        for i, otp in enumerate(otps[:5])
                    ])
                    more = f"\n... and {len(otps)-5} more" if len(otps) > 5 else ""
                    result = f"✅ Found <b>{len(otps)}</b> OTP(s)\n\n{sample}{more}"
                else:
                    result = "✅ API responded but no OTPs found.\n\nRaw response (first 300 chars):\n<code>" + text[:300] + "</code>"
            else:
                result = f"❌ Error: HTTP {status}\n\nResponse:\n<code>{text[:500]}</code>"
    except Exception as e:
        result = f"❌ Exception: {str(e)}"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])
    await query.edit_message_text(
        f"{emoji_tag(CUSTOM_EMOJIS['API_TEST'], '🧪')} <b>Test Result: {config['panel_name']}</b>\n\n{result}",
        reply_markup=kb,
        parse_mode='HTML'
    )

# ==================== API STATS ====================

async def api_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    api_id = int(query.data.split('|')[1])
    config = get_api_config(api_id)
    if not config:
        await query.answer("API not found!", show_alert=True)
        return

    total_otps = config.get('total_otps', 0)
    last_otp_time = config.get('last_otp_time', 'Never')
    today = datetime.now().strftime("%Y-%m-%d")
    today_otps = db_fetch_one("SELECT SUM(otp_count) FROM api_logs WHERE api_id = ? AND timestamp LIKE ? AND status = 'success'",
                              (api_id, f"{today}%"))[0] or 0
    logs = db_fetch_all("SELECT status FROM api_logs WHERE api_id = ? ORDER BY timestamp DESC LIMIT 50", (api_id,))
    success = sum(1 for log in logs if log[0] == 'success')
    rate = (success / len(logs) * 100) if logs else 0

    text = (
        f"{emoji_tag(CUSTOM_EMOJIS['API_STATS'], '📊')} <b>Statistics: {config['panel_name']}</b>\n\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_TOTAL_OTP'], '📊')} Total OTP: <code>{total_otps}</code>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_TODAY_OTP'], '📈')} Today's OTP: <code>{today_otps}</code>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_SUCCESS_RATE'], '🏆')} Success Rate (last 50): <code>{rate:.1f}%</code>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_LAST_POLL'], '⏰')} Last OTP: <code>{last_otp_time}</code>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

# ==================== API LOGS ====================

async def api_logs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    api_id = int(query.data.split('|')[1])
    config = get_api_config(api_id)
    if not config:
        await query.answer("API not found!", show_alert=True)
        return

    logs = db_fetch_all("SELECT timestamp, status, message, otp_count FROM api_logs WHERE api_id = ? ORDER BY timestamp DESC LIMIT 10", (api_id,))
    if not logs:
        lines = ["No logs yet."]
    else:
        lines = []
        for ts, status, msg, count in logs:
            emoji = "✅" if status == "success" else "❌"
            count_str = f"{count} OTPs" if status == "success" else ""
            lines.append(f"{emoji} <code>{ts}</code> – {msg} {count_str}")
    text = f"{emoji_tag(CUSTOM_EMOJIS['API_LOGS'], '📜')} <b>Polling Logs: {config['panel_name']}</b>\n\n" + "\n".join(lines[:10])
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Refresh", callback_data=f"api_logs|{api_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_FORCE_POLL", "")))],
        [InlineKeyboardButton("Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

# ==================== API DELETE ====================

async def api_delete_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    api_id = int(query.data.split('|')[1])
    config = get_api_config(api_id)
    if not config:
        await query.answer("API not found!", show_alert=True)
        return

    text = (
        f"{emoji_tag(CUSTOM_EMOJIS['DELETE'], '🗑️')} <b>Confirm Delete</b>\n\n"
        f"Are you sure you want to delete API <b>{config['panel_name']}</b>?\n"
        f"This will remove all configuration and stop polling."
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("YES, DELETE", callback_data=f"api_delete_yes|{api_id}", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("YES", "")))],
        [InlineKeyboardButton("NO, CANCEL", callback_data=f"api_delete_no|{api_id}", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("NO", "")))]
    ])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

async def api_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    data = query.data.split('|')
    api_id = int(data[1])
    action = data[0]

    if action == "api_delete_yes":
        if api_id in polling_tasks:
            polling_tasks[api_id].cancel()
            del polling_tasks[api_id]
        db_exec("DELETE FROM api_keys WHERE id = ?", (api_id,))
        db_exec("DELETE FROM api_logs WHERE api_id = ?", (api_id,))
        await query.answer("API deleted.")
        await api_system_grid(update, context, user_id)
    else:
        await query.answer("Cancelled.")
        await api_detail_page(update, context, api_id, user_id)

# ==================== API FORCE POLL ====================

async def api_force_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    api_id = int(query.data.split('|')[1])
    config = get_api_config(api_id)
    if not config:
        await query.answer("API not found!", show_alert=True)
        return

    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['API_FORCE_POLL'], '🔄')} Force polling <b>{config['panel_name']}</b> ...", parse_mode='HTML')

    try:
        async with aiohttp.ClientSession() as session:
            method = config.get('method', 'GET')
            base_url = config.get('base_url', '')
            endpoint = config.get('endpoint', '/')
            headers = json.loads(config.get('headers', '{}')) if config.get('headers') else {}
            body_template = config.get('body_template')
            token = config.get('token', '')
            curl_command = config.get('curl_command')
            otp_list_path = config.get('otp_list_path', 'data')
            
            placeholders = {}
            user_placeholders = json.loads(config.get('placeholder_config', '{}')) if config.get('placeholder_config') else {}
            placeholders.update(user_placeholders)
            if base_url:
                placeholders["API_BASE"] = base_url
                placeholders["BASE_URL"] = base_url
                placeholders["API_URL"] = base_url
                placeholders["API"] = base_url
                placeholders["URL"] = base_url
            if token:
                placeholders["TOKEN"] = token
                placeholders["YOUR_TOKEN"] = token
                placeholders["API_TOKEN"] = token
                placeholders["AUTH_TOKEN"] = token
            placeholders["RECORDS"] = str(config.get('max_records', 200))
            
            if curl_command:
                parsed = parse_curl_complete(curl_command)
                parsed["placeholders"].update(placeholders)
                request = build_request_from_curl(parsed, placeholders)
                url = request["url"]
                method = request["method"]
                headers = request["headers"]
                data = request["data"]
            else:
                url = base_url.rstrip('/') + '/' + endpoint.lstrip('/')
                for key, value in placeholders.items():
                    url = url.replace(f"{{{key}}}", str(value))
                for key, value in headers.items():
                    if isinstance(value, str):
                        for ph_key, ph_value in placeholders.items():
                            value = value.replace(f"{{{ph_key}}}", str(ph_value))
                        headers[key] = value
                data = None
                if body_template:
                    try:
                        data = json.loads(body_template)
                        if data:
                            data_str = json.dumps(data)
                            for ph_key, ph_value in placeholders.items():
                                data_str = data_str.replace(f"{{{ph_key}}}", str(ph_value))
                            data = json.loads(data_str)
                    except:
                        data = body_template

            if method.upper() == 'GET':
                async with session.get(url, headers=headers, timeout=30) as response:
                    raw_bytes = await response.read()
                    status = response.status
            elif method.upper() == 'POST':
                async with session.post(url, headers=headers, json=data, timeout=30) as response:
                    raw_bytes = await response.read()
                    status = response.status
            else:
                async with session.request(method, url, headers=headers, json=data, timeout=30) as response:
                    raw_bytes = await response.read()
                    status = response.status

            # Decode with fallback
            try:
                text = raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text = raw_bytes.decode('latin-1')
                except:
                    text = raw_bytes.decode('utf-8', errors='ignore')

            if status == 200:
                config['otp_list_path'] = otp_list_path
                otps = ResponseParser.parse_response(text, config)
                if otps:
                    new_count = await process_otps(otps, bot=context.bot)
                    if new_count > 0:
                        db_exec("UPDATE api_keys SET total_otps = total_otps + ?, last_otp_time = ? WHERE id = ?",
                                (new_count, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), api_id))
                    result = f"✅ Found and processed <b>{new_count}</b> new OTP(s)."
                else:
                    result = "✅ API responded, but no OTPs found."
            else:
                result = f"❌ Error: HTTP {status}"
    except Exception as e:
        result = f"❌ Exception: {str(e)}"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])
    await query.edit_message_text(
        f"{emoji_tag(CUSTOM_EMOJIS['API_FORCE_POLL'], '🔄')} <b>Force Poll Result: {config['panel_name']}</b>\n\n{result}",
        reply_markup=kb,
        parse_mode='HTML'
    )

# ==================== MANAGE API MENU ====================

async def manage_api_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        if isinstance(update, CallbackQuery):
            await update.answer("Admin mode required!", show_alert=True)
        return
    admin_panel_state[user_id] = "manage_api"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("LIST API", callback_data="api_list", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("LIST_API_KEY", "")))],
        [InlineKeyboardButton("API SYSTEM", callback_data="api_system", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_SYSTEM", "")))],
        [InlineKeyboardButton("Back", callback_data="admin_back", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))],
    ])
    await reply_or_edit(update, "🔧 MANAGE API\n\nSelect an option:", reply_markup=kb, context=context, auto_delete=False)

# ==================== API LIST ====================

async def api_list(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    apis = db_fetch_all("SELECT id, panel_name, token, interval_sec FROM api_keys ORDER BY id")
    if not apis:
        text = "📭 No APIs configured."
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                                          icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
        await reply_or_edit(update, text, reply_markup=kb, context=context, auto_delete=False)
        return

    lines = []
    for api_id, panel_name, token, interval in apis:
        token_first7 = token[:7] if token and len(token) >= 7 else "N/A"
        panel_icon = CUSTOM_EMOJIS.get("API_LIST_ICON", "5411225014148014586")
        interval_icon = CUSTOM_EMOJIS.get("API_LIST_INTERVAL_ICON", "6235253239080555488")
        line = f"{emoji_tag(panel_icon, '📌')} <b>{panel_name}</b> | <code>{token_first7}</code> | <code>{interval}s</code> {emoji_tag(interval_icon, '⏱️')}"
        lines.append(line)

    text = f"{emoji_tag(CUSTOM_EMOJIS['LIST_API_KEY'], '📋')} <b>API LIST</b>\n\n" + "\n".join(lines)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

async def api_list_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await api_list(update, context, user_id)

async def api_system_grid_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await api_system_grid(update, context, user_id)

async def api_detail_page_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    api_id = int(query.data.split('|')[1])
    await api_detail_page(update, context, api_id, user_id)

async def api_edit_menu_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    api_id = int(query.data.split('|')[1])
    await api_edit_menu(update, context, api_id, user_id)

async def api_add_start_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await api_add_start(update, context, user_id)

async def manage_api_menu_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await manage_api_menu(update, context, user_id)

# ==================== COUNTRY CODE MAP ====================

COUNTRY_CODE_MAP = {
    "93": ("AF", "🇦🇫", "Afghanistan"),
    "355": ("AL", "🇦🇱", "Albania"),
    "213": ("DZ", "🇩🇿", "Algeria"),
    "1684": ("AS", "🇦🇸", "American Samoa"),
    "376": ("AD", "🇦🇩", "Andorra"),
    "244": ("AO", "🇦🇴", "Angola"),
    "1264": ("AI", "🇦🇮", "Anguilla"),
    "1268": ("AG", "🇦🇬", "Antigua and Barbuda"),
    "54": ("AR", "🇦🇷", "Argentina"),
    "374": ("AM", "🇦🇲", "Armenia"),
    "297": ("AW", "🇦🇼", "Aruba"),
    "61": ("AU", "🇦🇺", "Australia"),
    "43": ("AT", "🇦🇹", "Austria"),
    "994": ("AZ", "🇦🇿", "Azerbaijan"),
    "1242": ("BS", "🇧🇸", "Bahamas"),
    "973": ("BH", "🇧🇭", "Bahrain"),
    "880": ("BD", "🇧🇩", "Bangladesh"),
    "1246": ("BB", "🇧🇧", "Barbados"),
    "375": ("BY", "🇧🇾", "Belarus"),
    "32": ("BE", "🇧🇪", "Belgium"),
    "501": ("BZ", "🇧🇿", "Belize"),
    "229": ("BJ", "🇧🇯", "Benin"),
    "1441": ("BM", "🇧🇲", "Bermuda"),
    "975": ("BT", "🇧🇹", "Bhutan"),
    "591": ("BO", "🇧🇴", "Bolivia"),
    "387": ("BA", "🇧🇦", "Bosnia and Herzegovina"),
    "267": ("BW", "🇧🇼", "Botswana"),
    "55": ("BR", "🇧🇷", "Brazil"),
    "246": ("IO", "🇮🇴", "British Indian Ocean Territory"),
    "1284": ("VG", "🇻🇬", "British Virgin Islands"),
    "673": ("BN", "🇧🇳", "Brunei"),
    "359": ("BG", "🇧🇬", "Bulgaria"),
    "226": ("BF", "🇧🇫", "Burkina Faso"),
    "257": ("BI", "🇧🇮", "Burundi"),
    "855": ("KH", "🇰🇭", "Cambodia"),
    "237": ("CM", "🇨🇲", "Cameroon"),
    "1": ("CA", "🇨🇦", "Canada"),
    "238": ("CV", "🇨🇻", "Cape Verde"),
    "599": ("BQ", "🇧🇶", "Caribbean Netherlands"),
    "1345": ("KY", "🇰🇾", "Cayman Islands"),
    "236": ("CF", "🇨🇫", "Central African Republic"),
    "235": ("TD", "🇹🇩", "Chad"),
    "56": ("CL", "🇨🇱", "Chile"),
    "86": ("CN", "🇨🇳", "China"),
    "57": ("CO", "🇨🇴", "Colombia"),
    "269": ("KM", "🇰🇲", "Comoros"),
    "242": ("CG", "🇨🇬", "Congo"),
    "682": ("CK", "🇨🇰", "Cook Islands"),
    "506": ("CR", "🇨🇷", "Costa Rica"),
    "385": ("HR", "🇭🇷", "Croatia"),
    "53": ("CU", "🇨🇺", "Cuba"),
    "357": ("CY", "🇨🇾", "Cyprus"),
    "420": ("CZ", "🇨🇿", "Czech Republic"),
    "243": ("CD", "🇨🇩", "DR Congo"),
    "45": ("DK", "🇩🇰", "Denmark"),
    "253": ("DJ", "🇩🇯", "Djibouti"),
    "1767": ("DM", "🇩🇲", "Dominica"),
    "1809": ("DO", "🇩🇴", "Dominican Republic"),
    "670": ("TL", "🇹🇱", "East Timor"),
    "593": ("EC", "🇪🇨", "Ecuador"),
    "20": ("EG", "🇪🇬", "Egypt"),
    "503": ("SV", "🇸🇻", "El Salvador"),
    "240": ("GQ", "🇬🇶", "Equatorial Guinea"),
    "291": ("ER", "🇪🇷", "Eritrea"),
    "372": ("EE", "🇪🇪", "Estonia"),
    "268": ("SZ", "🇸🇿", "Eswatini"),
    "251": ("ET", "🇪🇹", "Ethiopia"),
    "500": ("FK", "🇫🇰", "Falkland Islands"),
    "298": ("FO", "🇫🇴", "Faroe Islands"),
    "679": ("FJ", "🇫🇯", "Fiji"),
    "358": ("FI", "🇫🇮", "Finland"),
    "33": ("FR", "🇫🇷", "France"),
    "594": ("GF", "🇬🇫", "French Guiana"),
    "689": ("PF", "🇵🇫", "French Polynesia"),
    "241": ("GA", "🇬🇦", "Gabon"),
    "220": ("GM", "🇬🇲", "Gambia"),
    "995": ("GE", "🇬🇪", "Georgia"),
    "49": ("DE", "🇩🇪", "Germany"),
    "233": ("GH", "🇬🇭", "Ghana"),
    "350": ("GI", "🇬🇮", "Gibraltar"),
    "30": ("GR", "🇬🇷", "Greece"),
    "299": ("GL", "🇬🇱", "Greenland"),
    "1473": ("GD", "🇬🇩", "Grenada"),
    "590": ("GP", "🇬🇵", "Guadeloupe"),
    "1671": ("GU", "🇬🇺", "Guam"),
    "502": ("GT", "🇬🇹", "Guatemala"),
    "224": ("GN", "🇬🇳", "Guinea"),
    "245": ("GW", "🇬🇼", "Guinea-Bissau"),
    "592": ("GY", "🇬🇾", "Guyana"),
    "509": ("HT", "🇭🇹", "Haiti"),
    "504": ("HN", "🇭🇳", "Honduras"),
    "852": ("HK", "🇭🇰", "Hong Kong"),
    "36": ("HU", "🇭🇺", "Hungary"),
    "354": ("IS", "🇮🇸", "Iceland"),
    "91": ("IN", "🇮🇳", "India"),
    "62": ("ID", "🇮🇩", "Indonesia"),
    "98": ("IR", "🇮🇷", "Iran"),
    "964": ("IQ", "🇮🇶", "Iraq"),
    "353": ("IE", "🇮🇪", "Ireland"),
    "972": ("IL", "🇮🇱", "Israel"),
    "39": ("IT", "🇮🇹", "Italy"),
    "225": ("CI", "🇨🇮", "Ivory Coast"),
    "1876": ("JM", "🇯🇲", "Jamaica"),
    "81": ("JP", "🇯🇵", "Japan"),
    "962": ("JO", "🇯🇴", "Jordan"),
    "254": ("KE", "🇰🇪", "Kenya"),
    "686": ("KI", "🇰🇮", "Kiribati"),
    "383": ("XK", "🇽🇰", "Kosovo"),
    "965": ("KW", "🇰🇼", "Kuwait"),
    "996": ("KG", "🇰🇬", "Kyrgyzstan"),
    "856": ("LA", "🇱🇦", "Laos"),
    "371": ("LV", "🇱🇻", "Latvia"),
    "961": ("LB", "🇱🇧", "Lebanon"),
    "266": ("LS", "🇱🇸", "Lesotho"),
    "231": ("LR", "🇱🇷", "Liberia"),
    "218": ("LY", "🇱🇾", "Libya"),
    "423": ("LI", "🇱🇮", "Liechtenstein"),
    "370": ("LT", "🇱🇹", "Lithuania"),
    "352": ("LU", "🇱🇺", "Luxembourg"),
    "853": ("MO", "🇲🇴", "Macau"),
    "261": ("MG", "🇲🇬", "Madagascar"),
    "265": ("MW", "🇲🇼", "Malawi"),
    "60": ("MY", "🇲🇾", "Malaysia"),
    "960": ("MV", "🇲🇻", "Maldives"),
    "223": ("ML", "🇲🇱", "Mali"),
    "356": ("MT", "🇲🇹", "Malta"),
    "692": ("MH", "🇲🇭", "Marshall Islands"),
    "596": ("MQ", "🇲🇶", "Martinique"),
    "222": ("MR", "🇲🇷", "Mauritania"),
    "230": ("MU", "🇲🇺", "Mauritius"),
    "52": ("MX", "🇲🇽", "Mexico"),
    "691": ("FM", "🇫🇲", "Micronesia"),
    "373": ("MD", "🇲🇩", "Moldova"),
    "377": ("MC", "🇲🇨", "Monaco"),
    "976": ("MN", "🇲🇳", "Mongolia"),
    "382": ("ME", "🇲🇪", "Montenegro"),
    "1664": ("MS", "🇲🇸", "Montserrat"),
    "212": ("MA", "🇲🇦", "Morocco"),
    "258": ("MZ", "🇲🇿", "Mozambique"),
    "95": ("MM", "🇲🇲", "Myanmar"),
    "264": ("NA", "🇳🇦", "Namibia"),
    "674": ("NR", "🇳🇷", "Nauru"),
    "977": ("NP", "🇳🇵", "Nepal"),
    "31": ("NL", "🇳🇱", "Netherlands"),
    "687": ("NC", "🇳🇨", "New Caledonia"),
    "64": ("NZ", "🇳🇿", "New Zealand"),
    "505": ("NI", "🇳🇮", "Nicaragua"),
    "227": ("NE", "🇳🇪", "Niger"),
    "234": ("NG", "🇳🇬", "Nigeria"),
    "683": ("NU", "🇳🇺", "Niue"),
    "672": ("NF", "🇳🇫", "Norfolk Island"),
    "850": ("KP", "🇰🇵", "North Korea"),
    "389": ("MK", "🇲🇰", "North Macedonia"),
    "1670": ("MP", "🇲🇵", "Northern Mariana Islands"),
    "47": ("NO", "🇳🇴", "Norway"),
    "968": ("OM", "🇴🇲", "Oman"),
    "92": ("PK", "🇵🇰", "Pakistan"),
    "680": ("PW", "🇵🇼", "Palau"),
    "970": ("PS", "🇵🇸", "Palestine"),
    "507": ("PA", "🇵🇦", "Panama"),
    "675": ("PG", "🇵🇬", "Papua New Guinea"),
    "595": ("PY", "🇵🇾", "Paraguay"),
    "51": ("PE", "🇵🇪", "Peru"),
    "63": ("PH", "🇵🇭", "Philippines"),
    "48": ("PL", "🇵🇱", "Poland"),
    "351": ("PT", "🇵🇹", "Portugal"),
    "1787": ("PR", "🇵🇷", "Puerto Rico"),
    "974": ("QA", "🇶🇦", "Qatar"),
    "262": ("RE", "🇷🇪", "Reunion"),
    "40": ("RO", "🇷🇴", "Romania"),
    "7": ("RU", "🇷🇺", "Russia"),
    "250": ("RW", "🇷🇼", "Rwanda"),
    "290": ("SH", "🇸🇭", "Saint Helena"),
    "1869": ("KN", "🇰🇳", "Saint Kitts and Nevis"),
    "1758": ("LC", "🇱🇨", "Saint Lucia"),
    "508": ("PM", "🇵🇲", "Saint Pierre and Miquelon"),
    "1784": ("VC", "🇻🇨", "Saint Vincent and the Grenadines"),
    "685": ("WS", "🇼🇸", "Samoa"),
    "378": ("SM", "🇸🇲", "San Marino"),
    "239": ("ST", "🇸🇹", "Sao Tome and Principe"),
    "966": ("SA", "🇸🇦", "Saudi Arabia"),
    "221": ("SN", "🇸🇳", "Senegal"),
    "381": ("RS", "🇷🇸", "Serbia"),
    "248": ("SC", "🇸🇨", "Seychelles"),
    "232": ("SL", "🇸🇱", "Sierra Leone"),
    "65": ("SG", "🇸🇬", "Singapore"),
    "1721": ("SX", "🇸🇽", "Sint Maarten"),
    "421": ("SK", "🇸🇰", "Slovakia"),
    "386": ("SI", "🇸🇮", "Slovenia"),
    "677": ("SB", "🇸🇧", "Solomon Islands"),
    "252": ("SO", "🇸🇴", "Somalia"),
    "27": ("ZA", "🇿🇦", "South Africa"),
    "82": ("KR", "🇰🇷", "South Korea"),
    "211": ("SS", "🇸🇸", "South Sudan"),
    "34": ("ES", "🇪🇸", "Spain"),
    "94": ("LK", "🇱🇰", "Sri Lanka"),
    "249": ("SD", "🇸🇩", "Sudan"),
    "597": ("SR", "🇸🇷", "Suriname"),
    "46": ("SE", "🇸🇪", "Sweden"),
    "41": ("CH", "🇨🇭", "Switzerland"),
    "963": ("SY", "🇸🇾", "Syria"),
    "886": ("TW", "🇹🇼", "Taiwan"),
    "992": ("TJ", "🇹🇯", "Tajikistan"),
    "255": ("TZ", "🇹🇿", "Tanzania"),
    "66": ("TH", "🇹🇭", "Thailand"),
    "228": ("TG", "🇹🇬", "Togo"),
    "690": ("TK", "🇹🇰", "Tokelau"),
    "676": ("TO", "🇹🇴", "Tonga"),
    "1868": ("TT", "🇹🇹", "Trinidad and Tobago"),
    "216": ("TN", "🇹🇳", "Tunisia"),
    "90": ("TR", "🇹🇷", "Turkey"),
    "993": ("TM", "🇹🇲", "Turkmenistan"),
    "1649": ("TC", "🇹🇨", "Turks and Caicos"),
    "688": ("TV", "🇹🇻", "Tuvalu"),
    "971": ("AE", "🇦🇪", "UAE"),
    "1340": ("VI", "🇻🇮", "U.S. Virgin Islands"),
    "256": ("UG", "🇺🇬", "Uganda"),
    "380": ("UA", "🇺🇦", "Ukraine"),
    "44": ("GB", "🇬🇧", "United Kingdom"),
    "1": ("US", "🇺🇸", "United States"),
    "598": ("UY", "🇺🇾", "Uruguay"),
    "998": ("UZ", "🇺🇿", "Uzbekistan"),
    "678": ("VU", "🇻🇺", "Vanuatu"),
    "58": ("VE", "🇻🇪", "Venezuela"),
    "84": ("VN", "🇻🇳", "Vietnam"),
    "681": ("WF", "🇼🇫", "Wallis and Futuna"),
    "967": ("YE", "🇾🇪", "Yemen"),
    "260": ("ZM", "🇿🇲", "Zambia"),
    "263": ("ZW", "🇿🇼", "Zimbabwe"),
}


ISO_TO_INFO = {}
for code, val in COUNTRY_CODE_MAP.items():
    if isinstance(val, tuple) and len(val) >= 3:
        ISO_TO_INFO[val[0]] = (val[1], val[2])

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

# ==================== RICH MESSAGE GROUP OTP (FIXED) ====================

def format_group_otp_rich(entry):
    number = entry.get("number", "")
    otp_code = entry.get("otp", "")
    service_name = entry.get("service", "Unknown")
    country_raw = entry.get("country", entry.get("country_code", "?"))
    country_iso = entry.get("country_code", "")
    if not country_iso and country_raw:
        country_iso = get_country_code(country_raw) or "??"
    
    # ---- COUNTRY EMOJI: priority: manual override (group_emojis) -> country data -> default ----
    country_emoji_id = None
    # 1) Check group_emojis (manual override)
    if country_iso:
        row = db_fetch_one("SELECT emoji_id FROM group_emojis WHERE type='country' AND key=?", (country_iso.upper(),))
        if not row:
            row = db_fetch_one("SELECT emoji_id FROM group_emojis WHERE type='country' AND key=?", (country_iso.lower(),))
        if row and row[0]:
            country_emoji_id = row[0]
    # 2) If not, get from country data (countries.json) via ISO or name
    if not country_emoji_id:
        # try to get country name from ISO
        country_name_from_iso = get_country_name_by_iso(country_iso) if country_iso else None
        if country_name_from_iso:
            country_info = get_country_info(country_name_from_iso)
            if country_info.get("emoji_id"):
                country_emoji_id = country_info["emoji_id"]
        elif country_raw and country_raw not in ["?", "??"]:
            # if we have country name directly (maybe from entry)
            country_info = get_country_info(country_raw)
            if country_info.get("emoji_id"):
                country_emoji_id = country_info["emoji_id"]
    # 3) Fallback to DEFAULT_EMOJIS
    if not country_emoji_id and country_iso and country_iso.lower() in DEFAULT_EMOJIS["countries"]:
        country_emoji_id = DEFAULT_EMOJIS["countries"][country_iso.lower()]
    
    flag_fallback = ISO_TO_INFO.get(country_iso, ("🏳", ""))[0] if country_iso else "🏳"
    if country_emoji_id:
        country_display = f'<tg-emoji emoji-id="{country_emoji_id}">{flag_fallback}</tg-emoji><b>{country_iso}</b>'
    else:
        country_display = f'{flag_fallback}<b>{country_iso}</b>'
    
    # ---- SERVICE EMOJI: priority: group_emojis (manual override) -> services table -> default ----
    service_emoji_id = None
    # 1) Check group_emojis (manual override)
    svc_row = db_fetch_one("SELECT emoji_id FROM group_emojis WHERE type='service' AND LOWER(key)=LOWER(?)", (service_name,))
    if svc_row and svc_row[0]:
        service_emoji_id = svc_row[0]
    else:
        # 2) Check services table
        svc_row = db_fetch_one("SELECT emoji_id FROM services WHERE LOWER(name) = LOWER(?)", (service_name,))
        if svc_row and svc_row[0]:
            service_emoji_id = svc_row[0]
    # 3) Default
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

# ==================== GLOBAL HELPER FOR INLINE KEYBOARD FROM DICT ====================
def build_inline_keyboard(keyboard_dict):
    rows = []
    for row in keyboard_dict.get("inline_keyboard", []):
        buttons = []
        for btn in row:
            kwargs = {"text": btn.get("text", "")}
            if "url" in btn:
                kwargs["url"] = btn["url"]
            if "callback_data" in btn:
                kwargs["callback_data"] = btn["callback_data"]
            if "copy_text" in btn:
                kwargs["copy_text"] = CopyTextButton(text=btn["copy_text"]["text"])
            buttons.append(InlineKeyboardButton(**kwargs))
        rows.append(buttons)
    return InlineKeyboardMarkup(rows)

# ==================== OTP PROCESSING (FIXED - MULTI-GROUP, SENDS TO ALL GROUPS VIA sendRichMessage) ====================

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
    """Process OTPs: send to multiple groups (using sendRichMessage) and to users.
       Returns count of new OTPs processed."""
    if context:
        bot = context.bot
    if not bot:
        if application and application.bot:
            bot = application.bot
        else:
            print("❌ process_otps: No bot instance!")
            return 0
    
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    active_rows = db_fetch_all(
        "SELECT number, user_id, country, assigned_date FROM numbers WHERE status='active' AND expiry_time > ?",
        (now_str,))
    
    num_map = {}
    for num, uid, country, assigned in active_rows:
        clean = num.replace('+', '')
        num_map.setdefault(clean, []).append((uid, country, assigned))
    
    # Use global GROUP_IDS list
    group_ids = GROUP_IDS

    semaphore = asyncio.Semaphore(50)  # concurrency increased
    new_otp_count = 0

    async def safe_send_message(chat_id, text, reply_markup=None, parse_mode='HTML'):
        async with semaphore:
            try:
                await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
            except Exception as e:
                print(f"Failed to send to {chat_id}: {e}")

    async def process_single_otp(otp_entry):
        nonlocal new_otp_count
        number = otp_entry.get("number", "")
        message = otp_entry.get("message", "")
        service_name = otp_entry.get("service", "Unknown")
        otp_timestamp_str = otp_entry.get("timestamp", now_str)
        
        if not otp_entry.get('country'):
            country = get_country_from_number(number)
            if country:
                otp_entry['country'] = country
        
        # --- NEW: Extract OTP using the universal detector ---
        otp_code = extract_otp_from_message(message)  # returns None if not found
        if otp_code is None:
            # If still no OTP, try to get from entry (maybe API gave explicit field)
            otp_code = otp_entry.get("otp", "")
            if not otp_code:
                # Final fallback: set to "N/A"
                otp_code = "N/A"
        else:
            # OTP found, use it
            pass
        
        # If we got "N/A", we still proceed but with N/A.
        if not number:
            return 0  # skip if no number

        existing = db_fetch_one("SELECT id FROM otps WHERE number=? AND otp=? AND (user_id=0 OR user_id>0)", (number, otp_code))
        is_new = existing is None

        # Send to groups (if new) - using sendRichMessage
        if is_new and group_ids:
            # Only insert if OTP is not "N/A"? Actually we want to insert even if N/A? We'll insert with OTP = N/A
            db_exec("INSERT INTO otps (number, otp, message, timestamp, forwarded, user_id) VALUES (?,?,?,?,1,0)",
                    (number, otp_code, message, otp_timestamp_str))
            try:
                grp_html, grp_kb_dict = format_group_otp_rich({
                    "number": number,
                    "otp": otp_code,
                    "service": service_name,
                    "country_code": otp_entry.get("country_code", ""),
                    "country": otp_entry.get("country", ""),
                    "message": message
                })
                # Send to each group using sendRichMessage (custom endpoint)
                for gid in group_ids:
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendRichMessage"
                    payload = {
                        "chat_id": gid,
                        "rich_message": {"html": grp_html},
                        "reply_markup": grp_kb_dict
                    }
                    requests.post(url, json=payload, timeout=10)
            except Exception as e:
                print(f"Group Rich message failed: {e}")

        # Send to users (via bot.send_message)
        clean_number = number.replace('+', '')
        local_tasks = []
        if clean_number in num_map:
            try:
                otp_timestamp = datetime.strptime(otp_timestamp_str, "%Y-%m-%d %H:%M:%S")
            except:
                otp_timestamp = now
            
            for uid, country, assigned_date_str in num_map[clean_number]:
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
                user_otp_exists = db_fetch_one("SELECT id FROM otps WHERE number=? AND otp=? AND user_id=?", (number, otp_code, uid))
                if user_otp_exists:
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
                    f'<blockquote>{emoji_tag("5278576134622056695", "🆕")} <b>NEW</b> '
                    f'{emoji_tag(flag_eid, "🏁")}<b>{country_iso} OTP ARRIVED</b> '
                    f'{emoji_tag("6100453534422013617", "✨")}</blockquote>\n'
                    f'{emoji_tag("6204108584381322968", "📱")} <b>NUMBER</b>: <code>+{number}</code>\n'
                    f'{emoji_tag("5976327845696251345", "📲")} <b>APP</b>: {emoji_tag(svc_eid, "⚙️")} <b>{service_name}</b>\n'
                    f'💰 <b>BALANCE ADDED</b>: <code>+${reward}</code>{emoji_tag("5976788549658221281", "💵")}'
                )
                button = InlineKeyboardMarkup([[
                    InlineKeyboardButton(text=otp_code, copy_text=CopyTextButton(text=otp_code),
                                         style=KBS.SUCCESS, icon_custom_emoji_id=safe_icon("5330115548900501467"))
                ]])
                local_tasks.append(safe_send_message(uid, header, button))
        
        if local_tasks:
            await asyncio.gather(*local_tasks)
        
        return 1 if is_new else 0

    # Process all OTPs in parallel
    tasks = [process_single_otp(otp) for otp in otps_list]
    results = await asyncio.gather(*tasks)
    new_otp_count = sum(results)

    save_user_data_json()
    return new_otp_count

# ==================== RESPONSE PARSER (FIXED) ====================

class ResponseParser:
    @staticmethod
    def _get_json_path(data, path, default=None):
        if not path:
            return data
        parts = path.split('.')
        current = data
        for part in parts:
            if part.isdigit():
                try:
                    idx = int(part)
                    if isinstance(current, list) and idx < len(current):
                        current = current[idx]
                    else:
                        return default
                except:
                    return default
            elif isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    found = False
                    for key in current:
                        if key.lower() == part.lower():
                            current = current[key]
                            found = True
                            break
                    if not found:
                        return default
            else:
                return default
        return current if current is not None else default

    @staticmethod
    def parse_json_response(content: dict, config: dict) -> list[dict]:
        otp_list_path = config.get('otp_list_path', 'data')
        if not otp_list_path:
            data = content
        else:
            data = ResponseParser._get_json_path(content, otp_list_path)
        
        if data is None:
            for key, value in content.items():
                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    data = value
                    break
            if data is None:
                return []
        
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            return []
        
        result = []
        number_path = config.get('number_path')
        message_path = config.get('message_path')
        service_path = config.get('service_path')
        timestamp_path = config.get('timestamp_path')
        country_path = config.get('country_path')
        
        for item in data:
            if not isinstance(item, dict):
                continue
            
            entry = {}
            if number_path:
                entry["number"] = ResponseParser._get_json_path(item, number_path, "")
            if message_path:
                entry["message"] = ResponseParser._get_json_path(item, message_path, "")
            else:
                # If no message_path, try to find a long string field
                for key, value in item.items():
                    if isinstance(value, str) and len(value) > 10:
                        entry["message"] = value
                        break
            if service_path:
                entry["service"] = ResponseParser._get_json_path(item, service_path, "")
            if timestamp_path:
                entry["timestamp"] = ResponseParser._get_json_path(item, timestamp_path, "")
            if country_path:
                entry["country"] = ResponseParser._get_json_path(item, country_path, "")
            
            # If we have a message but no explicit OTP, try to extract OTP
            if "message" in entry and entry["message"]:
                otp = extract_otp_from_message(entry["message"])
                if otp:
                    entry["otp"] = otp
            # If we still don't have an OTP, we might get it from a field named "otp" or "code"
            if "otp" not in entry:
                # Try to find an OTP field in item
                for key in ["otp", "code", "pin", "password"]:
                    if key in item and item[key]:
                        entry["otp"] = str(item[key])
                        break
            
            entry = {k: v for k, v in entry.items() if v}
            if entry.get("number") or entry.get("otp"):
                result.append(entry)
        
        return result

    @staticmethod
    def parse_response(content, config: dict) -> list[dict]:
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                # If not JSON, use the universal extractor on raw text
                otps = extract_all_otps_from_message(content)
                # Build entries for each potential OTP
                if otps:
                    return [{"message": content[:200], "otp": otp} for otp in otps]
                else:
                    return [{"message": content[:200], "otp": "N/A"}]
        if isinstance(content, dict):
            return ResponseParser.parse_json_response(content, config)
        return []

# ==================== GET API CONFIG ====================

def get_country_from_number(number: str) -> str | None:
    if not number:
        return None
    clean = number.replace('+', '').replace(' ', '').strip()
    for code in sorted(COUNTRY_CODE_MAP.keys(), key=len, reverse=True):
        if clean.startswith(code):
            return COUNTRY_CODE_MAP[code][2]
    return None

def get_api_config(api_id: int) -> dict | None:
    row = db_fetch_one("""
        SELECT id, panel_name, base_url, token, interval_sec, active,
               endpoint, method, headers, body_template, response_type,
               otp_list_path, number_path, message_path, country_path,
               service_path, timestamp_path, success_path, success_value,
               max_records, retry_count, retry_delay, error_count, last_poll_time,
               total_otps, last_otp_time, placeholder_config, curl_command
        FROM api_keys WHERE id = ?
    """, (api_id,))
    if not row:
        return None
    cols = ['id','panel_name','base_url','token','interval_sec','active',
            'endpoint','method','headers','body_template','response_type',
            'otp_list_path','number_path','message_path','country_path',
            'service_path','timestamp_path','success_path','success_value',
            'max_records','retry_count','retry_delay','error_count','last_poll_time',
            'total_otps','last_otp_time','placeholder_config','curl_command']
    return dict(zip(cols, row))

# ==================== GENERIC TEXT HANDLER ====================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if await handle_admin_text(update, context): return
    if await handle_api_add_text(update, context): return
    if await handle_edit_value_text(update, context): return

    user_id = update.effective_user.id
    if await ban_check(update, context): return
    text = update.message.text.strip()

    if text == BTN_GET_NUMBER: await send_get_number_panel(update, context)
    elif text == BTN_BALANCE: await send_balance_panel(update, context)
    elif text == BTN_SUPPORT: await send_support_panel(update, context)
    elif text == BTN_ADMIN: await send_admin_panel_msg(update, context)

async def handle_edit_value_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = admin_panel_state.get(user_id)
    if not state or not state.startswith("api_edit_value_"):
        return False

    api_id = int(state.split("_")[-1])
    data = admin_temp_data.get(user_id, {})
    field = data.get("field")
    if not field:
        await update.message.reply_text("Session expired. Please start over.")
        return True

    new_value = update.message.text.strip()
    if new_value.lower() == "/cancel":
        await api_edit_menu(update, context, api_id, user_id)
        return True

    if field in ["interval_sec", "max_records", "retry_count"]:
        try:
            new_value = int(new_value)
            if field == "interval_sec" and new_value < 1:
                await update.message.reply_text("Interval must be at least 1 second.")
                return True
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")
            return True
    elif field == "method":
        if new_value.upper() not in ["GET", "POST", "PUT", "DELETE"]:
            await update.message.reply_text("Method must be GET, POST, PUT, or DELETE.")
            return True
    elif field == "base_url":
        if not new_value.startswith(("http://", "https://")):
            await update.message.reply_text("Base URL must start with http:// or https://")
            return True
    elif field == "placeholder_config":
        try:
            new_value = json.loads(new_value)
            db_exec(f"UPDATE api_keys SET {field} = ? WHERE id = ?", (json.dumps(new_value), api_id))
        except:
            try:
                parts = [p.strip() for p in new_value.split(',')]
                new_placeholders = {}
                for part in parts:
                    if '=' in part:
                        k, v = part.split('=', 1)
                        new_placeholders[k.strip()] = v.strip()
                db_exec(f"UPDATE api_keys SET {field} = ? WHERE id = ?", (json.dumps(new_placeholders), api_id))
            except:
                await update.message.reply_text("Invalid format. Use JSON or key1=value1,key2=value2")
                return True
        admin_temp_data.pop(user_id, None)
        admin_panel_state[user_id] = "main"
        await update.message.reply_text(f"✅ {field} updated successfully!")
        await api_detail_page(update, context, api_id, user_id)
        return True

    db_exec(f"UPDATE api_keys SET {field} = ? WHERE id = ?", (new_value, api_id))
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await update.message.reply_text(f"✅ {field} updated successfully!")
    await api_detail_page(update, context, api_id, user_id)
    return True

# ==================== ERROR HANDLER ====================

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
    application.add_handler(CommandHandler("setcountry", set_country_command))
    application.add_handler(CommandHandler("setservice", set_service_command))
    application.add_handler(CommandHandler("testgroup", testgroup_command))

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

    application.add_handler(CallbackQueryHandler(stock_management_menu, pattern="^admin_stock_management$"))
    application.add_handler(CallbackQueryHandler(stock_upload_callback, pattern="^stock_upload$"))
    application.add_handler(CallbackQueryHandler(stock_remove_callback, pattern="^stock_remove$"))
    application.add_handler(CallbackQueryHandler(stock_remove_confirm_callback, pattern=r"^stock_remove_confirm\|"))
    application.add_handler(CallbackQueryHandler(stock_remove_yes_callback, pattern=r"^stock_remove_yes\|"))
    application.add_handler(CallbackQueryHandler(stock_remove_no_callback, pattern="^stock_remove_no$"))
    application.add_handler(CallbackQueryHandler(stock_status_callback, pattern="^stock_status$"))
    application.add_handler(CallbackQueryHandler(stock_toggle_callback, pattern="^stock_toggle$"))
    application.add_handler(CallbackQueryHandler(stock_toggle_do_callback, pattern=r"^stock_toggle_do\|"))
    application.add_handler(CallbackQueryHandler(stock_get_number_callback, pattern=r"^stock_get_number\|"))

    # API Management
    application.add_handler(CallbackQueryHandler(manage_api_menu_wrapper, pattern="^admin_manage_api$"))
    application.add_handler(CallbackQueryHandler(api_add_start_wrapper, pattern="^api_add$"))
    application.add_handler(CallbackQueryHandler(handle_api_add_skip, pattern="^api_add_skip$"))
    application.add_handler(CallbackQueryHandler(handle_api_add_cancel, pattern="^api_add_cancel$"))
    application.add_handler(CallbackQueryHandler(api_add_confirm_yes, pattern=r"^api_add_confirm_yes\|"))
    application.add_handler(CallbackQueryHandler(api_add_confirm_no, pattern=r"^api_add_confirm_no\|"))
    application.add_handler(CallbackQueryHandler(api_add_edit, pattern=r"^api_add_edit\|"))
    application.add_handler(CallbackQueryHandler(api_system_grid_wrapper, pattern="^api_system$"))
    application.add_handler(CallbackQueryHandler(api_detail_page_wrapper, pattern=r"^api_detail\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_toggle_callback, pattern=r"^api_toggle\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_edit_menu_wrapper, pattern=r"^api_edit\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_edit_field_prompt, pattern=r"^api_edit_field\|(\d+)\|(.+)$"))
    application.add_handler(CallbackQueryHandler(api_test_callback, pattern=r"^api_test\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_stats_callback, pattern=r"^api_stats\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_logs_callback, pattern=r"^api_logs\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_delete_prompt, pattern=r"^api_delete\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_delete_confirm, pattern=r"^api_delete_(yes|no)\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_force_poll, pattern=r"^api_force\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_list_wrapper, pattern="^api_list$"))
    # CURL confirmation buttons
    application.add_handler(CallbackQueryHandler(api_add_curl_continue, pattern="^api_add_curl_continue$"))
    application.add_handler(CallbackQueryHandler(api_add_curl_cancel, pattern="^api_add_curl_cancel$"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_error_handler(error_handler)

    if application.job_queue:
        application.job_queue.run_repeating(periodic_json_save, interval=60, first=10)

    async def start_api_tasks(app):
        print("🚀 Starting added API polling tasks...")
        await start_all_polling()

    application.post_init = start_api_tasks

    save_user_data_json()
    print(f"✅ Super Admins: {SUPER_ADMIN_IDS}")
    print("✅ Full bot started with Multi-API System and Country Map.")
    print("🔄 Starting polling...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
