# bot.py — SR NUMBER HUB (Full Original + New API System)
# Part 1/2 — All existing functionality + modifications up to new API system

import asyncio, json, os, re, sqlite3, threading, tempfile, zipfile, shutil
from datetime import datetime, timedelta
import random
from typing import Any, List, Dict, Optional

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

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8789807943:AAHae96lsddEva4nvB3LdEyJAS_q_0L06Yc"
SUPER_ADMIN_IDS = [8744359777]

AUTO_DELETE_DELAY = 2          # seconds (for normal messages)
MAIN_MENU_DELETE = 120         # 2 minutes

OTP_GROUP_URL = "https://t.me/NumberFlexOTP"
MIN_WITHDRAW = 0.1

ADMIN_WHATSAPP = "https://wa.me/8801962636806"
ADMIN_TELEGRAM = "t.me/SR_ADMIN_RAKESH"
ADMIN2_WHATSAPP = ""
ADMIN2_TELEGRAM = ""

GROUP_ID = -1003716770621
CHANNEL_URL = "https://t.me/WaCreationHub"
BOT_URL = "https://t.me/WA_CREATION_BOT"

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

# ==================== CUSTOM EMOJIS (FULL SET WITH NEW API ONES) ====================
CUSTOM_EMOJIS = {
    "USER_MANAGER": "6307777408300753473",
    "SEARCH_USER": "6206446249181189526",
    "DOWNLOAD_LIST": "6203886371363364022",
    "EDIT_BALANCE": "6204162490515855272",
    "BAN_USER": "6203761490894264678",
    "MANAGE_API": "6206188632747808299",
    "ADD_API_KEY": "6206375377925839184",
    "REMOVE_API_KEY": "6206108815075579644",
    "LIST_API_KEY": "6307686831735444755",
    "SUPPORT": SUPPORT_EMOJI,
    "SELECT_SERVICE_PREFIX": "6206236607532504295",
    "SELECT_SERVICE_SUFFIX": "5197474438970363734",
    "SELECT_COUNTRY_PREFIX": "5309748255637118475",
    "PROFILE_ICON": "5818715087237549366",
    "STOCK_MANAGER": "6206236607532504295",
    "REMOVE_STOCK": "4958534924278694938",
    "STOCK_STATUS": "4958506272551863292",
    "TOGGLE_STOCK": "4956583802240500602",
    "YES": "4956721670690702265",
    "NO": "6206110936789423908",
    "GET_NUMBER": "5303449763406954093",
    "NEW_NUMBER": "5877410604225924969",
    "BACK": "6068830682359010545",
    "DELETE": "6203761490894264678",
    "BROADCAST": "6203886371363364022",
    "COUNTRY_MANAGER": "5188540541922480562",
    "SERVICE_MANAGER": "5465590345108589516",
    "GIVEAWAY": "6282893896796082998",
    "STATS": "6266936886405633043",
    "PACKAGE": "5463412319948148591",
    "GEAR": "6206236607532504295",
    "CHANGE_COUNTRY": "5188540541922480562",
    "GREEN_CIRCLE": "5339112148175959615",
    "RED_CIRCLE": "5337017423906226569",
    "CLOCK": "6267229004311303657",
    "ADD": "6206375377925839184",
    "CANCEL": "6206003549722122915",
    "DEFAULT_FLAG": "5188540541922480562",
    "DEFAULT_SERVICE": "5465590345108589516",
    "JOIN_OTP_GROUP": "6204010762206189094",
    "ADMIN": "6206188632747808299",

    # ---- NEW API SYSTEM EMOJIS ----
    "API_SYSTEM": "6271486270384378674",
    "API_STATUS_ACTIVE": "5339112148175959615",
    "API_STATUS_INACTIVE": "5337017423906226569",
    "API_START_POLL": "6267264360482084046",
    "API_STOP_POLL": "6266797059450347770",
    "API_FORCE_POLL": "6282893896796082998",
    "API_TEST": "5978568938156461643",
    "API_STATS": "6266936886405633043",
    "API_LOGS": "5818774589714468177",
    "API_FIELD_NAME": "5818775306974006843",
    "API_FIELD_URL": "6285048454255220485",
    "API_FIELD_ENDPOINT": "6267172559851099903",
    "API_FIELD_TOKEN": "5821453562680448557",
    "API_FIELD_METHOD": "5926860096008098405",
    "API_FIELD_INTERVAL": "6093456762113888541",
    "API_FIELD_RECORDS": "5868569066154757449",
    "API_FIELD_RETRY": "5978846612087114958",
    "API_FIELD_OTP_PATH": "5818955300463447293",
    "API_FIELD_NUMBER": "5877410604225924969",
    "API_FIELD_MESSAGE": "5980911993140284450",
    "API_FIELD_COUNTRY": "5188381825701021648",
    "API_FIELD_SERVICE": "5818967150278218011",
    "API_FIELD_TIMESTAMP": "6285240160120477644",
    "API_FIELD_SUCCESS_PATH": "6267008582294705964",
    "API_FIELD_SUCCESS_VALUE": "6267039884016358504",
    "API_TODAY_OTP": "6224129999633388168",
    "API_TOTAL_OTP": "6266794310671275367",
    "API_LAST_POLL": "6267229004311303657",
    "API_ERROR_COUNT": "6267039884016358504",
    "API_SUCCESS_RATE": "6267058648728474885",
    "API_OTP_COUNT": "5978854270013804830",
    "API_BLOCK_START": "5947029782121155470",
    "API_BLOCK_END": "5947216621788465862",
    "API_SEPARATOR": "5870818207383686839",
}

# ==================== COUNTRY CODE MAP (abbreviated, you can add full) ====================
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
    "247": ("AC", "🇦🇨", "Ascension Island"),
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
    "238": ("CV", "🇨🇻", "Cabo Verde"),
    "855": ("KH", "🇰🇭", "Cambodia"),
    "237": ("CM", "🇨🇲", "Cameroon"),
    "1": ("US", "🇺🇸", "United States"),
    "238": ("CV", "🇨🇻", "Cape Verde"),
    "599": ("BQ", "🇧🇶", "Caribbean Netherlands"),
    "1345": ("KY", "🇰🇾", "Cayman Islands"),
    "236": ("CF", "🇨🇫", "Central African Republic"),
    "235": ("TD", "🇹🇩", "Chad"),
    "56": ("CL", "🇨🇱", "Chile"),
    "86": ("CN", "🇨🇳", "China"),
    "57": ("CO", "🇨🇴", "Colombia"),
    "269": ("KM", "🇰🇲", "Comoros"),
    "242": ("CG", "🇨🇬", "Republic of the Congo"),
    "243": ("CD", "🇨🇩", "Democratic Republic of the Congo"),
    "682": ("CK", "🇨🇰", "Cook Islands"),
    "506": ("CR", "🇨🇷", "Costa Rica"),
    "225": ("CI", "🇨🇮", "Côte d'Ivoire"),
    "385": ("HR", "🇭🇷", "Croatia"),
    "53": ("CU", "🇨🇺", "Cuba"),
    "5999": ("CW", "🇨🇼", "Curaçao"),
    "357": ("CY", "🇨🇾", "Cyprus"),
    "420": ("CZ", "🇨🇿", "Czechia"),
    "45": ("DK", "🇩🇰", "Denmark"),
    "253": ("DJ", "🇩🇯", "Djibouti"),
    "1767": ("DM", "🇩🇲", "Dominica"),
    "1809": ("DO", "🇩🇴", "Dominican Republic"),
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
    "44": ("GG", "🇬🇬", "Guernsey"),
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
    "1876": ("JM", "🇯🇲", "Jamaica"),
    "81": ("JP", "🇯🇵", "Japan"),
    "44": ("JE", "🇯🇪", "Jersey"),
    "962": ("JO", "🇯🇴", "Jordan"),
    "7": ("RU", "🇷🇺", "Russia"),
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
    "262": ("YT", "🇾🇹", "Mayotte"),
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
    "262": ("RE", "🇷🇪", "Réunion"),
    "40": ("RO", "🇷🇴", "Romania"),
    "250": ("RW", "🇷🇼", "Rwanda"),
    "290": ("SH", "🇸🇭", "Saint Helena"),
    "1869": ("KN", "🇰🇳", "Saint Kitts and Nevis"),
    "1758": ("LC", "🇱🇨", "Saint Lucia"),
    "508": ("PM", "🇵🇲", "Saint Pierre and Miquelon"),
    "1784": ("VC", "🇻🇨", "Saint Vincent and the Grenadines"),
    "685": ("WS", "🇼🇸", "Samoa"),
    "378": ("SM", "🇸🇲", "San Marino"),
    "239": ("ST", "🇸🇹", "São Tomé and Príncipe"),
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
    "670": ("TL", "🇹🇱", "Timor-Leste"),
    "228": ("TG", "🇹🇬", "Togo"),
    "690": ("TK", "🇹🇰", "Tokelau"),
    "676": ("TO", "🇹🇴", "Tonga"),
    "1868": ("TT", "🇹🇹", "Trinidad and Tobago"),
    "216": ("TN", "🇹🇳", "Tunisia"),
    "90": ("TR", "🇹🇷", "Türkiye"),
    "993": ("TM", "🇹🇲", "Turkmenistan"),
    "1649": ("TC", "🇹🇨", "Turks and Caicos Islands"),
    "688": ("TV", "🇹🇻", "Tuvalu"),
    "256": ("UG", "🇺🇬", "Uganda"),
    "380": ("UA", "🇺🇦", "Ukraine"),
    "971": ("AE", "🇦🇪", "United Arab Emirates"),
    "44": ("GB", "🇬🇧", "United Kingdom"),
    "598": ("UY", "🇺🇾", "Uruguay"),
    "998": ("UZ", "🇺🇿", "Uzbekistan"),
    "678": ("VU", "🇻🇺", "Vanuatu"),
    "379": ("VA", "🇻🇦", "Vatican City"),
    "58": ("VE", "🇻🇪", "Venezuela"),
    "84": ("VN", "🇻🇳", "Vietnam"),
    "1340": ("VI", "🇻🇮", "U.S. Virgin Islands"),
    "681": ("WF", "🇼🇫", "Wallis and Futuna"),
    "967": ("YE", "🇾🇪", "Yemen"),
    "260": ("ZM", "🇿🇲", "Zambia"),
    "263": ("ZW", "🇿🇼", "Zimbabwe"),
}
ISO_TO_INFO = {v[0]: (v[1], v[2]) for v in COUNTRY_CODE_MAP.values()}

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

