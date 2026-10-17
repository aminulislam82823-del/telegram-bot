import asyncio
import io
import re
import json
import html
import os
import httpx
import pyotp
import random
import string
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

# ==================== CONFIG SECTION ====================

BOT_TOKEN = "8946386467:AAEKTwoDOWtbq7gqX1FIIdRAJ1JH3-GDMNc"
USER_DATA_FILE = "users.json"
PAID_SMS_FILE = "paid_sms.json"
STATS_FILE = "user_stats.json"
REFERRAL_DATA_FILE = "referral_data.json"
BANNED_USERS_FILE = "banned_users.json"
WITHDRAW_DATA_FILE = "withdraw_requests.json"
ACTIVITY_LOGS_FILE = "activity_logs.json"
DATA_RANGE_FILE = "datarange.json"
SYS_CONFIG_FILE = "sys_config.json"

# ==================== MULTIPLE ADMINS CONFIGURATION ====================
ADMINS = [8380777485]
OTP_GROUP_ID = -1003941468281

# ==================== OTP RATE & VALUATION ====================
OTP_RATE = 0.20  # এটি আপনি আপনার ইচ্ছামতো পরিবর্তন করতে পারবেন
REFERRAL_PRICE = 0
MIN_WITHDRAW = 50
MAX_WITHDRAW = 10000

# ==================== SUPPORT & DEVELOPER LINKS ====================
SUPPORT_LINK = "https://t.me/shiyam7444"
DEVELOPER_LINK = "https://t.me/shiyam744"

