# THIS PREMIUM BOT IS DEVELOPED BY RAKESH DEV
# TG: @SR_ADMIN_RAKESH

import asyncio, json, os, re, sqlite3, threading, tempfile, zipfile, shutil, sys, logging
from datetime import datetime, timedelta
import random
import html
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
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# ================= GLOBAL STATE (DEFINED EARLY) =================
admin_mode = {}
admin_panel_state = {}
admin_temp_data = {}
last_activation_data = {}
polling_tasks = {}
cdr_polling_tasks = {}
polling_cycle_counts = {}
application = None

# ================= CONFIGURATION =================
BOT_TOKEN = "8769374062:AAHTIxugF2XHffjlg6p2Xrd4Br-OUezroro"
SUPER_ADMIN_IDS = [8744359777]
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
BOT_USERNAME = ""  # will be fetched

AUTO_DELETE_DELAY = 2
MAIN_MENU_DELETE = 120
OTP_GROUP_URL = "https://t.me/AIR_OTP"
MIN_WITHDRAW = 0.1
ADMIN_WHATSAPP = "https://wa.me/8801962636806"
ADMIN_TELEGRAM = "t.me/SR_ADMIN_RAKESH"
ADMIN2_WHATSAPP = ""
ADMIN2_TELEGRAM = ""
GROUP_ID = "-1003716770621","-1004309109716"
CHANNEL_URL = "https://t.me/A_S_COMMUNITY_9_x"
BOT_URL = "https://t.me/AIR_NUMBER_BOT?start=1"

GROUP_IDS = []
if GROUP_ID:
    if isinstance(GROUP_ID, (list, tuple)):
        GROUP_IDS = [int(str(gid).strip()) for gid in GROUP_ID if str(gid).strip()]
    elif isinstance(GROUP_ID, str):
        if ',' in GROUP_ID:
            GROUP_IDS = [int(gid.strip()) for gid in GROUP_ID.split(',') if gid.strip()]
        else:
            GROUP_IDS = [int(GROUP_ID.strip())] if GROUP_ID.strip() else []
    else:
        try:
            GROUP_IDS = [int(GROUP_ID)]
        except (ValueError, TypeError):
            GROUP_IDS = []

# ================= EMOJIS (PREMIUM) =================
GLOBAL_BODY_EMOJIS = {
    "🇺🇸": "5913463998522592692", "🇺🇦": "5911406692007941050", "🇵🇱": "5913550391789752571",
    "🇰🇿": "5913724621433082323", "🇨🇳": "5913779335021466780", "🇦🇿": "5911197578640233518",
    "🇪🇺": "5911106310585193018", "🇦🇲": "5913272455866093666", "🇷🇺": "5913274246867456342",
    "🇺🇿": "5911051846104912282", "🇩🇪": "5911096835887337583", "🇯🇵": "5913293711659241040",
    "🇹🇷": "5910995113881901195", "🇧🇾": "5911011185649521599", "🇬🇧": "5913443365499703513",
    "🇮🇳": "5913754823643107921", "🇧🇷": "5911148568768418614", "🇿🇲": "5913564754160389778",
    "🇾🇪": "5913346492512341993", "🏴󠁧󠁢󠁷󠁬󠁳󠁿": "5911297801702084799", "🇻🇳": "5913428887164949581",
    "🇻🇦": "5911211932420938860", "🇻🇺": "5913511535220625585", "🇺🇾": "5913623088406204470",
    "🇦🇪": "5913726554168365343", "🇺🇬": "5913488939397681980", "🇹🇲": "5913315521503170180",
    "🇹🇳": "5911332947419468671", "🇹🇹": "5911228635548750294", "🇹🇬": "5913423260757790970",
    "🇹🇭": "5913617968805187987", "🇹🇿": "5911418949844603556", "🇹🇯": "5911287639809463107",
    "🇨🇭": "5913271227505448072", "🇸🇪": "5911156510162949403", "🇸🇿": "5913374525763883286",
    "🇸🇷": "5913275539652611719", "🇸🇩": "5911387497799094470", "🇪🇸": "5911193287967904547",
    "🇱🇰": "5911293163137406640", "🇸🇸": "5911406262511211744", "🇿🇦": "5911203119148044594",
    "🇸🇴": "5911397852965244436", "🇸🇧": "5911482712929080608", "🇸🇮": "5913431983836368644",
    "🇸🇰": "5913751666842145020", "🇸🇬": "5911531460808051849", "🇸🇱": "5911210450657218661",
    "🇸🇨": "5911185183364616913", "🇷🇸": "5913592598433369871", "🇸🇳": "5910995302860461643",
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿": "5911460091336331851", "🇸🇹": "5913574331937462345", "🇸🇲": "5913587968458625465",
    "🇼🇸": "5913325971158602854", "🇰🇳": "5913691898077253637", "🇻🇨": "5911318941531116255",
    "🇱🇨": "5911243659344351824", "🇵🇸": "5913684768431541668", "🇷🇼": "5911455229433352234",
    "🇷🇴": "5913460373570195273", "🇶🇦": "5911260864983339619", "🇵🇷": "5911504350974317480",
    "🇵🇹": "5911023653939581472", "🇵🇭": "5911268638874145162", "🇵🇪": "5911207993935925780",
    "🇵🇾": "5911014265141072316", "🇵🇬": "5911107251183030903", "🇵🇦": "5913428968769327174",
    "🇵🇼": "5911283903187915549", "🇵🇰": "5913705895375672082", "🇴🇲": "5913570801474343473",
    "🇳🇴": "5913617397574537046", "🇳🇬": "5911143844304393105", "🇳🇪": "5911270086278124251",
    "🇳🇿": "5913640044937089340", "🇳🇱": "5913367645226275100", "🇳🇵": "5913496520014958723",
    "🇳🇦": "5911108535378252443", "🇲🇿": "5911333419865871464", "🇲🇦": "5911482111633658301",
    "🇲🇪": "5913239436157522151", "🇲🇳": "5911041383564580038", "🇲🇨": "5911245347266500057",
    "🇲🇩": "5913456847402045950", "🇲🇻": "5913501399097806832", "🇲🇱": "5911305266355245916",
    "🇲🇹": "5911023714069123567", "🇧🇲": "5913680005312811090", "🇲🇶": "5911378005921370347",
    "🇲🇭": "5913235935759175692", "🇲🇺": "5913291113204027321", "🇲🇽": "5913687302462246518",
    "🇫🇲": "5911271104185373336", "🇲🇾": "5913654360063087453", "🇰🇪": "5911154710571651231",
    "🇲🇬": "5913766918271012920", "🇲🇰": "5913394029210374721", "🇱🇺": "5913390842344640293",
    "🇱🇹": "5911172315642597775", "🇱🇮": "5911166650580734660", "🇱🇾": "5911236989260140996",
    "🇱🇷": "5913324167272337727", "🇰🇮": "5911294443037660118", "🇽🇰": "5911433681582429010",
    "🇰🇼": "5913290705182134003", "🇰🇬": "5911202161370337549", "🇱🇦": "5913718526874489279",
    "🇱🇻": "5913738489882480243", "🇱🇧": "5911504273664905447", "🇱🇸": "5911059881988723711",
    "🇮🇩": "5913479361620611038", "🇮🇷": "5911308891307643032", "🇮🇶": "5911382442622587735",
    "🇮🇪": "5913440715504881532", "🇮🇱": "5911471936856134692", "🇮🇹": "5913688444923547525",
    "🇯🇲": "5913232280742006526", "🇯🇴": "5913234136167878475", "🇮🇸": "5911047899029967246",
    "🇭🇺": "5913767635530551104", "🇭🇳": "5911406889576436289", "🇭🇹": "5913459789454643194",
    "🇬🇾": "5913579412883771480", "🇬🇼": "5911398694778836149", "🇬🇳": "5913471858312744319",
    "🇬🇹": "5913324858762072330", "🇬🇩": "5913228063084121946", "🇬🇷": "5911210399117611448",
    "🇬🇭": "5913391155877252952", "🇬🇪": "5913434771270144023", "🇬🇲": "5913657267755945883",
    "🇬🇦": "5911037896051137264", "🇫🇷": "5913605586414473124", "🇫🇮": "5911041344909873378",
    "🇫🇯": "5911393832875856716", "🇪🇹": "5911078333168227043", "🇩🇴": "5911152099231536123",
    "🇹🇱": "5911141915864076479", "🇪🇨": "5911273865849347408", "🇪🇬": "5913694831539916769",
    "🇸🇻": "5913238624408703010", "🏴󠁧󠁢󠁥󠁮󠁧󠁿": "5913475719488344315", "🇪🇪": "5910986042910969906",
    "🇩🇲": "5911377121158107430", "🇩🇯": "5911407709915190157", "🇩🇰": "5911206009661034712",
    "🇨🇾": "5911023550860366409", "🇭🇷": "5913692684056269311", "🇨🇷": "5911261745451635030",
    "🇨🇬": "5911338788574990168", "🇨🇩": "5913770362834783827", "🇰🇲": "5911338582416560604",
    "🇰🇭": "5913699998385573485", "🇨🇲": "5911172109484167745", "🇨🇦": "5913623736946265914",
    "🇨🇻": "5913571501554012193", "🇨🇫": "5913443245240619222", "🇹🇩": "5913299849167507310",
    "🇨🇿": "5911198691036764307", "🇨🇱": "5911470957603592832", "🇨🇴": "5913773060074246009",
    "🇧🇮": "5913766441529642752", "🇧🇼": "5911513782722499475", "🇧🇦": "5913700002680541032",
    "🇧🇴": "5913638795101606133", "🇧🇹": "5913236734623093021", "🇧🇯": "5913735869952430547",
    "🇦🇷": "5913573356979884082", "🇦🇺": "5913632326880858455", "🇦🇹": "5911338831524664592",
    "🇧🇸": "5911451643135660214", "🇧🇭": "5913581663446634403", "🇧🇩": "5911365056594973179",
    "🇧🇧": "5911016996740272263", "🇧🇪": "5913529642802745141", "🇧🇿": "5913355005137522807",
    "🇦🇬": "5913389025573475085", "🇦🇴": "5913753316109586411", "🇦🇩": "5911314702398396902",
    "🇩🇿": "5913782968563800236", "🇦🇱": "5911357458797826163", "🇦🇫": "5913492040364068694",
    "🇿🇼": "5911092502265336396", "🇨🇺": "5431551436502611633", "🇰🇵": "5434142701941437163",
    "🇻🇪": "5434009132753499322", "🇸🇾": "5433910876786670092", "🇲🇲": "5433666360003540231",
    "🇳🇮": "5334807849418003620", "🇰🇷": "5913371673905598425", "🇬🇶": "5911306279967529251",
    "🇬🇱": "5292014752283774878", "🇫🇴": "5296469342039327674", "🇨🇮": "5222233374948602940",
    "🇧🇳": "5911336409163109113", "🇧🇬": "5294329219965272288", "🇧🇫": "5913407764515786948",
    "🇪🇷": "5433723401464198287", "🇲🇼": "5433968339154122439", "🇲🇷": "5433859405898594234",
    "🇳🇷": "5434131139889478358", "🇸🇦": "4985897134424328239", "🇹🇴": "5433640100573491806",
    "🇹🇻": "5433684690923961019", "🇹🇼": "5366187256937726720", "🇭🇰": "5292166459118606932",
    "🇲🇴": "6323557758096377611"
}
def apply_emojis(text):
    for char, eid in GLOBAL_BODY_EMOJIS.items():
        text = text.replace(char, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>')
    return text

WELCOME_WAVE = "5199885118214255386"
WELCOME_THINK = "5314563983422798645"
INBOX_EMOJI = "5472239203590888751"
MONEY_EMOJI = "5805602131176069048"
MAIN_MENU_EMOJI = "5438499684270238914"
HEADER_EMOJI_1 = "6282641460093260838"
HEADER_EMOJI_2 = "6267315814190290529"
SUPPORT_EMOJI = "6264853036993090338"
EMOJI_SEPARATOR = "5213333270703387541"
EMOJI_PREFIX = "4958725487682650920"
EMOJI_OTP_BUTTON = "6206420230269310869"
EMOJI_CHANNEL_BUTTON = "6204010762206189094"
EMOJI_BOT_BUTTON = "5339267587337370029"
LEFT_ARROW_EMOJI = "6068830682359010545"
SEND_EMOJI = "5433614747381538714"
SKIP_EMOJI = "6267262260243076354"
DATABASE_EMOJI = "5818955300463447293"

CUSTOM_EMOJIS.update({
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
    "REMOVE_STOCK": "6206108815075579644",
    "STOCK_STATUS": "4958506272551863292",
    "TOGGLE_STOCK": "4956583802240500602",
    "YES": "4956721670690702265",
    "NO": "6206110936789423908",
    "GET_NUMBER": "5303449763406954093",
    "NEW_NUMBER": "5877410604225924969",
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
    "BACK": "6118297066247558366",
    "DELETE": "6206108815075579644",
    "ADMIN": "6206319341487527808",
    "UPLOAD": "6206046503690048595",
    "CANCEL": "6267000941547885720",
    "BROADCAST": "6206080502651164081",
    "ADD": "6206375377925839184",
    "GIVEAWAY": "6282893896796082998",
    "STATS": "6266936886405633043",
    "PACKAGE": "5463412319948148591",
    "GEAR": "6206236607532504295",
    "CHANGE_COUNTRY": "5188540541922480562",
    "GREEN_CIRCLE": "5339112148175959615",
    "RED_CIRCLE": "5337017423906226569",
    "CLOCK": "6267229004311303657",
    "DEFAULT_FLAG": "5188540541922480562",
    "DEFAULT_SERVICE": "5465590345108589516",
    "JOIN_OTP_GROUP": "6204010762206189094",
    "API_LIST_ICON": "5411225014148014586",
    "API_LIST_INTERVAL_ICON": "6235253239080555488",
    "API_FIELD_PLACEHOLDERS": "6267264360482084046",
    "CDR_PANEL": "6206236607532504295",
    "CDR_LOGIN_URL": "6285048454255220485",
    "CDR_SMSCDR_URL": "6267172559851099903",
    "CDR_USERNAME": "5818775306974006843",
    "CDR_PASSWORD": "5821453562680448557",
    "CDR_CAPTCHA": "5926860096008098405",
    "CDR_SHOW_REPORT": "6206046503690048595",
    "CDR_AJAX_LOAD": "6267264360482084046",
    "CDR_SESSION_ACTIVE": "5339112148175959615",
    "CDR_SESSION_EXPIRED": "5337017423906226569",
    "CDR_FIELD_NUMBER": "5877410604225924969",
    "CDR_FIELD_MESSAGE": "5980911993140284450",
    "CDR_FIELD_TIMESTAMP": "6285240160120477644",
    "CDR_FIELD_SERVICE": "5818967150278218011",
    "CDR_FIELD_ROW": "4958506272551863292",
    "CDR_STATS": "6266936886405633043",
    "CDR_LOGS": "5818774589714468177",
    "CDR_TEST_LOGIN": "5978568938156461643",
    "CDR_TEST_FETCH": "6204108584381322968",
    "CDR_FORCE_POLL": "6282893896796082998",
    "CDR_ACTIVE": "5339112148175959615",
    "CDR_INACTIVE": "5337017423906226569",
    "CDR_DELETE": "6206108815075579644",
    "CDR_EDIT": "6204162490515855272",
    "CDR_BACK": "6118297066247558366",
})

# ================= DATABASE SETUP =================
DB_DIR = "NUMBER-PANEL-DATA"
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "mrisbrand_master.db")
USER_DATA_FILE = os.path.join(DB_DIR, "user_data.json")

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
              banned INTEGER DEFAULT 0,
              persistent_message_id INTEGER DEFAULT NULL,
              total_invites INTEGER DEFAULT 0,
              invited_by INTEGER DEFAULT NULL)''')

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
              panel_name TEXT, base_url TEXT, token TEXT, interval_sec INTEGER,
              active INTEGER DEFAULT 1, endpoint TEXT DEFAULT '/', method TEXT DEFAULT 'GET',
              headers TEXT, body_template TEXT, response_type TEXT DEFAULT 'json',
              otp_list_path TEXT DEFAULT 'data', number_path TEXT DEFAULT 'num',
              message_path TEXT DEFAULT 'message', country_path TEXT DEFAULT 'country',
              service_path TEXT DEFAULT 'cli', timestamp_path TEXT DEFAULT 'dt',
              success_path TEXT DEFAULT 'status', success_value TEXT DEFAULT 'success',
              max_records INTEGER DEFAULT 200, retry_count INTEGER DEFAULT 3,
              retry_delay INTEGER DEFAULT 5, error_count INTEGER DEFAULT 0,
              last_poll_time TEXT, total_otps INTEGER DEFAULT 0, last_otp_time TEXT,
              created_by INTEGER, created_at TEXT, updated_at TEXT,
              placeholder_config TEXT DEFAULT '{}', curl_command TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS api_logs
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              api_id INTEGER, timestamp TEXT, status TEXT, message TEXT, otp_count INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS cdr_panels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    panel_name TEXT, login_url TEXT, smscdr_url TEXT,
    username TEXT, password TEXT,
    number_field TEXT, message_field TEXT, timestamp_field TEXT, service_field TEXT,
    interval_sec INTEGER DEFAULT 30, active INTEGER DEFAULT 1,
    last_poll_time TEXT, total_otps INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0, last_error TEXT,
    created_by INTEGER, created_at TEXT, updated_at TEXT,
    cookie_data TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS cdr_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    panel_id INTEGER, timestamp TEXT, status TEXT, message TEXT, otp_count INTEGER)''')

# Bot settings table
c.execute('''CREATE TABLE IF NOT EXISTS bot_settings (
    key TEXT PRIMARY KEY, value TEXT)''')
# Insert default settings if not present
default_settings = {
    "withdraw_on": "True",
    "min_withdraw": "10.0",
    "support_link": "",
    "w_group": "",
    "auto_br_on": "False",
    "auto_br_interval": "60",
    "cooldown": "5",
    "num_req": "1",
    "w_methods": '["bKash", "Nagad"]',
    "otp_default_rate": "0.5",
    "otp_service_rates": "{}",
    "main_channel_link": "",
    "refer_reward": "0.2",
    "force_join_status": "False",
    "force_join_channels": "[]"
}
for key, val in default_settings.items():
    c.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)", (key, val))
conn.commit()

# Add new columns if missing
for col in ['balance', 'withdrawn', 'total_otp', 'remove_cc', 'banned', 'last_bot_message_id', 'keyboard_message_id', 'persistent_message_id', 'total_invites', 'invited_by']:
    try:
        c.execute(f"ALTER TABLE users ADD COLUMN {col} {'REAL' if col in ['balance','withdrawn'] else 'INTEGER'} DEFAULT 0")
    except sqlite3.OperationalError:
        pass
try:
    c.execute("ALTER TABLE services ADD COLUMN emoji_id TEXT DEFAULT ''")
except sqlite3.OperationalError:
    pass

default_services = ["WhatsApp", "Telegram", "Facebook", "IMO", "Google", "Tinder", "Uber", "Instagram", "Twitter", "Snapchat"]
for service in default_services:
    c.execute("INSERT OR IGNORE INTO services (name, display_name, active, emoji_id) VALUES (?, ?, 1, '')", (service, service))