# ---- NEW API TABLES ----
c.execute('''CREATE TABLE IF NOT EXISTS api_keys
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              panel_name TEXT,
              base_url TEXT,
              token TEXT,
              interval_sec INTEGER,
              active INTEGER DEFAULT 1,
              endpoint TEXT DEFAULT '/all_otp',
              method TEXT DEFAULT 'GET',
              headers TEXT,
              body_template TEXT,
              response_type TEXT DEFAULT 'json',
              otp_list_path TEXT DEFAULT 'data.otps',
              number_path TEXT DEFAULT 'number',
              message_path TEXT DEFAULT 'message',
              country_path TEXT DEFAULT 'country',
              service_path TEXT DEFAULT 'service',
              timestamp_path TEXT DEFAULT 'timestamp',
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
              updated_at TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS api_logs
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              api_id INTEGER,
              timestamp TEXT,
              status TEXT,
              message TEXT,
              otp_count INTEGER)''')

# Add missing columns for compatibility
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
    c.execute("ALTER TABLE users ADD COLUMN keyboard_message_id INTEGER DEFAULT NULL")
except sqlite3.OperationalError: pass
try:
    c.execute("ALTER TABLE services ADD COLUMN emoji_id TEXT DEFAULT ''")
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
polling_tasks = {}          # NEW: for API polling tasks

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

# ==================== EMOJI HELPERS ====================
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

# ==================== DB HELPERS ====================
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

# -------------------- OTP EXTRACTION --------------------
def extract_otp_from_message(message: str) -> str | None:
    if not message:
        return None
    patterns = [
        r'(?:otp|code|verification|pin|passcode|auth|security|two[- ]factor|sms)\s*[:=]?\s*(\d{3,4}[-.\s]?\d{3,4})',
        r'(?:otp|code|verification|pin|passcode|auth|security|two[- ]factor|sms)\s+is\s+(\d{3,4}[-.\s]?\d{3,4})',
        r'(?:otp|code|verification|pin|passcode|auth|security|two[- ]factor|sms)\s+(\d{3,4}[-.\s]?\d{3,4})',
        r'(?:ওটিপি|ভেরিফিকেশন|পিন|কোড)\s*[:=]?\s*(\d{3,4}[-.\s]?\d{3,4})',
        r'(?:ओटीपी|कोड|पिन|सत्यापन)\s*[:=]?\s*(\d{3,4}[-.\s]?\d{3,4})',
        r'(?:código|verificación|pin|clave)\s*[:=]?\s*(\d{3,4}[-.\s]?\d{3,4})',
        r'(?:رمز|التحقق|كلمة المرور|OTP)\s*[:=]?\s*(\d{3,4}[-.\s]?\d{3,4})',
        r'(?:code|vérification|pin|mot de passe)\s*[:=]?\s*(\d{3,4}[-.\s]?\d{3,4})',
        r'(?:Code|Bestätigung|PIN|Sicherheit)\s*[:=]?\s*(\d{3,4}[-.\s]?\d{3,4})',
        r'\b(\d{3,4}[-.\s]?\d{3,4})\b',
        r'\[(\d{4,6})\]',
        r'\((\d{4,6})\)',
        r'\b(\d\s\d\s\d\s\d\s\d\s\d)\b',
        r'\b(\d\s\d\s\d\s\d)\b',
        r'\b(\d{4,6})\b',
        r'\b([A-Z0-9]{4,8})\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            otp = match.group(1)
            otp_clean = re.sub(r'[-\s.]', '', otp)
            if 4 <= len(otp_clean) <= 8:
                if len(otp_clean) == 4 and otp_clean.startswith(('19', '20')):
                    continue
                return otp_clean
    numbers = re.findall(r'\b(\d{4,6})\b', message)
    for num in numbers:
        if num.startswith(('19', '20')) and len(num) == 4:
            continue
        return num
    return None

def extract_all_otps_from_message(message: str) -> list[str]:
    if not message:
        return []
    otps = []
    numbers = re.findall(r'\b(\d{4,6})\b', message)
    for num in numbers:
        if num.startswith(('19', '20')) and len(num) == 4:
            continue
        if num not in otps:
            otps.append(num)
    hyphen = re.findall(r'\b(\d{3,4}-\d{3,4})\b', message)
    for h in hyphen:
        clean = h.replace('-', '')
        if 4 <= len(clean) <= 6 and clean not in otps:
            otps.append(clean)
    return otps

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

async def send_clean_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None, parse_mode=None, auto_delete: bool = True, persistent_menu: bool = True, delete_after: int = None):
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
    if auto_delete and reply_markup is None:
        await schedule_delete(context, user_id, sent.message_id)
    elif delete_after:
        await schedule_delete(context, user_id, sent.message_id, delete_after)
    return sent

async def edit_or_send(query: CallbackQuery, text: str, reply_markup=None, parse_mode=None, context: ContextTypes.DEFAULT_TYPE = None, auto_delete: bool = True, persistent_menu: bool = False, delete_after: int = None):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        if auto_delete and context and reply_markup is None:
            await schedule_delete(context, query.message.chat_id, query.message.message_id)
        elif delete_after:
            await schedule_delete(context, query.message.chat_id, query.message.message_id, delete_after)
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
            elif delete_after:
                await schedule_delete(context, query.message.chat_id, sent.message_id, delete_after)
            return sent
        return None

async def reply_or_edit(target, text: str, reply_markup=None, parse_mode=None, context: ContextTypes.DEFAULT_TYPE = None, auto_delete: bool = True, persistent_menu: bool = False, delete_after: int = None):
    if isinstance(target, CallbackQuery):
        await edit_or_send(target, text, reply_markup=reply_markup, parse_mode=parse_mode, context=context, auto_delete=auto_delete, persistent_menu=persistent_menu, delete_after=delete_after)
    elif hasattr(target, 'callback_query') and target.callback_query:
        await edit_or_send(target.callback_query, text, reply_markup=reply_markup, parse_mode=parse_mode, context=context, auto_delete=auto_delete, persistent_menu=persistent_menu, delete_after=delete_after)
    else:
        if context:
            await send_clean_message(target, context, text, reply_markup=reply_markup, parse_mode=parse_mode, auto_delete=auto_delete, persistent_menu=persistent_menu, delete_after=delete_after)
        else:
            if hasattr(target, 'message') and target.message:
                await target.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)

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

# ---- MODIFIED admin_panel_keyboard with API SYSTEM button ----
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
                                 icon_custom_emoji_id=safe_icon("6206236607532504295")),
        ],
        [
            InlineKeyboardButton("Back to Main Menu", callback_data="back_to_menu", style=KBS.PRIMARY,
                                 icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))),
        ],
    ])

def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Cancel", callback_data="admin_back", style=KBS.DANGER,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CANCEL", ""))),
    ]])

