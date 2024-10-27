from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text

# Токен бота
API_TOKEN = '7587699720:AAGl9kyRJQ8EgglSS9Rkt7TYNEk25XKqDIk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Списки пользователей и администраторов
user_ids = set()  # ID всех пользователей
admin_ids = set()  # ID администраторов

# Главные кнопки
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Төлем жасау"), KeyboardButton("SMS жіберуді бастау"))

# Кнопки «иә», «жоқ», «артқа»
sms_menu = InlineKeyboardMarkup(row_width=2)
sms_menu.add(InlineKeyboardButton("иә", callback_data="sms_yes"),
             InlineKeyboardButton("жоқ", callback_data="sms_no"),
             InlineKeyboardButton("артқа", callback_data="back"))

# /start - Добавление пользователя
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_ids.add(message.from_user.id)  # Добавляем пользователя в список
    await message.answer("Сәлеметсіз бе! Қандай қызмет қажет?", reply_markup=main_menu)

# Обработчик кнопки «Төлем жасау»
@dp.message_handler(Text(equals="Төлем жасау"))
async def payment_info(message: types.Message):
    await message.answer("Төлем жасау: 200 теңге. Аптасына бір рет. @asuxq админыңа жазыңыз.\nKazakh SMS - бұл жаңа бастаулар мен жаңа нәтежиелер. Бұл боттың арқасында әрқашан кез-келген адамға SMS жіберуге болады.")

# Обработчик кнопки «SMS жіберуді бастау»
@dp.message_handler(Text(equals="SMS жіберуді бастау"))
async def sms_start(message: types.Message):
    await message.answer("Сіз төйлем жасадыңызба?:", reply_markup=sms_menu)

# Обработка inline-кнопок для SMS меню
@dp.callback_query_handler(lambda c: c.data)
async def process_sms_menu(callback_query: types.CallbackQuery):
    if callback_query.data == "sms_yes":
        await bot.send_message(callback_query.from_user.id, "Жақсы, енді кез келген нөмір мен, неше SMS жіберу керек екенің жазыңыз.")
    elif callback_query.data == "sms_no":
        await bot.send_message(callback_query.from_user.id, "Төлем жасап болған соң оралыңыз.")
    elif callback_query.data == "back":
        await bot.send_message(callback_query.from_user.id, "Қызмет түрін таңдаңыз:", reply_markup=main_menu)

# Обработка сообщений после «иә»
@dp.message_handler(lambda message: "Жақсы" in message.text)
async def receive_sms_request(message: types.Message):
    # Отправить запрос администраторам
    for admin_id in admin_ids:
        await bot.send_message(admin_id, f"ID: {message.from_user.id} {message.text} сообщениесін жіберді.")

    # Показать кнопки «жіберу» и «артқа»
    confirm_menu = InlineKeyboardMarkup(row_width=2)
    confirm_menu.add(InlineKeyboardButton("жіберу", callback_data="send"),
                     InlineKeyboardButton("артқа", callback_data="exit"))
    await message.answer("Тапсырысты жіберуге дайынсыз ба?", reply_markup=confirm_menu)

# Обработка inline-кнопок для подтверждения отправки
@dp.callback_query_handler(lambda c: c.data in ["send", "exit"])
async def process_confirmation(callback_query: types.CallbackQuery):
    if callback_query.data == "send":
        await bot.send_message(callback_query.from_user.id, "Тапсырысыңыз жіберілді!")
    elif callback_query.data == "exit":
        await bot.send_message(callback_query.from_user.id, "Қызмет түрін таңдаңыз:", reply_markup=main_menu)

# Добавление администратора через ID
@dp.message_handler(commands=['add_admin'])
async def add_admin(message: types.Message):
    try:
        new_admin_id = int(message.get_args())
        if new_admin_id in user_ids:
            admin_ids.add(new_admin_id)
            await message.reply(f"ID {new_admin_id} әкімші ретінде қосылды!")
        else:
            await message.reply("Бұл пайдаланушы ботта жоқ!")
    except ValueError:
        await message.reply("ID нөмірін дұрыс енгізіңіз!")

# Список пользователей и их ID
@dp.message_handler(commands=['user_list'])
async def user_list(message: types.Message):
    user_list = "\n".join([f"ID: {user_id}" for user_id in user_ids])
    await message.reply(f"Боттағы пайдаланушылар:\n{user_list}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