conn.commit()
print("✅ Database setup completed")

# ================= HELPER FUNCTIONS (DEFINED EARLY) =================
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

def emoji_tag(emoji_id: str, fallback: str = " ") -> str:
    if not emoji_id or not emoji_id.isdigit() or len(emoji_id) < 10:
        return fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

def blockquote(text: str) -> str:
    return f'<blockquote>{text}</blockquote>'

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

# ================= COUNTRY MAP (ONLY BANGLADESH AS DEFAULT) =================
COUNTRY_CODE_MAP = {
    "1": ("US", "🇺🇸", "United States / Canada"),
    "7": ("RU", "🇷🇺", "Russia / Kazakhstan"),
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
    "247": ("AC", "🇦🇨", "Ascension Island"),
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
    "262": ("RE", "🇷🇪", "Reunion / Mayotte"),
    "263": ("ZW", "🇿🇼", "Zimbabwe"),
    "264": ("NA", "🇳🇦", "Namibia"),
    "265": ("MW", "🇲🇼", "Malawi"),
    "266": ("LS", "🇱🇸", "Lesotho"),
    "267": ("BW", "🇧🇼", "Botswana"),
    "268": ("SZ", "🇸🇿", "Eswatini"),
    "269": ("KM", "🇰🇲", "Comoros"),
    "290": ("SH", "🇸🇭", "Saint Helena / Tristan da Cunha"),
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
    "358": ("FI", "🇫🇮", "Finland / Åland Islands"),
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
    "379": ("VA", "🇻🇦", "Vatican City"),
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
    "508": ("PM", "🇵🇲", "Saint Pierre and Miquelon"),
    "509": ("HT", "🇭🇹", "Haiti"),
    "590": ("GP", "🇬🇵", "Guadeloupe / Saint Martin / Saint Barthélemy"),
    "591": ("BO", "🇧🇴", "Bolivia"),
    "592": ("GY", "🇬🇾", "Guyana"),
    "593": ("EC", "🇪🇨", "Ecuador"),
    "594": ("GF", "🇬🇫", "French Guiana"),
    "595": ("PY", "🇵🇾", "Paraguay"),
    "596": ("MQ", "🇲🇶", "Martinique"),
    "597": ("SR", "🇸🇷", "Suriname"),
    "598": ("UY", "🇺🇾", "Uruguay"),
    "599": ("CW", "🇨🇼", "Curaçao / Caribbean Netherlands"),
    "670": ("TL", "🇹🇱", "East Timor"),
    "672": ("NF", "🇳🇫", "Norfolk Island / Australian External Territories"),
    "673": ("BN", "🇧🇳", "Brunei"),
    "674": ("NR", "🇳🇷", "Nauru"),
    "675": ("PG", "🇵🇬", "Papua New Guinea"),
    "676": ("TO", "🇹🇴", "Tonga"),
    "677": ("SB", "🇸🇧", "Solomon Islands"),
    "678": ("VU", "🇻🇺", "Vanuatu"),
    "679": ("FJ", "🇫🇯", "Fiji"),
    "680": ("PW", "🇵🇼", "Palau"),
    "681": ("WF", "🇼🇫", "Wallis and Futuna"),
    "682": ("CK", "🇨🇰", "Cook Islands"),
    "683": ("NU", "🇳🇺", "Niue"),
    "685": ("WS", "🇼🇸", "Samoa"),
    "686": ("KI", "🇰🇮", "Kiribati"),
    "687": ("NC", "🇳🇨", "New Caledonia"),
    "688": ("TV", "🇹🇻", "Tuvalu"),
    "689": ("PF", "🇵🇫", "French Polynesia"),
    "690": ("TK", "🇹🇰", "Tokelau"),
    "691": ("FM", "🇫🇲", "Micronesia"),
    "692": ("MH", "🇲🇭", "Marshall Islands"),
    "850": ("KP", "🇰🇵", "North Korea"),
    "852": ("HK", "🇭🇰", "Hong Kong"),
    "853": ("MO", "🇲🇴", "Macau"),
    "855": ("KH", "🇰🇭", "Cambodia"),
    "856": ("LA", "🇱🇦", "Laos"),
    "880": ("BD", "🇧🇩", "Bangladesh"),
    "886": ("TW", "🇹🇼", "Taiwan"),
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
    "1242": ("BS", "🇧🇸", "Bahamas"),
    "1246": ("BB", "🇧🇧", "Barbados"),
    "1264": ("AI", "🇦🇮", "Anguilla"),
    "1268": ("AG", "🇦🇬", "Antigua and Barbuda"),
    "1284": ("VG", "🇻🇬", "British Virgin Islands"),
    "1340": ("VI", "🇻🇮", "U.S. Virgin Islands"),
    "1345": ("KY", "🇰🇾", "Cayman Islands"),
    "1441": ("BM", "🇧🇲", "Bermuda"),
    "1473": ("GD", "🇬🇩", "Grenada"),
    "1649": ("TC", "🇹🇨", "Turks and Caicos"),
    "1664": ("MS", "🇲🇸", "Montserrat"),
    "1670": ("MP", "🇲🇵", "Northern Mariana Islands"),
    "1671": ("GU", "🇬🇺", "Guam"),
    "1684": ("AS", "🇦🇸", "American Samoa"),
    "1721": ("SX", "🇸🇽", "Sint Maarten"),
    "1758": ("LC", "🇱🇨", "Saint Lucia"),
    "1767": ("DM", "🇩🇲", "Dominica"),
    "1784": ("VC", "🇻🇨", "Saint Vincent and the Grenadines"),
    "1787": ("PR", "🇵🇷", "Puerto Rico"),
    "1809": ("DO", "🇩🇴", "Dominican Republic"),
    "1829": ("DO", "🇩🇴", "Dominican Republic"),
    "1849": ("DO", "🇩🇴", "Dominican Republic"),
    "1868": ("TT", "🇹🇹", "Trinidad and Tobago"),
    "1869": ("KN", "🇰🇳", "Saint Kitts and Nevis"),
    "1876": ("JM", "🇯🇲", "Jamaica"),
    "1939": ("PR", "🇵🇷", "Puerto Rico"),
}
ISO_TO_INFO = {}
for code, val in COUNTRY_CODE_MAP.items():
    if len(val) >= 3:
        iso, flag, name = val[0], val[1], val[2]
        ISO_TO_INFO[iso] = (flag, name)

def get_country_code(country_name):
    if not country_name:
        return ""
    lower = country_name.lower()
    for code, (iso, flag, name) in COUNTRY_CODE_MAP.items():
        if lower == name.lower() or lower == iso.lower():
            return iso
    return country_name.upper()[:2]

def get_country_from_number(number: str) -> str | None:
    if not number:
        return None
    clean = number.replace('+', '').replace(' ', '').strip()
    for code in sorted(COUNTRY_CODE_MAP.keys(), key=len, reverse=True):
        if clean.startswith(code):
            return COUNTRY_CODE_MAP[code][2] if len(COUNTRY_CODE_MAP[code]) >= 3 else None
    return None

# ================= BOT SETTINGS (AIR CONTROL) =================
def get_bot_setting(key, default=None):
    row = db_fetch_one("SELECT value FROM bot_settings WHERE key=?", (key,))
    if row:
        val = row[0]
        # Try to parse JSON if it looks like a list/dict
        if val.startswith('[') or val.startswith('{'):
            try:
                return json.loads(val)
            except:
                pass
        return val
    return default