def admin_back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Back to Admin Panel", callback_data="admin_back", style=KBS.PRIMARY,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))),
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

# ==================== BOT HANDLERS ====================

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

def is_admin(user_id):
    return db_fetch_one("SELECT user_id FROM admins WHERE user_id=?", (user_id,)) is not None

def is_super_admin(user_id):
    return user_id in SUPER_ADMIN_IDS

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
    sent = await update.message.reply_text(start_welcome_html(), reply_markup=bottom_menu_keyboard(user_id), parse_mode='HTML')
    db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?", (sent.message_id, user_id))
    db_exec("UPDATE users SET keyboard_message_id=? WHERE user_id=?", (sent.message_id, user_id))

# ==================== MAIN MENU ====================
async def show_main_menu(update: Update, user_id, first_name, context: ContextTypes.DEFAULT_TYPE = None):
    username = None
    if hasattr(update, 'effective_user') and update.effective_user:
        username = update.effective_user.username
    ensure_user(user_id, username, first_name)
    short_msg = f'{emoji_tag(MAIN_MENU_EMOJI, "✨")} <b>Main Menu</b>'
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, short_msg, reply_markup=None, parse_mode='HTML',
                           context=context, persistent_menu=True,
                           auto_delete=False, delete_after=MAIN_MENU_DELETE)
    else:
        if context:
            await send_clean_message(update, context, short_msg, reply_markup=None, parse_mode='HTML',
                                     persistent_menu=True,
                                     auto_delete=False, delete_after=MAIN_MENU_DELETE)

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
    text = "CONTACT SUPPORT\n\n━━━━━━━━━━━━━━━━━━━━\nFor any issues, contact admin directly.\n\nDeveloper: 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓"
    if isinstance(update, CallbackQuery):
        user_id = update.effective_user.id
        await edit_or_send(update, text, reply_markup=support_keyboard(), context=context, auto_delete=False)
        kb_id_row = db_fetch_one("SELECT keyboard_message_id FROM users WHERE user_id=?", (user_id,))
        if not kb_id_row or not kb_id_row[0]:
            anchor = await context.bot.send_message(chat_id=user_id, text="Main Menu", reply_markup=bottom_menu_keyboard(user_id))
            db_exec("UPDATE users SET keyboard_message_id=? WHERE user_id=?", (anchor.message_id, user_id))
    else:
        if context:
            await send_clean_message(update, context, text, reply_markup=None, persistent_menu=True)

# ==================== ADMIN PANEL ====================
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

# ==================== COUNTRY MANAGER ====================
async def country_manager_menu(update: Update, user_id, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(user_id):
        await update.callback_query.answer("Admin mode required!", show_alert=True)
        return
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
    if not is_admin(user_id):
        await query.answer("Admin mode required!", show_alert=True)
        return
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
    if not is_admin(user_id):
        await query.answer("Admin mode required!", show_alert=True)
        return
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
    if len(parts) != 3:
        await query.answer("Invalid.", show_alert=True)
        return
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
    if not is_admin(user_id):
        await update.callback_query.answer("Admin mode required!", show_alert=True)
        return
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
    if not service_name:
        await update.message.reply_text("Session expired.")
        return True
    if text == "/skip":
        text = ""
    db_exec("UPDATE services SET emoji_id = ? WHERE name = ?", (text, service_name))
    await update.message.reply_text(f"Emoji for {service_name} updated!")
    admin_panel_state[user_id] = "service_manager"
    await service_manager_menu(update, user_id, context)
    return True

# ==================== DATABASE MANAGER ====================
async def database_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.callback_query.answer("Admin mode required!", show_alert=True)
        return
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
    if not is_admin(user_id):
        return
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
    if not is_admin(user_id):
        return
    admin_panel_state[user_id] = "waiting_db_upload"
    await edit_or_send(query, "Upload the sr-number-data.zip file to restore the database.",
                       reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)

# ==================== API ADD/REMOVE/LIST (Original) ====================
async def manage_api_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        if isinstance(update, CallbackQuery):
            await update.answer("Admin mode required!", show_alert=True)
        return
    admin_panel_state[user_id] = "manage_api"
    # Modified to include API SYSTEM button
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("ADD API", callback_data="api_add", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADD_API_KEY", "")))],
        [InlineKeyboardButton("LIST API", callback_data="api_list", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("LIST_API_KEY", "")))],
        [InlineKeyboardButton("REMOVE API", callback_data="api_remove", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("REMOVE_API_KEY", "")))],
        [InlineKeyboardButton("API SYSTEM", callback_data="api_system", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_SYSTEM", "")))],
        [InlineKeyboardButton("Back", callback_data="admin_back", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))],
    ])
    await reply_or_edit(update, "🔧 MANAGE API\n\nSelect an option:", reply_markup=kb, context=context, auto_delete=False)

# ---- API ADD (Enhanced) ----
async def api_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    admin_temp_data[user_id] = {}
    admin_panel_state[user_id] = "api_add_name"
    await reply_or_edit(update,
        "**ADD API - Step 1: Panel Name**\n\nSend the name for this API (e.g., MyProvider):",
        reply_markup=admin_cancel_keyboard(),
        parse_mode='HTML',
        context=context,
        auto_delete=False)