# ==================== PERSISTENT CONFIGURATION LOADER ====================
def load_sys_config():
    if not os.path.exists(SYS_CONFIG_FILE):
        default_config = {
            "official_channel_id": None,
            "official_channel_link": "",
            "api_key": "FASTXOTP_6F62B5EFBBD6E0392DADC775",
            "base_url": "https://otpapi.miahhost.com/@Telegram/@Bot/3oo10/@public"
        }
        with open(SYS_CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    try:
        with open(SYS_CONFIG_FILE, "r") as f:
            cfg = json.load(f)
            if "api_key" not in cfg:
                cfg["api_key"] = "FASTXOTP_6F62B5EFBBD6E0392DADC775"
            if "base_url" not in cfg:
                cfg["base_url"] = "https://otpapi.miahhost.com/@Telegram/@Bot/3oo10/@public"
            return cfg
    except Exception:
        return {
            "official_channel_id": None, 
            "official_channel_link": "",
            "api_key": "FASTXOTP_6F62B5EFBBD6E0392DADC775",
            "base_url": "https://otpapi.miahhost.com/@Telegram/@Bot/3oo10/@public"
        }

def save_sys_config(cfg):
    with open(SYS_CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

sys_cfg = load_sys_config()

def get_api_key():
    return load_sys_config().get("api_key", "")

def get_base_url():
    return load_sys_config().get("base_url", "").rstrip("/")

def get_async_client():
    return httpx.AsyncClient(
        timeout=httpx.Timeout(connect=3.0, read=8.0, write=5.0, pool=3.0),
        headers={"X-API-Key": get_api_key()},
        limits=httpx.Limits(max_connections=1000, max_keepalive_connections=200)
    )

LANG_TEXTS = {
    "en": {
        "welcome": "💎 <b>[ ACCESS GRANTED ]</b> 💎\n━━━━━━━━━━━━━━━━━━━━━━\n🟢 Connection Status: <code>SECURE</code>\n⚙️ Decryption Protocol: <code>ACTIVE</code>",
        "btn_get_num": "📲 GET NUMBER",
        "btn_search_otp": "🔎 SEARCH OTP",
        "btn_2fa": "🔑 GET 2FA",
        "btn_balance": "🪙 BALANCE",
        "btn_refer": "👥 REFER & EARN",
        "btn_profile": "👑 PROFILE",
        "btn_leaderboard": "🏆 LEADERBOARD",
        "btn_support": "💬 SUPPORT",
        "btn_lang": "🌐 LANGUAGE",
        "btn_admin": "⚙️ ADMIN PANEL ⚙️",
        "banned": "🛑 YOU ARE BANNED!",
        "join_prompt": "🔔 <b>Official Channel Subscription</b>\n━━━━━━━━━━━━━━━━━━━━━━\nPlease subscribe to our channel to proceed with utilizing bot services safely.",
        "btn_join": "🔔 Join Channel",
        "btn_continue": "❇️ Continue",
        "balance_title": "🪙 <b>CORE WALLET BALANCE</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n💵 Liquid Funds: <code>{bal} BDT</code>",
        "btn_withdraw": "💳 WITHDRAW",
        "withdraw_min_err": "<blockquote>🪙 Current balance: {bal} BDT\n📉 Minimum withdrawal boundary is {min_val} BDT</blockquote>",
        "withdraw_method_prompt": "💳 Select your destination payment gateway:",
        "withdraw_amount_prompt": "🪙 Please enter withdrawal valuation (Min: {min_val} BDT):",
        "withdraw_number_prompt": "📲 Send your receiving address (Format: 017XXXXXXXX):",
        "withdraw_proposed": "✨ <b>PROPOSED TRANSACTION DETAILS</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n<blockquote>💳 GATEWAY: {method}\n📲 DESTINATION: {num}\n🪙 AMOUNT: {amount} BDT</blockquote>\n\nConfirm to proceed.",
        "search_otp_prompt": "🔎 <b>Enter the target number to decrypt OTP:</b>",
        "search_otp_searching": "🔎 Checking database logs, please wait...",
        "search_otp_not_found": "🛑 <b>NO OTP RECORDED</b>\n━━━━━━━━━━━━━━━━━━━━━━\n📟 Address: `+{num}`\n⏳ Status: No active packet found.",
        "get_2fa_prompt": "🔑 <b>Enter your 2FA Secret Key:</b>",
        "2fa_invalid": "🛑 <b>INVALID SECRET KEY</b>\n\nPlease check the parameters and try again.",
        "node_alloc_fail": "🛑 <b>NODE ALLOCATION FAILED</b>\n\nNo available numbers at this range right now.",
        "get_active_node": "📲 <b>[ GET ACTIVE NODE ]</b>\n\nSelect your target service from the database:",
        "pick_country": "📲 <b>[ GET ACTIVE NODE ]</b>\n\n🎯 Service: <b>{sid}</b>\n🌍 Select origin prefix:",
        "custom_range_prompt": "⚙️ <b>[ CUSTOM RANGE ]</b>\n\nType custom range parameter (e.g. 234XXX):",
        "invalid_range": "🛑 <b>INVALID RANGE PARAMETERS!</b>\nFormat example: <code>234XXX</code>"
    },
    "bn": {
        "welcome": "💎 <b>[ নোড অ্যাক্সেস সফল ]</b> 💎\n━━━━━━━━━━━━━━━━━━━━━━\n🟢 সংযোগ স্ট্যাটাস: <code>সক্রিয়</code>\n⚙️ ডিক্রিপশন প্রোটোকল: <code>চলমান</code>",
        "btn_get_num": "📲 নম্বর নিন",
        "btn_search_otp": "🔎 ওটিপি খুঁজুন",
        "btn_2fa": "🔑 2FA কোড নিন",
        "btn_balance": "🪙 ব্যালেন্স",
        "btn_refer": "👥 রেফার করুন",
        "btn_profile": "👑 প্রোফাইল",
        "btn_leaderboard": "🏆 লিডারবোর্ড",
        "btn_support": "💬 সাপোর্ট",
        "btn_lang": "🌐 ভাষা পরিবর্তন",
        "btn_admin": "⚙️ অ্যাডমিন প্যানেল ⚙️",
        "banned": "🛑 আপনি ব্যান হয়েছেন!",
        "join_prompt": "🔔 <b>অফিশিয়াল চ্যানেলে জয়েন করুন</b>\n━━━━━━━━━━━━━━━━━━━━━━\nবটের সার্ভিসগুলো নিরাপদে ব্যবহার করতে আমাদের আপডেট চ্যানেলে যুক্ত হোন।",
        "btn_join": "🔔 চ্যানেলে জয়েন করুন",
        "btn_continue": "❇️ প্রবেশ করুন",
        "balance_title": "🪙 <b>ওয়ালেট ব্যালেন্স</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n💵 মোট ব্যালেন্স: <code>{bal} BDT</code>",
        "btn_withdraw": "💸 উইথড্র করুন",
        "withdraw_min_err": "<blockquote>🪙 বর্তমান ব্যালেন্স: {bal} BDT\n📉 সর্বনিম্ন উইথড্র হচ্ছে {min_val} BDT</blockquote>",
        "withdraw_method_prompt": "💳 পেমেন্ট গেটওয়ে সিলেক্ট করুন (বিকাশ অথবা নগদ):",
        "withdraw_amount_prompt": "🪙 উইথড্র করার পরিমাণটি লিখুন (সর্বনিম্ন: {min_val} BDT):",
        "withdraw_number_prompt": "📲 পেমেন্ট নম্বরটি পাঠান (যেমন: 017XXXXXXXX):",
        "withdraw_proposed": "✨ <b>প্রস্তাবিত উইথড্র ডিটেইলস</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n<blockquote>💳 গেটওয়ে: {method}\n📲 নম্বর: {num}\n🪙 পরিমাণ: {amount} BDT</blockquote>\n\nনিশ্চিত করতে কনফার্ম বাটনে ক্লিক করুন।",
        "search_otp_prompt": "🔎 <b>ওটিপি খুঁজতে নম্বরটি দিন:</b>",
        "search_otp_searching": "🔎 ডেটাবেজ চেক করা হচ্ছে, দয়া করে অপেক্ষা করুন...",
        "search_otp_not_found": "🛑 <b>কোনো ওটিপি পাওয়া যায়নি</b>\n━━━━━━━━━━━━━━━━━━━━━━\n📟 নম্বর: `+{num}`\n⏳ স্ট্যাটাস: কোনো সক্রিয় ওটিপি পাওয়া যায়নি।",
        "get_2fa_prompt": "🔑 <b>আপনার 2FA সিক্রেট কী-টি পাঠান:</b>",
        "2fa_invalid": "🛑 <b>ভুল সিক্রেট কী!</b>\n\nদয়া করে সঠিক কী-টি পুনরায় ট্রাই করুন।",
        "node_alloc_fail": "🛑 <b>নম্বর অ্যালোকেশন ব্যর্থ</b>\n\nএই রেঞ্জে বর্তমানে কোনো নম্বর খালি নেই।",
        "get_active_node": "📲 <b>[ নম্বর নোড কানেকশন ]</b>\n\nনিচের লিস্ট থেকে আপনার টার্গেট সার্ভিসটি সিলেক্ট করুন:",
        "pick_country": "📲 <b>[ নম্বর নোড কানেকশন ]</b>\n\n🎯 সার্ভিস: <b>{sid}</b>\n🌍 কান্ট্রি বা দেশ সিলেক্ট করুন:",
        "custom_range_prompt": "⚙️ <b>[ কাস্টম রেঞ্জ সেটআপ ]</b>\n\nম্যানুয়ালি রেঞ্জ ইনপুট করুন (যেমন: 234XXX বা 225XXX):",
        "invalid_range": "🛑 <b>ভুল রেঞ্জ ফরম্যাট!</b>\nসঠিক ফরম্যাটের উদাহরণ: <code>234XXX</code>"
    }
}

T_GET_NUM = ["📲 GET NUMBER", "📲 নম্বর নিন"]
T_SEARCH_OTP = ["🔎 SEARCH OTP", "🔎 ওটিপি খুঁজুন"]
T_2FA = ["🔑 GET 2FA", "🔑 2FA কোড নিন"]
T_BALANCE = ["🪙 BALANCE", "🪙 ব্যালেন্স"]
T_REFER = ["👥 REFER & EARN", "👥 রেফার করুন"]
T_PROFILE = ["👑 PROFILE", "👑 প্রোফাইল"]
T_LEADERBOARD = ["🏆 LEADERBOARD", "🏆 লিডারবোর্ড"]
T_SUPPORT = ["💬 SUPPORT", "💬 সাপোর্ট"]
T_LANG = ["🌐 LANGUAGE", "🌐 ভাষা পরিবর্তন"]
T_ADMIN = ["⚙️ ADMIN PANEL ⚙️", "⚙️ অ্যাডমিন প্যানেল ⚙️"]
T_CANCEL = ["🛑 CANCEL", "🛑 বাতিল", "🛑 ABORT"]

request_queue = asyncio.Queue()
active_numbers = {}
last_range = {}
CHECK_INTERVAL = 1.5

_liveaccess_cache = {"services": []}
LIVEACCESS_REFRESH_INTERVAL = 25

async def _do_liveaccess_fetch():
    global _liveaccess_cache
    base_url = get_base_url()
    if not base_url:
        return
    try:
        async with get_async_client() as client_async:
            r = await client_async.get(f"{base_url}/api/liveaccess")
            data = r.json()
            if data.get("status") == "ok":
                svcs = data.get("services", [])
                if svcs:
                    _liveaccess_cache["services"] = svcs
    except Exception as e:
        print(f"[liveaccess] fetch error: {e}")

async def liveaccess_refresh_loop():
    while True:
        await _do_liveaccess_fetch()
        await asyncio.sleep(LIVEACCESS_REFRESH_INTERVAL)

def get_cached_services():
    return _liveaccess_cache["services"]

def is_admin(user_id):
    return user_id in ADMINS

def load_data(filename=USER_DATA_FILE):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data, filename=USER_DATA_FILE):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def get_user(uid):
    uid = str(uid)
    data = load_data()
    if uid not in data:
        data[uid] = {
            "user_id": uid, "balance": 0.0, "total_numbers": 0, 
            "referral_count": 0, "lang": None, "verified": False
        }
        save_data(data)
    else:
        modified = False
        if "lang" not in data[uid]:
            data[uid]["lang"] = None
            modified = True
        if "verified" not in data[uid]:
            data[uid]["verified"] = False
            modified = True
        if modified:
            save_data(data)
    return data[uid]

def set_user_lang(uid, lang):
    uid = str(uid)
    data = load_data()
    if uid in data:
        data[uid]["lang"] = lang
        save_data(data)

def get_user_lang(uid):
    user = get_user(uid)
    return user.get("lang") or "bn"

def set_user_verified(uid, verified=True):
    uid = str(uid)
    data = load_data()
    if uid in data:
        data[uid]["verified"] = verified
        save_data(data)

def is_user_verified(uid):
    user = get_user(uid)
    return user.get("verified", False)

async def update_db_balance(uid, amount):
    uid = str(uid)
    data = load_data()
    if uid in data:
        data[uid]["balance"] = round(data[uid].get("balance", 0.0) + amount, 2)
        save_data(data)
        return data[uid]["balance"]
    return 0.0

def get_all_users():
    data = load_data(USER_DATA_FILE)
    return list(data.keys()) if data else []

def user_exists(uid):
    data = load_data(USER_DATA_FILE)
    return str(uid) in data

def load_withdraw_requests():
    return load_data(WITHDRAW_DATA_FILE)

def save_withdraw_requests(data):
    save_data(data, WITHDRAW_DATA_FILE)

def generate_payment_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        with open(BANNED_USERS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(BANNED_USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_banned_users(banned_list):
    save_data(banned_list, BANNED_USERS_FILE)

def is_user_banned(uid):
    banned_list = load_banned_users()
    return str(uid) in banned_list

def ban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str not in banned_list:
        banned_list.append(uid_str)
        save_banned_users(banned_list)
        return True
    return False

def unban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str in banned_list:
        banned_list.remove(uid_str)
        save_banned_users(banned_list)
        return True
    return False

def load_referral_data():
    return load_data(REFERRAL_DATA_FILE)

def save_referral_data(data):
    save_data(data, REFERRAL_DATA_FILE)

def update_referral_count(uid, count):
    referral_data = load_referral_data()
    uid_str = str(uid)
    if uid_str not in referral_data:
        referral_data[uid_str] = {"referral_count": 0}
    referral_data[uid_str]["referral_count"] = count
    save_referral_data(referral_data)

def get_referral_count(uid):
    referral_data = load_referral_data()
    uid_str = str(uid)
    return referral_data.get(uid_str, {}).get("referral_count", 0)

def load_range_db():
    return load_data(DATA_RANGE_FILE)

def save_range_db(data):
    save_data(data, DATA_RANGE_FILE)

def save_number_range_info(uid, number, range_text):
    db = load_range_db()
    flag, name = get_country_info(number)
    db[normalize_number(number)] = {
        "user_id": str(uid),
        "number": f"+{normalize_number(number)}",
        "range": range_text,
        "country": f"{flag} {name}"
    }
    save_range_db(db)

def get_country_info(number):
    number = str(number).strip()
    country_map = {
        "2376": ("🇨🇲", "Cameroon"), "2250": ("🇨🇮", "Ivory Coast"), "2613": ("🇲🇬", "Madagascar"), "4077": ("🇷🇴", "Romania"),
        "237": ("🇨🇲", "Cameroon"), "225": ("🇨🇮", "Ivory Coast"), "261": ("🇲🇬", "Madagascar"), "20": ("🇪🇬", "Egypt"),
        "27": ("🇿🇦", "South Africa"), "234": ("🇳🇬", "Nigeria"), "254": ("🇰🇪", "Kenya"), "233": ("🇬🇭", "Ghana"),
        "212": ("🇲🇦", "Morocco"), "213": ("🇩ℤ", "Algeria"), "216": ("🇹🇳", "Tunisia"), "218": ("🇱🇾", "Libya"),
        "249": ("🇸🇩", "Sudan"), "251": ("🇪🇹", "Ethiopia"), "252": ("🇸🇴", "Somalia"), "253": ("🇩🇯", "Djibouti"),
        "255": ("🇹🇿", "Tanzania"), "256": ("🇺🇬", "Uganda"), "257": ("🇧🇮", "Burundi"), "258": ("🇲🇿", "Mozambique"),
        "260": ("🇿🇲", "Zambia"), "263": ("🇿🇼", "Zimbabwe"), "264": ("🇳🇦", "Namibia"), "265": ("🇲🇼", "Malawi"),
        "266": ("🇱🇸", "Lesotho"), "267": ("🇧🇼", "Botswana"), "268": ("🇸🇿", "Swaziland"), "269": ("🇰🇲", "Comoros"),
        "220": ("🇬🇲", "Gambia"), "221": ("🇸🇳", "Senegal"), "222": ("🇲🇷", "Mauritania"), "223": ("🇲🇱", "Mali"),
        "224": ("🇬🇳", "Guinea"), "226": ("🇧🇫", "Burkina Faso"), "227": ("🇳🇪", "Niger"), "228": ("🇹🇬", "Togo"),
        "229": ("🇧🇯", "Benin"), "230": ("🇲🇺", "Mauritius"), "231": ("🇱🇷", "Liberia"), "232": ("🇸🇱", "Sierra Leone"),
        "235": ("🇹🇩", "Chad"), "236": ("🇨🇫", "Central African Republic"), "238": ("🇨🇻", "Cape Verde"),
        "239": ("🇸🇹", "Sao Tome and Principe"), "240": ("🇬🇶", "Equatorial Guinea"), "241": ("🇬🇦", "Gabon"),
        "242": ("🇨🇬", "Congo"), "243": ("🇨🇩", "DR Congo"), "244": ("🇦🇴", "Angola"), "245": ("🇬🇼", "Guinea-Bissau"),
        "247": ("🇸🇭", "Saint Helena"), "248": ("🇸🇨", "Seychelles"), "250": ("🇷🇼", "Rwanda"), "290": ("🇸🇭", "Saint Helena"),
        "291": ("🇪🇷", "Eritrea"), "40": ("🇷🇴", "Romania"), "44": ("🇬🇧", "United Kingdom"), "33": ("🇫🇷", "France"),
        "49": ("🇩🇪", "Germany"), "39": ("🇮🇹", "Italy"), "34": ("🇪🇸", "Spain"), "31": ("🇳🇱", "Netherlands"),
        "32": ("🇧🇪", "Belgium"), "41": ("🇨🇭", "Switzerland"), "43": ("🇦🇹", "Austria"), "46": ("🇸🇪", "Sweden"),
        "47": ("🇳🇴", "Norway"), "45": ("🇩🇰", "Denmark"), "358": ("🇫🇮", "Finland"), "351": ("🇵🇹", "Portugal"),
        "353": ("🇮🇪", "Ireland"), "36": ("🇭🇺", "Hungary"), "48": ("🇵🇱", "Poland"), "380": ("🇺🇦", "Ukraine"),
        "370": ("🇱🇹", "Lithuania"), "371": ("🇱🇻", "Latvia"), "372": ("🇪🇪", "Estonia"), "373": ("🇲🇩", "Moldova"),
        "374": ("🇦🇲", "Armenia"), "375": ("🇧🇾", "Belarus"), "376": ("🇦🇩", "Andorra"), "377": ("🇲🇨", "Monaco"),
        "381": ("🇷🇸", "Serbia"), "382": ("🇲🇪", "Montenegro"), "385": ("🇭🇷", "Croatia"), "386": ("🇸🇮", "Slovenia"),
        "387": ("🇧🇦", "Bosnia and Herzegovina"), "389": ("🇲🇰", "North Macedonia"), "350": ("🇬🇮", "Gibraltar"),
        "352": ("🇱🇺", "Luxembourg"), "354": ("🇮🇸", "Iceland"), "355": ("🇦🇱", "Albania"), "356": ("🇲🇹", "Malta"),
        "357": ("🇨🇾", "Cyprus"), "359": ("🇧🇬", "Bulgaria"), "421": ("🇸🇰", "Slovakia"), "420": ("🇨🇿", "Czech Republic"),
        "298": ("🇫🇴", "Faroe Islands"), "299": ("🇬🇱", "Greenland"), "1": ("🇺🇸", "United States"), "7": ("🇷🇺", "Russia"),
        "91": ("🇮🇳", "India"), "92": ("🇵🇰", "Pakistan"), "880": ("🇧🇩", "Bangladesh"), "86": ("🇨🇳", "China"),
        "81": ("🇯🇵", "Japan"), "82": ("🇰🇷", "South Korea"), "84": ("🇻🇳", "Vietnam"), "66": ("🇹🇭", "Thailand"),
        "62": ("🇮🇩", "Indonesia"), "60": ("🇲🇾", "Malaysia"), "65": ("🇸🇬", "Singapore"), "63": ("🇵🇭", "Philippines"),
        "95": ("🇲🇲", "Myanmar"), "94": ("🇱🇱", "Sri Lanka"), "977": ("🇳🇵", "Nepal"), "93": ("🇦🇫", "Afghanistan"),
        "98": ("🇮🇷", "Iran"), "90": ("🇹🇷", "Turkey"), "964": ("🇮🇶", "Iraq"), "963": ("🇸🇾", "Syria"),
        "961": ("🇱🇧", "Lebanon"), "962": ("🇯🇴", "Jordan"), "965": ("🇰🇼", "Kuwait"), "966": ("🇸🇦", "Saudi Arabia"),
        "967": ("🇾🇲", "Yemen"), "968": ("🇴🇲", "Oman"), "971": ("🇦🇪", "United Arab Emirates"), "972": ("🇮🇱", "Israel"),
        "973": ("🇧🇭", "Bahrain"), "974": ("🇶🇦", "Qatar"), "994": ("🇦🇿", "Azerbaijan"), "995": ("🇬🇪", "Georgia"),
        "996": ("🇰🇬", "Kyrgyzstan"), "992": ("🇹🇯", "Tajikistan"), "993": ("🇹🇲", "Turkmenistan"), "998": ("🇺🇿", "Uzbekistan"),
        "855": ("🇰🇭", "Cambodia"), "856": ("🇱🇦", "Laos"), "976": ("🇲🇳", "Mongolia"), "850": ("🇰🇵", "North Korea"),
        "55": ("🇧🇷", "Brazil"), "52": ("🇲🇽", "Mexico"), "54": ("🇦🇷", "Argentina"), "57": ("🇨🇴", "Colombia"),
        "51": ("🇵🇪", "Peru"), "58": ("🇻🇪", "Venezuela"), "56": ("🇨🇱", "Chile"), "593": ("🇪🇨", "Ecuador"),
        "591": ("🇧🇴", "Bolivia"), "595": ("🇵🇾", "Paraguay"), "598": ("🇺🇾", "Uruguay"), "502": ("🇬🇹", "Guatemala"),
        "503": ("🇸🇻", "El Salvador"), "504": ("🇭🇳", "Honduras"), "506": ("🇨🇷", "Costa Rica"), "507": ("🇵🇦", "Panama"),
        "509": ("🇭🇹", "Haiti"), "501": ("🇧🇿", "Belize"), "61": ("🇦🇺", "Australia"), "64": ("🇳ℤ", "New Zealand"),
        "675": ("🇵🇬", "Papua New Guinea"), "679": ("🇫🇯", "Fiji"), "1246": ("🇧🇧", "Barbados"), "1876": ("🇯🇲", "Jamaica"),
        "53": ("🇨🇺", "Cuba"), "592": ("🇬🇾", "Guyana"),
    }
    clean_num = str(number).replace('+', '').replace(' ', '').replace('-', '').strip()
    sorted_prefixes = sorted(country_map.keys(), key=len, reverse=True)
    for prefix in sorted_prefixes:
        if clean_num.startswith(prefix):
            return country_map[prefix]
    return ("🌍", "Unknown")

def detect_service(full_sms):
    if not full_sms:
        return "SMS SERVICE"
    sms_lower = full_sms.lower()
    service_keywords = {
        "facebook": "FACEBOOK", "fb": "FACEBOOK", "instagram": "INSTAGRAM", "insta": "INSTAGRAM",
        "tiktok": "TIKTOK", "twitter": "TWITTER", "x.com": "TWITTER", "snapchat": "SNAPCHAT", "snap": "SNAPCHAT",
        "whatsapp": "WHATSAPP", "telegram": "TELEGRAM", "discord": "DISCORD", "messenger": "MESSENGER",
        "linkedin": "LINKEDIN", "google": "GOOGLE", "gmail": "GOOGLE", "amazon": "AMAZON", "microsoft": "MICROSOFT",
        "outlook": "MICROSOFT", "yahoo": "YAHOO", "paypal": "PAYPAL", "binance": "BINANCE", "coinbase": "COINBASE",
        "spotify": "SPOTIFY", "netflix": "NETFLIX", "uber": "UBER", "apple": "APPLE", "icloud": "APPLE",
        "bkash": "BKASH", "nagad": "NAGAD", "stripe": "STRIPE", "line": "LINE", "wechat": "WECHAT",
        "viber": "VIBER", "signal": "SIGNAL", "pubg": "PUBG", "free fire": "FREE FIRE"
    }
    for keyword, service_name in sorted(service_keywords.items(), key=lambda x: len(x[0]), reverse=True):
        if keyword in sms_lower:
            return service_name
    return "SMS SERVICE"

def get_service_logo(service_name):
    service_upper = str(service_name).upper()
    SERVICE_LOGOS = {
        "FACEBOOK": "🔵 FACEBOOK", "INSTAGRAM": "📸 INSTAGRAM", "TIKTOK": "🎵 TIKTOK", "TWITTER": "🐦 TWITTER",
        "SNAPCHAT": "👻 SNAPCHAT", "WHATSAPP": "🟢 WHATSAPP", "TELEGRAM": "✈️ TELEGRAM", "DISCORD": "👾 DISCORD",
        "MESSENGER": "💬 MESSENGER", "LINKEDIN": "💼 LINKEDIN", "GOOGLE": "📨 GOOGLE", "AMAZON": "🛒 AMAZON",
        "MICROSOFT": "💻 MICROSOFT", "YAHOO": "🟣 YAHOO", "PAYPAL": "💳 PAYPAL", "BINANCE": "🔶 BINANCE",
        "COINBASE": "🔵 COINBASE", "SPOTIFY": "🎧 SPOTIFY", "NETFLIX": "🎬 NETFLIX", "UBER": "🚗 UBER",
        "APPLE": "🍎 APPLE", "BKASH": "🌸 BKASH", "NAGAD": "🍊 NAGAD", "STRIPE": "💳 STRIPE",
        "LINE": "🟢 LINE", "WECHAT": "💬 WECHAT", "VIBER": "🟣 VIBER", "SIGNAL": "💬 SIGNAL",
        "PUBG": "🎮 PUBG", "FREE FIRE": "🔥 FREE FIRE"
    }
    return SERVICE_LOGOS.get(service_upper, "📩 SMS SERVICE")

def main_keyboard(user_id):
    lang = get_user_lang(user_id)
    t_get_num = LANG_TEXTS[lang]["btn_get_num"]
    t_search_otp = LANG_TEXTS[lang]["btn_search_otp"]
    t_2fa = LANG_TEXTS[lang]["btn_2fa"]
    t_balance = LANG_TEXTS[lang]["btn_balance"]
    t_refer = LANG_TEXTS[lang]["btn_refer"]
    t_profile = LANG_TEXTS[lang]["btn_profile"]
    t_leaderboard = LANG_TEXTS[lang]["btn_leaderboard"]
    t_support = LANG_TEXTS[lang]["btn_support"]
    t_lang = LANG_TEXTS[lang]["btn_lang"]
    t_admin = LANG_TEXTS[lang]["btn_admin"]

    keyboard = [
        [KeyboardButton(text=t_get_num)],
        [KeyboardButton(text=t_search_otp), KeyboardButton(text=t_2fa)],
        [KeyboardButton(text=t_balance)],
        [KeyboardButton(text=t_refer), KeyboardButton(text=t_profile)],
        [KeyboardButton(text=t_leaderboard)],
        [KeyboardButton(text=t_support), KeyboardButton(text=t_lang)]
    ]
    if is_admin(user_id):
        keyboard.append([KeyboardButton(text=t_admin)])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard(user_id):
    lang = get_user_lang(user_id)
    btn_lbl = "🛑 CANCEL" if lang == "en" else "🛑 বাতিল"
    return ReplyKeyboardMarkup([[KeyboardButton(text=btn_lbl)]], resize_keyboard=True)

def admin_main_keyboard():
    keyboard = [
        [KeyboardButton(text="👥 USER MANAGEMENT")],
        [KeyboardButton(text="⚙️ SYSTEM CONFIGURATION")],
        [KeyboardButton(text="🔙 BACK TO MAIN")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def user_management_keyboard():
    keyboard = [
        [KeyboardButton(text="📢 SEND MESSAGE TO ALL USERS")],
        [KeyboardButton(text="🆔 ALL USER ID")],
        [KeyboardButton(text="📜 BAN USER LIST")],
        [KeyboardButton(text="💰 ALL USER BALANCE")],
        [KeyboardButton(text="🔙 BACK TO ADMIN")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def system_config_keyboard():
    keyboard = [
        [KeyboardButton(text="📈 TODAY ALL STATUS"), KeyboardButton(text="👤 USER STATUS CHECK")],
        [KeyboardButton(text="📢 UPDATE JOINS"), KeyboardButton(text="🌐 UPDATE API SETTINGS")],
        [KeyboardButton(text="⛔ BAN USER"), KeyboardButton(text="🔓 UNBAN USER")],
        [KeyboardButton(text="📜 BAN USER LIST")],
        [KeyboardButton(text="➖ REMOVE BALANCE"), KeyboardButton(text="➕ ADD BALANCE")],
        [KeyboardButton(text="🔙 BACK TO ADMIN")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# উইথড্র অপশনে শুধু বিকাশ ও নগদ রাখা হয়েছে
def withdraw_method_keyboard(user_id):
    lang = get_user_lang(user_id)
    cancel_lbl = "🛑 CANCEL" if lang == "en" else "🛑 বাতিল"
    
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(text="📱 BKASH"), KeyboardButton(text="💵 NAGAD")],
        [KeyboardButton(text=cancel_lbl)]
    ], resize_keyboard=True)
    return keyboard

EMOJI_POOL = ['🍎', '🦊', '🚗', '🥑', '🍕', '⚽', '🎸', '🚀', '🐱', '🐼', '🍩', '🏀']

def generate_emoji_captcha():
    correct = random.sample(EMOJI_POOL, 3)
    correct_str = " ".join(correct)
    options = [correct_str]
    while len(options) < 4:
        wrong = random.sample(EMOJI_POOL, 3)
        wrong_str = " ".join(wrong)
        if wrong_str not in options:
            options.append(wrong_str)
    random.shuffle(options)
    return correct_str, options

async def send_verification_captcha(chat_id, context: ContextTypes.DEFAULT_TYPE, uid):
    correct_ans, options = generate_emoji_captcha()
    context.user_data["captcha_correct"] = correct_ans

    lang = get_user_lang(uid)
    if lang == "bn":
        text = (
            f"🛡️ <b>[ সিকিউরিটি ভেরিফিকেশন ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"নিচের ৩-ইমোজি সিকোয়েন্সটি হুবহু মিলিয়ে সঠিক বাটনে ক্লিক করুন:\n"
            f"👉 <code>{correct_ans}</code>"
        )
    else:
        text = (
            f"🛡️ <b>[ SECURITY VERIFICATION ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Please match the exact 3-emoji sequence below to proceed:\n"
            f"👉 <code>{correct_ans}</code>"
        )

    buttons = []
    for i, opt in enumerate(options):
        buttons.append([InlineKeyboardButton(text=opt, callback_data=f"captcha_opt_{i}")])
    
    context.user_data["captcha_options"] = options
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

def format_balance(balance):
    return f"{balance:.2f}"

def extract_otp(text):
    if not text or text == "No Content":
        return "N/A"
    spaced_otp = re.search(r'\b(\d{3}\s\d{3})\b', text)
    if spaced_otp:
        return spaced_otp.group(1).replace(" ", "")
    match = re.search(r'\b(\d{4,8})\b', text)
    return match.group(1) if match else "N/A"

def normalize_number(num):
    return re.sub(r'\D', '', str(num))

def mask_number(num):
    if len(num) > 6:
        return f"{num[:4]}****{num[-6:]}"
    return num

def get_date_reset_time():
    now = datetime.now()
    return datetime(now.year, now.month, now.day, 0, 0, 0)

def is_valid_bangladesh_number(number):
    number = re.sub(r'\D', '', str(number))
    return len(number) == 11 and number.startswith('01')

def is_range_request(param):
    return 'X' in param.upper()

def is_referral_request(param):
    return param.isdigit()

def load_stats():
    return load_data(STATS_FILE)

def save_stats(stats):
    save_data(stats, STATS_FILE)

def add_number_taken(uid, count=1):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    now = datetime.now().isoformat()
    for _ in range(count):
        stats[uid]["numbers_taken"].append(now)
    log_global_activity(uid, "NUMBER_TAKEN", {"count": count})
    save_stats(stats)

def add_otp_received(uid):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    stats[uid]["otps_received"].append(datetime.now().isoformat())
    save_stats(stats)

def get_user_stats(uid):
    uid = str(uid)
    stats = load_stats()
    user_stats = stats.get(uid, {"numbers_taken": [], "otps_received": []})
    now = datetime.now()
    today_midnight = get_date_reset_time()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    numbers_taken = user_stats.get("numbers_taken", [])
    otps_received = user_stats.get("otps_received", [])
    today_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) >= today_midnight)
    today_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) >= today_midnight)
    last24h_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_24h)
    last24h_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_24h)
    last7d_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_7d)
    last7d_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_7d)
    return {
        "total_numbers": len(numbers_taken), "total_otps": len(otps_received),
        "today_numbers": today_numbers, "today_otps": today_otps,
        "last24h_numbers": last24h_numbers, "last24h_otps": last24h_otps,
        "last7d_numbers": last7d_numbers, "last7d_otps": last7d_otps
    }

