from datetime import datetime

import telebot
import settings
import models
import constants

# TODO ddos check
# TODO edit message
import service

bot = telebot.TeleBot(settings.BOT_TOKEN)


def get_name(message, error=False):
    if error:
        msg = "Пожалуйста, укажите Ваше имя корректно (имя должно содержать только буквы)"
    else:
        msg = "📨 Чтобы мы понимали, как к Вам обращаться, напишите, пожалуйста, как Вас зовут в ответном сообщении 👇👇👇"
    first_dialog = bot.send_message(message.chat.id, msg)
    bot.register_next_step_handler(first_dialog, create_user)


def create_user(message):
    if message.content_type == 'text':
        users = models.RDB()
        chat_id = message.chat.id
        tm_id = message.from_user.id
        name = message.text.strip()
        m_id = message.id
        if service.name_is_valid(name):
            body = users.init_item(chat_id, tm_id, name, m_id)
            users.set_item(chat_id, body)
            bot.send_message(message.chat.id, f"❓ {name}, являетесь ли Вы верующим человеком?",
                             reply_markup=service.render_keyboard(constants.STATUS))
        else:
            get_name(message, True)
    else:
        send_welcome(message)


def get_trouble(message, action):
    users = models.RDB()
    bot.send_message(message.chat.id,
                     f'{users.get_item_value(message.chat.id, "name")}, Ваше обращение принято в обработку. С Вами свяжутся в ближайшее время!🕐 Благодарим за обращение!',
                     reply_markup=service.returntomainmenu_keyboard())
    bot.forward_message(settings.get_env_value(action), message.chat.id, message_id=message.id)
    bot.send_message(settings.get_env_value(action),
                     f'Заявка №: f"{message.chat.id}{message.id}"\n'
                     f'Пользователь: @{message.from_user.username}\n'
                     f'Имя: {users.get_item_value(message.chat.id, "name")}\n'
                     f'Статус (верующий/неверующий): {constants.STATUS.get(users.get_item_value(message.chat.id, "status"))}\n'
                     f'Тема: {settings.ACTIONS[action]}\n'
                     f'Сообщение: {message.text}')
    users.change_item(message.chat.id, "request", "1")
    users.change_item(message.chat.id, "last_message_id", f"{message.id}")
    users.change_item(message.chat.id, "last_message", message.text)
    users.change_item(message.chat.id, "last_message_date", f"{datetime.now()}")
    users.change_item(message.chat.id, "action_type", f"{settings.ACTIONS[action]}")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    # answer = ''
    if call.data == 'contact':
        answer = f'Сайт: {settings.get_env_value("website")}\nАдрес: пр. Комсомольский, 80, офис 304\n'
        bot.send_message(call.message.chat.id, answer,
                         reply_markup=service.returntomainmenu_keyboard(show_website=True))
    elif call.data in settings.ACTIONS.keys():
        answer = '📨 Опишите свою ситуацию в ответе одним сообщением, пожалуйста. 👇'
        sent = bot.send_message(call.message.chat.id, answer)
        bot.register_next_step_handler(sent, get_trouble, action=call.data)
    elif call.data == 'menu':
        bot.send_message(call.message.chat.id, 'Выберите тему для Вашего обращения',
                         reply_markup=service.render_keyboard(settings.ACTIONS, True))
    elif call.data in constants.STATUS.keys():
        chat_id = call.message.chat.id
        users = models.RDB()
        users.change_item(chat_id, "status", str(call.data))

        bot.send_message(chat_id,
                         f'Приятно познакомиться, {users.get_item_value(chat_id, "name")}! Спасибо, что уделили время и ответили на вопросы! 🙏\n\n'
                         f'Какое направление Вас интересует? 👇\nКонсультации бесплатны 🔥 ',
                         reply_markup=service.render_keyboard(settings.ACTIONS, True))
    elif call.data == 'ignored':
        message = call.message
        chat_id = message.chat.id
        users = models.RDB()
        users.change_item(chat_id, "request", "3")
        bot.send_message(settings.get_env_value('admin'),
                         f'❌ ПОЛЬЗОВАТЕЛЬ НЕ ПОЛУЧИЛ КОНСУЛЬТАЦИЮ!\n'
                         f'Заявка №: {chat_id}{users.get_item_value(chat_id, "last_message_id")}"\n'
                         f'Пользователь: @{users.get_item_value(chat_id, "username")}\n'
                         f'Имя: {users.get_item_value(chat_id, "name")}\n'
                         f'Статус (верующий/неверующий): {constants.STATUS.get(users.get_item_value(chat_id, "status"))}\n'
                         f'Тема: {users.get_item_value(chat_id, "action_type")}\n'
                         f'Дата обращения: {users.get_item_value(chat_id, "last_message_date")}\n'
                         f'Сообщение: {users.get_item_value(chat_id, "last_message")}')
        bot.forward_message(settings.get_env_value("admin"), chat_id,
                            message_id=users.get_item_value(chat_id, "last_message_id"))
        answer = 'Ваше обращение отправлено специалисту повторно. Приносим извинения за задержку консультации'
        bot.send_message(chat_id, answer, reply_markup=service.returntomainmenu_keyboard(show_website=True))
    elif call.data == 'answered':
        chat_id = call.message.chat.id
        users = models.RDB()
        users.change_item(chat_id, "request", "2")
        answer = 'Благодарим за доверие к нам в Вашей ситуации! ' \
                 'При возникновении вопросов всегда готовы Вас проконсультировать!\n\n Пусть Господь благословит Вас!'
        bot.send_message(chat_id, answer, reply_markup=service.returntomainmenu_keyboard(show_website=True))
    else:
        pass


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.is_bot:
        return
    # bot.reply_to(message, greeting_message(), reply_markup=standart_keyboard())
    bot.reply_to(message, service.greeting_message())
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent
    img = open(BASE_DIR / 'static' / 'church22.jpg', 'rb')
    # img = open('static' / 'church22.jpg', 'rb')
    bot.send_photo(message.chat.id, img)
    if not models.RDB().get_item_value(message.chat.id, 'name'):
        get_name(message)
    else:
        bot.send_message(message.chat.id, 'Выберите тему для Вашего обращения',
                         reply_markup=service.render_keyboard(settings.ACTIONS, True))


from threading import Thread
from time import sleep


def feedback_checker():
    while True:
        for chat_id in models.db.scan_iter('*'):
            users = models.RDB()
            # print(chat_id)
            # print(type(chat_id))
            obj = users.get_object(chat_id)
            request_status = users.get_item_value(chat_id, 'request')
            last_message_date = users.get_item_value(chat_id, 'last_message_date')
            name = users.get_item_value(chat_id, 'name')

            if request_status == '1' and last_message_date:
                dt_format = '%Y-%m-%d %H:%M:%S.%f'
                dt = datetime.strptime(last_message_date, dt_format)
                if abs(datetime.now() - dt).days >= 1:
                    bot.send_message(chat_id.decode(), f'Здравствуйте, {name}! '
                                              f'Недавно Вы оставляли обращение для консультации.\n\n'
                                              f'С Вами связались по Вашему обращению? (выберите соответствующий вариант ниже 👇)',
                                     reply_markup=service.render_keyboard(constants.FEEDBACK))
                    users.change_item(chat_id.decode(), "request", "4")

        sleep(1000)


if __name__ == '__main__':
    # bot.polling(none_stop=True)
    Thread(target=feedback_checker).start()
    bot.polling()