# ---- API ADD continuation via text handler ----
async def handle_api_add_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = admin_panel_state.get(user_id)
    if not state or not state.startswith("api_add_"):
        return False
    text = update.message.text.strip()
    if text == "/cancel":
        admin_temp_data.pop(user_id, None)
        admin_panel_state[user_id] = "main"
        await update.message.reply_text("API addition cancelled.", reply_markup=admin_panel_keyboard())
        return True

    data = admin_temp_data.get(user_id, {})
    if state == "api_add_name":
        data["panel_name"] = text
        admin_panel_state[user_id] = "api_add_base_url"
        await update.message.reply_text("**Step 2: Base URL**\n\nSend the base URL (e.g., http://example.com):", parse_mode='HTML')
    elif state == "api_add_base_url":
        data["base_url"] = text.rstrip('/')
        admin_panel_state[user_id] = "api_add_endpoint"
        await update.message.reply_text("**Step 3: Endpoint**\n\nSend the endpoint path (e.g., /otp/list). Use {API_TOKEN} and {records} as placeholders:", parse_mode='HTML')
    elif state == "api_add_endpoint":
        data["endpoint"] = text
        admin_panel_state[user_id] = "api_add_token"
        await update.message.reply_text("**Step 4: Token**\n\nSend the API token/key:", parse_mode='HTML')
    elif state == "api_add_token":
        data["token"] = text
        admin_panel_state[user_id] = "api_add_method"
        await update.message.reply_text("**Step 5: Method**\n\nSend GET or POST (default GET):", parse_mode='HTML')
    elif state == "api_add_method":
        data["method"] = text.upper() if text.upper() in ["GET","POST","PUT","DELETE"] else "GET"
        admin_panel_state[user_id] = "api_add_interval"
        await update.message.reply_text("**Step 6: Polling Interval (seconds)**\n\nSend a number >= 10 (default 30):", parse_mode='HTML')
    elif state == "api_add_interval":
        try:
            interval = int(text)
            if interval < 10:
                await update.message.reply_text("Interval must be >= 10. Try again.")
                return True
        except ValueError:
            await update.message.reply_text("Invalid number. Try again.")
            return True
        data["interval"] = interval
        admin_panel_state[user_id] = "api_add_response_type"
        await update.message.reply_text("**Step 7: Response Type**\n\nSend `json` or `text` (default json):", parse_mode='HTML')
    elif state == "api_add_response_type":
        data["response_type"] = text.lower() if text.lower() in ["json","text"] else "json"
        admin_panel_state[user_id] = "api_add_otp_list_path"
        await update.message.reply_text("**Step 8: OTP List Path**\n\nJSON path to the OTP list (e.g., data.otps). Default: `data.otps`\nSend /skip to use default.", parse_mode='HTML')
    elif state == "api_add_otp_list_path":
        data["otp_list_path"] = text if text != "/skip" else "data.otps"
        admin_panel_state[user_id] = "api_add_number_path"
        await update.message.reply_text("**Step 9: Number Field Path**\n\nJSON field for phone number. Default: `number`\nSend /skip for default.", parse_mode='HTML')
    elif state == "api_add_number_path":
        data["number_path"] = text if text != "/skip" else "number"
        admin_panel_state[user_id] = "api_add_message_path"
        await update.message.reply_text("**Step 10: Message Field Path**\n\nJSON field for full SMS. Default: `message`\nSend /skip for default.", parse_mode='HTML')
    elif state == "api_add_message_path":
        data["message_path"] = text if text != "/skip" else "message"
        admin_panel_state[user_id] = "api_add_country_path"
        await update.message.reply_text("**Step 11: Country Field Path**\n\nJSON field for country. Default: `country`\nSend /skip for default.", parse_mode='HTML')
    elif state == "api_add_country_path":
        data["country_path"] = text if text != "/skip" else "country"
        # Save everything
        db_exec("""
            INSERT INTO api_keys (
                panel_name, base_url, endpoint, token, method, interval_sec,
                response_type, otp_list_path, number_path, message_path, country_path,
                active, created_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (
            data["panel_name"],
            data["base_url"],
            data["endpoint"],
            data["token"],
            data["method"],
            data["interval"],
            data["response_type"],
            data["otp_list_path"],
            data["number_path"],
            data["message_path"],
            data["country_path"],
            user_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        api_id = db_fetch_one("SELECT last_insert_rowid()")[0]
        await start_polling_for_api(api_id)   # we will define this later
        admin_temp_data.pop(user_id, None)
        admin_panel_state[user_id] = "main"
        await update.message.reply_text(f"✅ API '{data['panel_name']}' added successfully (ID: {api_id}) and polling started.", reply_markup=admin_panel_keyboard())
    admin_temp_data[user_id] = data
    return True

# ---- API REMOVE ----
async def api_remove_list(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    apis = db_fetch_all("SELECT id, panel_name FROM api_keys WHERE active=1")
    if not apis:
        await reply_or_edit(update, "No active APIs to remove.", reply_markup=admin_back_button(), context=context)
        return
    rows = []
    for api_id, name in apis:
        rows.append([InlineKeyboardButton(f"❌ {name}", callback_data=f"api_remove_do|{api_id}",
                                          style=KBS.DANGER,
                                          icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DELETE", "")))])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await reply_or_edit(update, "Select API to remove:", reply_markup=InlineKeyboardMarkup(rows), context=context, auto_delete=False)

async def api_remove_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        return
    api_id = int(query.data.split('|')[1])
    if api_id in polling_tasks:
        polling_tasks[api_id].cancel()
        del polling_tasks[api_id]
    db_exec("DELETE FROM api_keys WHERE id = ?", (api_id,))
    db_exec("DELETE FROM api_logs WHERE api_id = ?", (api_id,))
    await query.answer("API removed.")
    await api_remove_list(update, context, user_id)

# ---- API LIST ----
async def api_list(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    apis = db_fetch_all("SELECT id, panel_name, active, interval_sec, total_otps FROM api_keys ORDER BY id")
    if not apis:
        text = "No APIs configured."
    else:
        lines = []
        for api_id, name, active, interval, total in apis:
            status = "🟢 Active" if active else "🔴 Inactive"
            lines.append(f"• {name} (ID: {api_id}) – {status} | Interval: {interval}s | Total OTPs: {total}")
        text = "\n".join(lines)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
    await reply_or_edit(update, text, reply_markup=kb, context=context, auto_delete=False)


# ==================== END OF PART 1 ====================
# The remainder — NEW API SYSTEM FUNCTIONS — will be in Part 2.
# ==================== PART 2 — NEW API SYSTEM & REMAINING FUNCTIONS ====================
# Continue from Part 1. This is the second half of bot.py

# ==================== NEW API SYSTEM FUNCTIONS ====================

def get_api_config(api_id: int) -> Optional[Dict]:
    """Fetch a single API configuration as dict"""
    row = db_fetch_one("""
        SELECT id, panel_name, base_url, token, interval_sec, active,
               endpoint, method, headers, body_template, response_type,
               otp_list_path, number_path, message_path, country_path,
               service_path, timestamp_path, success_path, success_value,
               max_records, retry_count, retry_delay, error_count, last_poll_time,
               total_otps, last_otp_time
        FROM api_keys WHERE id = ?
    """, (api_id,))
    if not row:
        return None
    cols = ['id','panel_name','base_url','token','interval_sec','active',
            'endpoint','method','headers','body_template','response_type',
            'otp_list_path','number_path','message_path','country_path',
            'service_path','timestamp_path','success_path','success_value',
            'max_records','retry_count','retry_delay','error_count','last_poll_time',
            'total_otps','last_otp_time']
    return dict(zip(cols, row))


class ResponseParser:
    """Parse different API response formats (JSON, text) using configured paths"""
    
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
                    # Case-insensitive fallback
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
    def parse_json_response(content: dict, config: dict) -> List[dict]:
        """Extract OTP entries from JSON using configured paths"""
        data = ResponseParser._get_json_path(content, config.get('otp_list_path', 'data.otps'))
        if data is None:
            return []
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            return []
        result = []
        for item in data:
            if not isinstance(item, dict):
                continue
            entry = {
                "number": ResponseParser._get_json_path(item, config.get('number_path', 'number'), ""),
                "otp": ResponseParser._get_json_path(item, config.get('otp_path', 'otp'), ""),
                "message": ResponseParser._get_json_path(item, config.get('message_path', 'message'), ""),
                "service": ResponseParser._get_json_path(item, config.get('service_path', 'service'), ""),
                "timestamp": ResponseParser._get_json_path(item, config.get('timestamp_path', 'timestamp'), ""),
                "country": ResponseParser._get_json_path(item, config.get('country_path', 'country'), ""),
            }
            # Remove empty values
            entry = {k: v for k, v in entry.items() if v}
            if entry.get("otp") or entry.get("number"):
                result.append(entry)
        return result

    @staticmethod
    def parse_response(content, config: dict) -> List[dict]:
        """Main entry point — detects JSON/text and parses accordingly"""
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                # Fallback to text extraction using regex
                otps = extract_all_otps_from_message(content)
                return [{"otp": otp, "message": content[:200]} for otp in otps]
        if isinstance(content, dict):
            return ResponseParser.parse_json_response(content, config)
        return []


# ---- Polling System ----
async def poll_single_api(api_id: int):
    """Background task that polls one API at its configured interval"""
    while True:
        config = get_api_config(api_id)
        if not config or not config.get('active'):
            break
        interval = config.get('interval_sec', 30)
        try:
            # Build URL
            base_url = config['base_url'].rstrip('/')
            endpoint = config['endpoint'].lstrip('/')
            url = f"{base_url}/{endpoint}"
            url = url.replace('{API_TOKEN}', config['token']).replace('{token}', config['token']).replace('{records}', str(config.get('max_records', 200)))

            # Build headers
            headers = json.loads(config.get('headers', '{}')) if config.get('headers') else {}
            for k, v in headers.items():
                if isinstance(v, str):
                    headers[k] = v.replace('{API_TOKEN}', config['token']).replace('{token}', config['token'])

            # Execute request
            method = config.get('method', 'GET').upper()
            resp = None
            if method == 'GET':
                resp = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                body = json.loads(config.get('body_template', '{}')) if config.get('body_template') else {}
                # Recursively replace placeholders
                def replace_placeholders(obj):
                    if isinstance(obj, dict):
                        return {k: replace_placeholders(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [replace_placeholders(v) for v in obj]
                    elif isinstance(obj, str):
                        return obj.replace('{API_TOKEN}', config['token']).replace('{token}', config['token']).replace('{records}', str(config.get('max_records', 200)))
                    return obj
                body = replace_placeholders(body)
                resp = requests.post(url, headers=headers, json=body, timeout=30)
            else:
                resp = requests.request(method, url, headers=headers, timeout=30)

            if resp and resp.status_code == 200:
                # Parse response
                otps = ResponseParser.parse_response(resp.text, config)
                if otps:
                    await process_otps(otps, bot=application.bot)
                    db_exec("UPDATE api_keys SET total_otps = total_otps + ?, last_otp_time = ? WHERE id = ?",
                            (len(otps), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), api_id))
                # Log success
                db_exec("INSERT INTO api_logs (api_id, timestamp, status, message, otp_count) VALUES (?, ?, 'success', ?, ?)",
                        (api_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "OK", len(otps) if otps else 0))
                db_exec("UPDATE api_keys SET error_count = 0, last_poll_time = ? WHERE id = ?",
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), api_id))
            else:
                error_msg = f"HTTP {resp.status_code if resp else 'No response'}"
                db_exec("INSERT INTO api_logs (api_id, timestamp, status, message, otp_count) VALUES (?, ?, 'error', ?, 0)",
                        (api_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error_msg))
                db_exec("UPDATE api_keys SET error_count = error_count + 1 WHERE id = ?", (api_id,))
        except Exception as e:
            print(f"API {api_id} error: {e}")
            db_exec("INSERT INTO api_logs (api_id, timestamp, status, message, otp_count) VALUES (?, ?, 'error', ?, 0)",
                    (api_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(e)[:200]))
            db_exec("UPDATE api_keys SET error_count = error_count + 1 WHERE id = ?", (api_id,))
        await asyncio.sleep(interval)


async def start_polling_for_api(api_id: int):
    """Start the polling task for a given API if active and not already running"""
    config = get_api_config(api_id)
    if not config or not config.get('active'):
        return
    if api_id not in polling_tasks or polling_tasks[api_id].done():
        task = asyncio.create_task(poll_single_api(api_id))
        polling_tasks[api_id] = task


async def stop_polling_for_api(api_id: int):
    """Stop the polling task for an API and set active=0"""
    if api_id in polling_tasks:
        polling_tasks[api_id].cancel()
        del polling_tasks[api_id]
    db_exec("UPDATE api_keys SET active = 0 WHERE id = ?", (api_id,))


async def start_all_polling():
    """Called on bot startup to start polling for all active APIs"""
    apis = db_fetch_all("SELECT id FROM api_keys WHERE active = 1")
    for (api_id,) in apis:
        await start_polling_for_api(api_id)


# ---- API SYSTEM Grid View ----
async def api_system_grid(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Show all APIs in a 2-column grid with status"""
    if not is_admin(user_id):
        if isinstance(update, CallbackQuery):
            await update.answer("Admin only!", show_alert=True)
        return
    admin_panel_state[user_id] = "api_system"
    apis = db_fetch_all("SELECT id, panel_name, active FROM api_keys ORDER BY id")
    if not apis:
        text = f"{emoji_tag(CUSTOM_EMOJIS['API_SYSTEM'], '🖥️')} No APIs configured yet."
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add API", callback_data="api_add", style=KBS.SUCCESS,
                                  icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADD_API_KEY", "")))],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                  icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
        ])
        await reply_or_edit(update, text, reply_markup=kb, context=context, auto_delete=False)
        return

    rows = []
    row = []
    for api_id, panel_name, active in apis:
        status_emoji = emoji_tag(CUSTOM_EMOJIS["API_STATUS_ACTIVE"] if active else CUSTOM_EMOJIS["API_STATUS_INACTIVE"],
                                 "🟢" if active else "🔴")
        label = f"{status_emoji} {panel_name}"
        style = KBS.SUCCESS if active else KBS.DANGER
        btn = InlineKeyboardButton(
            label,
            callback_data=f"api_detail|{api_id}",
            style=style,
            icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_SYSTEM", ""))
        )
        row.append(btn)
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    # Add "Add API" and "Back" buttons
    rows.append([
        InlineKeyboardButton("➕ Add API", callback_data="api_add", style=KBS.SUCCESS,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADD_API_KEY", "")))
    ])
    rows.append([
        InlineKeyboardButton("🔙 Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))
    ])

    text = f"{emoji_tag(CUSTOM_EMOJIS['API_SYSTEM'], '🖥️')} <b>API SYSTEM</b> ({len(apis)} configured)"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)


# ---- API Detail Page (1×1 inline) ----
async def api_detail_page(update: Update, context: ContextTypes.DEFAULT_TYPE, api_id: int, user_id: int):
    """Show detailed management page for a single API (1×1 layout)"""
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

    # Toggle Start/Stop
    if config['active']:
        btns.append(InlineKeyboardButton(
            f"{emoji_tag(CUSTOM_EMOJIS['API_STOP_POLL'], '⏸️')} STOP POLLING",
            callback_data=f"api_toggle|{api_id}",
            style=KBS.DANGER,
            icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_STOP_POLL", ""))
        ))
    else:
        btns.append(InlineKeyboardButton(
            f"{emoji_tag(CUSTOM_EMOJIS['API_START_POLL'], '▶️')} START POLLING",
            callback_data=f"api_toggle|{api_id}",
            style=KBS.SUCCESS,
            icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_START_POLL", ""))
        ))

    # Edit
    btns.append(InlineKeyboardButton(
        f"{emoji_tag(CUSTOM_EMOJIS['EDIT_BALANCE'], '✏️')} EDIT",
        callback_data=f"api_edit|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("EDIT_BALANCE", ""))
    ))
    # Test
    btns.append(InlineKeyboardButton(
        f"{emoji_tag(CUSTOM_EMOJIS['API_TEST'], '🧪')} TEST",
        callback_data=f"api_test|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_TEST", ""))
    ))
    # Stats
    btns.append(InlineKeyboardButton(
        f"{emoji_tag(CUSTOM_EMOJIS['API_STATS'], '📊')} STATS",
        callback_data=f"api_stats|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_STATS", ""))
    ))
    # Logs
    btns.append(InlineKeyboardButton(
        f"{emoji_tag(CUSTOM_EMOJIS['API_LOGS'], '📜')} LOGS",
        callback_data=f"api_logs|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_LOGS", ""))
    ))
    # Delete
    btns.append(InlineKeyboardButton(
        f"{emoji_tag(CUSTOM_EMOJIS['DELETE'], '🗑️')} DELETE",
        callback_data=f"api_delete|{api_id}",
        style=KBS.DANGER,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DELETE", ""))
    ))
    # Force Poll
    btns.append(InlineKeyboardButton(
        f"{emoji_tag(CUSTOM_EMOJIS['API_FORCE_POLL'], '🔄')} FORCE POLL",
        callback_data=f"api_force|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_FORCE_POLL", ""))
    ))
    # Back to list
    btns.append(InlineKeyboardButton(
        f"{emoji_tag(CUSTOM_EMOJIS['BACK'], '🔙')} BACK TO LIST",
        callback_data="api_system",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))
    ))

    # Arrange 1×1: each button in its own row
    rows = [[btn] for btn in btns]
    sep = emoji_tag(CUSTOM_EMOJIS["API_SEPARATOR"], "➖") * 20
    text = f"{header}\n\n{info}\n\n{sep}\n\n"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)