def log_global_activity(uid, action, details):
    if not os.path.exists(ACTIVITY_LOGS_FILE):
        with open(ACTIVITY_LOGS_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(ACTIVITY_LOGS_FILE, "r") as f:
            logs = json.load(f)
    except Exception:
        logs = []
    now = datetime.now()
    logs.append({
        "uid": str(uid), "action": action, "details": details,
        "timestamp": now.isoformat(),
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%H:%M:%S")
    })
    save_data(logs, ACTIVITY_LOGS_FILE)

def get_global_system_stats():
    stats = load_stats()
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day)
    last_7d = now - timedelta(days=7)
    total_n = total_o = today_n = today_o = seven_n = seven_o = 0
    for uid in stats:
        u = stats[uid]
        n_list = u.get("numbers_taken", [])
        o_list = u.get("otps_received", [])
        total_n += len(n_list)
        total_o += len(o_list)
        for t in n_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_n += 1
            if dt >= last_7d: seven_n += 1
        for t in o_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_o += 1
            if dt >= last_7d: seven_o += 1
    return today_n, today_o, seven_n, seven_o, total_n, total_o

async def check_channel_membership(bot, user_id, channel_id):
    if not channel_id:
        return True
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Membership verification failed: {e}")
        return True

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    stats_data = load_stats()
    today_midnight = get_date_reset_time()
    user_data_all = load_data(USER_DATA_FILE)
    user_today_counts = []
    for uid_str, user_stats in stats_data.items():
        otps_received = user_stats.get("otps_received", [])
        today_count = sum(1 for ts in otps_received if datetime.fromisoformat(ts) >= today_midnight)
        if today_count > 0:
            name = user_data_all.get(uid_str, {}).get("full_name") or user_data_all.get(uid_str, {}).get("username") or f"User {uid_str}"
            user_today_counts.append((uid_str, today_count, html.escape(name)))
    user_today_counts.sort(key=lambda x: x[1], reverse=True)
    top10 = user_today_counts[:10]

    title = "🏆 <b>TOP 10 OTP LEADERBOARD</b> 🏆\n━━━━━━━━━━━━━━━━━━━━━━\n\n" if lang == "en" else "🏆 <b>টপ ১০ ওটিপি লিডারবোর্ড</b> 🏆\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if not top10:
        msg = title + ("🛑 No decrypted OTP entries recorded today." if lang == "en" else "🛑 আজ এখনও কেউ ওটিপি পায়নি।")
    else:
        msg = title
        for idx, (uid_str, count, name) in enumerate(top10, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}️⃣"
            msg += f"{medal} <b>{name}</b> → 🔑 <code>{count}</code> OTPs\n"
        msg += "\n━━━━━━━━━━━━━━━━━━━━━━\n" + ("📊 <i>Resets at midnight automatically.</i>" if lang == "en" else "📊 <i>প্রতিদিন রাত ১২ টায় স্বয়ংক্রিয়ভাবে রিসেট হয়।</i>")

    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(uid))

def generate_2fa_code(secret_key):
    clean_secret = secret_key.replace(" ", "").strip()
    if not clean_secret:
        return None, None
    try:
        totp = pyotp.TOTP(clean_secret)
        return totp.now(), clean_secret
    except Exception:
        return None, None

async def get_2fa_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    context.user_data["mode"] = "get_2fa"
    await update.message.reply_text(
        LANG_TEXTS[lang]["get_2fa_prompt"],
        parse_mode="HTML",
        reply_markup=cancel_keyboard(uid)
    )

async def process_2fa_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    secret_key = update.message.text.strip()
    context.user_data["mode"] = None
    otp_code, clean_key = generate_2fa_code(secret_key)
    if otp_code is None:
        await update.message.reply_text(
            LANG_TEXTS[lang]["2fa_invalid"],
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return
    now = datetime.now()
    final_msg = (
        f"⏳ <b>[ 2FA DECRYPTION COMPLETE ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>🔑 SECRET_KEY: <code>{clean_key}</code></blockquote>\n"
        f"<blockquote>🔢 PIN_CODE: <code>{otp_code}</code></blockquote>\n"
        f"<blockquote>⏳ EXPIRES_IN: 30 SECONDS</blockquote>\n\n"
        f"📅 {now.strftime('%d %B, %Y')} | {now.strftime('%I:%M %p')}"
    )
    await update.message.reply_text(final_msg, parse_mode="HTML", reply_markup=main_keyboard(uid))

def _build_services_keyboard(services, user_id):
    buttons = []
    for i, svc in enumerate(services):
        sid = svc.get("sid", f"Service {i+1}")
        ranges = svc.get("ranges", [])
        label = f"🚀 {sid} ({len(ranges)})"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"svc_{i}")])
    custom_lbl = "⚙️ CUSTOM RANGE" if get_user_lang(user_id) == "en" else "⚙️ কাস্টম রেঞ্জ"
    buttons.append([InlineKeyboardButton(text=custom_lbl, callback_data="custom_range")])
    return InlineKeyboardMarkup(buttons)

def _build_countries_keyboard(ranges, service_idx, user_id):
    lang = get_user_lang(user_id)
    btns = []
    seen = {}
    for i, r in enumerate(ranges[:24]):
        prefix = re.sub(r'[xX]+$', '', str(r)).strip()
        prefix_clean = re.sub(r'\D', '', prefix)
        flag, cname = get_country_info(prefix_clean)
        label = f"{flag} {cname}"
        if label not in seen:
            seen[label] = i
            btns.append(InlineKeyboardButton(text=label, callback_data=f"rng_{i}"))
    rows = [btns[j:j+2] for j in range(0, len(btns), 2)]
    back_lbl = "◀️ BACK" if lang == "en" else "◀️ ফিরে যান"
    rows.append([InlineKeyboardButton(text=back_lbl, callback_data="back_services")])
    return InlineKeyboardMarkup(rows)

