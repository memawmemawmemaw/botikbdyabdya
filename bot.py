import sqlite3
import ssl
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
import requests
from telegram import Update, CallbackQuery
from telegram.ext import Updater, CommandHandler,Filters, MessageHandler, CallbackContext, ConversationHandler, CallbackQueryHandler
import certifi

from telegram import ReplyKeyboardMarkup, KeyboardButton


# Определяем константу для состояния регистрации пользователя
REGISTERING_USER, REGISTERING_NICKNAME = range(2)

DEPOSIT_AMOUNT, CHOOSING_NETWORK = range(2)




def create_connection():
    """
    Создаёт соединение с базой данных.

    :return: Соединение с базой данных.
    """
    # В функции create_connection() измените имя базы данных на "users_new.db"
    conn = sqlite3.connect("users.db")

    return conn





def start_registration(update: Update, context: CallbackContext) -> int:
    """
    Начинает процесс регистрации нового пользователя.

    :param update: Обновление Telegram.
    :param context: Контекст вызова обработчика.
    :return: Состояние регистрации пользователя.
    """
    update.message.reply_text("Давайте начнем регистрацию. Пожалуйста, введите ваш уникальный никнейм:")
    return REGISTERING_USER






REGISTERING_NICKNAME = 0

def register_user(update: Update, context: CallbackContext) -> int:
    """
    Регистрирует нового пользователя.

    :param update: Обновление Telegram.
    :param context: Контекст вызова обработчика.
    :return: Состояние регистрации пользователя.
    """
    user = update.message.from_user
    nickname = update.message.text

    conn = create_connection()
    cursor = conn.cursor()
    while True:
        cursor.execute("SELECT * FROM users WHERE username=?", (nickname,))
        result = cursor.fetchone()
        if result:
            update.message.reply_text("Этот никнейм уже занят! Пожалуйста, введите другой никнейм:")
            # Запрашиваем ввод никнейма еще раз
            return REGISTERING_NICKNAME
        else:
            cursor.execute("INSERT INTO users (username) VALUES (?)", (nickname,))
            conn.commit()
            conn.close()
            on_successful_registration(update, context)  # Вызываем функцию после успешной регистрации
            return ConversationHandler.END
        
        
        
        
        
def cancel_registration(update: Update, context: CallbackContext) -> int:
    """
    Отменяет процесс регистрации пользователя.

    :param update: Обновление Telegram.
    :param context: Контекст вызова обработчика.
    :return: Состояние регистрации пользователя.
    """
    update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END




from telegram import ReplyKeyboardMarkup, KeyboardButton

def on_successful_registration(update: Update, context: CallbackContext):
    """
    Обработчик успешной регистрации пользователя.

    :param update: Обновление Telegram.
    :param context: Контекст вызова обработчика.
    :return: None
    """
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Кошелек"),
                KeyboardButton(text="Кнопка"),
                KeyboardButton(text="О проекте"),
                
            ]
        ],
        resize_keyboard=True
    )

    update.message.reply_text("Вы успешно зарегистрированы. Выберите функцию:", reply_markup=reply_markup)
    
    
    
    