# ---- Toggle (Start/Stop Polling) ----
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

    # Refresh detail page
    await api_detail_page(update, context, api_id, user_id)


# ---- Edit Menu (all fields as 1×1 inline buttons) ----
async def api_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, api_id: int, user_id: int):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    config = get_api_config(api_id)
    if not config:
        await update.answer("API not found!", show_alert=True)
        return

    admin_panel_state[user_id] = f"api_edit_{api_id}"

    # List of editable fields: (display label, emoji key, db field, fallback emoji)
    fields = [
        ("NAME", "API_FIELD_NAME", "panel_name", "📛"),
        ("BASE URL", "API_FIELD_URL", "base_url", "🌐"),
        ("ENDPOINT", "API_FIELD_ENDPOINT", "endpoint", "📍"),
        ("TOKEN", "API_FIELD_TOKEN", "token", "🔑"),
        ("METHOD", "API_FIELD_METHOD", "method", "📩"),
        ("INTERVAL", "API_FIELD_INTERVAL", "interval_sec", "⏱️"),
        ("MAX RECORDS", "API_FIELD_RECORDS", "max_records", "📊"),
        ("RETRY COUNT", "API_FIELD_RETRY", "retry_count", "🔄"),
        ("OTP LIST PATH", "API_FIELD_OTP_PATH", "otp_list_path", "📦"),
        ("NUMBER PATH", "API_FIELD_NUMBER", "number_path", "📱"),
        ("MESSAGE PATH", "API_FIELD_MESSAGE", "message_path", "💬"),
        ("COUNTRY PATH", "API_FIELD_COUNTRY", "country_path", "🌍"),
        ("SERVICE PATH", "API_FIELD_SERVICE", "service_path", "🔧"),
        ("TIMESTAMP PATH", "API_FIELD_TIMESTAMP", "timestamp_path", "🕐"),
        ("SUCCESS PATH", "API_FIELD_SUCCESS_PATH", "success_path", "✅"),
        ("SUCCESS VALUE", "API_FIELD_SUCCESS_VALUE", "success_value", "🎯"),
    ]

    rows = []
    for label, emoji_key, field, fallback in fields:
        value = config.get(field, "")
        display_value = str(value)[:20] + "..." if len(str(value)) > 20 else value
        btn_text = f"{emoji_tag(CUSTOM_EMOJIS.get(emoji_key, ''), fallback)} {label}: <code>{display_value}</code>"
        rows.append([InlineKeyboardButton(
            btn_text,
            callback_data=f"api_edit_field|{api_id}|{field}",
            style=KBS.PRIMARY,
            parse_mode='HTML'
        )])

    rows.append([InlineKeyboardButton(
        f"{emoji_tag(CUSTOM_EMOJIS['BACK'], '🔙')} BACK TO DETAIL",
        callback_data=f"api_detail|{api_id}",
        style=KBS.PRIMARY,
        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))
    )])

    text = f"{emoji_tag(CUSTOM_EMOJIS['EDIT_BALANCE'], '✏️')} <b>Edit Configuration: {config['panel_name']}</b>\n\nSelect a field to edit:"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)


