import telebot
import settings
import models
import constants

# TODO ddos check
# TODO edit message
# TODO greeting message with photo or video
# TODO опрос статуса ответа на обращение - фоновый таск
# TODO если вопрос не решён, напомнить ответственному - фоновый таск

bot = telebot.TeleBot(settings.BOT_TOKEN)


def get_trouble(message, action):
    bot.send_message(message.chat.id,
                     'Ваше обращение принято в обработку. С вами свяжутся в ближайшее время! Благодарим за обращение!',
                     reply_markup=returntomainmenu_keyboard())
    user = models.RDB()
    bot.send_message(settings.get_env_value(action),
                     f'Пользователь: @{message.from_user.username}\n'
                     f'Имя: {user.get_item(message.chat.id, "name")}\n'
                     f'Статус: {constants.status.get(user.get_item(message.chat.id, "status"))}\n'
                     f'Тема: {settings.ACTIONS[action]}\n'
                     f'Сообщение: {message.text}')
    bot.forward_message(settings.get_env_value(action), message.chat.id, message_id=message.id)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    # answer = ''
    if call.data == 'contact':
        answer = f'Сайт: {settings.get_env_value("website")}\nАдрес: пр. Комсомольский, 80, офис 304\n'
        bot.send_message(call.message.chat.id, answer, reply_markup=returntomainmenu_keyboard(show_website=True))
    elif call.data in settings.ACTIONS.keys():
        answer = 'Опишите свою ситуацию в ответе одним сообщением, пожалуйста.'
        sent = bot.send_message(call.message.chat.id, answer)
        bot.register_next_step_handler(sent, get_trouble, action=call.data)
    elif call.data == 'menu':
        bot.send_message(call.message.chat.id, 'Выберите действие',
                         reply_markup=render_keyboard(settings.ACTIONS, True))
    elif call.data in constants.status.keys():
        chat_id = call.message.chat.id
        db_item = models.RDB()
        db_item.change_item(chat_id, "status", str(call.data))

        bot.send_message(chat_id,
                         f'{db_item.get_item(chat_id, "name")}, приятно познакомиться! Спасибо, что уделили время и ответили на вопросы!\n\n'
                         f'{greeting_message()}\n\n Какое действие хотите выполнить?',
                         reply_markup=render_keyboard(settings.ACTIONS, True))
    else:
        pass


def returntomainmenu_keyboard(show_website=False):
    kboard = telebot.types.InlineKeyboardMarkup()
    if show_website:
        kboard.add(telebot.types.InlineKeyboardButton(text='Перейти на сайт', url=settings.get_env_value("website")))
    kboard.add(telebot.types.InlineKeyboardButton(text='Вернуться к действиям', callback_data='menu'))
    return kboard


def render_keyboard(params: dict, standart=False):
    kboard = telebot.types.InlineKeyboardMarkup(row_width=6)
    if standart:
        kboard.add(telebot.types.InlineKeyboardButton(text='Контакты', callback_data='contact'))
    for k, v in params.items():
        kboard.add(telebot.types.InlineKeyboardButton(text=v, callback_data=k))
    return kboard


def greeting_message():
    return (f'Я могу ответить на самые частые вопросы: показать контакты, рассказать об основных направлениях, '
            f'мероприятиях и принять обращение.\n\n')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.is_bot:
        return
    # bot.reply_to(message, greeting_message(), reply_markup=standart_keyboard())
    bot.reply_to(message, greeting_message())
    if not models.RDB().get_item(message.chat.id, 'name'):
        get_name(message)


def get_name(message, error=False):
    if error:
        msg = "Пожалуйста, укажите Ваше имя корректно (имя должно содержать только буквы)"
    else:
        msg = "Напишите, как Вас зовут (как к Вам обращаться)"
    first_dialog = bot.send_message(message.chat.id, msg)
    bot.register_next_step_handler(first_dialog, create_user)


def name_is_valid(name: str):
    return name.replace('-', '').isalpha() and len(name) <= 100


def create_user(message):
    if message.content_type == 'text':
        db_item = models.RDB()
        chat_id = message.chat.id
        tm_id = message.from_user.id
        name = message.text.strip()
        m_id = message.id
        if name_is_valid(name):
            body = db_item.init_item(chat_id, tm_id, name, m_id)
            db_item.set_item(chat_id, body)
            bot.send_message(message.chat.id, "Являетесь ли вы верующим человеком?",
                             reply_markup=render_keyboard(constants.status))
        else:
            get_name(message, True)
    else:
        send_welcome(message)



if __name__ == '__main__':
    # bot.polling(none_stop=True)
    bot.polling()