def set_bot_setting(key, value):
    if isinstance(value, (list, dict)):
        value = json.dumps(value)
    db_exec("INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, str(value)))

def load_bot_settings():
    settings = {}
    rows = db_fetch_all("SELECT key, value FROM bot_settings")
    for key, val in rows:
        if val.startswith('[') or val.startswith('{'):
            try:
                settings[key] = json.loads(val)
            except:
                settings[key] = val
        else:
            settings[key] = val
    return settings

bot_settings = load_bot_settings()  # Now db_fetch_all is defined

# Convenience functions
def get_setting(key, default=None):
    return bot_settings.get(key, default)

def update_setting(key, value):
    bot_settings[key] = value
    set_bot_setting(key, value)

# Force join helpers
def get_force_join_channels():
    val = get_setting('force_join_channels', [])
    if isinstance(val, str):
        try:
            return json.loads(val)
        except:
            return []
    return val

def set_force_join_channels(channels):
    update_setting('force_join_channels', channels)

def get_force_join_status():
    val = get_setting('force_join_status', 'False')
    return val in ('True', 'true', True)

def set_force_join_status(status):
    update_setting('force_join_status', str(status))

# ================= COUNTRIES =================
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
            "Bangladesh": {"code": "+880", "iso": "BD", "payout": "0.001$", "emoji_id": "5911365056594973179"},
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

def country_flag_emoji(country_name: str) -> str:
    eid = get_country_info(country_name).get("emoji_id") or CUSTOM_EMOJIS.get("DEFAULT_FLAG", "")
    return emoji_tag(eid, "🏁")

def service_emoji_tag(service_name: str) -> str:
    row = db_fetch_one("SELECT emoji_id FROM services WHERE LOWER(name) = LOWER(?)", (service_name,))
    eid = row[0] if row and row[0] else CUSTOM_EMOJIS.get("DEFAULT_SERVICE", "")
    return emoji_tag(eid, "⚙️")

# ================= OTP DETECTION =================
def extract_otp_from_message(message: str) -> str | None:
    if not message:
        return None
    patterns = [
        r'(?:otp|code|pin|verification|passcode|auth|security)\s*[:=]?\s*(\d{4,8})',
        r'(?:otp|code|pin|verification|passcode|auth|security)\s+is\s+(\d{4,8})',
        r'(?:otp|code|pin|verification|passcode|auth|security)\s+(\d{4,8})',
        r'(?:ওটিপি|ভেরিফিকেশন|পিন|কোড)\s*[:=]?\s*(\d{4,8})',
        r'(?:ओटीपी|कोड|पिन|सत्यापन)\s*[:=]?\s*(\d{4,8})',
        r'(?:código|verificación|pin|clave)\s*[:=]?\s*(\d{4,8})',
        r'(?:رمز|التحقق|كلمة المرور)\s*[:=]?\s*(\d{4,8})',
        r'\b(\d{3,4}[-.\s]\d{3,4})\b',
        r'\b(\d{2,3}[-.\s]\d{2,3}[-.\s]\d{2,3})\b',
        r'\[(\d{4,8})\]',
        r'\((\d{4,8})\)',
        r'\b(\d\s\d\s\d\s\d\s\d\s\d)\b',
        r'\b(\d\s\d\s\d\s\d)\b',
        r'\b(\d{4,8})\b',
    ]
    all_matches = []
    for pat in patterns:
        matches = re.findall(pat, message, re.IGNORECASE)
        for m in matches:
            cleaned = re.sub(r'[-\s.]', '', str(m))
            if 4 <= len(cleaned) <= 8:
                if len(cleaned) == 4 and cleaned.startswith(('19', '20')):
                    continue
                all_matches.append(cleaned)
    if not all_matches:
        return None
    keywords = ['otp', 'code', 'pin', 'verification', 'instagram', 'whatsapp', 'telegram', 'facebook']
    scored = []
    for cand in all_matches:
        score = 0
        if len(cand) == 6:
            score += 10
        elif len(cand) in (4, 5):
            score += 5
        idx = message.find(cand)
        if idx != -1:
            score += max(0, 100 - idx // 10)
            msg_lower = message.lower()
            for kw in keywords:
                kw_pos = msg_lower.find(kw)
                if kw_pos != -1:
                    dist = abs(idx - kw_pos)
                    if dist < 20:
                        score += 30
                    elif dist < 50:
                        score += 15
        scored.append((cand, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[0]
    if best[1] > 0:
        return best[0]
    else:
        return all_matches[0]

def extract_all_otps_from_message(message: str) -> list[str]:
    if not message:
        return []
    nums = re.findall(r'\b(\d{4,8})\b', message)
    filtered = [n for n in nums if not (len(n)==4 and n.startswith(('19','20')))]
    return list(set(filtered))

# ================= FORMAT NUMBERS =================
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
        f'{emoji_tag(EMOJI_EYE, "👁️")} <b>STOCK</b> '
        f'{emoji_tag(EMOJI_PACKAGE, "📦")} <b>ADDED SUCCESSFULLY</b> '
        f'{emoji_tag(EMOJI_CHECK, "✅")}\n\n'
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

# ================= KEYBOARDS =================
BTN_GET_NUMBER = "GET NUMBER"
BTN_BALANCE = "BALANCE"
BTN_SUPPORT = "SUPPORT"
BTN_ADMIN = "Admin Panel"
BTN_INVITE = "INVITE FRIEND"

def bottom_menu_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    rows = [
        [
            KeyboardButton(BTN_GET_NUMBER, style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("GET_NUMBER", ""))),
            KeyboardButton(BTN_BALANCE, style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon("5312123810638483121")),
        ],
        [
            KeyboardButton(BTN_INVITE, style=KBS.SUCCESS, icon_custom_emoji_id=safe_icon("5384394344859974865")),
            KeyboardButton(BTN_SUPPORT, style=KBS.SUCCESS, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("SUPPORT", ""))),
        ],
    ]
    if is_admin(user_id):
        rows.append([KeyboardButton(BTN_ADMIN, style=KBS.DANGER, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADMIN", "")))])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True, input_field_placeholder="")

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
                                 icon_custom_emoji_id=safe_icon(DATABASE_EMOJI)),
        ],
        # NEW BUTTONS: AIR CONTROL and FORCE JOIN
        [
            InlineKeyboardButton("AIR CONTROL", callback_data="admin_air_control", style=KBS.DANGER,
                                 icon_custom_emoji_id=safe_icon("6206236607532504295")),
            InlineKeyboardButton("FORCE JOIN", callback_data="admin_force_join", style=KBS.PRIMARY,
                                 icon_custom_emoji_id=safe_icon("5429353834881261942")),
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

# ================= AIR CONTROL KEYBOARDS =================
def air_control_keyboard():
    min_w = get_setting('min_withdraw', '10.0')
    ref_r = get_setting('refer_reward', '0.2')
    cooldown = get_setting('cooldown', '5')
    num_req = get_setting('num_req', '1')
    w_group = get_setting('w_group', 'NOT SET')
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"MIN WITHDRAW: {min_w}", callback_data="air_min_w", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon("5352877703043258544")),
         InlineKeyboardButton("OTP CONTROL", callback_data="air_otp_control", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon("5190576863226933563"))],
        [InlineKeyboardButton(f"REFER REWARD: {ref_r}", callback_data="air_ref_r", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon("5420396762189831222")),
         InlineKeyboardButton(f"COOLDOWN: {cooldown}s", callback_data="air_cool", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon("5337172996211648018"))],
        [InlineKeyboardButton(f"NUM/REQ: {num_req}", callback_data="air_num_req", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon("5337132498965010628")),
         InlineKeyboardButton("W. METHODS", callback_data="manage_w_methods", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon("5190899075968441286"))],
        [InlineKeyboardButton(f"W. GROUP: {w_group}", callback_data="air_w_group", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon("5420517437885943844"))],
        [InlineKeyboardButton("BACK", callback_data="back_to_admin", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])

def air_otp_control_keyboard():
    default_rate = get_setting('otp_default_rate', '0.5')
    service_rates = get_setting('otp_service_rates', {})
    rows = [
        [InlineKeyboardButton(f"Default Rate: {default_rate}", callback_data="air_def_rate", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon("5352877703043258544"))],
        [InlineKeyboardButton("Set Service Rate", callback_data="air_srv_rate", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon("5395444784611480792"))]
    ]
    for srv_name, rate in service_rates.items():
        app_info = PREMIUM_APPS.get(srv_name, {"emoji": "📱", "id": "5465590345108589516"})
        rows.append([InlineKeyboardButton(f"Delete: {srv_name} ({rate})", callback_data=f"del_srv_rate_{srv_name}", style=KBS.DANGER,
                                          icon_custom_emoji_id=safe_icon(app_info['id']))])
    rows.append([InlineKeyboardButton("BACK", callback_data="air_control", style=KBS.DANGER,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    return InlineKeyboardMarkup(rows)

def manage_w_methods_keyboard():
    methods = get_setting('w_methods', [])
    rows = []
    for idx, method in enumerate(methods):
        rows.append([InlineKeyboardButton(f"Delete: {method}", callback_data=f"del_w_method_{idx}", style=KBS.DANGER,
                                          icon_custom_emoji_id=safe_icon("5438178416421544431"))])
    rows.append([InlineKeyboardButton("Add Method", callback_data="add_w_method", style=KBS.SUCCESS,
                                      icon_custom_emoji_id=safe_icon("5429501315468270290"))])
    rows.append([InlineKeyboardButton("BACK", callback_data="air_control", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    return InlineKeyboardMarkup(rows)

# ================= FORCE JOIN KEYBOARDS =================
def force_join_keyboard():
    status = get_force_join_status()
    channels = get_force_join_channels()
    kb_rows = []
    status_text = "STATUS: ON" if status else "STATUS: OFF"
    status_icon = "5339112148175959615" if status else "5337017423906226569"
    kb_rows.append([InlineKeyboardButton(status_text, callback_data="toggle_fj", style=KBS.SUCCESS if status else KBS.DANGER,
                                         icon_custom_emoji_id=safe_icon(status_icon))])
    for idx, ch in enumerate(channels):
        name = ch.get('username', ch.get('title', f"Channel {idx}"))
        kb_rows.append([InlineKeyboardButton(f"Delete: {name}", callback_data=f"del_fj_{idx}", style=KBS.DANGER,
                                             icon_custom_emoji_id=safe_icon("5438178416421544431"))])
    kb_rows.append([InlineKeyboardButton("Add Channel", callback_data="add_fj", style=KBS.SUCCESS,
                                         icon_custom_emoji_id=safe_icon("5429501315468270290"))])
    kb_rows.append([InlineKeyboardButton("BACK", callback_data="back_to_admin", style=KBS.PRIMARY,
                                         icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    return InlineKeyboardMarkup(kb_rows)

def force_join_alert_keyboard():
    channels = get_force_join_channels()
    kb_rows = []
    for ch in channels:
        name = ch.get('title', ch.get('username', 'Channel'))
        url = ch.get('invite_link', '')
        if not url and ch.get('username'):
            url = f"https://t.me/{ch['username'].replace('@', '')}"
        kb_rows.append([InlineKeyboardButton(f"JOIN {name}", url=url, style=KBS.PRIMARY)])
    kb_rows.append([InlineKeyboardButton("✅ I HAVE JOINED", callback_data="check_fj_joined", style=KBS.SUCCESS,
                                         icon_custom_emoji_id=safe_icon("4956721670690702265"))])
    return InlineKeyboardMarkup(kb_rows)

# ================= PREMIUM APPS (for service detection) =================
PREMIUM_APPS = {
    "Facebook": {"emoji": "📘", "id": "5429172110520003976"},
    "WhatsApp": {"emoji": "💬", "id": "5429612632430654504"},
    "Telegram": {"emoji": "✈️", "id": "5429136513831057777"},
    "Instagram": {"emoji": "📸", "id": "5429478178479447442"},
    "Google": {"emoji": "🔍", "id": "5429558795015593080"},
    "Microsoft": {"emoji": "🪟", "id": "5979047775470358891"},
    "TikTok": {"emoji": "🎵", "id": "5429132656950419591"},
    "Bkash": {"emoji": "🏦", "id": "5431552076452766597"},
    "Binance": {"emoji": "💱", "id": "5429438106434575354"},
    "Snapchat": {"emoji": "👻", "id": "5429398137468919845"},
    "Uber": {"emoji": "🚗", "id": "5298715455316303708"},
    "Discord": {"emoji": "🎬", "id": "5429594374524676604"},
    "Amazon": {"emoji": "🌟", "id": "5431358656895568355"},
    "Viber": {"emoji": "💜", "id": "5429470576387335368"},
    "Twitter": {"emoji": "🐦", "id": "5431899135580087595"},
    "Netflix": {"emoji": "🎥", "id": "5431641055290235797"},
    "Spotify": {"emoji": "🎵", "id": "5429235839244739644"},
    "Foodpanda": {"emoji": "🐼", "id": "5336879280578138635"},
    "Pathao": {"emoji": "🛵", "id": "5336879280578138635"},
    "ChatGPT": {"emoji": "🤖", "id": "5429503209548847635"},
    "Imo": {"emoji": "💭", "id": "5431378937731129128"},
    "Other": {"emoji": "📶", "id": "5429353834881261942"}
}

SERVICE_SMS_KEYWORDS = {
    "Facebook": ["facebook", "fb code", "fb", "meta"],
    "WhatsApp": ["whats", "whatsapp", "whatsapp code"],
    "Telegram": ["telegram", "tg code"],
    "Instagram": ["instagram", "ig code"],
    "Google": ["google", "Googl"],
    "Microsoft": ["microsoft", "micro", "Microsof", "xbox"],
    "TikTok": ["tiktok", "tik tok"],
    "Bkash": ["bkash"],
    "Binance": ["binance", "bnb"],
    "Snapchat": ["snapchat", "snap"],
    "Uber": ["uber"],
    "Discord": ["discord"],
    "Amazon": ["amazon", "aws"],
    "Viber": ["viber"],
    "Twitter": ["twitter", "x.com"],
    "Netflix": ["netflix"],
    "Spotify": ["spotify"],
    "Foodpanda": ["foodpanda", "panda"],
    "Pathao": ["pathao"],
    "ChatGPT": ["openai", "chatgpt"],
    "Imo": ["imo code", "imo"]
}

def detect_service(message_text, raw_sid=""):
    msg_lower = str(message_text).lower()
    sid_lower = str(raw_sid).lower()
    for service, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf'\b{re.escape(kw)}\b', msg_lower) or kw in msg_lower:
                return service
    for service in PREMIUM_APPS.keys():
        if service.lower() in sid_lower:
            return service
    return "Other"

# ================= ZEBRA-STYLE OTP FORMAT =================
def detect_language(text):
    try:
        from langdetect import detect
        lang_code = detect(text)
        language_map = {
            'en': 'English', 'bn': 'Bangla', 'hi': 'Hindi', 'ur': 'Urdu',
            'ar': 'Arabic', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
            'ko': 'Korean', 'zh-cn': 'Chinese', 'ta': 'Tamil', 'te': 'Telugu',
            'mr': 'Marathi', 'gu': 'Gujarati', 'kn': 'Kannada', 'ml': 'Malayalam',
            'or': 'Odia', 'pa': 'Punjabi', 'ne': 'Nepali', 'si': 'Sinhala',
            'th': 'Thai', 'vi': 'Vietnamese', 'id': 'Indonesian', 'ms': 'Malay',
            'tl': 'Tagalog', 'tr': 'Turkish', 'fa': 'Persian', 'he': 'Hebrew',
            'el': 'Greek', 'nl': 'Dutch', 'pl': 'Polish', 'sv': 'Swedish',
            'no': 'Norwegian', 'da': 'Danish', 'fi': 'Finnish'
        }
        return language_map.get(lang_code, lang_code.upper())
    except:
        return "Unknown"

def format_group_otp_rich(entry):
    number = entry.get("number", "")
    otp_code = entry.get("otp", "")
    service_name = entry.get("service", "Unknown")
    raw_country = entry.get("country", entry.get("country_code", "?"))
    country_iso = entry.get("country_code", "")
    if not country_iso and raw_country:
        country_iso = get_country_code(raw_country) or "??"

    # Get flag and iso
    flag_emoji = "🏳"
    if country_iso:
        info = ISO_TO_INFO.get(country_iso, ("🏳", ""))
        flag_emoji = info[0] if info else "🏳"
    # Get emoji ID for flag (use default if not in map)
    flag_eid = GLOBAL_BODY_EMOJIS.get(flag_emoji, "")
    if flag_eid:
        country_display = f'<tg-emoji emoji-id="{flag_eid}">{flag_emoji}</tg-emoji><b>{country_iso}</b>'
    else:
        country_display = f'{flag_emoji}<b>{country_iso}</b>'

    # Service emoji
    service_emoji_id = PREMIUM_APPS.get(service_name, PREMIUM_APPS["Other"])["id"]
    service_emoji = PREMIUM_APPS.get(service_name, PREMIUM_APPS["Other"])["emoji"]

    # Masked number
    clean = number.replace('+', '').replace(' ', '').strip()
    if len(clean) >= 7:
        first4 = clean[:4]
        last3 = clean[-3:]
        masked = f'+<b>{first4}</b><tg-emoji emoji-id="6206093275013380471">🫀</tg-emoji><b>{last3}</b>'
    else:
        masked = f'+<b>{clean}</b>'

    # Language
    lang = detect_language(entry.get("message", ""))
    lang_emoji_id = "6206046503690048595"  # envelope

    top_line = (
        f'{country_display} | '
        f'<tg-emoji emoji-id="{service_emoji_id}">{service_emoji}</tg-emoji> | '
        f'{masked} | '
        f'<tg-emoji emoji-id="{lang_emoji_id}">✉️</tg-emoji> <b>{lang}</b>'
    )

    # Full SMS (without details block, just show)
    message_text = entry.get("message", "")[:500]
    sms_safe = message_text.replace("<", "&lt;").replace(">", "&gt;")
    full_text = f"{top_line}\n\n<blockquote><b>{sms_safe}</b></blockquote>"

    # Buttons: OTP copy, NUMBER, CHANNEL
    channel_link = get_setting('main_channel_link', CHANNEL_URL)
    bot_link = BOT_URL

    keyboard = {
        "inline_keyboard": [
            [{"text": otp_code, "icon_custom_emoji_id": "6206420230269310869", "style": "success", "copy_text": {"text": otp_code}}],
            [
                {"text": "𝐍𝐔𝐌𝐁𝐄𝐑", "icon_custom_emoji_id": "5877410604225924969", "style": "primary", "url": bot_link},
                {"text": "𝐂𝐇𝐀𝐍𝐍𝐄𝐋", "icon_custom_emoji_id": "6204010762206189094", "style": "primary", "url": channel_link}
            ]
        ]
    }
    return full_text, keyboard

# ================= PERSISTENT WELCOME =================
async def ensure_persistent_welcome(context: ContextTypes.DEFAULT_TYPE, user_id: int):
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

def start_welcome_html():
    wave = emoji_tag(WELCOME_WAVE, "👋")
    think = emoji_tag(WELCOME_THINK, "🤔")
    inbox = emoji_tag(INBOX_EMOJI, "📩")
    money = emoji_tag(MONEY_EMOJI, "🤑")
    block = blockquote(f"{wave} <b>WELCOME TO OUR 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓</b> {think}")
    sub = f'<b>{inbox} RECEIVE OTP\'S AND START EARNING MONEY {money}</b>'
    return f'{block}\n{sub}'

# ================= AUTO CLEAN =================
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
    try:
        sent = await context.bot.send_message(chat_id=user_id, text=apply_emojis(text), reply_markup=reply_markup, parse_mode=parse_mode)
    except BadRequest as e:
        if "Entity_text_invalid" in str(e) or "Parse" in str(e):
            sent = await context.bot.send_message(chat_id=user_id, text=apply_emojis(text), reply_markup=reply_markup)
        else:
            raise
    db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?", (sent.message_id, user_id))
    if auto_delete and delete_after is None:
        await schedule_delete(context, user_id, sent.message_id)
    elif delete_after:
        await schedule_delete(context, user_id, sent.message_id, delete_after)
    return sent

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    main_text = f'{emoji_tag(MAIN_MENU_EMOJI, "📱")} <b>Main Menu</b>'
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, main_text, reply_markup=bottom_menu_keyboard(user_id), parse_mode='HTML', context=context, auto_delete=False, delete_after=None)
    else:
        await send_clean_message(update, context, main_text, reply_markup=bottom_menu_keyboard(user_id), parse_mode='HTML', auto_delete=False)

# ================= SAFE EDIT/SEND =================
async def edit_or_send(query: CallbackQuery, text: str, reply_markup=None, parse_mode=None, context: ContextTypes.DEFAULT_TYPE = None, auto_delete: bool = True, delete_after: int = None):
    user_id = query.from_user.id
    try:
        await query.edit_message_text(apply_emojis(text), reply_markup=reply_markup, parse_mode=parse_mode)
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
            try:
                sent = await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=apply_emojis(text),
                    reply_markup=reply_markup
                )
            except:
                sent = await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="An error occurred. Please try again.",
                    reply_markup=reply_markup
                )
            db_exec("UPDATE users SET last_bot_message_id=? WHERE user_id=?", (sent.message_id, user_id))
            if auto_delete and delete_after is None:
                await schedule_delete(context, query.message.chat_id, sent.message_id)
            elif delete_after:
                await schedule_delete(context, query.message.chat_id, sent.message_id, delete_after)
            return sent
        return None

async def reply_or_edit(target, text: str, reply_markup=None, parse_mode=None, context: ContextTypes.DEFAULT_TYPE = None, auto_delete: bool = True, delete_after: int = None):
    if isinstance(target, CallbackQuery):
        await edit_or_send(target, text, reply_markup=reply_markup, parse_mode=parse_mode, context=context, auto_delete=auto_delete, delete_after=delete_after)
    elif hasattr(target, 'callback_query') and target.callback_query:
        await edit_or_send(target.callback_query, text, reply_markup=reply_markup, parse_mode=parse_mode, context=context, auto_delete=auto_delete, delete_after=delete_after)
    else:
        if context:
            await send_clean_message(target, context, text, reply_markup=reply_markup, parse_mode=parse_mode, auto_delete=auto_delete, delete_after=delete_after)
        else:
            if hasattr(target, 'message'):
                await target.message.reply_text(apply_emojis(text), reply_markup=reply_markup, parse_mode=parse_mode)
            elif hasattr(target, 'edit_message_text'):
                await target.edit_message_text(apply_emojis(text), reply_markup=reply_markup, parse_mode=parse_mode)

# ================= START =================
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
    # Handle referral
    if update.message and update.message.text and len(update.message.text.split()) > 1:
        params = update.message.text.split()[1]
        if params.isdigit():
            inviter_id = int(params)
            if inviter_id != user_id:
                inviter = db_fetch_one("SELECT user_id FROM users WHERE user_id=?", (inviter_id,))
                if inviter:
                    reward = float(get_setting('refer_reward', '0.2'))
                    db_exec("UPDATE users SET balance = balance + ?, total_invites = total_invites + 1 WHERE user_id = ?", (reward, inviter_id))
                    db_exec("UPDATE users SET invited_by = ? WHERE user_id = ?", (inviter_id, user_id))
                    try:
                        await context.bot.send_message(inviter_id, f"🎉 <b>New Referral!</b>\nSomeone joined using your link. You received {reward} BDT.", parse_mode='HTML')
                    except:
                        pass

# ================= BAN CHECK =================
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
    # Force Join check
    if get_force_join_status() and not is_admin(user_id):
        channels = get_force_join_channels()
        joined = True
        for ch in channels:
            chat_id = ch.get('id')
            if chat_id:
                try:
                    res = requests.get(BASE_URL + f"getChatMember?chat_id={chat_id}&user_id={user_id}").json()
                    if res.get('ok'):
                        status = res['result']['status']
                        if status in ['left', 'kicked']:
                            joined = False
                            break
                    else:
                        joined = False
                        break
                except:
                    joined = False
                    break
        if not joined:
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    "⚠️ <b>Please join our channels to use the bot!</b>",
                    reply_markup=force_join_alert_keyboard(),
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    "⚠️ <b>Please join our channels to use the bot!</b>",
                    reply_markup=force_join_alert_keyboard(),
                    parse_mode='HTML'
                )
            return True
    return False

def is_admin(user_id):
    return db_fetch_one("SELECT user_id FROM admins WHERE user_id=?", (user_id,)) is not None

def is_super_admin(user_id):
    return user_id in SUPER_ADMIN_IDS

# ================= MAIN MENU CALLBACKS =================
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
        f'{emoji_tag(emoji_id, "🆔")} USER ID: <code>{user_id}</code>\n'
        f'{emoji_tag(emoji_money, "💰")} BALANCE: <code>${balance:.3f}</code>\n'
        f'{emoji_tag(emoji_withdraw, "💸")} WITHDRAWED: <code>${withdrawn:.3f}</code>\n'
        f'{emoji_tag(emoji_warning, "⚠️")} MINIMUM WITHDRAW: <code>${get_setting("min_withdraw", "10.0")}</code>\n'
        f'{emoji_tag(emoji_inbox, "📨")} TOTAL OTP: <code>{total_otp}</code>'
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
    min_w = float(get_setting('min_withdraw', '10.0'))
    if balance >= min_w:
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
        need = round(min_w - balance, 3)
        text = (
            f'{emoji_tag("4956611513369494230", "🔻")} YOUR MAIN BALANCE IS LOW{emoji_tag("4956387556594811916", "😞")}\n\n'
            f'{emoji_tag("4958534696645428119", "⚠️")} MINIMUM WITHDRAW: ${min_w}\n'
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

async def show_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db_fetch_one("SELECT first_name, total_invites FROM users WHERE user_id=?", (user_id,))
    if not user_data:
        return
    first_name, total_invites = user_data
    invite_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    ref_reward = get_setting('refer_reward', '0.2')
    text = (
        f"━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id=\"5420145051336485498\">👥</tg-emoji> <b>Referral Program</b>\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id=\"5420517437885943844\">🔗</tg-emoji> <b>Your Invite Link:</b>\n"
        f"<code>{invite_link}</code>\n"
        f"— — — — — — — — — —\n"
        f"<tg-emoji emoji-id=\"5420396762189831222\">🎁</tg-emoji> <b>PER INVITE : {ref_reward} TK</b>\n"
        f"— — — — — — — — — —\n"
        f"<tg-emoji emoji-id=\"5353032893096567467\">📊</tg-emoji> <b>Total Invites:</b> {total_invites}\n"
        f"━━━━━━━━━━━━━━━━━"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("COPY LINK", copy_text=CopyTextButton(invite_link), style=KBS.SUCCESS, icon_custom_emoji_id=safe_icon("5379889727325350343"))]])
    if isinstance(update, CallbackQuery):
        await edit_or_send(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)
    else:
        await send_clean_message(update, context, text, reply_markup=kb, parse_mode='HTML', auto_delete=False)

# ================= ADMIN COMMANDS =================
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

# ================= ADMIN PANEL MENU =================
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

# ================= USER DATA JSON =================
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

# ================= USER MANAGER =================
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

# ================= DATABASE DOWNLOAD/UPLOAD =================
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

# ================= SINGLE DOCUMENT HANDLER =================
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
                    f"✅ {count} numbers loaded for {country}.\nNew service '{service}' detected.\nSend the custom emoji ID (or /skip).",
                    reply_markup=admin_cancel_keyboard())
                return
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
        else:
            admin_temp_data[user_id] = {"pending_file_path": file_path, "pending_filename": document.file_name}
            countries = db_fetch_all("SELECT name FROM countries GROUP BY name ORDER BY name")
            if not countries:
                await update.message.reply_text("No countries defined. Add a country first.", reply_markup=admin_panel_keyboard())
                return
            keyboard = []
            for (cname,) in countries:
                keyboard.append([InlineKeyboardButton(cname, callback_data=f"fu_country|{cname}")])
            keyboard.append([InlineKeyboardButton("Cancel", callback_data="admin_back")])
            await update.message.reply_text("❌ Could not detect country from filename.\nSelect the correct country:", reply_markup=InlineKeyboardMarkup(keyboard))
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

# ================= FORCE UPLOAD CALLBACKS =================
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
    await edit_or_send(query, f"Country: {country}\nSelect the service for this file:", reply_markup=InlineKeyboardMarkup(keyboard), context=context, auto_delete=False)
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
            await edit_or_send(query, f"✅ {count} numbers loaded.\nNew service '{service}' detected.\nSend emoji ID or /skip.", reply_markup=admin_cancel_keyboard(), context=context, auto_delete=False)
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
        await edit_or_send(query, "No valid numbers found in the file.", reply_markup=admin_panel_keyboard(), context=context, auto_delete=False)
    admin_panel_state[user_id] = "main"

# ================= ADMIN TEXT HANDLER =================
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
            if len(parts) < 4:
                await update.message.reply_text("Format: CountryName | Code | ISO | payout | emoji_id")
                return True
            name, code, iso, payout = parts[0], parts[1], parts[2].upper(), parts[3]
            emoji_id = parts[4] if len(parts) >= 5 else ""
            COUNTRIES_DATA[name] = {"code": code, "iso": iso, "payout": payout, "emoji_id": emoji_id}
            save_countries_db(COUNTRIES_DATA)
            await country_add_service_selection(update, user_id, name, context)
            return True
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
        return True
    elif state == "waiting_country_edit":
        if text.strip() == "/skip":
            admin_panel_state[user_id] = "country_manager"
            await update.message.reply_text("No changes.")
            await country_manager_menu(update, user_id, context)
            return True
        try:
            parts = [p.strip() for p in text.split('|')]
            if len(parts) < 3:
                await update.message.reply_text("At least Code | ISO | payout required.")
                return True
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
        return True
    elif state == "waiting_service_name":
        try:
            db_exec("INSERT INTO services (name, display_name, active, emoji_id) VALUES (?, ?, 1, '')", (text, text))
            await update.message.reply_text(f"Service {text} added!")
        except sqlite3.IntegrityError:
            await update.message.reply_text(f"Service {text} already exists!")
        admin_panel_state[user_id] = "service_manager"
        await service_manager_menu(update, user_id, context)
        return True
    elif state == "waiting_service_emoji":
        return await handle_service_emoji_set(update, context)
    elif state == "waiting_service_emoji_upload":
        if text.strip() == "/skip":
            text = ""
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
    # AIR CONTROL text handlers
    elif state == "waiting_air_min_w":
        try:
            val = float(text.strip())
            update_setting('min_withdraw', str(val))
            await update.message.reply_text(f"✅ Min withdraw set to {val}")
            await admin_air_control(update, context)
            return True
        except:
            await update.message.reply_text("Invalid number.")
            return True
    elif state == "waiting_air_ref_r":
        try:
            val = float(text.strip())
            update_setting('refer_reward', str(val))
            await update.message.reply_text(f"✅ Referral reward set to {val}")
            await admin_air_control(update, context)
            return True
        except:
            await update.message.reply_text("Invalid number.")
            return True
    elif state == "waiting_air_cool":
        try:
            val = int(text.strip())
            if val < 1: val = 1
            update_setting('cooldown', str(val))
            await update.message.reply_text(f"✅ Cooldown set to {val}s")
            await admin_air_control(update, context)
            return True
        except:
            await update.message.reply_text("Invalid number.")
            return True
    elif state == "waiting_air_num_req":
        try:
            val = int(text.strip())
            if val < 1: val = 1
            update_setting('num_req', str(val))
            await update.message.reply_text(f"✅ Number per request set to {val}")
            await admin_air_control(update, context)
            return True
        except:
            await update.message.reply_text("Invalid number.")
            return True
    elif state == "waiting_air_w_group":
        try:
            chat_id = int(text.strip())
            # Verify it's a group
            chat_info = requests.get(BASE_URL + f"getChat?chat_id={chat_id}").json()
            if chat_info.get('ok') and chat_info['result']['type'] in ['group', 'supergroup']:
                update_setting('w_group', str(chat_id))
                await update.message.reply_text(f"✅ Withdraw group set to {chat_id}")
            else:
                await update.message.reply_text("Invalid group ID. Please send a valid group ID.")
            await admin_air_control(update, context)
            return True
        except:
            await update.message.reply_text("Invalid group ID.")
            return True
    elif state == "waiting_w_method":
        methods = get_setting('w_methods', [])
        if text.strip() not in methods:
            methods.append(text.strip())
            update_setting('w_methods', methods)
            await update.message.reply_text(f"✅ Method '{text}' added.")
        else:
            await update.message.reply_text("Method already exists.")
        await admin_air_control(update, context)
        return True
    elif state == "waiting_air_def_rate":
        try:
            val = float(text.strip())
            update_setting('otp_default_rate', str(val))
            await update.message.reply_text(f"✅ Default OTP rate set to {val}")
            await admin_air_otp_control(update, context)
            return True
        except:
            await update.message.reply_text("Invalid number.")
            return True
    elif state == "waiting_air_srv_rate":
        try:
            parts = text.split('-')
            if len(parts) != 2:
                await update.message.reply_text("Format: ServiceName - Rate (e.g., Telegram - 2.5)")
                return True
            srv = parts[0].strip()
            rate = float(parts[1].strip())
            rates = get_setting('otp_service_rates', {})
            rates[srv] = rate
            update_setting('otp_service_rates', rates)
            await update.message.reply_text(f"✅ Rate for {srv} set to {rate}")
            await admin_air_otp_control(update, context)
            return True
        except:
            await update.message.reply_text("Invalid format. Use ServiceName - Rate")
            return True
    elif state == "waiting_air_main_channel":
        if text.strip().startswith('http'):
            update_setting('main_channel_link', text.strip())
            await update.message.reply_text(f"✅ Main channel link updated.")
        else:
            await update.message.reply_text("Invalid URL. Must start with http/https.")
        admin_panel_state[user_id] = "main"
        await admin_panel_menu(update, user_id, context)
        return True
    # Force Join text handler
    elif state == "waiting_fj_channel":
        try:
            chat_identifier = text.strip()
            res = requests.get(BASE_URL + f"getChat?chat_id={chat_identifier}").json()
            if res.get('ok'):
                chat = res['result']
                if chat['type'] in ['channel', 'supergroup']:
                    invite_link = None
                    try:
                        inv = requests.post(BASE_URL + f"exportChatInviteLink?chat_id={chat['id']}").json()
                        if inv.get('ok'):
                            invite_link = inv['result']
                    except:
                        pass
                    channel_data = {
                        'id': chat['id'],
                        'username': chat.get('username', ''),
                        'title': chat.get('title', 'Channel'),
                        'invite_link': invite_link or ''
                    }
                    channels = get_force_join_channels()
                    channels.append(channel_data)
                    set_force_join_channels(channels)
                    await update.message.reply_text(f"✅ Channel '{chat.get('title')}' added successfully!")
                    await admin_force_join(update, context)
                    admin_panel_state[user_id] = None
                else:
                    await update.message.reply_text("❌ This is not a channel or supergroup.")
            else:
                await update.message.reply_text("❌ Failed to fetch channel. Ensure the bot is admin and the chat ID/username is correct.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
        return True
    return False

# ================= STOCK GET NUMBER CALLBACK =================
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

# ================= /testgroup COMMAND =================
async def testgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Unauthorized. Admin only.")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /testgroup <service> <iso2>\nExample: /testgroup WhatsApp BD")
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
    grp_text, grp_kb = format_group_otp_rich(entry)
    success_count = 0
    failed_groups = []
    for gid in GROUP_IDS:
        try:
            await context.bot.send_message(chat_id=gid, text=grp_text, reply_markup=InlineKeyboardMarkup(grp_kb['inline_keyboard']), parse_mode='HTML')
            success_count += 1
        except Exception as e:
            failed_groups.append(f"{gid} ({str(e)})")
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

# ================= CALLBACK HANDLERS =================
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

async def balance_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
    await query.answer()
    await show_balance(update, query.from_user.id, context)

async def withdraw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
    await query.answer()
    await show_withdraw(update, query.from_user.id, context)

async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "User"
    await query.answer()
    await send_main_menu(query, context, user_id)

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
        await edit_or_send(query, "No active numbers to display.", reply_markup=back_to_main_keyboard(), context=context, auto_delete=False)
        return
    country, service, numbers, msg_id = data
    msg, kb = format_numbers_message(country, service, numbers, user_id=user_id)
    await edit_or_send(query, msg, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

async def service_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
    user_id = query.from_user.id
    await query.answer()
    service = query.data.split('|', 1)[1]
    db_exec("UPDATE users SET current_service = ? WHERE user_id = ?", (service, user_id))
    text = f'{emoji_tag(CUSTOM_EMOJIS["SELECT_COUNTRY_PREFIX"], "🌍")} <b>Select country for {service.upper()}</b> {service_emoji_tag(service)}'
    await edit_or_send(query, text, reply_markup=countries_for_service_keyboard(service), parse_mode='HTML', context=context, auto_delete=False)

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
    if await ban_check(update, context):
        return
    user_id = query.from_user.id
    await query.answer()
    db_exec("UPDATE users SET current_service = NULL, current_country = NULL, current_number = NULL, number_expiry = NULL WHERE user_id = ?", (user_id,))
    text = f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_PREFIX"], "🔧")} <b>Select service</b> {emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_SUFFIX"], "📱")}'
    await edit_or_send(query, text, reply_markup=services_keyboard(), parse_mode='HTML', context=context, auto_delete=False)

async def next_number_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await ban_check(update, context):
        return
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
        if fallback:
            country, service = fallback
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

# ================= ADMIN CALLBACKS =================
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
    if action == "stats":
        await show_admin_stats(update, user_id, context)
    elif action == "upload":
        await request_upload(update, user_id, context)
    elif action == "delete":
        await show_delete_options(query, user_id, context)
    elif action == "broadcast":
        await request_broadcast(update, user_id, context)
    elif action == "giveaway":
        await request_giveaway(update, user_id, context)
    elif action == "country_manager":
        await country_manager_menu(update, user_id, context)
    elif action == "service_manager":
        await service_manager_menu(update, user_id, context)
    elif action == "user_manager":
        await _user_manager_wrapper(update, context)
    elif action == "database":
        await _database_wrapper(update, context)
    elif action == "manage_api":
        await _manage_api_wrapper(update, context)
    # AIR CONTROL
    elif action == "air_control":
        await admin_air_control(update, context)
    # FORCE JOIN
    elif action == "force_join":
        await admin_force_join(update, context)
    elif action == "exit":
        await exit_admin_callback_query(query, user_id, context.bot)
    elif action == "back":
        admin_panel_state[user_id] = "main"
        await edit_or_send(query, "ADMIN PANEL\n\nDeveloper: 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓\n\nSelect an action below:", reply_markup=admin_panel_keyboard(), context=context, auto_delete=False)
    elif action == "stock_management":
        await stock_management_menu(query, context, user_id)

# ================= STOCK MANAGEMENT =================
async def send_stock_management_menu(target, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    text = f'{emoji_tag(CUSTOM_EMOJIS["STOCK_MANAGER"], "📦")} <b>STOCK MANAGEMENT</b>\n\nSelect an action below:'
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
        kb_buttons.append([InlineKeyboardButton(label, callback_data=cb_data, style=KBS.DANGER, icon_custom_emoji_id=safe_icon(country_eid))])
    kb_buttons.append([InlineKeyboardButton("Back", callback_data="admin_stock_management", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    await edit_or_send(query, "Select stock to remove:", reply_markup=InlineKeyboardMarkup(kb_buttons), parse_mode='HTML', context=context, auto_delete=False)

async def stock_remove_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only.")
        return
    await query.answer()
    _, country, service = query.data.split('|')
    text = f'Do you want to remove all numbers for {country_flag_emoji(country)} <b>{country}</b> with service {service_emoji_tag(service)}?'
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("YES", callback_data=f"stock_remove_yes|{country}|{service}", style=KBS.SUCCESS, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("YES", "")))],
        [InlineKeyboardButton("NO", callback_data="stock_remove_no", style=KBS.DANGER, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("NO", "")))]
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
            line = f'{service_emoji_tag(service)}|{country_flag_emoji(country)}<b>{country}</b>|<code>{payout}</code>|{stock}'
            lines.append(line)
        text = "\n".join(lines)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="admin_stock_management", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
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
        kb_buttons.append([InlineKeyboardButton(label, callback_data=cb_data, style=style, icon_custom_emoji_id=safe_icon(country_eid))])
    kb_buttons.append([InlineKeyboardButton("Back", callback_data="admin_stock_management", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
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

# ================= ADMIN STATS =================
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

# ================= AIR CONTROL FUNCTIONS =================
async def admin_air_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id if query else update.effective_user.id
    if not is_admin(user_id):
        if query: await query.answer("Unauthorized!", show_alert=True)
        return
    admin_panel_state[user_id] = "air_control"
    text = "⚙️ <b>AIR CONTROL PANEL</b>\nManage core bot configurations:"
    if query:
        await edit_or_send(query, text, reply_markup=air_control_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    else:
        await send_clean_message(update, context, text, reply_markup=air_control_keyboard(), parse_mode='HTML', auto_delete=False)

async def admin_air_otp_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Unauthorized!", show_alert=True)
        return
    admin_panel_state[user_id] = "air_otp_control"
    text = "💰 <b>OTP REWARD CONTROL</b>\nManage rates below:"
    await edit_or_send(query, text, reply_markup=air_otp_control_keyboard(), parse_mode='HTML', context=context, auto_delete=False)

async def admin_air_otp_control_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if data == "air_def_rate":
        admin_panel_state[user_id] = "waiting_air_def_rate"
        await edit_or_send(query, "💰 Enter new Default OTP Rate (e.g., 0.5):", reply_markup=admin_cancel_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    elif data == "air_srv_rate":
        admin_panel_state[user_id] = "waiting_air_srv_rate"
        await edit_or_send(query, "💰 Enter Specific Service Rate.\nFormat: <code>ServiceName - Rate</code>\nExample: <code>Telegram - 2.5</code>", reply_markup=admin_cancel_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    elif data.startswith("del_srv_rate_"):
        srv = data[13:]
        rates = get_setting('otp_service_rates', {})
        if srv in rates:
            del rates[srv]
            update_setting('otp_service_rates', rates)
            await query.answer(f"Rate for {srv} deleted!")
        await admin_air_otp_control(update, context)

async def air_control_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if data == "air_min_w":
        admin_panel_state[user_id] = "waiting_air_min_w"
        await edit_or_send(query, "💸 Enter new Minimum Withdraw Amount (e.g., 50):", reply_markup=admin_cancel_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    elif data == "air_ref_r":
        admin_panel_state[user_id] = "waiting_air_ref_r"
        await edit_or_send(query, "💸 Enter new Referral Reward Amount (e.g., 5.0):", reply_markup=admin_cancel_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    elif data == "air_cool":
        admin_panel_state[user_id] = "waiting_air_cool"
        await edit_or_send(query, "⏳ Enter new Cooldown time in seconds (e.g., 10):", reply_markup=admin_cancel_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    elif data == "air_num_req":
        admin_panel_state[user_id] = "waiting_air_num_req"
        await edit_or_send(query, "📱 Enter how many numbers a user gets per request (e.g., 3):", reply_markup=admin_cancel_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    elif data == "air_w_group":
        admin_panel_state[user_id] = "waiting_air_w_group"
        await edit_or_send(query, "📢 Send the Group ID for withdraw requests (e.g., -1001234567890):", reply_markup=admin_cancel_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    elif data == "manage_w_methods":
        await edit_or_send(query, "💳 <b>WITHDRAW METHODS</b>\nManage methods below:", reply_markup=manage_w_methods_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    elif data == "add_w_method":
        admin_panel_state[user_id] = "waiting_w_method"
        await edit_or_send(query, "💳 Enter new Withdraw Method Name (e.g., bKash):", reply_markup=admin_cancel_keyboard(), parse_mode='HTML', context=context, auto_delete=False)
    elif data.startswith("del_w_method_"):
        idx = int(data[13:])
        methods = get_setting('w_methods', [])
        if idx < len(methods):
            methods.pop(idx)
            update_setting('w_methods', methods)
            await query.answer("Method deleted!")
        await admin_air_control(update, context)
    elif data == "air_otp_control":
        await admin_air_otp_control(update, context)

# ================= FORCE JOIN FUNCTIONS =================
async def admin_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Unauthorized!", show_alert=True)
        return
    admin_panel_state[user_id] = "force_join"
    text = "🔗 <b>FORCE JOIN SYSTEM</b>\nManage channels below:"
    await edit_or_send(query, text, reply_markup=force_join_keyboard(), parse_mode='HTML', context=context, auto_delete=False)

async def force_join_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Unauthorized!", show_alert=True)
        return
    current = get_force_join_status()
    set_force_join_status(not current)
    await query.answer(f"Force Join {'ON' if not current else 'OFF'}")
    await admin_force_join(update, context)

async def force_join_add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Unauthorized!", show_alert=True)
        return
    admin_panel_state[user_id] = "waiting_fj_channel"
    await edit_or_send(query, "🔗 Please send the channel ID or @username of the channel to add.\nMake sure the bot is admin in that channel.", reply_markup=admin_cancel_keyboard(), parse_mode='HTML', context=context, auto_delete=False)

async def force_join_delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if data.startswith("del_fj_"):
        idx = int(data[6:])
        channels = get_force_join_channels()
        if idx < len(channels):
            channels.pop(idx)
            set_force_join_channels(channels)
            await query.answer("Channel deleted!")
        await admin_force_join(update, context)

async def force_join_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if get_force_join_status():
        channels = get_force_join_channels()
        joined = True
        for ch in channels:
            chat_id = ch.get('id')
            if chat_id:
                try:
                    res = requests.get(BASE_URL + f"getChatMember?chat_id={chat_id}&user_id={user_id}").json()
                    if res.get('ok'):
                        status = res['result']['status']
                        if status in ['left', 'kicked']:
                            joined = False
                            break
                    else:
                        joined = False
                        break
                except:
                    joined = False
                    break
        if joined:
            await query.answer("✅ You have joined all required channels.")
            await query.delete_message()
            await send_main_menu(query, context, user_id)
        else:
            await query.answer("❌ You haven't joined all channels!", show_alert=True)

# ================= COUNTRY & SERVICE CALLBACKS =================
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
        rows.append([InlineKeyboardButton(s[1], callback_data=f"cnt_add_svc|{country_name}|{s[0]}", style=KBS.PRIMARY,
                                          icon_custom_emoji_id=safe_icon(s[2]) if s[2] else None)])
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

# ================= SERVICE MANAGER =================
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
        rows.append([InlineKeyboardButton(f"Remove {s[1]}", callback_data=f"service_remove|{s[0]}", style=KBS.DANGER,
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
        rows.append([InlineKeyboardButton(f"{s[1]} ({status})", callback_data=f"service_toggle|{s[0]}", style=style,
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
        rows.append([InlineKeyboardButton(f"{s[1]} ({s[0]})", callback_data=f"service_emoji_set|{s[0]}", style=KBS.PRIMARY,
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

# ================= /setcountry & /setservice =================
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

# ================= /country & /service (legacy) =================
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

# ================= BOTTOM MENU TEXT ROUTERS =================
async def send_get_number_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await ban_check(update, context):
        return
    ensure_user(user_id, update.effective_user.username, update.effective_user.first_name)
    db_exec("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    text = f'{emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_PREFIX"], "🔧")} <b>Select service</b> {emoji_tag(CUSTOM_EMOJIS["SELECT_SERVICE_SUFFIX"], "📱")}'
    await send_clean_message(update, context, text, reply_markup=services_keyboard(), parse_mode='HTML', auto_delete=False)

async def send_balance_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await ban_check(update, context):
        return
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
        f'{emoji_tag(emoji_id, "🆔")} USER ID: <code>{user_id}</code>\n'
        f'{emoji_tag(emoji_money, "💰")} BALANCE: <code>${balance:.3f}</code>\n'
        f'{emoji_tag(emoji_withdraw, "💸")} WITHDRAWED: <code>${withdrawn:.3f}</code>\n'
        f'{emoji_tag(emoji_warning, "⚠️")} MINIMUM WITHDRAW: <code>${get_setting("min_withdraw", "10.0")}</code>\n'
        f'{emoji_tag(emoji_inbox, "📨")} TOTAL OTP: <code>{total_otp}</code>'
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
    await send_clean_message(update, context, "ADMIN PANEL\n\nDeveloper: 𝐖𝐀 𝐂𝐑𝐄𝐀𝐓𝐈𝐎𝐍 𝐑 𝐁𝐎𝐓", reply_markup=admin_panel_keyboard(), auto_delete=False)

# ================= CURL PARSER =================
import re
import json
from urllib.parse import urlparse, parse_qs

def parse_curl_complete(curl_string: str) -> dict:
    result = {"method": "GET", "url": "", "headers": {}, "data": None, "raw_curl": curl_string,
              "placeholders": {}, "base_url": "", "endpoint": "/", "original_url": ""}
    curl_string = curl_string.replace('\\', ' ').replace('\n', ' ').replace('\r', ' ')
    curl_string = re.sub(r'\s+', ' ', curl_string).strip()
    if curl_string.startswith("curl"):
        curl_string = curl_string[4:].strip()
    url_match = re.search(r'["\']((?:https?://)?[^\s"\']+)["\']', curl_string)
    if url_match:
        result["url"] = url_match.group(1)
        result["original_url"] = result["url"]
        curl_string = curl_string.replace(url_match.group(0), "").strip()
    else:
        url_match = re.search(r'((?:https?://)?[^\s"\']+)', curl_string)
        if url_match:
            result["url"] = url_match.group(1)
            result["original_url"] = result["url"]
            curl_string = curl_string.replace(url_match.group(0), "").strip()
    if not result["url"]:
        placeholder_url_match = re.search(r'\{[A-Za-z_]+\}/[^\s"]+', curl_string)
        if placeholder_url_match:
            result["url"] = placeholder_url_match.group(0)
            result["original_url"] = result["url"]
            curl_string = curl_string.replace(placeholder_url_match.group(0), "").strip()
    method_pattern = r'-[Xx]\s+["\']?([A-Z]+)["\']?'
    method_match = re.search(method_pattern, curl_string)
    if method_match:
        result["method"] = method_match.group(1).upper()
        curl_string = re.sub(method_pattern, "", curl_string).strip()
    header_pattern = r'-H\s+["\']([^"\']+)["\']'
    header_matches = re.findall(header_pattern, curl_string)
    for header in header_matches:
        if ": " in header:
            key, value = header.split(": ", 1)
            result["headers"][key.strip()] = value.strip()
    curl_string = re.sub(header_pattern, "", curl_string).strip()
    header_long_pattern = r'--header\s+["\']([^"\']+)["\']'
    header_long_matches = re.findall(header_long_pattern, curl_string)
    for header in header_long_matches:
        if ": " in header:
            key, value = header.split(": ", 1)
            result["headers"][key.strip()] = value.strip()
    curl_string = re.sub(header_long_pattern, "", curl_string).strip()
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
    placeholder_pattern = r'\{([^{}]+)\}'
    if result["url"]:
        placeholders = re.findall(placeholder_pattern, result["url"])
        for ph in placeholders:
            result["placeholders"][ph] = ""
    for key, value in result["headers"].items():
        placeholders = re.findall(placeholder_pattern, value)
        for ph in placeholders:
            result["placeholders"][ph] = ""
    if result["data"] and isinstance(result["data"], str):
        placeholders = re.findall(placeholder_pattern, result["data"])
        for ph in placeholders:
            result["placeholders"][ph] = ""
    elif result["data"] and isinstance(result["data"], (dict, list)):
        data_str = json.dumps(result["data"])
        placeholders = re.findall(placeholder_pattern, data_str)
        for ph in placeholders:
            result["placeholders"][ph] = ""
    if result["url"]:
        if result["url"].startswith(("http://", "https://")):
            parsed = urlparse(result["url"])
            result["base_url"] = f"{parsed.scheme}://{parsed.netloc}"
            result["endpoint"] = parsed.path or "/"
            if parsed.query:
                result["endpoint"] += "?" + parsed.query
        else:
            parts = result["url"].split('/', 1)
            if len(parts) > 1:
                result["base_url"] = parts[0]
                result["endpoint"] = "/" + parts[1]
            else:
                result["base_url"] = parts[0]
                result["endpoint"] = "/"
    return result

def replace_all_placeholders(text: str, placeholders: dict) -> str:
    if not text:
        return text
    for key, value in placeholders.items():
        text = text.replace(f"{{{key}}}", str(value))
    return text

def build_request_from_curl(parsed: dict, placeholders: dict = None) -> dict:
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
    return {"method": parsed.get("method", "GET"), "url": url, "headers": headers,
            "data": data, "base_url": parsed.get("base_url", ""), "endpoint": parsed.get("endpoint", ""),
            "placeholders": placeholders}

# ================= API ADD STEPS =================
STEP_ORDER = [
    "api_add_name", "api_add_base_url", "api_add_endpoint", "api_add_token",
    "api_add_interval", "api_add_otp_list_path", "api_add_number_path",
    "api_add_message_path", "api_add_timestamp_path", "api_add_service_path",
    "api_add_curl", "api_add_confirm"
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
SKIPPABLE_STEPS = ["api_add_name", "api_add_endpoint", "api_add_token", "api_add_interval",
                   "api_add_otp_list_path", "api_add_number_path", "api_add_message_path",
                   "api_add_timestamp_path", "api_add_service_path", "api_add_curl"]
NON_SKIPPABLE_STEPS = ["api_add_base_url", "api_add_confirm"]

def get_step_keyboard(step: str) -> InlineKeyboardMarkup:
    buttons = []
    if step in SKIPPABLE_STEPS:
        buttons.append(InlineKeyboardButton("SKIP", callback_data="api_add_skip", style=KBS.PRIMARY,
                                            icon_custom_emoji_id=safe_icon(SKIP_EMOJI)))
    buttons.append(InlineKeyboardButton("CANCEL", callback_data="api_add_cancel", style=KBS.DANGER,
                                        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CANCEL", ""))))
    return InlineKeyboardMarkup([buttons])

async def api_add_step(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, step: str):
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
    example_text = ""
    if field in STEP_EXAMPLES:
        example_text = f"\n\n💡 <b>EXAMPLE</b>:\n<code>{STEP_EXAMPLES[field]}</code>"
    required_text = "⚠️ <b>Required</b>" if step in NON_SKIPPABLE_STEPS else "✅ <b>Optional</b> (Can SKIP)"
    text = f"""{emoji_tag(CUSTOM_EMOJIS['ADD_API_KEY'], '➕')} <b>ADD API – Step {step_num}/{total_steps}</b>

<b>{label}</b>
{required_text}

Current value: <code>{current_value or 'Not set'}</code>
{example_text}

Send the value or press SKIP:"""
    await reply_or_edit(update, text, reply_markup=get_step_keyboard(step), parse_mode='HTML', context=context, auto_delete=False)

async def show_confirm_step(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    data = admin_temp_data.get(user_id, {})
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
            safe_val = html.escape(str(value))
            if len(safe_val) > 30:
                safe_val = safe_val[:30] + "..."
            confirm_text += f"{emoji_tag(emoji_id, '•')} {label}: <code>{safe_val}</code>\n"
    if data.get("curl_command"):
        raw_curl = data["curl_command"][:200]
        curl_cmd = html.escape(raw_curl)
        if len(data["curl_command"]) > 200:
            curl_cmd += "..."
        confirm_text += f"\n{emoji_tag(curl_icon, '📌')} <b>CURL Command</b>:\n<code>{curl_cmd}</code>\n"
        parsed = data.get("parsed_curl")
        if parsed and parsed.get("placeholders"):
            ph_list = [html.escape(ph) for ph in parsed["placeholders"].keys()]
            ph_str = ", ".join([f"<code>{{{ph}}}</code>" for ph in ph_list])
            confirm_text += f"{emoji_tag(CUSTOM_EMOJIS['API_FIELD_TOKEN'], '🔑')} <b>Placeholders</b>: {ph_str}\n"
    else:
        confirm_text += f"\n{emoji_tag(curl_icon, '📌')} <b>CURL</b>: <i>Skipped (Not Used)</i>\n"
    confirm_text += f"\n💡 <b>Is all correct?</b>"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("YES ADD", callback_data=f"api_add_confirm_yes|{user_id}", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("YES", "4956721670690702265"))),
         InlineKeyboardButton("CANCEL", callback_data=f"api_add_confirm_no|{user_id}", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("NO", "6206110936789423908")))],
        [InlineKeyboardButton("EDIT VALUE", callback_data=f"api_add_edit|{user_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("EDIT_BALANCE", "6204162490515855272")))]
    ])
    admin_panel_state[user_id] = "api_add_confirm"
    async def send_confirm(chat_id, message_id=None):
        try:
            if message_id:
                await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=confirm_text, reply_markup=kb, parse_mode='HTML')
            else:
                await context.bot.send_message(chat_id=chat_id, text=confirm_text, reply_markup=kb, parse_mode='HTML')
        except BadRequest as e:
            if "Message is not modified" in str(e):
                return
            plain_text = re.sub(r'<[^>]+>', '', confirm_text)
            plain_text = plain_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            try:
                if message_id:
                    await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=plain_text, reply_markup=kb)
                else:
                    await context.bot.send_message(chat_id=chat_id, text=plain_text, reply_markup=kb)
            except Exception as fallback_err:
                print(f"Fallback also failed: {fallback_err}")
    chat_id = update.message.chat.id if hasattr(update, 'message') else update.message.chat.id
    message_id = update.message.message_id if hasattr(update, 'message') else None
    await send_confirm(chat_id, message_id)

async def handle_api_add_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("⏭ Step skipped! This field will not be used.")
    current_step = admin_panel_state.get(user_id)
    if not current_step or not current_step.startswith("api_add_"):
        await query.edit_message_text("❌ No active API addition session.", reply_markup=admin_panel_keyboard())
        return
    data = admin_temp_data.get(user_id, {})
    label, field, next_step = STEP_MESSAGES.get(current_step, ("", "", ""))
    if field:
        data[field] = None
    admin_temp_data[user_id] = data
    if next_step:
        await api_add_step(update, context, user_id, next_step)
    else:
        await show_confirm_step(query, context, user_id)

async def handle_api_add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("❌ Cancelled!")
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await query.edit_message_text("❌ API addition cancelled.", reply_markup=admin_panel_keyboard())

async def api_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    admin_temp_data[user_id] = {}
    admin_panel_state[user_id] = "api_add_name"
    await api_add_step(update, context, user_id, "api_add_name")

async def api_add_curl_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("Proceeding to confirmation...")
    await show_confirm_step(query, context, user_id)

async def api_add_curl_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("Cancelled.")
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await query.edit_message_text("❌ API addition cancelled.", reply_markup=admin_panel_keyboard())

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
                await update.message.reply_text("❌ <b>Invalid CURL Command</b>\n\nCould not extract URL. Please check your CURL command.\n\nMake sure your CURL has a URL like:\n<code>curl https://example.com/api/endpoint</code>\nor\n<code>curl {API_BASE}/api/endpoint</code>\n\nOr send <code>/skip</code> to skip this step.", parse_mode='HTML')
                return True
            data["curl_command"] = text
            data["parsed_curl"] = parsed
            admin_temp_data[user_id] = data
            placeholders = parsed.get("placeholders", {})
            ph_list = [html.escape(ph) for ph in placeholders.keys()]
            placeholders_list = ", ".join([f"<code>{{{ph}}}</code>" for ph in ph_list]) if ph_list else "None"
            check_icon = CUSTOM_EMOJIS.get("YES", "4956721670690702265")
            url_icon = CUSTOM_EMOJIS.get("API_FIELD_URL", "6285048454255220485")
            method_icon = CUSTOM_EMOJIS.get("API_FIELD_METHOD", "5926860096008098405")
            headers_icon = CUSTOM_EMOJIS.get("API_FIELD_HEADERS", "5926860096008098405")
            data_icon = CUSTOM_EMOJIS.get("API_FIELD_MESSAGE", "5980911993140284450")
            token_icon = CUSTOM_EMOJIS.get("API_FIELD_TOKEN", "5821453562680448557")
            url_display = html.escape(parsed.get('url', 'N/A'))
            method_display = html.escape(parsed.get('method', 'GET'))
            headers_count = len(parsed.get('headers', {}))
            data_present = 'Yes' if parsed.get('data') else 'No'
            info_text = f"""
{emoji_tag(check_icon, '✅')} <b>CURL Parsed Successfully</b>

{emoji_tag(url_icon, '🌐')} <b>URL</b>: <code>{url_display}</code>
{emoji_tag(method_icon, '📌')} <b>Method</b>: <code>{method_display}</code>
{emoji_tag(headers_icon, '📋')} <b>Headers</b>: <code>{headers_count}</code>
{emoji_tag(data_icon, '📦')} <b>Data</b>: {data_present}
{emoji_tag(token_icon, '🔑')} <b>Placeholders</b>: {placeholders_list}

✅ Bot will use this exact format for polling
"""
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("CONTINUE", callback_data="api_add_curl_continue", style=KBS.SUCCESS,
                                      icon_custom_emoji_id=safe_icon("6266818250818983044")),
                 InlineKeyboardButton("CANCEL", callback_data="api_add_curl_cancel", style=KBS.DANGER,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CANCEL", "")))]
            ])
            admin_panel_state[user_id] = "api_add_curl_confirm"
            await update.message.reply_text(info_text, reply_markup=kb, parse_mode='HTML')
            return True
        except Exception as e:
            await update.message.reply_text(f"❌ <b>Error parsing CURL</b>\n\n<code>{html.escape(str(e))}</code>\n\nPlease send a valid CURL command or <code>/skip</code>", parse_mode='HTML')
            return True
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

async def api_add_confirm_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = admin_temp_data.get(user_id, {})
    if not data:
        await query.answer("Session expired.", show_alert=True)
        return
    parsed_curl = data.get("parsed_curl")
    curl_command = data.get("curl_command")
    panel_name = data.get("panel_name") or "API_" + str(user_id)[-4:]
    base_url = data.get("base_url") or ""
    endpoint = data.get("endpoint") or "/"
    token = data.get("token") or ""
    interval = data.get("interval_sec") or 30
    otp_list_path = data.get("otp_list_path") or "data"
    number_path = data.get("number_path")
    message_path = data.get("message_path")
    timestamp_path = data.get("timestamp_path")
    service_path = data.get("service_path")
    if parsed_curl:
        if parsed_curl.get("base_url") and "{" not in parsed_curl["base_url"]:
            base_url = parsed_curl["base_url"]
        elif not base_url and parsed_curl.get("base_url"):
            base_url = parsed_curl["base_url"]
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
        panel_name, base_url, endpoint, token, interval,
        method, json.dumps(headers) if headers else "{}",
        json.dumps(body_template) if body_template else None,
        otp_list_path, number_path, message_path, timestamp_path, service_path,
        user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        placeholder_config, curl_command
    ))
    api_id = db_fetch_one("SELECT last_insert_rowid()")[0]
    await start_polling_for_api(api_id)
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
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
    
💡 <b>Next Steps</b>:
1. Go to <b>API System</b> → {panel_name}
2. Click <b>TEST</b> to verify API works
3. Click <b>EDIT</b> to adjust any settings
4. Check <b>LOGS</b> for polling status
"""
    await query.edit_message_text(success_text, reply_markup=admin_panel_keyboard(), parse_mode='HTML')

async def api_add_confirm_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await query.edit_message_text("❌ API addition cancelled.", reply_markup=admin_panel_keyboard())

async def api_add_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = admin_temp_data.get(user_id, {})
    if not data:
        await query.answer("Session expired.", show_alert=True)
        return
    admin_panel_state[user_id] = "api_add_name"
    await query.edit_message_text("✏️ Edit mode: You can re-enter each step. Press SKIP to keep current value.", reply_markup=admin_cancel_keyboard())
    await api_add_step(update, context, user_id, "api_add_name")

# ================= API POLLING (WITH RECOVERY) =================
async def poll_single_api_curl_based(api_id: int):
    if api_id not in polling_cycle_counts:
        polling_cycle_counts[f"api_{api_id}"] = 0
    consecutive_failures = 0
    last_success_time = datetime.now()
    async with aiohttp.ClientSession() as session:
        while True:
            config = get_api_config(api_id)
            if not config or not config.get('active'):
                break
            interval = config.get('interval_sec', 30)
            polling_cycle_counts[f"api_{api_id}"] += 1
            cycle = polling_cycle_counts[f"api_{api_id}"]
            try:
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
                try:
                    text = raw_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text = raw_bytes.decode('latin-1')
                    except:
                        text = raw_bytes.decode('utf-8', errors='ignore')
                if status == 200:
                    consecutive_failures = 0
                    last_success_time = datetime.now()
                    config['otp_list_path'] = otp_list_path
                    otps = ResponseParser.parse_response(text, config)
                    if otps:
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
                    logger.info(f"[API: {config.get('panel_name', api_id)}] 🔄 Polling cycle #{cycle} – ✅ Success ({new_count} OTPs)")
                else:
                    error_msg = f"HTTP {status}"
                    db_exec("INSERT INTO api_logs (api_id, timestamp, status, message, otp_count) VALUES (?, ?, 'error', ?, 0)",
                            (api_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error_msg))
                    db_exec("UPDATE api_keys SET error_count = error_count + 1 WHERE id = ?", (api_id,))
                    consecutive_failures += 1
                    logger.warning(f"[API: {config.get('panel_name', api_id)}] 🔄 Polling cycle #{cycle} – ❌ {error_msg}")
            except Exception as e:
                error_msg = str(e)[:200]
                logger.error(f"[API: {config.get('panel_name', api_id)}] 🔄 Polling cycle #{cycle} – ❌ {error_msg}")
                db_exec("INSERT INTO api_logs (api_id, timestamp, status, message, otp_count) VALUES (?, ?, 'error', ?, 0)",
                        (api_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error_msg, 0))
                db_exec("UPDATE api_keys SET error_count = error_count + 1 WHERE id = ?", (api_id,))
                consecutive_failures += 1

            if consecutive_failures >= 3 or (datetime.now() - last_success_time).total_seconds() > 120:
                logger.warning(f"[API: {config.get('panel_name', api_id)}] ⚠️ Recovery triggered (failures={consecutive_failures}, inactivity={(datetime.now()-last_success_time).seconds}s). Resetting counters...")
                consecutive_failures = 0
                last_success_time = datetime.now()

            await asyncio.sleep(interval)

# ================= API MANAGEMENT =================
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

# ================= API SYSTEM GRID =================
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
            [InlineKeyboardButton("Add API", callback_data="api_add_choice", style=KBS.SUCCESS,
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
        btn = InlineKeyboardButton(panel_name, callback_data=f"api_detail|{api_id}", style=style,
                                   icon_custom_emoji_id=safe_icon(icon_id))
        row.append(btn)
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("Add API", callback_data="api_add_choice", style=KBS.SUCCESS,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADD_API_KEY", "")))])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    text = f"{emoji_tag(CUSTOM_EMOJIS['API_SYSTEM'], '🖥️')} <b>API SYSTEM</b> ({len(apis)} configured)"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)

# ================= API ADD CHOICE =================
async def api_add_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    await query.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("API PANEL", callback_data="api_choice_api", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_SYSTEM", ""))),
         InlineKeyboardButton("NON API PANEL", callback_data="api_choice_cdr", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CDR_PANEL", "")))],
        [InlineKeyboardButton("Cancel", callback_data="admin_manage_api", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CANCEL", "")))]
    ])
    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['ADD_API_KEY'], '➕')} <b>Select Panel Type</b>\n\nChoose the type of panel you want to add:", reply_markup=kb, parse_mode='HTML')

async def api_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    choice = query.data
    await query.answer()
    if choice == "api_choice_api":
        await api_add_start(update, context, user_id)
    else:
        await cdr_add_start(update, context, user_id)

# ================= CDR PANEL MANAGEMENT =================
async def _solve_captcha(page) -> str | None:
    body_text = await page.locator("body").inner_text()
    match = re.search(r"(\d+)\s*([\+\-])\s*(\d+)", body_text)
    if not match:
        print("⚠️ Captcha pattern not found")
        return None
    a, op, b = int(match.group(1)), match.group(2), int(match.group(3))
    return str(a + b if op == '+' else a - b)

CDR_STEP_ORDER = [
    "cdr_add_name", "cdr_add_login_url", "cdr_add_smscdr_url",
    "cdr_add_username", "cdr_add_password", "cdr_add_number_field",
    "cdr_add_message_field", "cdr_add_timestamp_field",
    "cdr_add_service_field", "cdr_add_interval", "cdr_add_confirm"
]
CDR_STEP_MESSAGES = {
    "cdr_add_name": ("Panel Name", "panel_name", "cdr_add_login_url"),
    "cdr_add_login_url": ("Login URL", "login_url", "cdr_add_smscdr_url"),
    "cdr_add_smscdr_url": ("SMSCDR URL", "smscdr_url", "cdr_add_username"),
    "cdr_add_username": ("Username", "username", "cdr_add_password"),
    "cdr_add_password": ("Password", "password", "cdr_add_number_field"),
    "cdr_add_number_field": ("Number Field (field|row)", "number_field", "cdr_add_message_field"),
    "cdr_add_message_field": ("Message Field (field|row)", "message_field", "cdr_add_timestamp_field"),
    "cdr_add_timestamp_field": ("Timestamp Field (field|row, optional)", "timestamp_field", "cdr_add_service_field"),
    "cdr_add_service_field": ("Service Field (field|row, optional)", "service_field", "cdr_add_interval"),
    "cdr_add_interval": ("Interval (seconds)", "interval_sec", "cdr_add_confirm"),
    "cdr_add_confirm": ("", "", ""),
}
CDR_SKIPPABLE_STEPS = ["cdr_add_timestamp_field", "cdr_add_service_field"]
CDR_NON_SKIPPABLE_STEPS = ["cdr_add_name", "cdr_add_login_url", "cdr_add_smscdr_url",
                           "cdr_add_username", "cdr_add_password", "cdr_add_number_field",
                           "cdr_add_message_field", "cdr_add_interval", "cdr_add_confirm"]

def cdr_get_step_keyboard(step: str) -> InlineKeyboardMarkup:
    buttons = []
    if step in CDR_SKIPPABLE_STEPS:
        buttons.append(InlineKeyboardButton("SKIP", callback_data="cdr_add_skip", style=KBS.PRIMARY,
                                            icon_custom_emoji_id=safe_icon(SKIP_EMOJI)))
    buttons.append(InlineKeyboardButton("CANCEL", callback_data="cdr_add_cancel", style=KBS.DANGER,
                                        icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CANCEL", ""))))
    return InlineKeyboardMarkup([buttons])

async def cdr_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    admin_temp_data[user_id] = {}
    admin_panel_state[user_id] = "cdr_add_name"
    await cdr_add_step(update, context, user_id, "cdr_add_name")

async def cdr_add_step(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, step: str):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    admin_panel_state[user_id] = step
    step_num = CDR_STEP_ORDER.index(step) + 1
    total_steps = len(CDR_STEP_ORDER)
    label, field, next_step = CDR_STEP_MESSAGES.get(step, ("", "", ""))
    if step == "cdr_add_confirm":
        await cdr_show_confirm_step(update, context, user_id)
        return
    data = admin_temp_data.get(user_id, {})
    current_value = data.get(field, "")
    example_text = ""
    if field == "number_field":
        example_text = "\n\n💡 Example: <code>num|1</code> means field 'num' from row 1 (first column)"
    elif field == "message_field":
        example_text = "\n\n💡 Example: <code>msg|2</code> means field 'msg' from row 2"
    elif field == "timestamp_field":
        example_text = "\n\n💡 Example: <code>time|3</code> (optional)"
    elif field == "service_field":
        example_text = "\n\n💡 Example: <code>sender|4</code> (optional)"
    elif field == "interval_sec":
        example_text = "\n\n💡 Interval in seconds (minimum 1)"
    required_text = "⚠️ <b>Required</b>" if step in CDR_NON_SKIPPABLE_STEPS else "✅ <b>Optional</b> (Can SKIP)"
    text = f"""{emoji_tag(CUSTOM_EMOJIS['CDR_PANEL'], '📦')} <b>ADD NON API PANEL – Step {step_num}/{total_steps}</b>

<b>{label}</b>
{required_text}

Current value: <code>{current_value or 'Not set'}</code>
{example_text}

Send the value or press SKIP:"""
    await reply_or_edit(update, text, reply_markup=cdr_get_step_keyboard(step), parse_mode='HTML', context=context, auto_delete=False)

async def cdr_handle_add_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("⏭ Step skipped!")
    current_step = admin_panel_state.get(user_id)
    if not current_step or not current_step.startswith("cdr_add_"):
        await query.edit_message_text("❌ No active session.", reply_markup=admin_panel_keyboard())
        return
    data = admin_temp_data.get(user_id, {})
    label, field, next_step = CDR_STEP_MESSAGES.get(current_step, ("", "", ""))
    if field:
        data[field] = None
    admin_temp_data[user_id] = data
    if next_step:
        await cdr_add_step(update, context, user_id, next_step)
    else:
        await cdr_show_confirm_step(query, context, user_id)

async def cdr_handle_add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("❌ Cancelled!")
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await query.edit_message_text("❌ Panel addition cancelled.", reply_markup=admin_panel_keyboard())

async def cdr_show_confirm_step(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    data = admin_temp_data.get(user_id, {})
    text = f"{emoji_tag(CUSTOM_EMOJIS['CDR_PANEL'], '📦')} <b>Confirm NON API Panel Details</b>\n\n"
    fields = [
        ("Panel Name", "panel_name", CUSTOM_EMOJIS.get("API_FIELD_NAME", "5818775306974006843")),
        ("Login URL", "login_url", CUSTOM_EMOJIS.get("CDR_LOGIN_URL", "6285048454255220485")),
        ("SMSCDR URL", "smscdr_url", CUSTOM_EMOJIS.get("CDR_SMSCDR_URL", "6267172559851099903")),
        ("Username", "username", CUSTOM_EMOJIS.get("CDR_USERNAME", "5818775306974006843")),
        ("Password", "password", CUSTOM_EMOJIS.get("CDR_PASSWORD", "5821453562680448557")),
        ("Number Field", "number_field", CUSTOM_EMOJIS.get("CDR_FIELD_NUMBER", "5877410604225924969")),
        ("Message Field", "message_field", CUSTOM_EMOJIS.get("CDR_FIELD_MESSAGE", "5980911993140284450")),
        ("Timestamp Field", "timestamp_field", CUSTOM_EMOJIS.get("CDR_FIELD_TIMESTAMP", "6285240160120477644")),
        ("Service Field", "service_field", CUSTOM_EMOJIS.get("CDR_FIELD_SERVICE", "5818967150278218011")),
        ("Interval", "interval_sec", CUSTOM_EMOJIS.get("API_FIELD_INTERVAL", "6093456762113888541")),
    ]
    for label, key, emoji_id in fields:
        value = data.get(key)
        if value is None:
            text += f"{emoji_tag(emoji_id, '•')} {label}: <i>Skipped (Not Used)</i>\n"
        elif value == "":
            text += f"{emoji_tag(emoji_id, '•')} {label}: <i>Not set</i>\n"
        else:
            safe_val = html.escape(str(value))
            if len(safe_val) > 30:
                safe_val = safe_val[:30] + "..."
            text += f"{emoji_tag(emoji_id, '•')} {label}: <code>{safe_val}</code>\n"
    text += f"\n💡 <b>Is all correct?</b>"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("YES ADD", callback_data="cdr_add_confirm_yes", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("YES", "4956721670690702265"))),
         InlineKeyboardButton("CANCEL", callback_data="cdr_add_confirm_no", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("NO", "6206110936789423908")))],
        [InlineKeyboardButton("EDIT VALUE", callback_data="cdr_add_edit", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("EDIT_BALANCE", "6204162490515855272")))]
    ])
    admin_panel_state[user_id] = "cdr_add_confirm"
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

async def cdr_add_confirm_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = admin_temp_data.get(user_id, {})
    if not data:
        await query.answer("Session expired.", show_alert=True)
        return
    panel_name = data.get("panel_name") or "CDR_" + str(user_id)[-4:]
    login_url = data.get("login_url")
    smscdr_url = data.get("smscdr_url")
    username = data.get("username")
    password = data.get("password")
    number_field = data.get("number_field")
    message_field = data.get("message_field")
    timestamp_field = data.get("timestamp_field")
    service_field = data.get("service_field")
    interval = data.get("interval_sec") or 30
    if not all([login_url, smscdr_url, username, password, number_field, message_field]):
        await query.answer("Missing required fields!", show_alert=True)
        return
    db_exec("""
        INSERT INTO cdr_panels (
            panel_name, login_url, smscdr_url, username, password,
            number_field, message_field, timestamp_field, service_field,
            interval_sec, active, created_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
    """, (
        panel_name, login_url, smscdr_url, username, password,
        number_field, message_field, timestamp_field, service_field,
        interval, user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    panel_id = db_fetch_one("SELECT last_insert_rowid()")[0]
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await start_cdr_polling(panel_id)
    success_text = f"""
✅ {emoji_tag(CUSTOM_EMOJIS['CDR_PANEL'], '📦')} <b>NON API Panel '{panel_name}' added successfully!</b>

🆔 <b>Panel ID</b>: <code>{panel_id}</code>
📛 <b>Name</b>: {panel_name}
🌐 <b>Login URL</b>: <code>{login_url}</code>
📡 <b>SMSCDR URL</b>: <code>{smscdr_url}</code>
👤 <b>Username</b>: {username}
🔑 <b>Password</b>: {'*' * len(password)}
📱 <b>Number Field</b>: {number_field}
💬 <b>Message Field</b>: {message_field}
🕐 <b>Timestamp Field</b>: {timestamp_field or 'Not used'}
🔧 <b>Service Field</b>: {service_field or 'Not used'}
⏱️ <b>Interval</b>: {interval}s

✅ Polling started automatically.
"""
    await query.edit_message_text(success_text, reply_markup=admin_panel_keyboard(), parse_mode='HTML')

async def cdr_add_confirm_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await query.edit_message_text("❌ Panel addition cancelled.", reply_markup=admin_panel_keyboard())

async def cdr_add_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = admin_temp_data.get(user_id, {})
    if not data:
        await query.answer("Session expired.", show_alert=True)
        return
    admin_panel_state[user_id] = "cdr_add_name"
    await query.edit_message_text("✏️ Edit mode: You can re-enter each step. Press SKIP to keep current value.", reply_markup=admin_cancel_keyboard())
    await cdr_add_step(update, context, user_id, "cdr_add_name")

async def cdr_handle_add_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = admin_panel_state.get(user_id)
    if not state or not state.startswith("cdr_add_"):
        return False
    text = update.message.text.strip()
    if text == "/cancel":
        admin_temp_data.pop(user_id, None)
        admin_panel_state[user_id] = "main"
        await update.message.reply_text("❌ Addition cancelled.", reply_markup=admin_panel_keyboard())
        return True
    data = admin_temp_data.get(user_id, {})
    label, field, next_step = CDR_STEP_MESSAGES.get(state, ("", "", ""))
    if field:
        if field == "interval_sec":
            try:
                val = int(text)
                if val < 1:
                    await update.message.reply_text("⏱️ Interval must be at least 1 second.")
                    return True
                data[field] = val
            except ValueError:
                await update.message.reply_text("❌ Please enter a valid number.")
                return True
        else:
            data[field] = text
        admin_temp_data[user_id] = data
    if next_step:
        await cdr_add_step(update, context, user_id, next_step)
    else:
        await cdr_show_confirm_step(update, context, user_id)
    return True

# ================= CDR PANEL DETAIL =================
async def cdr_test_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    panel_id = int(query.data.split('|')[1])
    panel = get_cdr_panel(panel_id)
    if not panel:
        await query.answer("Panel not found!", show_alert=True)
        return

    await query.edit_message_text(
        f"{emoji_tag(CUSTOM_EMOJIS['CDR_TEST_LOGIN'], '🧪')} Testing login for <b>{panel['panel_name']}</b> ...",
        parse_mode='HTML'
    )

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=500)
            context = await browser.new_context()
            page = await context.new_page()

            print(f"🌐 Navigating to: {panel['login_url']}")
            await page.goto(panel['login_url'], wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(2000)

            await page.locator("input[type='text']").first.fill(panel['username'])
            print("✅ Username filled")
            await page.locator("input[type='password']").fill(panel['password'])
            print("✅ Password filled")

            captcha_answer = await _solve_captcha(page)
            if captcha_answer:
                inputs = await page.locator("input").element_handles()
                if inputs:
                    await inputs[-1].fill(captcha_answer)
                    print(f"✅ Captcha solved: {captcha_answer}")

            login_btn = page.locator("button").first
            if await login_btn.count() == 0:
                login_btn = page.locator("input[type='submit']").first
            if await login_btn.count() == 0:
                await page.locator("form").first.evaluate("form => form.submit()")
                print("✅ Form submitted via JS")
            else:
                await login_btn.click()
                print("✅ Login button clicked")

            await page.wait_for_timeout(5000)
            current_url = page.url
            print(f"🔗 Current URL after login: {current_url}")

            if "login" in current_url.lower():
                screenshot = await page.screenshot()
                with open("login_failed.png", "wb") as f:
                    f.write(screenshot)
                print("📸 Screenshot saved as login_failed.png")
                result = "❌ Login failed – still on login page. Check credentials and captcha."
            else:
                storage = await context.storage_state()
                db_exec("UPDATE cdr_panels SET cookie_data = ? WHERE id = ?",
                        (json.dumps(storage), panel_id))
                result = "✅ Login successful! Cookie saved."

            await browser.close()
    except Exception as e:
        result = f"❌ Exception: {str(e)}"

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("Back", callback_data=f"cdr_detail|{panel_id}", style=KBS.PRIMARY,
                             icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))
    ]])
    await query.edit_message_text(
        f"{emoji_tag(CUSTOM_EMOJIS['CDR_TEST_LOGIN'], '🧪')} <b>Test Login Result: {panel['panel_name']}</b>\n\n{result}",
        reply_markup=kb, parse_mode='HTML'
    )

async def cdr_fetch_once(panel: dict) -> list[dict]:
    max_retries = 2
    last_exception = None
    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = await browser.new_context()

                cookie_data = panel.get('cookie_data')
                if cookie_data:
                    try:
                        storage = json.loads(cookie_data)
                        await context.add_cookies(storage.get('cookies', []))
                    except Exception as e:
                        print(f"Cookie load error: {e}")

                page = await context.new_page()

                await page.goto(panel['login_url'], wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(2000)

                if "login" in page.url.lower():
                    print(f"Panel {panel['id']}: Session expired, logging in...")
                    await page.locator("input[type='text']").first.fill(panel['username'])
                    await page.locator("input[type='password']").fill(panel['password'])

                    captcha_answer = await _solve_captcha(page)
                    if captcha_answer:
                        inputs = await page.locator("input").element_handles()
                        if inputs:
                            await inputs[-1].fill(captcha_answer)
                            print(f"Captcha solved: {captcha_answer}")

                    login_btn = page.locator("button").first
                    if await login_btn.count() == 0:
                        login_btn = page.locator("input[type='submit']").first
                    if await login_btn.count() == 0:
                        await page.locator("form").first.evaluate("form => form.submit()")
                    else:
                        await login_btn.click()

                    await page.wait_for_timeout(5000)
                    if "login" in page.url.lower():
                        raise Exception("Login failed – still on login page")

                    storage = await context.storage_state()
                    db_exec("UPDATE cdr_panels SET cookie_data = ? WHERE id = ?",
                            (json.dumps(storage), panel['id']))
                    print(f"Panel {panel['id']}: Login successful, cookies saved.")
                else:
                    print(f"Panel {panel['id']}: Session active, proceeding.")

                try:
                    await page.goto(panel['smscdr_url'], wait_until="domcontentloaded", timeout=60000)
                except Exception as e:
                    print(f"Panel {panel['id']}: Page.goto failed: {e}")
                    await browser.close()
                    raise Exception("Page crashed on goto")

                await page.wait_for_timeout(3000)

                show_btn = page.locator("button:has-text('Show Report'), input[value='Show Report']").first
                try:
                    if await show_btn.count() > 0:
                        await show_btn.wait_for(state="visible", timeout=10000)
                        is_disabled = await show_btn.get_attribute("disabled")
                        if is_disabled is None or is_disabled.lower() != "disabled":
                            await show_btn.click(force=True, timeout=10000)
                            print(f"Panel {panel['id']}: Show Report clicked")
                            await page.wait_for_timeout(5000)
                            try:
                                await page.wait_for_load_state("networkidle", timeout=10000)
                            except:
                                pass
                except Exception as e:
                    print(f"Panel {panel['id']}: Show Report click failed - {e}")

                table_found = False
                for retry in range(3):
                    try:
                        count = await page.locator('table tbody tr').count()
                        if count > 0:
                            table_found = True
                            break
                    except:
                        pass
                    await page.wait_for_timeout(1000)

                if not table_found:
                    no_data = await page.locator("text='No data available'").count()
                    if no_data > 0:
                        await browser.close()
                        return []
                    await page.screenshot(path=f"panel_{panel['id']}_no_table.png")
                    print(f"Panel {panel['id']}: No table found")
                    await browser.close()
                    return []

                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.select_one('table.dataTable tbody')
                if not table:
                    table = soup.select_one('table tbody')
                if not table:
                    table = soup.find('table')
                    if table:
                        table = table.find('tbody')
                if not table:
                    await browser.close()
                    return []

                rows = table.find_all('tr')
                if not rows:
                    await browser.close()
                    return []

                number_field, number_row = parse_field_row(panel['number_field'])
                message_field, message_row = parse_field_row(panel['message_field'])
                timestamp_field, timestamp_row = parse_field_row(panel.get('timestamp_field'))
                service_field, service_row = parse_field_row(panel.get('service_field'))

                results = []
                for tr in rows:
                    cols = tr.find_all('td')
                    if len(cols) < max(number_row, message_row, timestamp_row or 0, service_row or 0):
                        continue
                    number = cols[number_row - 1].get_text(strip=True) if number_row <= len(cols) else ""
                    message = cols[message_row - 1].get_text(strip=True) if message_row <= len(cols) else ""
                    timestamp = cols[timestamp_row - 1].get_text(strip=True) if timestamp_row and timestamp_row <= len(cols) else ""
                    service = cols[service_row - 1].get_text(strip=True) if service_row and service_row <= len(cols) else ""

                    if not number or not message:
                        continue

                    otp = extract_otp_from_message(message)
                    if not otp:
                        otp = "N/A"

                    country = get_country_from_number(number)
                    country_code = get_country_code(country) if country else ""

                    results.append({
                        "number": number,
                        "otp": otp,
                        "message": message,
                        "service": service or "UNKNOWN",
                        "country": country or "Unknown",
                        "country_code": country_code,
                        "timestamp": timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                await browser.close()
                return results

        except Exception as e:
            last_exception = e
            print(f"Panel {panel['id']} attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                raise last_exception

    return []

async def cdr_poll_loop(panel_id: int):
    if panel_id not in polling_cycle_counts:
        polling_cycle_counts[f"cdr_{panel_id}"] = 0
    consecutive_failures = 0
    last_success_time = datetime.now()
    while True:
        try:
            panel = get_cdr_panel(panel_id)
            if not panel or not panel['active']:
                break
            interval = panel.get('interval_sec', 30)
            polling_cycle_counts[f"cdr_{panel_id}"] += 1
            cycle = polling_cycle_counts[f"cdr_{panel_id}"]

            otps = await cdr_fetch_once(panel)
            if otps is not None:
                consecutive_failures = 0
                last_success_time = datetime.now()
                new_count = len(otps)
                if new_count > 0:
                    processed = await process_otps(otps, bot=application.bot)
                    if processed > 0:
                        db_exec("UPDATE cdr_panels SET total_otps = total_otps + ?, last_poll_time = ? WHERE id = ?",
                                (processed, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), panel_id))
                        logger.info(f"[CDR: {panel.get('panel_name', panel_id)}] 🔄 Polling cycle #{cycle} – ✅ Success ({processed} new OTPs)")
                    else:
                        logger.info(f"[CDR: {panel.get('panel_name', panel_id)}] 🔄 Polling cycle #{cycle} – ℹ️ Found {new_count} OTP(s), but no new ones")
                else:
                    logger.info(f"[CDR: {panel.get('panel_name', panel_id)}] 🔄 Polling cycle #{cycle} – ℹ️ No OTPs found")
                db_exec("INSERT INTO cdr_logs (panel_id, timestamp, status, message, otp_count) VALUES (?, ?, 'success', ?, ?)",
                        (panel_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "OK", new_count))
                db_exec("UPDATE cdr_panels SET error_count = 0 WHERE id = ?", (panel_id,))
            else:
                consecutive_failures += 1
                logger.warning(f"[CDR: {panel.get('panel_name', panel_id)}] 🔄 Polling cycle #{cycle} – ❌ Fetch returned None")
                db_exec("UPDATE cdr_panels SET error_count = error_count + 1 WHERE id = ?", (panel_id,))

            if consecutive_failures >= 3 or (datetime.now() - last_success_time).total_seconds() > 120:
                logger.warning(f"[CDR: {panel.get('panel_name', panel_id)}] ⚠️ Recovery triggered (failures={consecutive_failures}, inactivity={(datetime.now()-last_success_time).seconds}s). Clearing cookies and resetting...")
                db_exec("UPDATE cdr_panels SET cookie_data = NULL WHERE id = ?", (panel_id,))
                consecutive_failures = 0
                last_success_time = datetime.now()

        except Exception as e:
            err_msg = str(e)[:200]
            consecutive_failures += 1
            db_exec("INSERT INTO cdr_logs (panel_id, timestamp, status, message, otp_count) VALUES (?, ?, 'error', ?, 0)",
                    (panel_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), err_msg, 0))
            db_exec("UPDATE cdr_panels SET error_count = error_count + 1, last_error = ? WHERE id = ?",
                    (err_msg, panel_id))
            logger.error(f"[CDR: {panel.get('panel_name', panel_id)}] 🔄 Polling cycle #{cycle} – ❌ {err_msg}")

        await asyncio.sleep(interval)

# ================= CDR HELPER FUNCTIONS =================
def get_cdr_panel(panel_id: int) -> dict | None:
    row = db_fetch_one("""
        SELECT id, panel_name, login_url, smscdr_url, username, password,
               number_field, message_field, timestamp_field, service_field,
               interval_sec, active, last_poll_time, total_otps, error_count, last_error,
               created_by, created_at, updated_at, cookie_data
        FROM cdr_panels WHERE id = ?
    """, (panel_id,))
    if not row:
        return None
    cols = ['id','panel_name','login_url','smscdr_url','username','password',
            'number_field','message_field','timestamp_field','service_field',
            'interval_sec','active','last_poll_time','total_otps','error_count','last_error',
            'created_by','created_at','updated_at','cookie_data']
    return dict(zip(cols, row))

def parse_field_row(field_str: str) -> tuple:
    if not field_str:
        return "", 0
    parts = field_str.split('|')
    if len(parts) == 2:
        return parts[0].strip(), int(parts[1].strip())
    return field_str.strip(), 1

async def cdr_panel_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, panel_id: int, user_id: int):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    panel = get_cdr_panel(panel_id)
    if not panel:
        await update.answer("Panel not found!", show_alert=True)
        return
    admin_panel_state[user_id] = f"cdr_detail_{panel_id}"
    header = f"{emoji_tag(CUSTOM_EMOJIS['CDR_PANEL'], '📦')} <b>Manage: {panel['panel_name']}</b>"
    info = (
        f"{emoji_tag(CUSTOM_EMOJIS['CDR_ACTIVE'] if panel['active'] else CUSTOM_EMOJIS['CDR_INACTIVE'], '🟢' if panel['active'] else '🔴')} Status: <b>{'ACTIVE' if panel['active'] else 'INACTIVE'}</b>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_TODAY_OTP'], '📈')} Total OTPs: <code>{panel.get('total_otps', 0)}</code>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_LAST_POLL'], '⏰')} Last Poll: <code>{panel.get('last_poll_time', 'Never')}</code>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_ERROR_COUNT'], '❌')} Errors: <code>{panel.get('error_count', 0)}</code>"
    )
    btns = []
    if panel['active']:
        btns.append(InlineKeyboardButton("STOP POLLING", callback_data=f"cdr_toggle|{panel_id}", style=KBS.DANGER,
                                         icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_STOP_POLL", ""))))
    else:
        btns.append(InlineKeyboardButton("START POLLING", callback_data=f"cdr_toggle|{panel_id}", style=KBS.SUCCESS,
                                         icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_START_POLL", ""))))
    btns.append(InlineKeyboardButton("EDIT", callback_data=f"cdr_edit|{panel_id}", style=KBS.PRIMARY,
                                     icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("EDIT_BALANCE", ""))))
    btns.append(InlineKeyboardButton("TEST LOGIN", callback_data=f"cdr_test_login|{panel_id}", style=KBS.PRIMARY,
                                     icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CDR_TEST_LOGIN", ""))))
    btns.append(InlineKeyboardButton("TEST FETCH", callback_data=f"cdr_test_fetch|{panel_id}", style=KBS.PRIMARY,
                                     icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CDR_TEST_FETCH", ""))))
    btns.append(InlineKeyboardButton("FORCE POLL", callback_data=f"cdr_force|{panel_id}", style=KBS.PRIMARY,
                                     icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CDR_FORCE_POLL", ""))))
    btns.append(InlineKeyboardButton("STATS", callback_data=f"cdr_stats|{panel_id}", style=KBS.PRIMARY,
                                     icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CDR_STATS", ""))))
    btns.append(InlineKeyboardButton("LOGS", callback_data=f"cdr_logs|{panel_id}", style=KBS.PRIMARY,
                                     icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CDR_LOGS", ""))))
    btns.append(InlineKeyboardButton("DELETE", callback_data=f"cdr_delete|{panel_id}", style=KBS.DANGER,
                                     icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CDR_DELETE", ""))))
    btns.append(InlineKeyboardButton("BACK TO LIST", callback_data="cdr_list", style=KBS.PRIMARY,
                                     icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))))
    rows = [[btn] for btn in btns]
    sep = emoji_tag(CUSTOM_EMOJIS["API_SEPARATOR"], "➖") * 20
    text = f"{header}\n\n{info}\n\n{sep}\n\n"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)

# ================= CDR TOGGLE, EDIT, DELETE, TEST, STATS, LOGS =================
async def cdr_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    panel_id = int(query.data.split('|')[1])
    panel = get_cdr_panel(panel_id)
    if not panel:
        await query.answer("Panel not found!", show_alert=True)
        return
    if panel['active']:
        await stop_cdr_polling(panel_id)
        db_exec("UPDATE cdr_panels SET active = 0 WHERE id = ?", (panel_id,))
        await query.answer("Polling stopped.")
    else:
        db_exec("UPDATE cdr_panels SET active = 1 WHERE id = ?", (panel_id,))
        await start_cdr_polling(panel_id)
        await query.answer("Polling started.")
    await cdr_panel_detail(update, context, panel_id, user_id)

async def cdr_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    panel_id = int(query.data.split('|')[1])
    panel = get_cdr_panel(panel_id)
    if not panel:
        await query.answer("Panel not found!", show_alert=True)
        return
    admin_panel_state[user_id] = f"cdr_edit_{panel_id}"
    fields = [
        ("Panel Name", "panel_name", CUSTOM_EMOJIS.get("API_FIELD_NAME", "5818775306974006843"), KBS.SUCCESS),
        ("Login URL", "login_url", CUSTOM_EMOJIS.get("CDR_LOGIN_URL", "6285048454255220485"), KBS.SUCCESS),
        ("SMSCDR URL", "smscdr_url", CUSTOM_EMOJIS.get("CDR_SMSCDR_URL", "6267172559851099903"), KBS.SUCCESS),
        ("Username", "username", CUSTOM_EMOJIS.get("CDR_USERNAME", "5818775306974006843"), KBS.SUCCESS),
        ("Password", "password", CUSTOM_EMOJIS.get("CDR_PASSWORD", "5821453562680448557"), KBS.SUCCESS),
        ("Number Field", "number_field", CUSTOM_EMOJIS.get("CDR_FIELD_NUMBER", "5877410604225924969"), KBS.PRIMARY),
        ("Message Field", "message_field", CUSTOM_EMOJIS.get("CDR_FIELD_MESSAGE", "5980911993140284450"), KBS.PRIMARY),
        ("Timestamp Field", "timestamp_field", CUSTOM_EMOJIS.get("CDR_FIELD_TIMESTAMP", "6285240160120477644"), KBS.PRIMARY),
        ("Service Field", "service_field", CUSTOM_EMOJIS.get("CDR_FIELD_SERVICE", "5818967150278218011"), KBS.PRIMARY),
        ("Interval", "interval_sec", CUSTOM_EMOJIS.get("API_FIELD_INTERVAL", "6093456762113888541"), KBS.SUCCESS),
    ]
    rows = []
    for label, key, emoji_id, style in fields:
        value = panel.get(key)
        if key == "password":
            display = '*' * len(value) if value else 'Not set'
        else:
            display = str(value)[:30] + "..." if len(str(value)) > 30 else value
        rows.append([InlineKeyboardButton(f"{label}: {display}", callback_data=f"cdr_edit_field|{panel_id}|{key}",
                                          style=style, icon_custom_emoji_id=safe_icon(emoji_id))])
    rows.append([InlineKeyboardButton("BACK TO DETAIL", callback_data=f"cdr_detail|{panel_id}", style=KBS.DANGER,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    text = f"{emoji_tag(CUSTOM_EMOJIS['CDR_EDIT'], '✏️')} <b>Edit CDR Panel: {panel['panel_name']}</b>\n\nSelect a field to edit:"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)

async def cdr_edit_field_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    data = query.data.split('|')
    panel_id = int(data[1])
    field = data[2]
    panel = get_cdr_panel(panel_id)
    if not panel:
        await query.answer("Panel not found!", show_alert=True)
        return
    admin_temp_data[user_id] = {"cdr_panel_id": panel_id, "cdr_field": field, "cdr_current": panel.get(field)}
    admin_panel_state[user_id] = f"cdr_edit_value_{panel_id}"
    current_val = panel.get(field, "")
    if field == "password":
        display_val = '*' * len(current_val) if current_val else "Not set"
    else:
        display_val = str(current_val)
    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['CDR_EDIT'], '✏️')} Edit <b>{field}</b>\n\nCurrent value:\n<code>{display_val}</code>\n\nSend new value (or /cancel):",
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data=f"cdr_edit|{panel_id}", style=KBS.DANGER, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]]),
                                  parse_mode='HTML')

async def cdr_edit_value_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = admin_panel_state.get(user_id)
    if not state or not state.startswith("cdr_edit_value_"):
        return False
    panel_id = int(state.split("_")[-1])
    data = admin_temp_data.get(user_id, {})
    field = data.get("cdr_field")
    if not field:
        await update.message.reply_text("Session expired. Please start over.")
        return True
    new_value = update.message.text.strip()
    if new_value.lower() == "/cancel":
        await cdr_edit_menu(update, context)
        return True
    if field == "interval_sec":
        try:
            new_value = int(new_value)
            if new_value < 1:
                await update.message.reply_text("Interval must be at least 1 second.")
                return True
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")
            return True
    db_exec(f"UPDATE cdr_panels SET {field} = ?, updated_at = ? WHERE id = ?",
            (new_value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), panel_id))
    admin_temp_data.pop(user_id, None)
    admin_panel_state[user_id] = "main"
    await update.message.reply_text(f"✅ {field} updated successfully!")
    await cdr_panel_detail(update, context, panel_id, user_id)
    return True

async def cdr_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    panel_id = int(query.data.split('|')[1])
    panel = get_cdr_panel(panel_id)
    if not panel:
        await query.answer("Panel not found!", show_alert=True)
        return
    text = f"{emoji_tag(CUSTOM_EMOJIS['CDR_DELETE'], '🗑️')} <b>Confirm Delete</b>\n\nAre you sure you want to delete CDR panel <b>{panel['panel_name']}</b>?\nThis will remove all configuration and stop polling."
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("YES, DELETE", callback_data=f"cdr_delete_yes|{panel_id}", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("YES", ""))),
         InlineKeyboardButton("NO, CANCEL", callback_data=f"cdr_delete_no|{panel_id}", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("NO", "")))]
    ])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

async def cdr_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    data = query.data.split('|')
    panel_id = int(data[1])
    action = data[0]
    if action == "cdr_delete_yes":
        await stop_cdr_polling(panel_id)
        db_exec("DELETE FROM cdr_panels WHERE id = ?", (panel_id,))
        db_exec("DELETE FROM cdr_logs WHERE panel_id = ?", (panel_id,))
        await query.answer("Panel deleted.")
        await cdr_list(update, context, user_id)
    else:
        await query.answer("Cancelled.")
        await cdr_panel_detail(update, context, panel_id, user_id)

async def cdr_test_fetch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    panel_id = int(query.data.split('|')[1])
    panel = get_cdr_panel(panel_id)
    if not panel:
        await query.answer("Panel not found!", show_alert=True)
        return
    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['CDR_TEST_FETCH'], '📥')} Testing fetch for <b>{panel['panel_name']}</b> ...", parse_mode='HTML')
    try:
        result = await cdr_fetch_once(panel)
        if result:
            count = len(result)
            sample = "\n".join([f"• {r.get('number','')} → OTP: {r.get('otp','N/A')}" for r in result[:3]])
            more = f"\n... and {count-3} more" if count > 3 else ""
            msg = f"✅ Found <b>{count}</b> OTP(s)\n\n{sample}{more}"
        else:
            msg = "✅ Fetched successfully, but no new OTPs found."
    except Exception as e:
        msg = f"❌ Exception: {str(e)}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=f"cdr_detail|{panel_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['CDR_TEST_FETCH'], '📥')} <b>Test Fetch Result: {panel['panel_name']}</b>\n\n{msg}", reply_markup=kb, parse_mode='HTML')

async def cdr_force(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    panel_id = int(query.data.split('|')[1])
    panel = get_cdr_panel(panel_id)
    if not panel:
        await query.answer("Panel not found!", show_alert=True)
        return
    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['CDR_FORCE_POLL'], '🔄')} Force polling <b>{panel['panel_name']}</b> ...", parse_mode='HTML')
    try:
        otps = await cdr_fetch_once(panel)
        if otps:
            new_count = await process_otps(otps, bot=application.bot)
            if new_count > 0:
                db_exec("UPDATE cdr_panels SET total_otps = total_otps + ?, last_poll_time = ? WHERE id = ?",
                        (new_count, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), panel_id))
            result = f"✅ Found and processed <b>{new_count}</b> new OTP(s)."
        else:
            result = "✅ Fetched successfully, but no new OTPs found."
    except Exception as e:
        result = f"❌ Exception: {str(e)}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=f"cdr_detail|{panel_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['CDR_FORCE_POLL'], '🔄')} <b>Force Poll Result: {panel['panel_name']}</b>\n\n{result}", reply_markup=kb, parse_mode='HTML')

async def cdr_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    panel_id = int(query.data.split('|')[1])
    panel = get_cdr_panel(panel_id)
    if not panel:
        await query.answer("Panel not found!", show_alert=True)
        return
    total_otps = panel.get('total_otps', 0)
    last_poll = panel.get('last_poll_time', 'Never')
    today = datetime.now().strftime("%Y-%m-%d")
    today_otps = db_fetch_one("SELECT SUM(otp_count) FROM cdr_logs WHERE panel_id = ? AND timestamp LIKE ? AND status = 'success'",
                              (panel_id, f"{today}%"))[0] or 0
    logs = db_fetch_all("SELECT status FROM cdr_logs WHERE panel_id = ? ORDER BY timestamp DESC LIMIT 50", (panel_id,))
    success = sum(1 for log in logs if log[0] == 'success')
    rate = (success / len(logs) * 100) if logs else 0
    text = (
        f"{emoji_tag(CUSTOM_EMOJIS['CDR_STATS'], '📊')} <b>Statistics: {panel['panel_name']}</b>\n\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_TOTAL_OTP'], '📊')} Total OTPs: <code>{total_otps}</code>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_TODAY_OTP'], '📈')} Today's OTPs: <code>{today_otps}</code>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_SUCCESS_RATE'], '🏆')} Success Rate (last 50): <code>{rate:.1f}%</code>\n"
        f"{emoji_tag(CUSTOM_EMOJIS['API_LAST_POLL'], '⏰')} Last Poll: <code>{last_poll}</code>"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=f"cdr_detail|{panel_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

async def cdr_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("Admin only!", show_alert=True)
        return
    panel_id = int(query.data.split('|')[1])
    panel = get_cdr_panel(panel_id)
    if not panel:
        await query.answer("Panel not found!", show_alert=True)
        return
    logs = db_fetch_all("SELECT timestamp, status, message, otp_count FROM cdr_logs WHERE panel_id = ? ORDER BY timestamp DESC LIMIT 10", (panel_id,))
    if not logs:
        lines = ["No logs yet."]
    else:
        lines = []
        for ts, status, msg, count in logs:
            emoji = "✅" if status == "success" else "❌"
            count_str = f"{count} OTPs" if status == "success" else ""
            lines.append(f"{emoji} <code>{ts}</code> – {msg} {count_str}")
    text = f"{emoji_tag(CUSTOM_EMOJIS['CDR_LOGS'], '📜')} <b>Logs: {panel['panel_name']}</b>\n\n" + "\n".join(lines[:10])
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Refresh", callback_data=f"cdr_logs|{panel_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_FORCE_POLL", "")))],
        [InlineKeyboardButton("Back", callback_data=f"cdr_detail|{panel_id}", style=KBS.PRIMARY,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

# ================= CDR LIST =================
async def cdr_list(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    panels = db_fetch_all("SELECT id, panel_name, active FROM cdr_panels ORDER BY id")
    if not panels:
        text = "📭 No NON API panels configured."
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add Panel", callback_data="cdr_add_choice", style=KBS.SUCCESS,
                                  icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADD_API_KEY", "")))],
            [InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                  icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
        ])
        await reply_or_edit(update, text, reply_markup=kb, context=context, auto_delete=False)
        return
    rows = []
    for pid, pname, active in panels:
        style = KBS.SUCCESS if active else KBS.DANGER
        icon = CUSTOM_EMOJIS.get("CDR_ACTIVE" if active else "CDR_INACTIVE", "")
        rows.append([InlineKeyboardButton(pname, callback_data=f"cdr_detail|{pid}", style=style, icon_custom_emoji_id=safe_icon(icon))])
    rows.append([InlineKeyboardButton("Add Panel", callback_data="cdr_add_choice", style=KBS.SUCCESS,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("ADD_API_KEY", "")))])
    rows.append([InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    text = f"{emoji_tag(CUSTOM_EMOJIS['CDR_PANEL'], '📦')} <b>NON API PANELS</b> ({len(panels)} configured)"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)

# ================= CDR POLL START/STOP =================
async def start_cdr_polling(panel_id: int):
    if panel_id in cdr_polling_tasks and not cdr_polling_tasks[panel_id].done():
        return
    task = asyncio.create_task(cdr_poll_loop(panel_id))
    cdr_polling_tasks[panel_id] = task

async def stop_cdr_polling(panel_id: int):
    if panel_id in cdr_polling_tasks:
        cdr_polling_tasks[panel_id].cancel()
        del cdr_polling_tasks[panel_id]
    db_exec("UPDATE cdr_panels SET active = 0 WHERE id = ?", (panel_id,))

async def start_all_cdr_panels():
    panels = db_fetch_all("SELECT id FROM cdr_panels WHERE active = 1")
    for (pid,) in panels:
        await start_cdr_polling(pid)

# ================= CDR WRAPPERS =================
async def cdr_detail_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    panel_id = int(query.data.split('|')[1])
    await cdr_panel_detail(update, context, panel_id, user_id)

async def cdr_list_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await cdr_list(update, context, user_id)

async def cdr_add_choice_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await cdr_add_start(update, context, user_id)

# ================= MANAGE API MENU =================
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
        [InlineKeyboardButton("NON API PANELS", callback_data="cdr_list", style=KBS.SUCCESS,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("CDR_PANEL", "")))],
        [InlineKeyboardButton("Back", callback_data="admin_back", style=KBS.DANGER,
                              icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))],
    ])
    await reply_or_edit(update, "🔧 MANAGE API & PANELS\n\nSelect an option:", reply_markup=kb, context=context, auto_delete=False)

# ================= MANAGE API MENU WRAPPER (MISSING) =================
async def manage_api_menu_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await manage_api_menu(update, context, user_id)

# ================= API LIST (UNIFIED) =================
async def api_list(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not is_admin(user_id):
        await update.answer("Admin only!", show_alert=True)
        return
    apis = db_fetch_all("SELECT id, panel_name, active FROM api_keys ORDER BY id")
    cdrs = db_fetch_all("SELECT id, panel_name, active FROM cdr_panels ORDER BY id")
    lines = []
    for pid, pname, active in apis:
        status = "🟢" if active else "🔴"
        icon = CUSTOM_EMOJIS.get("API_LIST_ICON", "5411225014148014586")
        lines.append(f"{emoji_tag(icon, '📌')} <b>{pname}</b> (API) {status}")
    for cid, cname, active in cdrs:
        status = "🟢" if active else "🔴"
        icon = CUSTOM_EMOJIS.get("CDR_PANEL", "6206236607532504295")
        lines.append(f"{emoji_tag(icon, '📦')} <b>{cname}</b> (CDR) {status}")
    if not lines:
        text = "📭 No panels configured."
    else:
        text = f"{emoji_tag(CUSTOM_EMOJIS['LIST_API_KEY'], '📋')} <b>ALL PANELS</b>\n\n" + "\n".join(lines)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="admin_manage_api", style=KBS.PRIMARY,
                                                      icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

async def api_list_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await api_list(update, context, user_id)

async def api_system_grid_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await api_system_grid(update, context, user_id)

# ================= API DETAIL PAGE =================
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
        btns.append(InlineKeyboardButton("STOP POLLING", callback_data=f"api_toggle|{api_id}", style=KBS.DANGER, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_STOP_POLL", ""))))
    else:
        btns.append(InlineKeyboardButton("START POLLING", callback_data=f"api_toggle|{api_id}", style=KBS.SUCCESS, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_START_POLL", ""))))
    btns.append(InlineKeyboardButton("EDIT", callback_data=f"api_edit|{api_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("EDIT_BALANCE", ""))))
    btns.append(InlineKeyboardButton("TEST", callback_data=f"api_test|{api_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_TEST", ""))))
    btns.append(InlineKeyboardButton("STATS", callback_data=f"api_stats|{api_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_STATS", ""))))
    btns.append(InlineKeyboardButton("LOGS", callback_data=f"api_logs|{api_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_LOGS", ""))))
    btns.append(InlineKeyboardButton("DELETE", callback_data=f"api_delete|{api_id}", style=KBS.DANGER, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("DELETE", ""))))
    btns.append(InlineKeyboardButton("FORCE POLL", callback_data=f"api_force|{api_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_FORCE_POLL", ""))))
    btns.append(InlineKeyboardButton("BACK TO LIST", callback_data="api_system", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", ""))))
    rows = [[btn] for btn in btns]
    sep = emoji_tag(CUSTOM_EMOJIS["API_SEPARATOR"], "➖") * 20
    text = f"{header}\n\n{info}\n\n{sep}\n\n"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)

async def api_detail_page_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    api_id = int(query.data.split('|')[1])
    await api_detail_page(update, context, api_id, user_id)

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
        rows.append([InlineKeyboardButton(f"{label}: {display_value}", callback_data=f"api_edit_field|{api_id}|{field}",
                                          style=style, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get(emoji_key, "")))])
    rows.append([InlineKeyboardButton("BACK TO DETAIL", callback_data=f"api_detail|{api_id}", style=KBS.DANGER, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))])
    text = f"{emoji_tag(CUSTOM_EMOJIS['EDIT_BALANCE'], '✏️')} <b>Edit Configuration: {config['panel_name']}</b>\n\nSelect a field to edit:"
    await reply_or_edit(update, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode='HTML', context=context, auto_delete=False)

async def api_edit_menu_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    api_id = int(query.data.split('|')[1])
    await api_edit_menu(update, context, api_id, user_id)

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
    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['EDIT_BALANCE'], '✏️')} Edit <b>{field}</b>\n\nCurrent value:\n<code>{display_val}</code>\n\nSend new value (or /cancel):",
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data=f"api_edit|{api_id}", style=KBS.DANGER, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]]),
                                  parse_mode='HTML')

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
                    sample = "\n".join([f"{emoji_tag(CUSTOM_EMOJIS['API_OTP_COUNT'], '📨')} {i+1}. {otp.get('number', 'N/A')} – OTP: {otp.get('otp', '?')}" for i, otp in enumerate(otps[:5])])
                    more = f"\n... and {len(otps)-5} more" if len(otps) > 5 else ""
                    result = f"✅ Found <b>{len(otps)}</b> OTP(s)\n\n{sample}{more}"
                else:
                    result = "✅ API responded but no OTPs found.\n\nRaw response (first 300 chars):\n<code>" + text[:300] + "</code>"
            else:
                result = f"❌ Error: HTTP {status}\n\nResponse:\n<code>{text[:500]}</code>"
    except Exception as e:
        result = f"❌ Exception: {str(e)}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['API_TEST'], '🧪')} <b>Test Result: {config['panel_name']}</b>\n\n{result}", reply_markup=kb, parse_mode='HTML')

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
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

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
        [InlineKeyboardButton("Refresh", callback_data=f"api_logs|{api_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("API_FORCE_POLL", "")))],
        [InlineKeyboardButton("Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]
    ])
    await reply_or_edit(update, text, reply_markup=kb, parse_mode='HTML', context=context, auto_delete=False)

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
    text = f"{emoji_tag(CUSTOM_EMOJIS['DELETE'], '🗑️')} <b>Confirm Delete</b>\n\nAre you sure you want to delete API <b>{config['panel_name']}</b>?\nThis will remove all configuration and stop polling."
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("YES, DELETE", callback_data=f"api_delete_yes|{api_id}", style=KBS.DANGER, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("YES", ""))),
         InlineKeyboardButton("NO, CANCEL", callback_data=f"api_delete_no|{api_id}", style=KBS.SUCCESS, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("NO", "")))]
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
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=f"api_detail|{api_id}", style=KBS.PRIMARY, icon_custom_emoji_id=safe_icon(CUSTOM_EMOJIS.get("BACK", "")))]])
    await query.edit_message_text(f"{emoji_tag(CUSTOM_EMOJIS['API_FORCE_POLL'], '🔄')} <b>Force Poll Result: {config['panel_name']}</b>\n\n{result}", reply_markup=kb, parse_mode='HTML')

# ================= RESPONSE PARSER =================
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
            if "message" in entry and entry["message"]:
                otp = extract_otp_from_message(entry["message"])
                if otp:
                    entry["otp"] = otp
            if "otp" not in entry:
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
                otps = extract_all_otps_from_message(content)
                if otps:
                    return [{"message": content[:200], "otp": otp} for otp in otps]
                else:
                    return [{"message": content[:200], "otp": "N/A"}]
        if isinstance(content, dict):
            return ResponseParser.parse_json_response(content, config)
        return []

# ================= GET API CONFIG =================
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

# ================= OTP PROCESSING =================
async def process_otps(otps_list, context: ContextTypes.DEFAULT_TYPE = None, bot=None):
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
    group_ids = GROUP_IDS
    semaphore = asyncio.Semaphore(50)
    new_otp_count = 0

    async def safe_send_message(chat_id, text, reply_markup=None, parse_mode='HTML'):
        async with semaphore:
            try:
                await bot.send_message(chat_id=chat_id, text=apply_emojis(text), reply_markup=reply_markup, parse_mode=parse_mode)
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
        otp_code = extract_otp_from_message(message)
        if otp_code is None:
            otp_code = otp_entry.get("otp", "")
            if not otp_code:
                otp_code = "N/A"
        if not number:
            return 0

        # DEDUPLICATION: 1 second window (global)
        existing = db_fetch_one(
            "SELECT id, timestamp FROM otps WHERE number=? AND otp=? AND (user_id=0 OR user_id>0) ORDER BY timestamp DESC LIMIT 1",
            (number, otp_code)
        )
        if existing:
            try:
                last_ts = datetime.strptime(existing[1], "%Y-%m-%d %H:%M:%S")
                if (now - last_ts).total_seconds() < 1:
                    return 0
            except:
                pass

        if not existing:
            db_exec("INSERT INTO otps (number, otp, message, timestamp, forwarded, user_id) VALUES (?,?,?,?,1,0)",
                    (number, otp_code, message, otp_timestamp_str))
            
            # Send to group only if new globally
            if group_ids:
                try:
                    grp_text, grp_kb = format_group_otp_rich({
                        "number": number,
                        "otp": otp_code,
                        "service": service_name,
                        "country_code": otp_entry.get("country_code", ""),
                        "country": otp_entry.get("country", ""),
                        "message": message
                    })
                    for gid in group_ids:
                        await bot.send_message(chat_id=gid, text=apply_emojis(grp_text), reply_markup=InlineKeyboardMarkup(grp_kb['inline_keyboard']), parse_mode='HTML')
                except Exception as e:
                    print(f"Group send failed: {e}")

        clean_number = number.replace('+', '')
        local_tasks = []
        if clean_number in num_map:
            print(f"✅ Found {len(num_map[clean_number])} active users for number {clean_number}")
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
                # Check duplicate for this specific user
                user_otp_exists = db_fetch_one("SELECT id FROM otps WHERE number=? AND otp=? AND user_id=?", (number, otp_code, uid))
                if user_otp_exists:
                    continue
                user_recent = db_fetch_one(
                    "SELECT timestamp FROM otps WHERE number=? AND otp=? AND user_id=? ORDER BY timestamp DESC LIMIT 1",
                    (number, otp_code, uid)
                )
                if user_recent:
                    try:
                        last_ts = datetime.strptime(user_recent[0], "%Y-%m-%d %H:%M:%S")
                        if (now - last_ts).total_seconds() < 1:
                            continue
                    except:
                        pass

                # Send to user
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
                    f'{emoji_tag(flag_eid, "🏁")}<b>{country_iso} OTP ARRIVED</b> '
                    f'{emoji_tag("6100453534422013617", "✨")}\n'
                    f'{emoji_tag("6204108584381322968", "📱")} <b>NUMBER</b>: <code>+{number}</code>\n'
                    f'{emoji_tag("5976327845696251345", "📲")} <b>APP</b>: {emoji_tag(svc_eid, "⚙️")} <b>{service_name}</b>\n'
                    f'💰 <b>BALANCE ADDED</b>: <code>+${reward}</code>{emoji_tag("5976788549658221281", "💵")}'
                )
                button = InlineKeyboardMarkup([[InlineKeyboardButton(text=otp_code, copy_text=CopyTextButton(text=otp_code), style=KBS.SUCCESS, icon_custom_emoji_id=safe_icon("5330115548900501467"))]])
                local_tasks.append(safe_send_message(uid, header, button))
                new_otp_count += 1
        else:
            print(f"❌ No active user found for number: {clean_number}")

        if local_tasks:
            await asyncio.gather(*local_tasks)
        return 1 if existing is None else 0

    tasks = [process_single_otp(otp) for otp in otps_list]
    results = await asyncio.gather(*tasks)
    total_global_new = sum(results)
    save_user_data_json()
    return total_global_new

# ================= GENERIC TEXT HANDLER =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if await handle_admin_text(update, context):
        return
    if await handle_api_add_text(update, context):
        return
    if await handle_edit_value_text(update, context):
        return
    if await cdr_handle_add_text(update, context):
        return
    if await cdr_edit_value_text(update, context):
        return
    if await force_join_text_handler(update, context):
        return
    user_id = update.effective_user.id
    if await ban_check(update, context):
        return
    text = update.message.text.strip()
    if text == BTN_GET_NUMBER:
        await send_get_number_panel(update, context)
    elif text == BTN_BALANCE:
        await send_balance_panel(update, context)
    elif text == BTN_INVITE:
        await show_invite(update, context)
    elif text == BTN_SUPPORT:
        await send_support_panel(update, context)
    elif text == BTN_ADMIN:
        await send_admin_panel_msg(update, context)

# ================= FORCE JOIN TEXT HANDLER =================
async def force_join_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = admin_panel_state.get(user_id)
    if state == "waiting_fj_channel":
        chat_identifier = update.message.text.strip()
        # Try to fetch channel info
        try:
            res = requests.get(BASE_URL + f"getChat?chat_id={chat_identifier}").json()
            if res.get('ok'):
                chat = res['result']
                if chat['type'] in ['channel', 'supergroup']:
                    invite_link = None
                    try:
                        inv = requests.post(BASE_URL + f"exportChatInviteLink?chat_id={chat['id']}").json()
                        if inv.get('ok'):
                            invite_link = inv['result']
                    except:
                        pass
                    channel_data = {
                        'id': chat['id'],
                        'username': chat.get('username', ''),
                        'title': chat.get('title', 'Channel'),
                        'invite_link': invite_link or ''
                    }
                    channels = get_force_join_channels()
                    channels.append(channel_data)
                    set_force_join_channels(channels)
                    await update.message.reply_text(f"✅ Channel '{chat.get('title')}' added successfully!")
                    await admin_force_join(update, context)
                    admin_panel_state[user_id] = None
                else:
                    await update.message.reply_text("❌ This is not a channel or supergroup.")
            else:
                await update.message.reply_text("❌ Failed to fetch channel. Ensure the bot is admin and the chat ID/username is correct.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
        return True
    return False

# ================= handle_edit_value_text (MISSING) =================
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

# ================= ERROR HANDLER =================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

# ================= MAIN =================
def main():
    global application, BOT_USERNAME
    os.system('cls' if os.name == 'nt' else 'clear')
    # Fetch bot username
    try:
        res = requests.get(BASE_URL + "getMe").json()
        if res.get('ok'):
            BOT_USERNAME = res['result']['username']
    except:
        BOT_USERNAME = "SRNumberHubBot"
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

    application.add_handler(CallbackQueryHandler(manage_api_menu_wrapper, pattern="^admin_manage_api$"))
    application.add_handler(CallbackQueryHandler(api_add_choice, pattern="^api_add_choice$"))
    application.add_handler(CallbackQueryHandler(api_choice_handler, pattern="^api_choice_(api|cdr)$"))
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
    application.add_handler(CallbackQueryHandler(api_add_curl_continue, pattern="^api_add_curl_continue$"))
    application.add_handler(CallbackQueryHandler(api_add_curl_cancel, pattern="^api_add_curl_cancel$"))

    application.add_handler(CallbackQueryHandler(cdr_add_choice_wrapper, pattern="^cdr_add_choice$"))
    application.add_handler(CallbackQueryHandler(cdr_handle_add_skip, pattern="^cdr_add_skip$"))
    application.add_handler(CallbackQueryHandler(cdr_handle_add_cancel, pattern="^cdr_add_cancel$"))
    application.add_handler(CallbackQueryHandler(cdr_add_confirm_yes, pattern="^cdr_add_confirm_yes$"))
    application.add_handler(CallbackQueryHandler(cdr_add_confirm_no, pattern="^cdr_add_confirm_no$"))
    application.add_handler(CallbackQueryHandler(cdr_add_edit, pattern="^cdr_add_edit$"))
    application.add_handler(CallbackQueryHandler(cdr_list_wrapper, pattern="^cdr_list$"))
    application.add_handler(CallbackQueryHandler(cdr_detail_wrapper, pattern=r"^cdr_detail\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(cdr_toggle, pattern=r"^cdr_toggle\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(cdr_edit_menu, pattern=r"^cdr_edit\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(cdr_edit_field_prompt, pattern=r"^cdr_edit_field\|(\d+)\|(.+)$"))
    application.add_handler(CallbackQueryHandler(cdr_delete, pattern=r"^cdr_delete\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(cdr_delete_confirm, pattern=r"^cdr_delete_(yes|no)\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(cdr_test_login, pattern=r"^cdr_test_login\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(cdr_test_fetch, pattern=r"^cdr_test_fetch\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(cdr_force, pattern=r"^cdr_force\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(cdr_stats, pattern=r"^cdr_stats\|(\d+)$"))
    application.add_handler(CallbackQueryHandler(cdr_logs, pattern=r"^cdr_logs\|(\d+)$"))

    # AIR CONTROL callbacks
    application.add_handler(CallbackQueryHandler(admin_air_control, pattern="^admin_air_control$"))
    application.add_handler(CallbackQueryHandler(admin_air_otp_control, pattern="^air_otp_control$"))
    application.add_handler(CallbackQueryHandler(admin_air_otp_control_edit, pattern="^(air_def_rate|air_srv_rate|del_srv_rate_.+)$"))
    application.add_handler(CallbackQueryHandler(air_control_edit, pattern="^(air_min_w|air_ref_r|air_cool|air_num_req|air_w_group|manage_w_methods|add_w_method|del_w_method_.+)$"))

    # Force Join callbacks
    application.add_handler(CallbackQueryHandler(admin_force_join, pattern="^admin_force_join$"))
    application.add_handler(CallbackQueryHandler(force_join_toggle, pattern="^toggle_fj$"))
    application.add_handler(CallbackQueryHandler(force_join_add_channel, pattern="^add_fj$"))
    application.add_handler(CallbackQueryHandler(force_join_delete_channel, pattern=r"^del_fj_\d+$"))
    application.add_handler(CallbackQueryHandler(force_join_check, pattern="^check_fj_joined$"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_error_handler(error_handler)

    if application.job_queue:
        application.job_queue.run_repeating(periodic_json_save, interval=60, first=10)

    async def start_api_tasks(app):
        print("🚀 Checking for configured API/CDR panels...")
        apis = db_fetch_all("SELECT id FROM api_keys WHERE active = 1")
        cdrs = db_fetch_all("SELECT id FROM cdr_panels WHERE active = 1")
        if not apis and not cdrs:
            print("ℹ️ No active API or CDR panels found. Polling not started.")
            return
        if apis:
            print(f"🚀 Starting {len(apis)} API polling tasks...")
            await start_all_polling()
        if cdrs:
            print(f"🚀 Starting {len(cdrs)} CDR panel polling tasks...")
            await start_all_cdr_panels()

    application.post_init = start_api_tasks

    save_user_data_json()
    print(f"✅ Super Admins: {SUPER_ADMIN_IDS}")
    print(f"✅ Bot username: @{BOT_USERNAME}")
    print("✅ Full bot started with Multi-API System, Country Map, and NON API CDR Panel support.")
    print("🔄 Starting polling...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
