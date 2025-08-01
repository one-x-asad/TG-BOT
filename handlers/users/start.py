from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from loader import dp, bot
import datetime
import asyncio
import io

ADMINS = [7174828209]  # Adminlar ID ro‘yxati
CHANNEL_USERNAME = "@N1TDMUZB"  # Majburiy obuna kanali

users = {}
device_limits = {}
user_index = 1
obzor_enabled = False
pending_refs = {}


def get_main_keyboard(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        "🎁 KONKURS SOVG'ALARI",
        "📅 KONKURS TUGASH SANASI",
        "📨 Mening balim",
        "🆔 Mening ID raqamim",
        "📨 Referal havolam",
        "🏆 Top referallar"
    ]
    if obzor_enabled:
        buttons.append("🆕 Konkursdagi akkaunt obzori")
    if user_id in ADMINS:
        buttons.append("📋 ISHTIROKCHILAR RO‘YXATI")
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    device_id = f"{user_id}_{message.from_user.first_name}"

    # Obuna tekshiruvi
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["left", "kicked"]:
            raise Exception("Not subscribed")
    except:
        if args.isdigit():
            pending_refs[user_id] = int(args)

        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("🔔 Obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
            InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
        )
        await message.answer("👋 Botdan foydalanish uchun kanalimizga obuna bo'ling!", reply_markup=keyboard)
        return

    # Obuna bo‘lgan — ro‘yxatdan o‘tkazamiz
    await register_user(message, int(args) if args.isdigit() else None)


@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(call: CallbackQuery):
    user_id = call.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status not in ["member", "administrator", "creator"]:
            raise Exception("Not subscribed")
    except:
        await call.answer("❌ Hali ham obuna bo‘lmagansiz!", show_alert=True)
        return

    await call.message.edit_text("✅ Obuna muvaffaqiyatli tasdiqlandi!")
    args = pending_refs.pop(user_id, None)
    await register_user(call.message, args)



async def register_user(message: types.Message, ref_id=None):
    global user_index
    user_id = message.from_user.id
    device_id = f"{user_id}_{message.from_user.first_name}"

    if device_id not in device_limits:
        device_limits[device_id] = []
    if user_id not in device_limits[device_id]:
        device_limits[device_id].append(user_id)
    if len(device_limits[device_id]) > 3:
        await message.answer("❌ Bir telefondan 3 tadan ortiq akkaunt bilan qatnashish mumkin emas!")
        return

    if user_id not in users:
        users[user_id] = {
            'ref_count': 0,
            'referred_by': None,
            'index': user_index
        }
        user_index += 1
        if ref_id and ref_id != user_id and ref_id in users:
            users[ref_id]['ref_count'] += 10
            users[user_id]['referred_by'] = ref_id
            try:
                await bot.send_message(
                    ref_id,
                    f"🎉 Sizning referal havolangiz orqali yangi foydalanuvchi ro‘yxatdan o‘tdi!\n"
                    f"Yangi ballaringiz: {users[ref_id]['ref_count']}"
                )
            except:
                pass

    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!\nSiz muvaffaqiyatli Konkursda ishtirok etyapsiz.",
        reply_markup=get_main_keyboard(user_id)
    )


@dp.message_handler(lambda msg: msg.text == "📨 Mening balim")
async def show_my_score(message: types.Message):
    user_id = message.from_user.id
    score = users.get(user_id, {}).get('ref_count', 0)
    await message.answer(f"🏅 Sizning balingiz: {score} ball")


@dp.message_handler(lambda msg: msg.text == "📅 KONKURS TUGASH SANASI")
async def contest_end_date(message: types.Message):
    today = datetime.datetime.now()
    end_date = today + datetime.timedelta(weeks=2)
    await message.answer(f"📅 Konkurs {end_date.strftime('%Y-%m-%d')} sanasida tugaydi.")


@dp.message_handler(lambda msg: msg.text == "🎁 KONKURS SOVG'ALARI")
async def prizes(message: types.Message):
    text = (
        "🎁 KONKURS SOVG'ALARI:\n\n"
        "🥇 1-o‘rin: 2,000 UC\n"
        "🥈 2-o‘rin: 1,500 UC\n"
        "🥉 3-o‘rin: 1,000 UC\n"
        "🔥 4-o‘rin: 500 RP\n"
        "🔥 5-o‘rin: 300 RP\n"
        "🎖 6-10-o‘rinlar: 100 RP"
    )
    await message.answer(text)


from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text

ebr_ids = []

@dp.message_handler(lambda msg: msg.text == "🆔 Mening ID raqamim")
async def my_id_handler(message: types.Message):
    user_id = message.from_user.id

    # Agar bu ID oldin yozilmagan bo‘lsa, ro‘yxatga qo‘shiladi
    if user_id not in ebr_ids:
        ebr_ids.append(user_id)

    # ebr_id raqamini hisoblash (1 dan boshlab)
    ebr_id_number = ebr_ids.index(user_id) + 1

    await message.answer(f"🆔 Sizning ID raqamingiz: {user_id}\n📌 Sizning ID raqamingiz: {ebr_id_number}")


@dp.message_handler(lambda msg: msg.text == "📋 ISHTIROKCHILAR RO‘YXATI")
async def all_users(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    if not users:
        await message.answer("📭 Hozircha ishtirokchilar ro‘yxati mavjud emas.")
        return

    file = io.StringIO()

    # Lug'atni tartiblab chiqaramiz (foydalanuvchi raqami 1 dan boshlab)
    for index, (uid, data) in enumerate(users.items(), start=1):
        file.write(f"{index}. ID: {uid} | Referallar: {data.get('ref_count', 0)} ball\n")

    file.seek(0)

    await bot.send_document(
        chat_id=message.chat.id,
        document=types.InputFile(file, filename="ishtirokchilar.txt")
    )


@dp.message_handler(lambda msg: msg.text == "📨 Referal havolam")
async def referral_link(message: types.Message):
    user_id = message.from_user.id
    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={user_id}"
    await message.answer(f"📨 Sizning referal havolangiz:\n\n🔗 {link}\n\nDo‘stlaringizga yuboring va ball to‘plang!")


@dp.message_handler(lambda msg: msg.text == "🏆 Top referallar")
async def top_referrals(message: types.Message):
    if not users:
        await message.answer("📭 Hozircha hech kim ro‘yxatdan o‘tmagan.")
        return

    top = sorted(users.items(), key=lambda x: x[1]['ref_count'], reverse=True)[:10]
    text = "🏆 TOP 10 REFERALLAR:\n\n"
    for i, (uid, data) in enumerate(top, 1):
        text += f"{i}. ID: {uid} — {data['ref_count']} ball\n"

    await message.answer(text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)