async def show_app_selection(update, context):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    services = get_cached_services()
    if not services:
        await _do_liveaccess_fetch()
        services = get_cached_services()
    if not services:
        err_msg = (
            "⚠️ <b>[ ACCESS FAIL ]</b>\n\n⏳ Server modules are currently sleeping or API is not configured. Check admin panel."
            if lang == "en" else "⚠️ <b>[ সংযোগ ব্যর্থ ]</b>\n\n⏳ সার্ভার মডিউল অফলাইন অথবা এপিআই কনফিগার করা নেই। অ্যাডমিন প্যানেল চেক করুন।"
        )
        await update.message.reply_text(err_msg, parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
    context.user_data["la_services"] = services
    keyboard = _build_services_keyboard(services, uid)
    await update.message.reply_text(
        LANG_TEXTS[lang]["get_active_node"],
        parse_mode="HTML",
        reply_markup=keyboard
    )

async def monitor_loop(app):
    while True:
        try:
            base_url = get_base_url()
            if not base_url:
                await asyncio.sleep(5)
                continue
            async with get_async_client() as client_async:
                r = await client_async.get(f"{base_url}/api/success-otp-info")
                res = r.json()
                if "data" in res and "otps" in res["data"]:
                    otps = res["data"]["otps"]
                    paid_data = load_data(PAID_SMS_FILE)
                    range_db = load_data(DATA_RANGE_FILE)
                    paid_keys_set = set(paid_data.keys())
                    processed_in_session = set()

                    for otp in otps:
                        num = normalize_number(otp.get("number", ""))
                        full_sms = otp.get('message') or otp.get('otp') or otp.get('sms') or "No SMS Content"
                        otp_code = extract_otp(full_sms)
                        otp_id = str(otp.get("otp_id", ""))
                        sms_key = otp_id if otp_id else f"{num}_{full_sms}"

                        if (num in active_numbers and
                                sms_key not in paid_keys_set and
                                sms_key not in processed_in_session):

                            details = active_numbers[num]
                            paid_keys_set.add(sms_key)
                            processed_in_session.add(sms_key)
                            paid_data[sms_key] = {"uid": details["uid"], "otp": otp_code}

                            await update_db_balance(details["uid"], OTP_RATE)
                            add_otp_received(details["uid"])
                            log_global_activity(details["uid"], "OTP_RECEIVED", {"number": num, "otp": otp_code, "sms": full_sms})

                            num_range_info = range_db.get(num, {}).get("range", "")
                            if not num_range_info:
                                num_range_info = active_numbers.get(num, {}).get("range", "")
                            if not num_range_info and num:
                                _d = re.sub(r'\D', '', str(num))
                                num_range_info = (_d[:-3] + 'XXX') if len(_d) > 3 else (_d + 'XXX')

                            country_flag, country_name = get_country_info(num)
                            service_name = detect_service(full_sms)
                            service_logo = get_service_logo(service_name)
                            clean_num = num.replace('+', '').strip()
                            full_number = f"+{clean_num}"
                            masked_number = f"+{mask_number(clean_num)}"

                            safe_full_sms = html.escape(str(full_sms))
                            safe_otp_code = html.escape(str(otp_code))

                            user_msg = (
                                f"🛰️ <b>[ INCOMING PACKET DECRYPTED ]</b>\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"🛰️ <b>NODE:</b> <code>{num_range_info}</code>\n"
                                f"🌍 <b>ORIGIN:</b> <code>{country_flag} {country_name}</code>\n"
                                f"📲 <b>TARGET:</b> <code>{service_logo}</code>\n"
                                f"📟 <b>ADDR:</b> <code>{full_number}</code>\n"
                                f"🔑 <b>KEY:</b> <code>{safe_otp_code}</code>\n\n"
                                f"<blockquote>📩 <b>FULL PACKET:</b>\n<code>{safe_full_sms}</code></blockquote>\n"
                                f"🪙 <b>Rewarded +{OTP_RATE:.2f} BDT to Wallet!</b>"
                            )

                            group_msg = (
                                f"🛰️ <b>[ INCOMING PACKET DECRYPTED ]</b>\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                f"🛰️ <b>NODE:</b> <code>{num_range_info}</code>\n"
                                f"🌍 <b>ORIGIN:</b> <code>{country_flag} {country_name}</code>\n"
                                f"📲 <b>TARGET:</b> <code>{service_logo}</code>\n"
                                f"📟 <b>ADDR:</b> <code>{masked_number}</code>\n"
                                f"🔑 <b>KEY:</b> <code>{safe_otp_code}</code>\n\n"
                                f"<blockquote>📩 <b>FULL PACKET:</b>\n<code>{safe_full_sms}</code></blockquote>"
                            )

                            # ইউজারের ইনবক্সে ওটিপি পাঠানোর ব্যবস্থা
                            try:
                                await app.bot.send_message(details["uid"], user_msg, parse_mode="HTML")
                            except Exception as e:
                                print(f"❌ User Message Send Fail: {e}")

                            # ওটিপি গ্রুপে ওটিপি পাঠানোর ব্যবস্থা
                            try:
                                await app.bot.send_message(OTP_GROUP_ID, group_msg, parse_mode="HTML")
                            except Exception as e:
                                print(f"❌ Group Send Fail: {e}")

                            save_data(paid_data, PAID_SMS_FILE)

                    current_time = datetime.now()
                    for num_key in list(active_numbers.keys()):
                        entry = active_numbers[num_key]
                        if 'timestamp' not in entry:
                            entry['timestamp'] = current_time
                        elif (current_time - entry['timestamp']).total_seconds() > 3600:
                            del active_numbers[num_key]

        except Exception as e:
            print(f"Monitor Error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

async def fetch_number_async(range_str):
    base_url = get_base_url()
    if not base_url:
        return None
    try:
        async with get_async_client() as client_async:
            r = await client_async.post(
                f"{base_url}/api/getnum",
                json={"range": range_str, "is_national": False}
            )
            data = r.json()
            d = data.get("data", {})
            if "full_number" in d:
                return {
                    "number":  d["full_number"],
                    "otp_now": bool(d.get("otp_now", False)),
                    "otp":     d.get("otp"),
                    "sms":     d.get("sms"),
                }
    except Exception as e:
        print(f"Fetch number error: {e}")
    return None

async def fast_allocate_number(query, context, range_text, sid):
    uid = query.from_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await query.message.edit_text(LANG_TEXTS[lang]["banned"])
        return
    try:
        res = await fetch_number_async(range_text)
    except Exception as e:
        await query.message.edit_text(f"❌ Server error: {str(e)[:100]}")
        return
    if not res or not res.get("number"):
        await query.message.edit_text(
            LANG_TEXTS[lang]["node_alloc_fail"],
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="◀️ BACK", callback_data="back_services")
            ]])
        )
        return

    clean_num = normalize_number(res["number"])
    add_number_taken(uid, 1)
    last_range[uid] = range_text
    active_numbers[clean_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now()}
    save_number_range_info(uid, clean_num, range_text)

    country_flag, country_name = get_country_info(clean_num)
    service_logo = get_service_logo(sid if sid else "SMS SERVICE")

    if res.get("otp_now") and res.get("otp"):
        otp_safe = html.escape(str(res["otp"]))
        sms_safe = html.escape(str(res.get("sms") or ""))
        add_otp_received(uid)
        text = (
            f"🛰️ <b>[ NODE DECRYPTED SUCCESSFULLY ]</b> 🛰️\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌍 <b>ORIGIN:</b> <code>{country_flag} {html.escape(country_name)}</code>\n"
            f"🛰️ <b>NODE:</b> <code>{range_text}</code>\n"
            f"📱 <b>TARGET:</b> <code>{service_logo}</code>\n"
            f"📟 <b>ADDR:</b> <code>+{clean_num}</code>\n"
            f"🔑 <b>KEY:</b> <code>{otp_safe}</code>"
            + (f"\n\n<blockquote>📩 PACKET: <code>{sms_safe}</code></blockquote>" if sms_safe else "")
        )
    else:
        text = (
            f"🛰️ <b>[ CYBER-NODE ALLOCATION ]</b> 🛰️\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌍 <b>ORIGIN:</b> <code>{country_flag} {html.escape(country_name)}</code>\n"
            f"🛰️ <b>NODE:</b> <code>{range_text}</code>\n"
            f"📱 <b>TARGET:</b> <code>{service_logo}</code>\n"
            f"📟 <b>ADDR:</b> <code>+{clean_num}</code>\n\n"
            f"📡 <b>SCAN STATUS: ⏳ SCANNING FOR DATA...</b>"
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🔄 SAME RANGE", callback_data="same_range")]
    ])
    try:
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"fast_allocate edit error: {e}")

async def worker():
    while True:
        task = await request_queue.get()
        try:
            if task['type'] == 'process_numbers':
                await process_numbers(task['update'], task['context'], task['range_text'], task['count'])
            elif task['type'] == 'search_otp':
                await perform_otp_search(task['update'], task['context'], task['target_num'])
            elif task['type'] == 'auto_number':
                await process_auto_number(task['update'], task['context'], task['range_text'])
        except Exception as e:
            print(f"Worker Error: {e}")
        finally:
            request_queue.task_done()

async def process_auto_number(update, context, range_text):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await context.bot.send_message(chat_id=chat_id, text=LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    status_msg = await context.bot.send_message(chat_id=chat_id, text="🔍 INJECTING NODE MODULES...")
    try:
        res = await fetch_number_async(range_text)
        if not res or not res.get("number"):
            await status_msg.edit_text(LANG_TEXTS[lang]["node_alloc_fail"])
            return
        generated_num = normalize_number(res["number"])
        add_number_taken(uid, 1)
        last_range[uid] = range_text
        active_numbers[generated_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now()}
        save_number_range_info(uid, generated_num, range_text)

        country_flag, country_name = get_country_info(generated_num)
        service_logo = get_service_logo("SMS SERVICE")

        if res.get("otp_now") and res.get("otp"):
            instant_otp = html.escape(str(res["otp"]))
            instant_sms = html.escape(str(res.get("sms") or ""))
            add_otp_received(uid)
            final_text = (
                f"🛰️ <b>[ NODE DECRYPTED SUCCESSFULLY ]</b> 🛰️\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🌍 <b>ORIGIN:</b> <code>{country_flag} {country_name}</code>\n"
                f"🛰️ <b>NODE:</b> <code>{range_text}</code>\n"
                f"📱 <b>TARGET:</b> <code>{service_logo}</code>\n"
                f"📟 <b>ADDR:</b> <code>+{generated_num}</code>\n"
                f"🔑 <b>KEY:</b> <code>{instant_otp}</code>"
                + (f"\n\n<blockquote>📩 PACKET: <code>{instant_sms}</code></blockquote>" if instant_sms else "")
            )
        else:
            final_text = (
                f"🛰️ <b>[ CYBER-NODE ALLOCATION ]</b> 🛰️\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🌍 <b>ORIGIN:</b> <code>{country_flag} {country_name}</code>\n"
                f"🛰️ <b>NODE:</b> <code>{range_text}</code>\n"
                f"📱 <b>TARGET:</b> <code>{service_logo}</code>\n"
                f"📟 <b>ADDR:</b> <code>+{generated_num}</code>\n\n"
                f"📡 <b>SCAN STATUS: ⏳ SCANNING FOR DATA...</b>"
            )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="🔄 SAME RANGE", callback_data="same_range")]
        ])
        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"Auto Number Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")

async def process_numbers(update_or_query, context, range_text, count):
    if isinstance(update_or_query, Update) and update_or_query.callback_query:
        uid = update_or_query.callback_query.from_user.id
        chat_id = update_or_query.callback_query.message.chat_id
    else:
        uid = update_or_query.effective_user.id
        chat_id = update_or_query.effective_chat.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await context.bot.send_message(chat_id=chat_id, text=LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return

    status_msg = await context.bot.send_message(chat_id=chat_id, text="🔍 INTRUDING SYSTEM PATHS...")
    try:
        add_number_taken(uid, count)
        last_range[uid] = range_text
        tasks = [fetch_number_async(range_text) for _ in range(count)]
        results = await asyncio.gather(*tasks)
        valid_results = [r for r in results if r and r.get("number")]

        if not valid_results:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return

        num_entries = []
        for r in valid_results:
            clean_num = normalize_number(r["number"])
            if clean_num:
                active_numbers[clean_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now()}
                save_number_range_info(uid, clean_num, range_text)
                num_entries.append({
                    "num":     clean_num,
                    "otp_now": r.get("otp_now", False),
                    "otp":     r.get("otp"),
                    "sms":     r.get("sms"),
                })

        country_flag, country_name = get_country_info(num_entries[0]["num"])
        service_logo = get_service_logo(detect_service(range_text))
        num_lines = []
        for entry in num_entries:
            if entry["otp_now"] and entry["otp"]:
                otp_safe = html.escape(str(entry["otp"]))
                sms_safe = html.escape(str(entry.get("sms") or ""))
                add_otp_received(uid)
                line = (
                    f"<blockquote>📟 ADDR: <code>+{entry['num']}</code>\n"
                    f"🔑 KEY: <code>{otp_safe}</code>"
                    + (f"\n📩 PACKET: <code>{sms_safe}</code>" if sms_safe else "")
                    + "</blockquote>"
                )
            else:
                line = f"<blockquote>📟 ADDR: <code>+{entry['num']}</code></blockquote>"
            num_lines.append(line)

        num_list_text = "\n".join(num_lines)
        any_instant = any(e["otp_now"] and e["otp"] for e in num_entries)
        sms_status = "🟢 ACTIVE DECRYPT" if any_instant else "📡 SCAN STATUS: ⏳ SCANNING FOR DATA..."

        final_text = (
            f"🛰️ <b>[ CYBER-NODE ALLOCATION ]</b> 🛰️\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌍 <b>ORIGIN:</b> <code>{country_flag} {country_name}</code>\n"
            f"🛰️ <b>NODE:</b> <code>{range_text}</code>\n"
            f"📱 <b>TARGET:</b> <code>{service_logo}</code>\n\n"
            f"📋 <b>DECRYPTED CHANNELS:</b>\n"
            f"{num_list_text}\n\n"
            f"<b>{sms_status}</b>"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="🔄 SAME RANGE", callback_data="same_range")]
        ])
        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"Process Number Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")