# ---- Edit Field Prompt ----
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
    await query.edit_message_text(
        f"{emoji_tag(CUSTOM_EMOJIS['EDIT_BALANCE'], '✏️')} Edit <b>{field}</b>\n\nCurrent value: <code>{current_val}</code>\n\nSend new value (or /cancel):",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Cancel", callback_data=f"api_edit|{api_id}", style=KBS.DANGER,
                                  icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
        ]),
        parse_mode='HTML'
    )


# ---- Test API ----
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
        # Build request
        base_url = config['base_url'].rstrip('/')
        endpoint = config['endpoint'].lstrip('/')
        url = f"{base_url}/{endpoint}"
        url = url.replace('{API_TOKEN}', config['token']).replace('{token}', config['token']).replace('{records}', str(config.get('max_records', 5)))

        headers = json.loads(config.get('headers', '{}')) if config.get('headers') else {}
        for k, v in headers.items():
            if isinstance(v, str):
                headers[k] = v.replace('{API_TOKEN}', config['token']).replace('{token}', config['token'])

        method = config.get('method', 'GET').upper()
        resp = None
        if method == 'GET':
            resp = requests.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            body = json.loads(config.get('body_template', '{}')) if config.get('body_template') else {}
            resp = requests.post(url, headers=headers, json=body, timeout=30)
        else:
            resp = requests.request(method, url, headers=headers, timeout=30)

        if resp and resp.status_code == 200:
            otps = ResponseParser.parse_response(resp.text, config)
            if otps:
                sample = "\n".join([
                    f"{emoji_tag(CUSTOM_EMOJIS['API_OTP_COUNT'], '📨')} {i+1}. {otp.get('number', 'N/A')} – OTP: {otp.get('otp', '?')}"
                    for i, otp in enumerate(otps[:5])
                ])
                more = f"\n... and {len(otps)-5} more" if len(otps) > 5 else ""
                result = f"✅ Found <b>{len(otps)}</b> OTP(s)\n\n{sample}{more}"
            else:
                result = "✅ API responded but no OTPs found.\n\nRaw response (first 300 chars):\n<code>" + resp.text[:300] + "</code>"
        else:
            result = f"❌ Error: HTTP {resp.status_code if resp else 'No response'}"
    except Exception as e:
        result = f"❌ Exception: {str(e)}"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])
    await query.edit_message_text(
        f"{emoji_tag(CUSTOM_EMOJIS['API_TEST'], '🧪')} <b>Test Result: {config['panel_name']}</b>\n\n{result}",
        reply_markup=kb,
        parse_mode='HTML'
    )


# ---- Stats ----
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
        [InlineKeyboardButton("🔙 Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)


# ---- Logs ----
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

    logs = db_fetch_all("SELECT timestamp, status, message, otp_count FROM api_logs WHERE api_id = ? ORDER BY timestamp DESC LIMIT 20", (api_id,))
    if not logs:
        lines = ["No logs yet."]
    else:
        lines = []
        for ts, status, msg, count in logs:
            emoji = "✅" if status == "success" else "❌"
            count_str = f"{count} OTPs" if status == "success" else ""
            lines.append(f"{emoji} <code>{ts}</code> – {msg} {count_str}")

    text = f"{emoji_tag(CUSTOM_EMOJIS['API_LOGS'], '📜')} <b>Polling Logs: {config['panel_name']}</b>\n\n" + "\n".join(lines[:20])
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data=f"api_logs|{api_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_FORCE_POLL", "")))],
        [InlineKeyboardButton("🔙 Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)


# ---- Delete (with YES/NO confirmation) ----
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
        [InlineKeyboardButton("✅ YES, DELETE", callback_data=f"api_delete_yes|{api_id}", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("YES", "")))],
        [InlineKeyboardButton("❌ NO, CANCEL", callback_data=f"api_delete_no|{api_id}", style=KBS.SUCCESS,
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
    action = data[0]  # api_delete_yes or api_delete_no

    if action == "api_delete_yes":
        # Stop polling task if running
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


# ---- Force Poll ----
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
        base_url = config['base_url'].rstrip('/')
        endpoint = config['endpoint'].lstrip('/')
        url = f"{base_url}/{endpoint}"
        url = url.replace('{API_TOKEN}', config['token']).replace('{token}', config['token']).replace('{records}', str(config.get('max_records', 200)))

        headers = json.loads(config.get('headers', '{}')) if config.get('headers') else {}
        for k, v in headers.items():
            if isinstance(v, str):
                headers[k] = v.replace('{API_TOKEN}', config['token']).replace('{token}', config['token'])

        method = config.get('method', 'GET').upper()
        resp = None
        if method == 'GET':
            resp = requests.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            body = json.loads(config.get('body_template', '{}')) if config.get('body_template') else {}
            resp = requests.post(url, headers=headers, json=body, timeout=30)
        else:
            resp = requests.request(method, url, headers=headers, timeout=30)

        if resp and resp.status_code == 200:
            otps = ResponseParser.parse_response(resp.text, config)
            if otps:
                await process_otps(otps, bot=context.bot)
                db_exec("UPDATE api_keys SET total_otps = total_otps + ?, last_otp_time = ? WHERE id = ?",
                        (len(otps), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), api_id))
                result = f"✅ Found and processed <b>{len(otps)}</b> OTP(s)."
            else:
                result = "✅ API responded, but no OTPs found."
        else:
            result = f"❌ Error: HTTP {resp.status_code if resp else 'No response'}"
    except Exception as e:
        result = f"❌ Exception: {str(e)}"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])
    await query.edit_message_text(
        f"{emoji_tag(CUSTOM_EMOJIS['API_FORCE_POLL'], '🔄')} <b>Force Poll Result: {config['panel_name']}</b>\n\n{result}",
        reply_markup=kb,
        parse_mode='HTML'
    )


# ==================== ORIGINAL CALLBACKS (MISSING FROM PART 1) ====================

# ---- Menu Callback ----
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if await ban_check(update, context):
        return
    first_name = query.from_user.first_name or "User"
    data = query.data
    await query.answer()
    action = data[len("menu_"):]
    if action == "get_number":
        await show_get_number(update, context, user_id, first_name)
    elif action == "balance":
        await show_balance(update, user_id, context)
    elif action == "support":
        await show_support(update, context)
    elif action == "admin":
        await admin_panel_menu(update, user_id, context)


# ---- Service Selection ----
async def service_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
    user_id = query.from_user.id
    await query.answer()
    service = query.data.split('|', 1)[1]
    db_exec("UPDATE users SET current_service = ? WHERE user_id = ?", (service, user_id))
    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_COUNTRY_PREFIX"], "🌍")} '
        f'<b>Select country for {service.upper()}</b> {service_emoji_tag(service)}'
    )
    await edit_or_send(query, text, reply_markup=countries_for_service_keyboard(service), parse_mode='HTML', context=context)


# ---- Country Selection ----
async def country_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
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


# ---- Back to Services ----
async def back_to_services_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
    user_id = query.from_user.id
    await query.answer()
    db_exec("UPDATE users SET current_service = NULL, current_country = NULL, current_number = NULL, number_expiry = NULL WHERE user_id = ?", (user_id,))
    text = (
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_PREFIX"], "🔧")} <b>Select service</b> '
        f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_SUFFIX"], "📱")}'
    )
    await edit_or_send(query, text, reply_markup=services_keyboard(), parse_mode='HTML', context=context)


# ---- Next Number ----
async def next_number_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
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
        if fallback:
            country, service = fallback
    if not country or not service:
        await query.answer("Please select a service and country first!", show_alert=True)
        await edit_or_send(query, "Select a Service:", reply_markup=services_keyboard(), context=context)
        return
    numbers = get_numbers_from_stock(country, service, 3)
    if not numbers:
        await query.answer(f"No more {country} {service} numbers!", show_alert=True)
        await edit_or_send(query, f"Select a Country for {service}:", reply_markup=countries_for_service_keyboard(service), context=context)
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


# ---- Toggle CC ----
async def toggle_cc_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
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


# ---- No-op ----
async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


# ==================== STOCK MANAGEMENT CALLBACKS ====================

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


