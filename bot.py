import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

# 🔑 Bot tokeni
TOKEN = "8665439848:AAHo3YD8RkPVG2QqoVzPa36aDv3S8ReWeQE"
bot = telebot.TeleBot(TOKEN)

# 👤 Admin ID
ADMIN_ID = 123456789  # sizning Telegram IDingiz

# 📢 Kanal
CHANNEL_LINK = "https://t.me/TROLLER_FF"
CHANNEL_NAME = "TROLLER_FF"

# 📥 Foydalanuvchilarni JSON faylda saqlash
USERS_FILE = "users.json"

MAX_DIAMOND = 100

# JSON fayldan o'qish
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# JSON faylga yozish
def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# 📩 START
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    args = message.text.split()

    if user_id not in users:
        users[user_id] = 0

        # Referral
        if len(args) > 1:
            ref_id = args[1]
            if ref_id != user_id:
                users[ref_id] = users.get(ref_id, 0) + 7
                if users[ref_id] > MAX_DIAMOND:
                    users[ref_id] = MAX_DIAMOND
                save_users()
                # Agar 100 ga yetgan bo‘lsa adminga habar
                if users[ref_id] >= MAX_DIAMOND:
                    bot.send_message(ADMIN_ID, 
                        f"Foydalanuvchi @{ref_id} maksimal 100 almazga yetdi. Iltimos, skrin yuboring.")

    save_users()
    show_menu(message)

# 📋 Menyu
def show_menu(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💎 Almaz ishlash", callback_data="work"),
        InlineKeyboardButton("👥 Referal link", callback_data="ref"),
        InlineKeyboardButton("💰 Balans", callback_data="balans"),
        InlineKeyboardButton("📢 Kanalga bonus olish", callback_data="channel_bonus"),
        InlineKeyboardButton("💸 Almazni yechib olish", callback_data="withdraw")
    )
    bot.send_message(message.chat.id, "🏠 Asosiy menyu", reply_markup=markup)

# 💎 Almaz ishlash (faqat ishga kirish, almaz bermaydi)
@bot.callback_query_handler(func=lambda call: call.data == "work")
def work(call):
    bot.answer_callback_query(call.id, "💎 Siz ishga kirishdingiz! Faqat referral qo‘shilganda almaz olasiz.")

# 👥 Referal
@bot.callback_query_handler(func=lambda call: call.data == "ref")
def ref(call):
    user_id = str(call.from_user.id)
    bot_name = bot.get_me().username
    link = f"https://t.me/{bot_name}?start={user_id}"
    bot.send_message(call.message.chat.id,
                     f"👥 Sizning referal linkingiz:\n{link}\nHar bir odam +7 almaz beradi")

# 💰 Balans
@bot.callback_query_handler(func=lambda call: call.data == "balans")
def balans(call):
    user_id = str(call.from_user.id)
    bal = users.get(user_id, 0)
    bot.send_message(call.message.chat.id, f"💰 Sizning almazingiz: {bal}")

# 📢 Kanalga bonus
@bot.callback_query_handler(func=lambda call: call.data == "channel_bonus")
def channel_bonus(call):
    user_id = str(call.from_user.id)
    current = users.get(user_id, 0)

    # Kanal linkini jo'natish
    bot.send_message(call.message.chat.id, f"📢 Kanalga obuna bo‘lish uchun link: {CHANNEL_LINK}")

    # Kanalga obuna bo‘lsa, +10 almaz
    if current >= MAX_DIAMOND:
        bot.answer_callback_query(call.id, "❌ Siz maksimal 100 almazga yetgansiz!")
        bot.send_message(ADMIN_ID, f"Foydalanuvchi @{call.from_user.username} maksimal almazga yetdi.")
        return

    # Avval +10 almazni qo‘shish
    users[user_id] = min(current + 10, MAX_DIAMOND)
    save_users()
    bot.answer_callback_query(call.id, f"✅ Kanalga bonus +10 almaz! Hozirgi balans: {users[user_id]}")

# 💸 Almazni yechib olish
@bot.callback_query_handler(func=lambda call: call.data == "withdraw")
def withdraw(call):
    user_id = str(call.from_user.id)
    current = users.get(user_id, 0)

    if current < MAX_DIAMOND:
        bot.answer_callback_query(call.id, "❌ Hisobingizda 100 ta almaz bo‘lishi kerak!")
    else:
        bot.answer_callback_query(call.id, "✅ Siz 100 ta almazga yetdingiz! Adminga screenshot yuboring.")
        bot.send_message(ADMIN_ID, 
                         f"Foydalanuvchi @{call.from_user.username} 100 ta almazga yetdi. Iltimos, skrin yuboring.")

# 🔄 Bot ishga tushishi
print("🔄 Bot ishga tushmoqda...")
bot.infinity_polling()