async def perform_otp_search(update, context, target_num):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    base_url = get_base_url()
    if not base_url:
        await update.message.reply_text("❌ API Base URL is not configured in Admin Panel.")
        return
    status_msg = await update.message.reply_text(LANG_TEXTS[lang]["search_otp_searching"])
    try:
        async with get_async_client() as client_async:
            r = await client_async.get(f"{base_url}/api/success-otp-info")
            res = r.json()
            if "data" in res and "otps" in res["data"]:
                all_otps = res["data"]["otps"]
                found_otps = [o for o in all_otps if normalize_number(o.get("number", "")) == target_num]

                if not found_otps:
                    await status_msg.delete()
                    err_text = LANG_TEXTS[lang]["search_otp_not_found"].format(num=target_num)
                    await update.message.reply_text(err_text, parse_mode="Markdown", reply_markup=main_keyboard(uid))
                else:
                    await status_msg.delete()
                    paid_data = load_data(PAID_SMS_FILE)
                    for o in found_otps:
                        full_sms = o.get('message') or o.get('otp') or o.get('sms') or "No Content"
                        otp_code = extract_otp(full_sms)
                        otp_id = str(o.get("otp_id", ""))
                        sms_key = otp_id if otp_id else f"{target_num}_{full_sms}"

                        if sms_key in paid_data:
                            payment_status = "❌ CORE ALREADY HARVESTED" if lang == "en" else "❌ এটি ইতিমধ্যে রিওয়ার্ড করা হয়েছে"
                        else:
                            await update_db_balance(uid, OTP_RATE)
                            add_otp_received(uid)
                            paid_data[sms_key] = {"uid": str(uid), "otp": otp_code}
                            payment_status = f"💵 Reward +{OTP_RATE:.2f} BDT Added to Balance!"

                        save_data(paid_data, PAID_SMS_FILE)
                        country_flag, country_name = get_country_info(target_num)
                        service_name = detect_service(full_sms)
                        service_logo = get_service_logo(service_name)

                        msg = (
                            f"♻️ <b>[ ENCRYPTED DATA RECOVERED ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"🌍 <b>ORIGIN:</b> <code>{country_flag} {country_name}</code>\n"
                            f"📱 <b>TARGET:</b> <code>{service_logo}</code>\n"
                            f"📟 <b>ADDR:</b> <code>+{target_num}</code>\n"
                            f"🔑 <b>KEY:</b> <code>{html.escape(otp_code)}</code>\n\n"
                            f"<blockquote>📩 <b>FULL SMS PACKET:</b>\n<code>{html.escape(str(full_sms))}</code></blockquote>\n"
                            f"<b>{payment_status}</b>"
                        )
                        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(uid))
            else:
                await status_msg.edit_text("❌ Database connectivity failure.")
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")

async def refer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return
    bot_info = await context.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={uid}"
    successful_refers = get_referral_count(uid)
    total_reward = float(successful_refers) * REFERRAL_PRICE

    if lang == "bn":
        refer_msg = (
            f"🎁 <b>[ রেফারেল সেন্টার ]</b> 🎁\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>👥 সফল রেফারেল: <code>{successful_refers}</code>\n"
            f"🪙 অর্জিত রিওয়ার্ড: <code>{format_balance(total_reward)} BDT</code></blockquote>\n\n"
            f"🔗 <b>আপনার রেফারেল লিংক:</b>\n"
            f"<blockquote><code>{referral_link}</code></blockquote>\n\n"
            f"<i>বন্ধুদের আমন্ত্রণ জানান এবং প্রতিটি আমন্ত্রণে এক্সট্রা রিওয়ার্ড লাভ করুন।</i>"
        )
    else:
        refer_msg = (
            f"🎁 <b>[ REFERRAL PORTAL ]</b> 🎁\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>👥 Successful Invites: <code>{successful_refers}</code>\n"
            f"🪙 Harvested Income: <code>{format_balance(total_reward)} BDT</code></blockquote>\n\n"
            f"🔗 <b>YOUR REFERRAL LINK:</b>\n"
            f"<blockquote><code>{referral_link}</code></blockquote>\n\n"
            f"<i>Share and replicate system node access with friends to earn commission.</i>"
        )
    await update.message.reply_text(
        refer_msg,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text="👥 INVITED USERS REPORT", callback_data=f"my_ref_{uid}")
        ]])
    )

async def withdraw_method_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if text in T_CANCEL:
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ TRANSACTION ABORTED", reply_markup=main_keyboard(uid))
        return
    
    # শুধুমাত্র বিকাশ এবং নগদ গেটওয়ে যাচাইকরণ
    method_map = {"📱 BKASH": "BKASH", "💵 NAGAD": "NAGAD"}
    if text in method_map:
        context.user_data["withdraw_method"] = method_map[text]
        context.user_data["withdraw_mode"] = "amount"
        await update.message.reply_text(
            LANG_TEXTS[lang]["withdraw_amount_prompt"].format(min_val=MIN_WITHDRAW),
            parse_mode="HTML",
            reply_markup=cancel_keyboard(uid)
        )
    else:
        await update.message.reply_text("⚠️ দয়া করে বিকাশ অথবা নগদ সিলেক্ট করুন!", reply_markup=withdraw_method_keyboard(uid))

async def withdraw_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if text in T_CANCEL:
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ TRANSACTION ABORTED", reply_markup=main_keyboard(uid))
        return
    try:
        amount = float(text)
    except Exception:
        await update.message.reply_text("⚠️ Invalid numerical value!", reply_markup=cancel_keyboard(uid))
        return
    balance = get_user(uid)['balance']
    if amount < MIN_WITHDRAW or amount > MAX_WITHDRAW:
        await update.message.reply_text(f"📉 RANGE LIMITS: MIN: {MIN_WITHDRAW} BDT | MAX: {MAX_WITHDRAW} BDT", reply_markup=cancel_keyboard(uid))
        return
    if amount > balance:
        await update.message.reply_text("🚫 VALUATION INSUFFICIENT!", reply_markup=cancel_keyboard(uid))
        return
    context.user_data["withdraw_amount"] = amount
    context.user_data["withdraw_mode"] = "number"
    await update.message.reply_text(
        LANG_TEXTS[lang]["withdraw_number_prompt"],
        parse_mode="HTML",
        reply_markup=cancel_keyboard(uid)
    )

async def withdraw_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    if text in T_CANCEL:
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ TRANSACTION ABORTED", reply_markup=main_keyboard(uid))
        return
    if not is_valid_bangladesh_number(text):
        await update.message.reply_text("⚠️ FORMAT CONFLICT! MUST BE 017XXXXXXXX", reply_markup=cancel_keyboard(uid))
        return

    method = context.user_data.get("withdraw_method")
    amount = context.user_data.get("withdraw_amount")
    payment_number = text
    payment_id = generate_payment_id()
    context.user_data["temp_withdraw"] = {
        "method": method, "amount": amount,
        "number": payment_number, "payment_id": payment_id
    }
    proposal_msg = LANG_TEXTS[lang]["withdraw_proposed"].format(method=method, num=payment_number, amount=amount)
    
    await update.message.reply_text(
        proposal_msg,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text="❌ ABORT", callback_data="withdraw_cancel"),
            InlineKeyboardButton(text="✅ CONFIRM", callback_data="withdraw_confirm")
        ]])
    )

async def process_withdraw_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    temp_data = context.user_data.get("temp_withdraw")
    if not temp_data:
        await query.message.reply_text("⚠️ TRANSACTION PACKET EXPIRED.", reply_markup=main_keyboard(uid))
        return

    method = temp_data["method"]
    amount = temp_data["amount"]
    payment_number = temp_data["number"]
    payment_id = temp_data["payment_id"]

    await update_db_balance(uid, -amount)
    wr = load_withdraw_requests()
    wr[str(payment_id)] = {
        "user_id": uid, "method": method, "amount": amount,
        "number": payment_number, "payment_id": payment_id,
        "status": "pending", "timestamp": datetime.now().isoformat()
    }
    save_withdraw_requests(wr)

    await query.message.edit_text(
        f"✅ <b>TRANSACTION FORWARDED TO CORES</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>📝 GATEWAY: <code>{method}</code>\n"
        f"📞 TARGET_ADDR: <code>{payment_number}</code>\n"
        f"💰 VALUATION: <code>{format_balance(amount)} BDT</code>\n"
        f"🆔 HASH_ID: <code>{payment_id}</code></blockquote>",
        parse_mode="HTML"
    )
    await context.bot.send_message(uid, "🎉 REQUEST SUBMITTED SUCCESSFULLY!", reply_markup=main_keyboard(uid))

    admin_msg = (
        f"✅ <b>[ NEW WITHDRAW REQUEST ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 NODE_USER: <code>{uid}</code>\n"
        f"📝 GATEWAY: <code>{method}</code>\n"
        f"📞 TARGET_ADDR: <code>{payment_number}</code>\n"
        f"💰 VALUATION: <code>{format_balance(amount)} BDT</code>\n"
        f"🆔 HASH_ID: <code>{payment_id}</code>"
    )
    admin_kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(text="❌ REJECT", callback_data=f"admin_reject_{payment_id}"),
        InlineKeyboardButton(text="✅ APPROVE", callback_data=f"admin_approve_{payment_id}")
    ]])
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(admin_id, admin_msg, parse_mode="HTML", reply_markup=admin_kb)
        except Exception as e:
            print(f"Admin notify fail {admin_id}: {e}")

    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None

async def process_withdraw_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None
    await query.message.edit_text("❌ TRANSACTION TERMINATED")
    await context.bot.send_message(uid, "🔹 SECURE CONTROLS RE-ENGAGED:", reply_markup=main_keyboard(uid))