def wallet(update: Update, context: CallbackContext):
    username = update.effective_user.username  # Получаем username пользователя
    balances = get_user_balances_from_database(username)
    if balances:
        rub_balance = balances.get("RUB", 0)  # Получаем баланс в рублях
        usdt_balance = balances.get("USDT", 0)  # Получаем баланс в USDT
        money_bag_emoji = "💰"  # Эмодзи с деньгами
        message = f"{money_bag_emoji} Ваш текущий баланс:\nRUB: {rub_balance} \nUSDT: {usdt_balance}"
        
        # Создаем клавиатуру с кнопками
        keyboard = [
            [InlineKeyboardButton("Пополнить", callback_data="deposit")],
            [InlineKeyboardButton("Перевести", callback_data="transfer")],
            [InlineKeyboardButton("Вывести", callback_data="withdraw")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем сообщение с балансом и клавиатурой
        update.message.reply_text(message, reply_markup=reply_markup)
        
        
        
        
# Определяем состояние для запроса суммы пополнения
def deposit(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Введите сумму пополнения:")
    return DEPOSIT_AMOUNT



def deposit_amount(update: Update, context: CallbackContext):
    amount = update.message.text
    converted_amount = convert_to_usdt(amount)
    if converted_amount is not None:
        update.message.reply_text(f"Сумма успешно сконвертирована в USDT: {converted_amount}\n"
                                  "Пожалуйста, переведите данную сумму на наш криптокошелек: [ADDRESS].\n"
                                  "После перевода, пожалуйста, отправьте нам транзакционный ID.")
    else:
        update.message.reply_text("Произошла ошибка при конвертации суммы. Попробуйте позже.")
    return ConversationHandler.END
    
# Функция для обработки введенной суммы пополнения
def handle_deposit_amount(update: Update, context: CallbackContext):
    try:
        text = update.message.text
        amount_rub = float(text)
        if amount_rub <= 0:  # Убедитесь, что введенная сумма больше нуля
            raise ValueError
        # Сохраняем введенную сумму в user_data
        context.user_data['deposit_amount'] = amount_rub
        keyboard = [
            [InlineKeyboardButton("TRON (TRC20)", callback_data="tron")],
            [InlineKeyboardButton("USDT (ERC20)", callback_data="tether")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Выберите сеть пополнения:", reply_markup=reply_markup)
        return CHOOSING_NETWORK  # Переход в состояние выбора сети пополнения
    except (ValueError, AttributeError):
        update.message.reply_text("Пожалуйста, введите корректную сумму пополнения.")


def get_usdt_rate():
    # Здесь предполагается использование CoinGecko API для получения курса USDT к RUB
    url = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=rub"
    response = requests.get(url, verify=True)  # Используем verify=True для проверки SSL
    if response.status_code == 200:
        data = response.json()
        print("Response data:", data)  # Добавляем отладочный вывод
        usdt_to_rub = data.get('tether', {}).get('rub')  # Здесь используем 'tether' вместо 'usdt'
        print("USDT to RUB rate:", usdt_to_rub)  # Добавляем отладочный вывод
        if usdt_to_rub:
            return 1 / usdt_to_rub  # Возвращаем курс USDT к RUB (обратный курс)
    return None



def convert_to_usdt(amount_rub):
    print("Amount rub:", amount_rub)  # Выводим введенное значение
    rate = get_usdt_rate()
    print("Rate:", rate)  # Выводим курс
    if rate is not None:
        try:
            amount_rub = float(amount_rub)  # Преобразуем строку в число
            amount_usdt = amount_rub * rate
            return amount_usdt
        except ValueError:
            print("Invalid amount_rub:", amount_rub)
            return None
    return None


def get_trx_rate():
    # Используем CoinGecko API для получения курса TRX к RUB
    url = "https://api.coingecko.com/api/v3/simple/price?ids=tron&vs_currencies=rub"
    response = requests.get(url, verify=True)
    if response.status_code == 200:
        data = response.json()
        trx_to_rub = data.get('tron', {}).get('rub')
        if trx_to_rub:
            return 1 / trx_to_rub  # Возвращаем курс TRX к RUB (обратный курс)
    return None


def convert_to_trx(amount_rub):
    print("Amount rub:", amount_rub)  # Выводим введенное значение
    rate = get_trx_rate()
    print("Rate:", rate)  # Выводим курс
    if rate is not None:
        try:
            amount_rub = float(amount_rub)  # Преобразуем строку в число
            amount_trx = amount_rub * rate
            return amount_trx
        except ValueError:
            print("Invalid amount_rub:", amount_rub)
            return None
    return None


# Функция для обработки выбора сети пополнения
def choose_network(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    network = query.data
    query.edit_message_text(text=f"Вы выбрали сеть пополнения: {network}")
    
    # Получаем введенную пользователем сумму
    user_input = context.user_data.get('deposit_amount')
    
    if user_input is not None:
        if network == 'tether':
            converted_amount = convert_to_usdt(user_input)
            address = "[USDT_ADDRESS]"  # Замените на адрес вашего кошелька для USDT
        elif network == 'tron':
            converted_amount = convert_to_trx(user_input)
            address = "[TRX_ADDRESS]"  # Замените на адрес вашего кошелька для TRX
            
        else:
            converted_amount = None
            address = None
        
        if converted_amount is not None:
            query.message.reply_text(f"Сумма успешно сконвертирована в {network.upper()}: {converted_amount}\n"
                                     f"Пожалуйста, переведите данную сумму на наш криптокошелек для {network.upper()}: {address}.\n"
                                     "После перевода, пожалуйста, отправьте нам транзакционный ID.")
            return ConversationHandler.END
        else:
            query.message.reply_text("Произошла ошибка при конвертации суммы. Попробуйте позже.")
    else:
        query.message.reply_text("Произошла ошибка. Попробуйте начать процесс пополнения заново.")
    return ConversationHandler.END



# Функция для отмены пополнения баланса
def cancel_deposit(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Пополнение баланса отменено.")
    return ConversationHandler.END





def get_user_balances_from_database(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT rub_balance, usdt_balance FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"RUB": result[0], "USDT": result[1]}
    else:
        return {"RUB": 0, "USDT": 0}







def main():
    updater = Updater("7166999778:AAGZKkTHppT5qhCTP9i9_z_tHrF1VDm7n4g", use_context=True)
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_registration)],
        states={
            REGISTERING_USER: [MessageHandler(Filters.text & (~Filters.command), register_user)],
        },
        fallbacks=[CommandHandler("cancel", cancel_registration)],
    )

    conv_handler_deposit = ConversationHandler(
        entry_points=[
            CommandHandler("deposit", deposit),
            MessageHandler(Filters.regex('^Пополнить$'), deposit),
            CallbackQueryHandler(deposit, pattern='^deposit$')
        ],
        states={
            DEPOSIT_AMOUNT: [
                MessageHandler(Filters.text & ~Filters.command, handle_deposit_amount),
                CallbackQueryHandler(deposit, pattern='^deposit$')  # Добавляем обработчик для кнопки "Пополнить"
            ],
            CHOOSING_NETWORK: [CallbackQueryHandler(choose_network, pattern='^(tron|tether)$')],
        },
        fallbacks=[CommandHandler("cancel", cancel_deposit)],
    )

    dp.add_handler(conv_handler)
    dp.add_handler(conv_handler_deposit)
    dp.add_handler(MessageHandler(Filters.regex('^Кошелек$'), wallet))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()