# ==================== STOCK MANAGEMENT MENU (WRAPPER) ====================
async def stock_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Wrapper for stock management menu"""
    await send_stock_management_menu(update, context, user_id)


# ==================== DOCUMENT HANDLER (FILE UPLOADS) ====================
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


# ==================== OTP PROCESSING (FULL ORIGINAL) ====================
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
    """Process OTPs: forward to group, credit users, and notify"""
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
        message = otp_entry.get("message", "")
        service_name = otp_entry.get("service", "Unknown")
        otp_timestamp_str = otp_entry.get("timestamp", now_str)

        otp_code = extract_otp_from_message(message)
        if not otp_code:
            otp_code = otp_entry.get("otp", "")

        if not number or not otp_code:
            continue

        # Forward to group
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

        # Credit users
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
                try:
                    await bot.send_message(uid, header, reply_markup=button, parse_mode='HTML')
                except Exception as e:
                    print(f"DM OTP failed for {uid}: {e}")
    save_user_data_json()


def format_group_otp_rich(entry):
    """Format OTP entry for rich group message"""
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
    if not country_emoji_id and country_iso and country_iso.lower() in DEFAULT_EMOJIS.get("countries", {}):
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


# ==================== FULL TEXT HANDLER ====================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if await handle_admin_text(update, context):
        return
    if await handle_api_add_text(update, context):
        return
    user_id = update.effective_user.id
    if await ban_check(update, context):
        return
    text = update.message.text.strip()

    # ---- Service emoji set ----
    state = admin_panel_state.get(user_id)
    if state == "waiting_service_emoji":
        if await handle_service_emoji_set(update, context):
            return

    # ---- Country edit/add states ----
    if state == "waiting_country_add":
        try:
            parts = [p.strip() for p in text.split('|')]
            if len(parts) < 4:
                await update.message.reply_text("Format: CountryName | Code | ISO | payout | emoji_id")
                return
            name, code, iso, payout = parts[0], parts[1], parts[2].upper(), parts[3]
            emoji_id = parts[4] if len(parts) >= 5 else ""
            COUNTRIES_DATA[name] = {"code": code, "iso": iso, "payout": payout, "emoji_id": emoji_id}
            save_countries_db(COUNTRIES_DATA)
            await country_add_service_selection(update, user_id, name, context)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
        return

    if state == "waiting_country_edit":
        if text == "/skip":
            admin_panel_state[user_id] = "country_manager"
            await update.message.reply_text("No changes.")
            await country_manager_menu(update, user_id, context)
            return
        try:
            parts = [p.strip() for p in text.split('|')]
            if len(parts) < 3:
                await update.message.reply_text("At least Code | ISO | payout required.")
                return
            code, iso, payout = parts[0], parts[1].upper(), parts[2]
            emoji_id = parts[3] if len(parts) >= 4 else ""
            country_name = admin_temp_data.get(user_id, {}).get("edit_country")
            COUNTRIES_DATA[country_name].update({"code": code, "iso": iso, "payout": payout, "emoji_id": emoji_id})
            save_countries_db(COUNTRIES_DATA)
            admin_panel_state[user_id] = "country_manager"
            await update.message.reply_text(f"Country {country_name} updated!")
            await country_manager_menu(update, user_id, context)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
        return

    if state == "waiting_service_name":
        try:
            db_exec("INSERT INTO services (name, display_name, active, emoji_id) VALUES (?, ?, 1, '')", (text, text))
            await update.message.reply_text(f"Service {text} added!")
        except sqlite3.IntegrityError:
            await update.message.reply_text(f"Service {text} already exists!")
        admin_panel_state[user_id] = "service_manager"
        await service_manager_menu(update, user_id, context)
        return

    # ---- Broadcast ----
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
        return

    # ---- API Edit Value ----
    if state and state.startswith("api_edit_value_"):
        api_id = int(state.split("_")[-1])
        data = admin_temp_data.get(user_id, {})
        field = data.get("field")
        if not field:
            await update.message.reply_text("Session expired. Please start over.")
            return
        new_value = text.strip()
        if new_value.lower() == "/cancel":
            await api_edit_menu(update, context, api_id, user_id)
            return

        # Validation
        if field in ["interval_sec", "max_records", "retry_count"]:
            try:
                new_value = int(new_value)
                if field == "interval_sec" and new_value < 10:
                    await update.message.reply_text("Interval must be at least 10 seconds.")
                    return
            except ValueError:
                await update.message.reply_text("Please enter a valid number.")
                return
        elif field == "method":
            if new_value.upper() not in ["GET", "POST", "PUT", "DELETE"]:
                await update.message.reply_text("Method must be GET, POST, PUT, or DELETE.")
                return
        elif field == "base_url":
            if not new_value.startswith(("http://", "https://")):
                await update.message.reply_text("Base URL must start with http:// or https://")
                return

        db_exec(f"UPDATE api_keys SET {field} = ? WHERE id = ?", (new_value, api_id))
        admin_temp_data.pop(user_id, None)
        admin_panel_state[user_id] = "main"
        await update.message.reply_text(f"✅ {field} updated successfully!")
        await api_detail_page(update, context, api_id, user_id)
        return

    # ---- User Manager Search/Edit ----
    if state == "um_searching":
        user = db_fetch_one("SELECT user_id, first_name, username, balance, withdrawn, total_otp, banned, joined_date, last_active FROM users WHERE user_id=? OR username=?", (text, text))
        if not user and text.isdigit():
            user = db_fetch_one("SELECT user_id, first_name, username, balance, withdrawn, total_otp, banned, joined_date, last_active FROM users WHERE user_id=?", (int(text),))
        if not user:
            await update.message.reply_text("User not found.")
            return
        admin_panel_state[user_id] = "user_manager"
        await show_user_detail(update, context, user)
        return

    if state == "um_editbal":
        data = admin_temp_data.pop(user_id, {})
        target_uid = data.get("target_uid")
        if not target_uid:
            await update.message.reply_text("Session expired.")
            return
        try:
            amount = float(text.split()[0])
        except ValueError:
            await update.message.reply_text("Invalid amount. Use format: +0.5 or -0.2")
            return
        current = db_fetch_one("SELECT balance FROM users WHERE user_id=?", (target_uid,))
        if not current:
            await update.message.reply_text("User not found.")
            return
        new_balance = (current[0] or 0.0) + amount
        db_exec("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, target_uid))
        save_user_data_json()
        await update.message.reply_text(f"Balance updated for {target_uid}. New balance: ${new_balance:.3f}")
        admin_panel_state[user_id] = "main"
        await admin_panel_menu(update, user_id, context)
        return

    # ---- Bottom menu ----
    if text == BTN_GET_NUMBER:
        await show_get_number(update, context, user_id, update.effective_user.first_name)
    elif text == BTN_BALANCE:
        await show_balance(update, user_id, context)
    elif text == BTN_SUPPORT:
        await show_support(update, context)
    elif text == BTN_ADMIN:
        await admin_panel_menu(update, user_id, context)


# ==================== ADMIN TEXT HANDLER (MODIFIED TO INCLUDE NEW STATES) ====================
async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Already used in text_handler; this is a wrapper.
    # The logic is inside text_handler; we keep this for compatibility.
    return False


# ==================== SAVE USER DATA JSON ====================
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


# ==================== ERROR HANDLER ====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")


# ==================== MAIN FUNCTION ====================
application = None

def main():
    global application
    application = Application.builder().token(BOT_TOKEN).build()

    # ---- Command Handlers ----
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("enteradmin", enter_admin_command))
    application.add_handler(CommandHandler("exitadmin", exit_admin_command))
    application.add_handler(CommandHandler("addadmin", add_admin_command))
    application.add_handler(CommandHandler("removeadmin", remove_admin_command))
    application.add_handler(CommandHandler("adminlist", admin_list_command))
    # The original bot also had /country, /service, /setcountry, /setservice, /testgroup
    application.add_handler(CommandHandler("country", group_country_command))
    application.add_handler(CommandHandler("service", group_service_command))
    application.add_handler(CommandHandler("setcountry", set_country_command))
    application.add_handler(CommandHandler("setservice", set_service_command))
    application.add_handler(CommandHandler("testgroup", testgroup_command))

    # ---- Document Handler ----
    application.add_handler(MessageHandler(filters.Document.ALL & filters.ChatType.PRIVATE, handle_all_documents), group=0)

    # ---- Text Handler ----
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler), group=1)

    # ---- Callback Query Handlers ----
    # Main menu / navigation
    application.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(noop_callback, pattern="^noop$"))

    # Balance
    application.add_handler(CallbackQueryHandler(withdraw_callback, pattern="^withdraw$"))

    # Get Number flow
    application.add_handler(CallbackQueryHandler(service_selection_callback, pattern="^svc_sel\|"))
    application.add_handler(CallbackQueryHandler(country_selection_callback, pattern="^cnt_sel\|"))
    application.add_handler(CallbackQueryHandler(back_to_services_callback, pattern="^back_to_services$"))
    application.add_handler(CallbackQueryHandler(next_number_callback, pattern="^next_number$"))
    application.add_handler(CallbackQueryHandler(toggle_cc_callback, pattern="^toggle_cc$"))

    # Country Manager
    application.add_handler(CallbackQueryHandler(country_callback, pattern="^country_"))
    application.add_handler(CallbackQueryHandler(country_add_service_callback, pattern="^cnt_add_svc\|"))

    # Service Manager
    application.add_handler(CallbackQueryHandler(service_callback, pattern="^service_"))
    application.add_handler(CallbackQueryHandler(service_callback, pattern="^service_set_emoji$"))
    application.add_handler(CallbackQueryHandler(service_callback, pattern=r"^service_emoji_set\|"))

    # User Manager
    application.add_handler(CallbackQueryHandler(user_manager_menu, pattern="^admin_user_manager$"))
    application.add_handler(CallbackQueryHandler(um_search_prompt, pattern="^um_search$"))
    application.add_handler(CallbackQueryHandler(send_user_list_file, pattern="^um_download$"))
    application.add_handler(CallbackQueryHandler(um_stats, pattern="^um_stats$"))
    application.add_handler(CallbackQueryHandler(um_edit_balance_prompt, pattern=r"^um_editbal\|"))
    application.add_handler(CallbackQueryHandler(um_ban_toggle, pattern=r"^um_ban\|"))
    application.add_handler(CallbackQueryHandler(user_manager_menu, pattern="^um_back$"))

    # Database
    application.add_handler(CallbackQueryHandler(database_menu, pattern="^admin_database$"))
    application.add_handler(CallbackQueryHandler(db_download, pattern="^db_download$"))
    application.add_handler(CallbackQueryHandler(db_upload_prompt, pattern="^db_upload$"))

    # Stock Management
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

    # Force Upload callbacks
    application.add_handler(CallbackQueryHandler(fu_country_callback, pattern=r"^fu_country\|"))
    application.add_handler(CallbackQueryHandler(fu_service_callback, pattern=r"^fu_service\|"))

    # API Management (original + new)
    application.add_handler(CallbackQueryHandler(manage_api_menu, pattern="^admin_manage_api$"))
    application.add_handler(CallbackQueryHandler(api_add_start, pattern="^api_add$"))
    application.add_handler(CallbackQueryHandler(api_remove_list, pattern="^api_remove$"))
    application.add_handler(CallbackQueryHandler(api_remove_execute, pattern=r"^api_remove_do\|"))
    application.add_handler(CallbackQueryHandler(api_list, pattern="^api_list$"))

    # API SYSTEM (new)
    application.add_handler(CallbackQueryHandler(api_system_grid, pattern="^api_system$"))
    application.add_handler(CallbackQueryHandler(api_detail_page, pattern=r"^api_detail\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_toggle_callback, pattern=r"^api_toggle\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_edit_menu, pattern=r"^api_edit\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_edit_field_prompt, pattern=r"^api_edit_field\|(\d+)\|(.+)$"))
    application.add_handler(CallbackQueryHandler(api_test_callback, pattern=r"^api_test\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_stats_callback, pattern=r"^api_stats\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_logs_callback, pattern=r"^api_logs\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_delete_prompt, pattern=r"^api_delete\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_delete_confirm, pattern=r"^api_delete_(yes|no)\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(api_force_poll, pattern=r"^api_force\|(\d+)$"))

    # Admin back / cancel
    application.add_handler(CallbackQueryHandler(admin_panel_menu, pattern="^admin_back$"))

    # ---- Error Handler ----
    application.add_error_handler(error_handler)

    # ---- Job Queue ----
    if application.job_queue:
        application.job_queue.run_repeating(periodic_json_save, interval=60, first=10)

    # ---- Post init (start polling tasks) ----
    async def start_api_tasks(app):
        print("🚀 Starting API polling tasks...")
        await start_all_polling()

    application.post_init = start_api_tasks

    # ---- Run ----
    save_user_data_json()
    print(f"✅ Super Admins: {SUPER_ADMIN_IDS}")
    print("✅ Full bot started with API System and Country Map.")
    application.run_polling(drop_pending_updates=True)


# ---- Force upload callbacks (for file uploads) ----
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


# ---- Group OTP commands (legacy) ----
async def group_country_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Admin only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /country ISO|EMOJI_ID")
        return
    parts = " ".join(context.args).split("|")
    if len(parts) != 2:
        await update.message.reply_text("Invalid format. Use ISO|EMOJI_ID")
        return
    iso = parts[0].strip().upper()
    eid = parts[1].strip()
    db_exec("INSERT OR REPLACE INTO group_emojis (type, key, emoji_id) VALUES ('country', ?, ?)", (iso, eid))
    DEFAULT_EMOJIS.setdefault("countries", {})[iso.lower()] = eid
    await update.message.reply_text(f"✅ Group country emoji for {iso} set to <code>{eid}</code>", parse_mode="HTML")


async def group_service_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Admin only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /service NAME|EMOJI_ID")
        return
    parts = " ".join(context.args).split("|")
    if len(parts) != 2:
        await update.message.reply_text("Invalid format. Use NAME|EMOJI_ID")
        return
    name = parts[0].strip().lower()
    eid = parts[1].strip()
    db_exec("INSERT OR REPLACE INTO group_emojis (type, key, emoji_id) VALUES ('service', ?, ?)", (name, eid))
    DEFAULT_EMOJIS.setdefault("services", {})[name.lower()] = eid
    await update.message.reply_text(f"✅ Group service emoji for {name} set to <code>{eid}</code>", parse_mode="HTML")


async def set_country_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /setcountry ISO|EMOJI_ID")
        return
    parts = " ".join(context.args).split("|")
    if len(parts) != 2:
        await update.message.reply_text("Invalid format. Use ISO|EMOJI_ID")
        return
    iso = parts[0].strip().upper()
    eid = parts[1].strip()
    db_exec("INSERT OR REPLACE INTO group_emojis (type, key, emoji_id) VALUES ('country', ?, ?)", (iso, eid))
    DEFAULT_EMOJIS.setdefault("countries", {})[iso.lower()] = eid
    await update.message.reply_text(f"✅ Country emoji for {iso} set to <code>{eid}</code>", parse_mode="HTML")


async def set_service_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /setservice NAME|EMOJI_ID")
        return
    parts = " ".join(context.args).split("|")
    if len(parts) != 2:
        await update.message.reply_text("Invalid format. Use NAME|EMOJI_ID")
        return
    name = parts[0].strip().lower()
    eid = parts[1].strip()
    db_exec("INSERT OR REPLACE INTO group_emojis (type, key, emoji_id) VALUES ('service', ?, ?)", (name, eid))
    DEFAULT_EMOJIS.setdefault("services", {})[name.lower()] = eid
    await update.message.reply_text(f"✅ Service emoji for {name} set to <code>{eid}</code>", parse_mode="HTML")


async def testgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to send a test OTP to the group using ISO2 country code."""
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

    try:
        grp_html, grp_kb = format_group_otp_rich(entry)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendRichMessage"
        payload = {
            "chat_id": GROUP_ID,
            "rich_message": {"html": grp_html},
            "reply_markup": grp_kb
        }
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            await update.message.reply_text(
                f"✅ Test OTP sent to group for {service} - {country_name} ({iso2}).\n"
                f"📱 Number: {test_number}\n"
                f"🔑 OTP: {test_otp}"
            )
        else:
            await update.message.reply_text(f"❌ Failed to send. Status: {resp.status_code}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# ---- Default emojis for group ----
DEFAULT_EMOJIS = {
    "countries": {},
    "services": {},
}


# ==================== BACK TO MAIN MENU CALLBACK ====================
async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    await query.answer()
    await show_main_menu(query, user_id, first_name, context)


# ==================== WITHDRAW CALLBACK ====================
async def withdraw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
    await query.answer()
    await show_withdraw(update, query.from_user.id, context)


# ==================== SEND STOCK MANAGEMENT MENU ====================
async def send_stock_management_menu(target, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    text = f"{emoji_tag(CUSTOM_EMOJIS['STOCK_MANAGER'], '📦')} <b>STOCK MANAGEMENT</b>\n\nSelect an action below:"
    kb = stock_management_menu_keyboard()
    if isinstance(target, CallbackQuery):
        await edit_or_send(target, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)
    else:
        await send_clean_message(target, context, text, reply_markup=kb, parse_mode='HTML', auto_delete=False)


# ==================== FINAL — RUN BOT ====================
if __name__ == "__main__":
    main()