# অ্যাডমিন এপ্রুভ করলে ইউজারের ইনবক্সে মেসেজ যাওয়ার ব্যবস্থা
async def admin_approve_withdraw(update, context, payment_id):
    query = update.callback_query
    await query.answer()
    wr = load_withdraw_requests()
    if payment_id not in wr:
        await query.message.reply_text("⚠️ Request not found.")
        return
    rd = wr[payment_id]
    uid = rd["user_id"]
    method = rd["method"]
    amount = rd["amount"]
    payment_number = rd["number"]
    wr[payment_id]["status"] = "approved"
    save_withdraw_requests(wr)
    try:
        await context.bot.send_message(
            uid,
            f"🎉 <b>[ আপনার উইথড্রটি সফলভাবে এক্সেপ্ট করা হয়েছে! ]</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>📝 গেটওয়ে: <code>{method}</code>\n"
            f"📞 পেমেন্ট নম্বর: <code>{payment_number}</code>\n"
            f"💰 পরিমাণ: <code>{format_balance(amount)} BDT</code></blockquote>",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await query.message.edit_text(f"✅ APPROVED | Node User: {uid} | Val: {format_balance(amount)} BDT")

async def admin_reject_withdraw(update, context, payment_id):
    query = update.callback_query
    await query.answer()
    wr = load_withdraw_requests()
    if payment_id not in wr:
        await query.message.reply_text("⚠️ Request not found.")
        return
    rd = wr[payment_id]
    uid = rd["user_id"]
    amount = rd["amount"]
    wr[payment_id]["status"] = "rejected"
    save_withdraw_requests(wr)
    try:
        await context.bot.send_message(uid, "❌ **[ উইথড্র রিকোয়েস্ট বাতিল করা হয়েছে ]**\n\nআপনার উইথড্র রিকোয়েস্টটি অ্যাডমিন কর্তৃক বাতিল করা হয়েছে।", parse_mode="Markdown")
    except Exception:
        pass
    await query.message.edit_text(f"❌ REJECTED | Node User: {uid} | Val: {format_balance(amount)} BDT")

async def admin_add_balance_start(update, context):
    context.user_data["add_balance_mode"] = True
    context.user_data["remove_balance_mode"] = False
    await update.message.reply_text("💰 Send target user ID to force inject balance:")

async def admin_remove_balance_start(update, context):
    context.user_data["remove_balance_mode"] = True
    context.user_data["add_balance_mode"] = False
    await update.message.reply_text("💸 Send target user ID to retrieve balance:")

async def process_add_balance_user(update, context):
    uid_to_add = update.message.text.strip()
    if not uid_to_add.isdigit():
        await update.message.reply_text("❌ Invalid ID.")
        return
    uid_to_add_int = int(uid_to_add)
    if not user_exists(uid_to_add_int):
        await update.message.reply_text("❌ User not found.")
        context.user_data["add_balance_mode"] = False
        return
    context.user_data["pending_add_user"] = uid_to_add_int
    await update.message.reply_text("💵 Send amount to inject:")

async def process_remove_balance_user(update, context):
    uid_to_remove = update.message.text.strip()
    if not uid_to_remove.isdigit():
        await update.message.reply_text("❌ Invalid ID.")
        return
    uid_to_remove_int = int(uid_to_remove)
    if not user_exists(uid_to_remove_int):
        await update.message.reply_text("❌ User not found.")
        context.user_data["remove_balance_mode"] = False
        return
    context.user_data["pending_remove_user"] = uid_to_remove_int
    await update.message.reply_text("💸 Send amount to remove:")

async def process_add_balance_amount(update, context):
    try:
        amount = float(update.message.text.strip())
        if amount <= 0:
            raise ValueError
    except Exception:
        await update.message.reply_text("❌ Invalid amount.")
        return
    uid = context.user_data.get("pending_add_user")
    if not uid:
        context.user_data["add_balance_mode"] = False
        await update.message.reply_text("⚠️ Session expired.")
        return
    new_balance = await update_db_balance(uid, amount)
    await update.message.reply_text(
        f"✅ **[ BALANCE INJECTED ]**\n🆔 Target User: `{uid}`\n"
        f"💰 Transferred: `{format_balance(amount)} BDT`\n"
        f"📈 New Balance: `{format_balance(new_balance)} BDT`",
        parse_mode="Markdown"
    )
    try:
        await context.bot.send_message(uid, f"🎉 Admin injected `{format_balance(amount)} BDT` credits to your account!\n💵 Wallet Balance: `{format_balance(new_balance)} BDT`", parse_mode="Markdown")
    except Exception:
        pass
    context.user_data["add_balance_mode"] = False
    context.user_data["pending_add_user"] = None

async def process_remove_balance_amount(update, context):
    try:
        amount = float(update.message.text.strip())
        if amount <= 0:
            raise ValueError
    except Exception:
        await update.message.reply_text("❌ Invalid amount.")
        return
    uid = context.user_data.get("pending_remove_user")
    if not uid:
        context.user_data["remove_balance_mode"] = False
        await update.message.reply_text("⚠️ Session expired.")
        return
    old_balance = get_user(uid).get("balance", 0)
    if amount > old_balance:
        await update.message.reply_text(f"❌ Target balance only has {format_balance(old_balance)} BDT.")
        context.user_data["remove_balance_mode"] = False
        context.user_data["pending_remove_user"] = None
        return
    new_balance = await update_db_balance(uid, -amount)
    await update.message.reply_text(
        f"✅ **[ BALANCE PURGED ]**\n🆔 Target User: `{uid}`\n"
        f"💸 Deducted: `{format_balance(amount)} BDT`\n"
        f"📈 New Balance: `{format_balance(new_balance)} BDT`",
        parse_mode="Markdown"
    )
    try:
        await context.bot.send_message(uid, f"⚠️ Admin extracted `{format_balance(amount)} BDT` from your account!\n💵 Wallet Balance: `{format_balance(new_balance)} BDT`", parse_mode="Markdown")
    except Exception:
        pass
    context.user_data["remove_balance_mode"] = False
    context.user_data["pending_remove_user"] = None

async def admin_ban_user_start(update, context):
    context.user_data["admin_ban_mode"] = True
    context.user_data["admin_unban_mode"] = False
    await update.message.reply_text("🚫 Send target user ID to enforce BAN status:")

async def admin_unban_user_start(update, context):
    context.user_data["admin_unban_mode"] = True
    context.user_data["admin_ban_mode"] = False
    await update.message.reply_text("🔓 Send target user ID to clear BAN status:")

async def process_ban_user(update, context):
    uid_to_ban = update.message.text.strip()
    if not uid_to_ban.isdigit():
        await update.message.reply_text("❌ Invalid ID.")
        return
    uid_to_ban_int = int(uid_to_ban)
    if not user_exists(uid_to_ban_int):
        await update.message.reply_text("❌ User not found.")
        context.user_data["admin_ban_mode"] = False
        return
    if is_user_banned(uid_to_ban_int):
        await update.message.reply_text("⚠️ Node is already blocked.")
        context.user_data["admin_ban_mode"] = False
        return
    ban_user(uid_to_ban_int)
    try:
        await context.bot.send_message(uid_to_ban_int, "🚫 **Your access profile has been suspended.**", parse_mode="Markdown")
    except Exception:
        pass
    await update.message.reply_text(f"✅ User `{uid_to_ban}` banned successfully!", parse_mode="Markdown", reply_markup=system_config_keyboard())
    context.user_data["admin_ban_mode"] = False

async def process_unban_user(update, context):
    uid_to_unban = update.message.text.strip()
    if not uid_to_unban.isdigit():
        await update.message.reply_text("❌ Invalid ID.")
        return
    uid_to_unban_int = int(uid_to_unban)
    if not is_user_banned(uid_to_unban_int):
        await update.message.reply_text("⚠️ User node is active.")
        context.user_data["admin_unban_mode"] = False
        return
    unban_user(uid_to_unban_int)
    try:
        await context.bot.send_message(uid_to_unban_int, "✅ **Your access profile suspension has been lifted!**", parse_mode="Markdown")
    except Exception:
        pass
    await update.message.reply_text(f"✅ User `{uid_to_unban}` unbanned successfully!", parse_mode="Markdown", reply_markup=system_config_keyboard())
    context.user_data["admin_unban_mode"] = False

async def show_banned_users_list(update, context):
    banned_list = load_banned_users()
    if not banned_list:
        await update.message.reply_text("📜 No banned nodes detected.", reply_markup=system_config_keyboard())
        return
    text = "📜 **BLOCKED SYSTEM NODES**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, uid in enumerate(banned_list, 1):
        text += f"{i}. `{uid}`\n"
    text += f"\n📊 Total: {len(banned_list)}"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=system_config_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    uid = update.effective_user.id
    text = update.message.text.strip() if update.message.text else ""
    lang = get_user_lang(uid)

    if text in T_CANCEL:
        context.user_data.clear()
        cancel_txt = "❌ OPERATION ABORTED" if lang == "en" else "❌ অপারেশন বাতিল করা হয়েছে"
        await update.message.reply_text(cancel_txt, reply_markup=main_keyboard(uid))
        return

    if not is_admin(uid) and is_user_banned(uid):
        await update.message.reply_text(LANG_TEXTS[lang]["banned"], reply_markup=main_keyboard(uid))
        return

    if not is_user_verified(uid) and not is_admin(uid):
        await send_verification_captcha(update.effective_chat.id, context, uid)
        return

    if context.user_data.get("admin_api_update_mode") and is_admin(uid):
        context.user_data["admin_api_update_mode"] = False
        parts = text.split("|")
        if len(parts) != 2:
            await update.message.reply_text("❌ ভুল ফরম্যাট! সঠিক ফরম্যাট: `API_KEY | BASE_URL`", parse_mode="Markdown")
            return
        try:
            new_key = parts[0].strip()
            new_url = parts[1].strip()
            
            sc = load_sys_config()
            sc["api_key"] = new_key
            sc["base_url"] = new_url
            save_sys_config(sc)
            
            await update.message.reply_text(
                f"✅ **API SETTINGS UPDATED SUCCESSFULLY!**\n\n"
                f"🔑 API Key: ` {new_key} `\n"
                f"🌐 Base URL: `{new_url}`",
                parse_mode="Markdown",
                reply_markup=system_config_keyboard()
            )
        except Exception as e:
            await update.message.reply_text(f"❌ API update failure: {e}")
        return

    # অ্যাডমিন প্যানেল থেকে চ্যানেল আইডি ও লিংক সেট করার অপশন
    if context.user_data.get("admin_channel_update_mode") and is_admin(uid):
        context.user_data["admin_channel_update_mode"] = False
        parts = text.split("|")
        if len(parts) != 2:
            await update.message.reply_text("❌ ভুল ফরম্যাট। সঠিক ফরম্যাট: `channel_id | invite_link`", parse_mode="Markdown")
            return
        try:
            ch_id = int(parts[0].strip())
            ch_lnk = parts[1].strip()
            
            sc = load_sys_config()
            sc["official_channel_id"] = ch_id
            sc["official_channel_link"] = ch_lnk
            save_sys_config(sc)
            
            await update.message.reply_text(
                f"✅ **চ্যানেল কনফিগারেশন সফলভাবে আপডেট হয়েছে!**\n\n"
                f"🆔 Channel ID: ` {ch_id} `\n"
                f"🔗 Channel Link: {ch_lnk}",
                parse_mode="Markdown",
                reply_markup=system_config_keyboard()
            )
        except Exception as e:
            await update.message.reply_text(f"❌ কনফিগারেশন ত্রুটি: {e}")
        return

    if not is_admin(uid):
        cur_cfg = load_sys_config()
        if cur_cfg.get("official_channel_id"):
            is_member = await check_channel_membership(context.bot, uid, cur_cfg["official_channel_id"])
            if not is_member:
                await show_join_prompt(update, context, uid)
                return

    if context.user_data.get("withdraw_mode") == "select_method":
        await withdraw_method_selected(update, context)
        return
    if context.user_data.get("withdraw_mode") == "amount":
        await withdraw_amount_received(update, context)
        return
    if context.user_data.get("withdraw_mode") == "number":
        await withdraw_number_received(update, context)
        return

    if context.user_data.get("add_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_add_user"):
            await process_add_balance_amount(update, context)
        else:
            await process_add_balance_user(update, context)
        return
    if context.user_data.get("remove_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_remove_user"):
            await process_remove_balance_amount(update, context)
        else:
            await process_remove_balance_user(update, context)
        return

    if context.user_data.get("admin_ban_mode") and is_admin(uid):
        await process_ban_user(update, context)
        return
    if context.user_data.get("admin_unban_mode") and is_admin(uid):
        await process_unban_user(update, context)
        return

    if context.user_data.get("mode") == "custom_range":
        context.user_data["mode"] = None
        range_text = text.strip().upper()
        if not re.search(r'\d', range_text):
            await update.message.reply_text(
                LANG_TEXTS[lang]["invalid_range"],
                parse_mode="HTML",
                reply_markup=main_keyboard(uid)
            )
            return
        await request_queue.put({
            'type': 'process_numbers',
            'update': update,
            'context': context,
            'range_text': range_text,
            'count': 1
        })
        return

    if text in T_PROFILE:
        user_data = get_user(uid)
        stats = get_user_stats(uid)
        user = update.effective_user
        full_name = html.escape(user.full_name)
        username = html.escape(user.username or "N/A")

        if lang == "bn":
            profile_text = (
                f"👤 <b>ইউজার প্রোফাইল</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏷️ <b>নাম:</b> <code>{full_name}</code>\n"
                f"🆔 <b>ইউজারনেম:</b> @{username}\n"
                f"🗝️ <b>ইউজার আইডি:</b> <code>{uid}</code>\n\n"
                f"💵 <b>ওয়ালেট ব্যালেন্স:</b> <code>{format_balance(user_data.get('balance', 0))} BDT</code>\n\n"
                f"📊 <b>আজকের স্ট্যাটাস:</b>\n"
                f"<blockquote>📱 নম্বর নিয়েছেন: <code>{stats['today_numbers']}</code>\n"
                f"🔑 ওটিপি পেয়েছেন: <code>{stats['today_otps']}</code></blockquote>\n\n"
                f"🌐 <b>সর্বমোট স্ট্যাটাস:</b>\n"
                f"<blockquote>📱 নম্বর নিয়েছেন: <code>{stats['total_numbers']}</code>\n"
                f"🔑 ওটিপি পেয়েছেন: <code>{stats['total_otps']}</code></blockquote>"
            )
        else:
            profile_text = (
                f"👤 <b>USER PROFILE</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏷️ <b>Name:</b> <code>{full_name}</code>\n"
                f"🆔 <b>Username:</b> @{username}\n"
                f"🗝️ <b>User ID:</b> <code>{uid}</code>\n\n"
                f"💵 <b>Wallet Balance:</b> <code>{format_balance(user_data.get('balance', 0))} BDT</code>\n\n"
                f"📊 <b>Today's Stats:</b>\n"
                f"<blockquote>📱 Numbers taken: <code>{stats['today_numbers']}</code>\n"
                f"🔑 OTPs received: <code>{stats['today_otps']}</code></blockquote>\n\n"
                f"🌐 <b>All-time Stats:</b>\n"
                f"<blockquote>📱 Numbers taken: <code>{stats['total_numbers']}</code>\n"
                f"🔑 OTPs received: <code>{stats['total_otps']}</code></blockquote>"
            )
        await update.message.reply_text(profile_text, parse_mode="HTML")
        return

    if text in T_BALANCE:
        balance = get_user(uid)['balance']
        text_bal = LANG_TEXTS[lang]["balance_title"].format(bal=format_balance(balance))
        btn_wd = LANG_TEXTS[lang]["btn_withdraw"]
        
        await update.message.reply_text(
            text_bal,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text=btn_wd, callback_data="withdraw_start")
            ]])
        )
        return

    if text in T_REFER:
        await refer_command(update, context)
        return

    if text in T_SEARCH_OTP:
        context.user_data["mode"] = "search_otp"
        await update.message.reply_text(
            LANG_TEXTS[lang]["search_otp_prompt"],
            parse_mode="HTML",
            reply_markup=cancel_keyboard(uid)
        )
        return

    if context.user_data.get("mode") == "search_otp":
        context.user_data["mode"] = None
        await request_queue.put({'type': 'search_otp', 'update': update, 'context': context, 'target_num': normalize_number(text)})
        return

    if text in T_2FA:
        await get_2fa_code(update, context)
        return

    if text in T_GET_NUM:
        await show_app_selection(update, context)
        return

    if context.user_data.get("mode") == "get_2fa":
        await process_2fa_key(update, context)
        return

    if text in T_LEADERBOARD:
        await leaderboard_command(update, context)
        return

    if text in T_LANG:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="🇺🇸 English", callback_data="set_lang_en"),
                InlineKeyboardButton(text="🇧🇩 বাংলা", callback_data="set_lang_bn")
            ]
        ])
        msg_txt = "🌐 <b>Please select your language / দয়া করে ভাষা সিলেক্ট করুন:</b>"
        await update.message.reply_text(msg_txt, parse_mode="HTML", reply_markup=keyboard)
        return

    if text in T_SUPPORT:
        if lang == "bn":
            support_text = "💬 <b>সাপোর্ট সেন্টার</b> 🎧\n━━━━━━━━━━━━━━━━━━━━━━\n\nযেকোনো সমস্যায় নিচে দেওয়া বাটনগুলোতে ক্লিক করে আমাদের সাথে যোগাযোগ করুন।"
            btn_hc = "💬 হেল্প সেন্টার"
            btn_dev = "👨‍💻 ডেভলপার সাপোর্ট"
        else:
            support_text = "💬 <b>SUPPORT TERMINAL</b> 🎧\n━━━━━━━━━━━━━━━━━━━━━━\n\nUse the buttons below to establish direct support channels."
            btn_hc = "💬 Help Center"
            btn_dev = "👨‍💻 Developer Support"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=btn_hc, url=SUPPORT_LINK)],
            [InlineKeyboardButton(text=btn_dev, url=DEVELOPER_LINK)]
        ])
        await update.message.reply_text(support_text, reply_markup=keyboard, parse_mode="HTML")
        return

    if text in T_ADMIN and is_admin(uid):
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text(
            "⌬━━━━━━━━━━━━━━━━━━━━⌬\n   WELCOME ADMIN SYSTEM CENTRAL\n⌬━━━━━━━━━━━━━━━━━━━━⌬",
            reply_markup=admin_main_keyboard()
        )
        return

    if text == "🔙 BACK TO MAIN" and context.user_data.get("admin_mode"):
        context.user_data["admin_mode"] = None
        await update.message.reply_text("🔙 Terminated panel system context.", reply_markup=main_keyboard(uid))
        return

    if text == "🔙 BACK TO ADMIN":
        context.user_data["user_management_mode"] = None
        context.user_data["system_config_mode"] = None
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text("Returned to master gateway.", reply_markup=admin_main_keyboard())
        return

    if text == "👥 USER MANAGEMENT" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["user_management_mode"] = "main"
        await update.message.reply_text("👥 User Management Interface:", reply_markup=user_management_keyboard())
        return

    if text == "⚙️ SYSTEM CONFIGURATION" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["system_config_mode"] = "main"
        await update.message.reply_text("⚙️ Core Configurations Enabled:", reply_markup=system_config_keyboard())
        return

    if text == "📈 TODAY ALL STATUS" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        t_n, t_o, s_n, s_o, tot_n, tot_o = get_global_system_stats()
        msg = (
            f"📊 <b>CORE TELEMETRY LOGS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✨ <b>TODAY LOGS</b>\n📱 NODES FETCHED: {t_n}\n🔑 DECRYPTED OTPS: {t_o}\n\n"
            f"🔥 <b>7D LOGS</b>\n📱 NODES FETCHED: {s_n}\n🔑 DECRYPTED OTPS: {s_o}\n\n"
            f"🌐 <b>CORE ALLTIME LOGS</b>\n📱 NODES FETCHED: {tot_n}\n🔑 DECRYPTED OTPS: {tot_o}"
        )
        await update.message.reply_text(msg, parse_mode="HTML")
        return

    if text == "🌐 UPDATE API SETTINGS" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        context.user_data["admin_api_update_mode"] = True
        cur_api = get_api_key() or "Not Set"
        cur_url = get_base_url() or "Not Set"
        await update.message.reply_text(
            f"🌐 <b>API Settings Configuration:</b>\n\n"
            f"বর্তমান API Key: <code>{cur_api}</code>\n"
            f"বর্তমান Base URL: <code>{cur_url}</code>\n\n"
            f"দয়া করে নতুন API Key এবং Base URL পাইপ (`|`) দিয়ে নিচে পাঠান।\n\n"
            f"উদাহরণ:\n`YOUR_API_KEY | https://otpapi.example.com`",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(uid)
        )
        return

    if text == "📢 UPDATE JOINS" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        context.user_data["admin_channel_update_mode"] = True
        cur_cfg = load_sys_config()
        ch_id_str = cur_cfg.get("official_channel_id") or "Not Set"
        ch_link_str = cur_cfg.get("official_channel_link") or "Not Set"
        await update.message.reply_text(
            f"📢 <b>চ্যানেল জয়েন কনফিগারেশন আপডেট করুন:</b>\n\n"
            f"বর্তমান Channel ID: ` {ch_id_str} `\n"
            f"বর্তমান Link: {ch_link_str}\n\n"
            "চ্যানেল আইডি এবং ইনভাইট লিংক পাইপ (`|`) চিহ্ন দিয়ে আলাদা করে পাঠান।\n\n"
            "উদাহরণ:\n` -1001234567890 | https://t.me/example_channel `",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(uid)
        )
        return

    if text == "👤 USER STATUS CHECK" and is_admin(uid):
        context.user_data["mode"] = "input_user_id"
        await update.message.reply_text("🔍 INPUT USER TELEGRAM ID PROTOCOL:", reply_markup=cancel_keyboard(uid))
        return

    if context.user_data.get("mode") == "input_user_id" and is_admin(uid):
        target_uid = text.strip()
        if not target_uid.isdigit():
            await update.message.reply_text("❌ INVALID NUMERIC FORMAT!")
            return
        context.user_data["mode"] = None
        stats = get_user_stats(target_uid)
        msg = (
            f"👤 <b>NODE TELEMETRY CHECK</b> — <code>{target_uid}</code>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✨ TODAY: 📱 {stats['today_numbers']} | 🔑 {stats['today_otps']}\n"
            f"🔥 7 DAYS: 📱 {stats['last7d_numbers']} | 🔑 {stats['last7d_otps']}\n"
            f"🌐 ALL TIME: 📱 {stats['total_numbers']} | 🔑 {stats['total_otps']}"
        )
        await update.message.reply_text(
            msg, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="📂 PARSE DUMPED DATA PACKETS", callback_data=f"full_logs_{target_uid}")
            ]])
        )
        return

    if text == "🆔 ALL USER ID" and context.user_data.get("user_management_mode") == "main" and is_admin(uid):
        users = get_all_users()
        if users:
            content = "\n".join(f"{i}. {u}" for i, u in enumerate(users, 1))
            f = io.BytesIO(content.encode())
            f.name = f"ALL_NODES_{len(users)}.txt"
            await update.message.reply_document(document=f, caption=f"👥 Monitored Nodes: {len(users)}", reply_markup=user_management_keyboard())
        else:
            await update.message.reply_text("No active nodes.", reply_markup=user_management_keyboard())
        return

    if text == "💰 ALL USER BALANCE" and context.user_data.get("user_management_mode") == "main" and is_admin(uid):
        user_db = load_data(USER_DATA_FILE)
        if user_db:
            total_bal = sum(v.get("balance", 0) for v in user_db.values())
            lines = [f"{i}. {uid_}: {v.get('balance', 0):.2f} BDT" for i, (uid_, v) in enumerate(user_db.items(), 1)]
            content = f"💰 TOTAL VALUE POOL: {total_bal:.2f} BDT\n\n" + "\n".join(lines)
            f = io.BytesIO(content.encode())
            f.name = f"CORES_{total_bal:.0f}.txt"
            await update.message.reply_document(document=f, caption=f"💵 System Vault pool: {total_bal:.2f} BDT", reply_markup=user_management_keyboard())
        else:
            await update.message.reply_text("Telemetry empty.", reply_markup=user_management_keyboard())
        return

    if text == "📜 BAN USER LIST" and is_admin(uid):
        await show_banned_users_list(update, context)
        return

    if text == "⛔ BAN USER" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_ban_user_start(update, context)
        return

    if text == "🔓 UNBAN USER" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_unban_user_start(update, context)
        return

    if text == "➕ ADD BALANCE" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_add_balance_start(update, context)
        return

    if text == "➖ REMOVE BALANCE" and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_remove_balance_start(update, context)
        return

    if text == "📢 SEND MESSAGE TO ALL USERS" and is_admin(uid):
        context.user_data["broadcast_mode"] = True
        await update.message.reply_text(
            "📢 <b>ADMIN BROADCAST SYSTEM (PRO)</b>\n\n"
            "💬 আপনি এখন যা পাঠাবেন – তা সকল ইউজারের কাছে প্রফেশনাল ক্যাপশনসহ চলে যাবে।\n\n"
            "✨ রেঞ্জ (যেমন: 237XXX) থাকলে তা অটোমেটিক ক্লিক-টু-কপি হয়ে যাবে।", 
            parse_mode="HTML", 
            reply_markup=cancel_keyboard(uid)
        )
        return

    if context.user_data.get("broadcast_mode") and is_admin(uid):
        context.user_data["broadcast_mode"] = False
        user_db = load_data(USER_DATA_FILE)
        all_uids = list(user_db.keys())
        if not all_uids:
            await update.message.reply_text("❌ পাঠানোর জন্য কোনো ইউজার পাওয়া যায়নি!")
            return

        success_ids, fail_ids = [], []
        status_msg = await update.message.reply_text(f"🚀 <b>ব্রডকাস্ট শুরু হয়েছে...</b>\n🎯 টার্গেট: {len(all_uids)} জন ইউজার।", parse_mode="HTML")

        def format_broadcast_caption(caption_text):
            if not caption_text:
                return "<blockquote>📢 <b>ADMIN NOTICE :</b></blockquote>"
            formatted = re.sub(r'(\d{3,}[xX]{3,})', r'<code>\1</code>', str(caption_text))
            return f"<blockquote>📢 <b>ADMIN NOTICE :</b></blockquote>\n\n{formatted}"

        for user_id_str in all_uids:
            try:
                target_id = int(user_id_str)
                if update.message.text:
                    await context.bot.send_message(chat_id=target_id, text=format_broadcast_caption(update.message.text), parse_mode="HTML")
                elif update.message.photo:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_photo(chat_id=target_id, photo=update.message.photo[-1].file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.video:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_video(chat_id=target_id, video=update.message.video.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.document:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_document(chat_id=target_id, document=update.message.document.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.audio:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_audio(chat_id=target_id, audio=update.message.audio.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.voice:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_voice(chat_id=target_id, voice=update.message.voice.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.animation:
                    caption = format_broadcast_caption(update.message.caption) if update.message.caption else None
                    await context.bot.send_animation(chat_id=target_id, animation=update.message.animation.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.sticker:
                    await context.bot.send_sticker(chat_id=target_id, sticker=update.message.sticker.file_id)
                else:
                    try:
                        await context.bot.copy_message(chat_id=target_id, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
                    except Exception:
                        await context.bot.send_message(chat_id=target_id, text="📢 <b>ADMIN NOTICE :</b>\n\nনতুন আপডেট এসেছে। চেক করুন।", parse_mode="HTML")
                success_ids.append(user_id_str)
            except Exception as e:
                print(f"Broadcast fail to {user_id_str}: {e}")
                fail_ids.append(user_id_str)
            await asyncio.sleep(0.05)

        report_text = (
            f"✅ <b>ADMIN NOTICE COMPLETE !</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>BROADCAST REPORT:</b>\n\n"
            f"<blockquote>✅ SUCCESSFULLY SENT: {len(success_ids)} USERS !</blockquote>\n"
            f"<blockquote>❌ FAILED TO SEND: {len(fail_ids)} USERS !</blockquote>"
        )
        await status_msg.delete()
        await context.bot.send_message(chat_id=uid, text=report_text, parse_mode="HTML", reply_markup=main_keyboard(uid))
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if success_ids:
            s_file = io.BytesIO(("\n".join(success_ids)).encode())
            s_file.name = f"SUCCESS_{random_suffix}.txt"
            await context.bot.send_document(chat_id=uid, document=s_file, caption="✅ Success User List")
        if fail_ids:
            f_file = io.BytesIO(("\n".join(fail_ids)).encode())
            f_file.name = f"FAILED_{random_suffix}.txt"
            await context.bot.send_document(chat_id=uid, document=f_file, caption="❌ Failed User List")
        return

    fallback_txt = "🔹 CHOOSE UTILITY INTERFACE:" if lang == "en" else "🔹 ব্যবহারের জন্য নিচে থেকে সার্ভিস সিলেক্ট করুন:"
    await update.message.reply_text(fallback_txt, reply_markup=main_keyboard(uid))

async def get1number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_app_selection(update, context)

async def searchotp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    context.user_data["mode"] = "search_otp"
    await update.message.reply_text(
        LANG_TEXTS[lang]["search_otp_prompt"],
        parse_mode="HTML",
        reply_markup=cancel_keyboard(uid)
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    balance = get_user(uid)['balance']
    await update.message.reply_text(f"💰 WALLET BALANCE: `{format_balance(balance)} BDT`", parse_mode="Markdown", reply_markup=main_keyboard(uid))

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_user_lang(uid)
    user_data = get_user(uid)
    stats = get_user_stats(uid)
    user = update.effective_user
    profile_text = (
        f"👤 **YOUR DATA PROFILE**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏷️ ALIAS: `{user.full_name}`\n"
        f"🆔 SECURE ADDR: @{user.username or 'No username'}\n"
        f"🗝️ HASH ID: `{uid}`\n\n"
        f"💵 WALLET BALANCE: {format_balance(user_data.get('balance', 0))} BDT\n\n"
        f"✨ TODAY STATS: 📱 {stats['today_numbers']} | 🔑 {stats['today_otps']}\n"
        f"🌐 ALLTIME LOGS: 📱 {stats['total_numbers']} | 🔑 {stats['total_otps']}"
    )
    await update.message.reply_text(profile_text, parse_mode="Markdown")

async def show_join_prompt(update_or_query, context, uid):
    lang = get_user_lang(uid)
    text = LANG_TEXTS[lang]["join_prompt"]
    btn_join = LANG_TEXTS[lang]["btn_join"]
    btn_cont = LANG_TEXTS[lang]["btn_continue"]
    
    cur_cfg = load_sys_config()
    channel_link = cur_cfg.get("official_channel_link", "")

    if not channel_link:
        await context.bot.send_message(
            chat_id=uid,
            text=LANG_TEXTS[lang]["welcome"],
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=btn_join, url=channel_link)],
        [InlineKeyboardButton(text=btn_cont, callback_data="verify_join")]
    ])
    
    if isinstance(update_or_query, Update) and update_or_query.message:
        await update_or_query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update_or_query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uid_str = str(uid)
    existing_data = load_data(USER_DATA_FILE)
    is_new_user = uid_str not in existing_data
    user_info = get_user(uid)

    args = context.args
    if args and is_new_user:
        param = args[0]
        if is_range_request(param):
            await request_queue.put({'type': 'auto_number', 'update': update, 'context': context, 'range_text': param})
            return
        elif is_referral_request(param):
            try:
                referrer_id = int(param)
                if referrer_id != uid and str(referrer_id) in existing_data:
                    context.user_data["pending_refer"] = referrer_id
            except Exception as e:
                print(f"Deep link referral mapping error: {e}")

    if not user_info.get("lang"):
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="🇺🇸 English", callback_data="set_lang_en"),
                InlineKeyboardButton(text="🇧🇩 বাংলা", callback_data="set_lang_bn")
            ]
        ])
        await update.message.reply_text(
            "🌐 <b>Please select your language / দয়া করে ভাষা সিলেক্ট করুন:</b>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        if not is_user_verified(uid) and not is_admin(uid):
            await send_verification_captcha(update.effective_chat.id, context, uid)
        else:
            cur_cfg = load_sys_config()
            if cur_cfg.get("official_channel_link"):
                await show_join_prompt(update, context, uid)
            else:
                await update.message.reply_text(
                    LANG_TEXTS[get_user_lang(uid)]["welcome"],
                    parse_mode="HTML",
                    reply_markup=main_keyboard(uid)
                )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data
    await query.answer()

    if not is_admin(uid) and is_user_banned(uid):
        await query.edit_message_text("🚫 SYSTEM BANNED 🚫")
        return

    if data == "set_lang_en":
        user_info = get_user(uid)
        had_lang = user_info.get("lang") is not None
        set_user_lang(uid, "en")
        
        if had_lang:
            await query.message.delete()
            await context.bot.send_message(chat_id=uid, text="🟢 <b>Language changed to English!</b>", parse_mode="HTML")
            await context.bot.send_message(chat_id=uid, text=LANG_TEXTS["en"]["welcome"], parse_mode="HTML", reply_markup=main_keyboard(uid))
        else:
            if not is_user_verified(uid) and not is_admin(uid):
                await send_verification_captcha(query.message.chat_id, context, uid)
            else:
                cur_cfg = load_sys_config()
                if cur_cfg.get("official_channel_link"):
                    await show_join_prompt(query, context, uid)
                else:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=LANG_TEXTS["en"]["welcome"],
                        parse_mode="HTML",
                        reply_markup=main_keyboard(uid)
                    )
        return

    if data == "set_lang_bn":
        user_info = get_user(uid)
        had_lang = user_info.get("lang") is not None
        set_user_lang(uid, "bn")
        
        if had_lang:
            await query.message.delete()
            await context.bot.send_message(chat_id=uid, text="🟢 <b>ভাষা পরিবর্তন সফল হয়েছে!</b>", parse_mode="HTML")
            await context.bot.send_message(chat_id=uid, text=LANG_TEXTS["bn"]["welcome"], parse_mode="HTML", reply_markup=main_keyboard(uid))
        else:
            if not is_user_verified(uid) and not is_admin(uid):
                await send_verification_captcha(query.message.chat_id, context, uid)
            else:
                cur_cfg = load_sys_config()
                if cur_cfg.get("official_channel_link"):
                    await show_join_prompt(query, context, uid)
                else:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=LANG_TEXTS["bn"]["welcome"],
                        parse_mode="HTML",
                        reply_markup=main_keyboard(uid)
                    )
        return

    if data.startswith("captcha_opt_"):
        idx = int(data.replace("captcha_opt_", ""))
        opts = context.user_data.get("captcha_options", [])
        correct_ans = context.user_data.get("captcha_correct", "")
        
        if not opts or idx >= len(opts):
            await query.edit_message_text("❌ Verification session expired. Please type /start again.")
            return

        selected = opts[idx]
        if selected == correct_ans:
            set_user_verified(uid, True)
            await query.message.delete()
            await context.bot.send_message(chat_id=uid, text="✅ <b>Verification Successful! / সিকিউরিটি ভেরিফিকেশন সফল!</b>", parse_mode="HTML")
            cur_cfg = load_sys_config()
            if cur_cfg.get("official_channel_link"):
                await show_join_prompt(query, context, uid)
            else:
                await context.bot.send_message(
                    chat_id=uid,
                    text=LANG_TEXTS[get_user_lang(uid)]["welcome"],
                    parse_mode="HTML",
                    reply_markup=main_keyboard(uid)
                )
        else:
            lang = get_user_lang(uid)
            alert_msg = "❌ Verification Failed! Try again." if lang == "en" else "❌ ভেরিফিকেশন ব্যর্থ হয়েছে! আবার চেষ্টা করুন।"
            await context.bot.send_message(chat_id=uid, text=f"⚠️ {alert_msg}")
            await send_verification_captcha(query.message.chat_id, context, uid)
        return

    if data == "verify_join":
        lang = get_user_lang(uid)
        cur_cfg = load_sys_config()
        
        if cur_cfg.get("official_channel_id"):
            is_member = await check_channel_membership(context.bot, uid, cur_cfg["official_channel_id"])
            if not is_member and not is_admin(uid):
                alert_fail = "🛑 You have not joined the official channel yet!" if lang == "en" else "🛑 এখনো চ্যানেল জয়েন করেন নাই!"
                await context.bot.send_message(chat_id=uid, text=f"⚠️ <b>{alert_fail}</b>", parse_mode="HTML")
                return

        pending_ref = context.user_data.get("pending_refer")
        if pending_ref:
            try:
                existing_data = load_data(USER_DATA_FILE)
                if str(pending_ref) in existing_data:
                    current_count = get_referral_count(pending_ref)
                    new_count = current_count + 1
                    update_referral_count(pending_ref, new_count)
                    await update_db_balance(pending_ref, REFERRAL_PRICE)
                    log_global_activity(pending_ref, "REFERRAL_JOINED", {"referred_user": uid})
                    try:
                        msg = (
                            f"🎉 <b>[ NODE REPLICATED ]</b>\n\n"
                            f"<blockquote>🗝️ NEW_ID: <code>{uid}</code>\n"
                            f"💰 REWARD_HARVESTED: {format_balance(REFERRAL_PRICE)} BDT\n"
                            f"👥 TOTAL NODES: {new_count}</blockquote>"
                        )
                        await context.bot.send_message(pending_ref, msg, parse_mode="HTML")
                    except Exception:
                        pass
            except Exception as e:
                print(f"Error executing pending referral: {e}")
            context.user_data["pending_refer"] = None

        await query.message.delete()
        await context.bot.send_message(
            chat_id=uid,
            text=LANG_TEXTS[lang]["welcome"],
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return

    if data.startswith("svc_"):
        idx = int(data.replace("svc_", ""))
        services = context.user_data.get("la_services", [])
        if not services:
            services = get_cached_services()
            context.user_data["la_services"] = services
        if idx >= len(services):
            await query.answer("Session expired.", show_alert=True)
            return
        svc = services[idx]
        sid = svc.get("sid", "Service")
        ranges = svc.get("ranges", [])
        if not ranges:
            await query.answer("No telemetry paths available.", show_alert=True)
            return

        context.user_data["la_svc_idx"] = idx
        context.user_data["la_sid"] = sid
        context.user_data["la_ranges"] = ranges
        keyboard = _build_countries_keyboard(ranges, idx, uid)
        await query.message.edit_text(
            LANG_TEXTS[get_user_lang(uid)]["pick_country"].format(sid=html.escape(sid)),
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    if data.startswith("rng_"):
        idx = int(data.replace("rng_", ""))
        ranges = context.user_data.get("la_ranges", [])
        if idx >= len(ranges):
            await query.answer("Timeout error. Re-try.", show_alert=True)
            return
        range_text = ranges[idx]
        sid = context.user_data.get("la_sid", "")
        asyncio.create_task(fast_allocate_number(query, context, range_text, sid))
        return

    if data == "custom_range":
        context.user_data["mode"] = "custom_range"
        await query.message.edit_text(
            LANG_TEXTS[get_user_lang(uid)]["custom_range_prompt"],
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="◀️ BACK", callback_data="back_services")
            ]])
        )
        return

    if data == "back_services":
        services = get_cached_services() or context.user_data.get("la_services", [])
        if not services:
            await query.message.edit_text("❌ Connection failed.")
            return
        context.user_data["la_services"] = services
        keyboard = _build_services_keyboard(services, uid)
        await query.message.edit_text(
            LANG_TEXTS[get_user_lang(uid)]["get_active_node"],
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    if data == "same_range":
        r_text = last_range.get(uid)
        if r_text:
            try:
                await query.message.edit_reply_markup(reply_markup=None)
            except Exception:
                pass
            await process_numbers(update, context, r_text, 1)
        return

    if data == "withdraw_start":
        balance = get_user(uid)['balance']
        if balance < MIN_WITHDRAW:
            await query.message.reply_text(
                LANG_TEXTS[get_user_lang(uid)]["withdraw_min_err"].format(bal=format_balance(balance), min_val=MIN_WITHDRAW),
                parse_mode="HTML"
            )
            return
        context.user_data["withdraw_mode"] = "select_method"
        await query.message.reply_text(
            LANG_TEXTS[get_user_lang(uid)]["withdraw_method_prompt"],
            reply_markup=withdraw_method_keyboard(uid)
        )
        return

    if data == "withdraw_confirm":
        await process_withdraw_confirm(update, context)
        return

    if data == "withdraw_cancel":
        await process_withdraw_cancel(update, context)
        return

    if data.startswith("admin_approve_"):
        await admin_approve_withdraw(update, context, data.replace("admin_approve_", ""))
        return

    if data.startswith("admin_reject_"):
        await admin_reject_withdraw(update, context, data.replace("admin_reject_", ""))
        return

    if data.startswith("my_ref_"):
        target_uid = data.replace("my_ref_", "")
        all_logs = load_data(ACTIVITY_LOGS_FILE)
        my_referrals = [log for log in all_logs if str(log.get('uid')) == str(target_uid) and log.get('action') == "REFERRAL_JOINED"]
        content = f"👥 REPLICATION METRICS — {target_uid}\n━━━━━━━━━━━━━━━━━━━━━━\nTOTAL NODES: {len(my_referrals)}\n\n"
        for i, log in enumerate(my_referrals, 1):
            try:
                dt_obj = datetime.fromisoformat(log['timestamp'])
                ref_id = log.get('details', {}).get('referred_user', 'N/A')
                content += f"{i}. NODE_ID: {ref_id} | {dt_obj.strftime('%d/%m/%Y %I:%M %p')}\n"
            except Exception:
                continue
        f = io.BytesIO(content.encode())
        f.name = f"REF_{target_uid}.txt"
        await context.bot.send_document(chat_id=uid, document=f, caption="✅ **REPLICATION LOGS GENERATED**", parse_mode="Markdown")
        return

    if data.startswith("full_logs_"):
        target_uid = data.replace("full_logs_", "")
        stats = get_user_stats(target_uid)
        all_logs = load_data(ACTIVITY_LOGS_FILE)
        user_db = load_data(USER_DATA_FILE)
        user_info = user_db.get(str(target_uid), {})
        user_otps = [log for log in all_logs if str(log.get('uid')) == str(target_uid) and log.get('action') == "OTP_RECEIVED"]
        content = (
            f"📊 PACKET ANALYSIS — {target_uid}\n"
            f"💰 WALLET: {user_info.get('balance', 0):.2f} BDT\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"TODAY NODES: {stats['today_numbers']}\n"
            f"TODAY OTPS: {stats['today_otps']}\n"
            f"ALL NODES: {stats['total_numbers']}\n"
            f"ALL OTPS: {stats['total_otps']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\nDECRYPTED PACKET LOGS:\n"
        )
        for i, log in enumerate(user_otps, 1):
            try:
                dt_obj = datetime.fromisoformat(log['timestamp'])
                d = log.get('details', {})
                content += f"{i}. {dt_obj.strftime('%d/%m/%Y %I:%M %p')}\n   📟 ADDR: {d.get('number', 'N/A')}\n   🔑 KEY: {d.get('otp', 'N/A')}\n\n"
            except Exception:
                continue
        f = io.BytesIO(content.encode())
        f.name = f"USER_{target_uid}.txt"
        await context.bot.send_document(
            chat_id=uid, document=f,
            caption=f"✅ <b>PACKET DATA DUMP FOR ID: <code>{target_uid}</code></b>",
            parse_mode="HTML"
        )
        return

async def post_init(application):
    for _ in range(20):
        asyncio.create_task(worker())
    asyncio.create_task(monitor_loop(application))
    asyncio.create_task(liveaccess_refresh_loop())

def main():
    try:
        app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).post_init(post_init).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("get1number", get1number_command))
        app.add_handler(CommandHandler("searchotp", searchotp_command))
        app.add_handler(CommandHandler("balance", balance_command))
        app.add_handler(CommandHandler("profile", profile_command))

        app.add_handler(CallbackQueryHandler(button_callback))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

        print("🚀 BOT RUNNING...")
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    except Exception as e:
        print(f"CRITICAL ERROR STARTING BOT: {e}")

if __name__ == "__main__":
    main()