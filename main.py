from datetime import datetime
import logging
from pathlib import Path

import telebot
import settings
import models
import constants

# TODO ddos check
# TODO edit message
# TODO refactor send message to manager and admin to one method

import service

BASE_DIR = Path(__file__).resolve().parent
logfile = str(BASE_DIR / 'logs' / 'main.log')
# logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG)
logging.basicConfig(filename=logfile, filemode='a')

bot = telebot.TeleBot(settings.BOT_TOKEN)


def get_name(message, error=False):
    if error:
        msg = "Пожалуйста, укажите Ваше имя корректно (имя должно содержать только буквы)"
    else:
        msg = "📨 Представьтесь, пожалуйста, как Вас зовут? 🙂\n(Напишите ответное сообщение) 👇👇👇"
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

    reserved_contact = users.get_item_value(message.chat.id, "contact")
    manager_chat = settings.get_env_value(action)

    msg = f'Заявка №: "{message.chat.id}_{message.id}"\n ' \
          f'Пользователь: @{message.from_user.username}\n' \
          f'Имя: {users.get_item_value(message.chat.id, "name")}\n' \
          f'Статус (верующий/неверующий): {constants.STATUS.get(users.get_item_value(message.chat.id, "status"))}\n' \
          f'Доп. контакт: {reserved_contact}\n' \
          f'Тема: {settings.ACTIONS[action]}\n' \
          f'Сообщение: {message.text}'
    msg_log = msg.replace("\n", " - ")
    logging.warning(f'{datetime.now} - in get_trouble - MANAGER - {manager_chat} DATA - {msg_log}')

    bot.forward_message(manager_chat, message.chat.id, message_id=message.id)

    if not reserved_contact:
        k_wargs = {"reply_markup": service.render_keyboard(
            {f'private_{message.chat.id}': "Спросить контакты (⚠️Нажимать только если аккаунт скрыт пользователем)"}
        )}
    else:
        k_wargs = {}

    bot.send_message(manager_chat, msg, **k_wargs)

    bot.reply_to(message,
                 f'{users.get_item_value(message.chat.id, "name")}, Ваше обращение принято в обработку. '
                 f'Мы с вами свяжемся в ближайшее время! 🕰 Благодарим за обращение! 🌷',
                 reply_markup=service.returntomainmenu_keyboard())

    users.change_item(message.chat.id, "request", "1")
    users.change_item(message.chat.id, "last_message_id", f"{message.id}")
    users.change_item(message.chat.id, "last_message", message.text)
    users.change_item(message.chat.id, "last_message_date", f"{datetime.now()}")
    users.change_item(message.chat.id, "action_type", f"{settings.ACTIONS[action]}")
    logging.warning(f'{datetime.now} - USER DATA AFTER GET TROUBLE - {users.get_object(message.chat.id)}')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    logging.warning(f'{datetime.now} - in query_handler/ Clicked Button - {call.data}')
    try:
        bot.answer_callback_query(callback_query_id=call.id)
        if call.data == 'contact':
            chat_id = call.message.chat.id
            answer = f'Сайт: {settings.get_env_value("website")}\nАдрес: пр. Комсомольский, 80, офис 304\n'
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.id, reply_markup=None)
            bot.send_message(call.message.chat.id, answer,
                             reply_markup=service.returntomainmenu_keyboard(show_website=True))
        elif call.data in settings.ACTIONS.keys():
            chat_id = call.message.chat.id
            answer = f'Вы выбрали тему:"{settings.ACTIONS[call.data]}"\n\n📨 Опишите, пожалуйста, свою ситуацию более подробно в ответе ОДНИМ текстовым сообщением 👇👇👇'
            sent = bot.send_message(chat_id, answer)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.id,
                                          reply_markup=service.returntomainmenu_keyboard())
            bot.clear_step_handler(call.message)
            bot.register_next_step_handler(sent, get_trouble, action=call.data)
        elif call.data == 'menu':
            chat_id = call.message.chat.id
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.id, reply_markup=None)
            bot.send_message(chat_id, 'Выберите тему для Вашего обращения',
                             reply_markup=service.render_keyboard(settings.ACTIONS, True))
        elif call.data in constants.STATUS.keys():
            chat_id = call.message.chat.id
            users = models.RDB()
            users.change_item(chat_id, "status", str(call.data))

            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.id, reply_markup=None)
            bot.send_message(chat_id,
                             f'Приятно познакомиться, {users.get_item_value(chat_id, "name")}! 😉'
                             f'Спасибо, что уделили время и представились 🙏\n\n'
                             f'❓На какую тему Ваш вопрос? 👇\n(Все консультации для Вас бесплатны 🔥)',
                             reply_markup=service.render_keyboard(settings.ACTIONS, True))

        elif call.data == 'ignored':
            message = call.message
            chat_id = message.chat.id

            users = models.RDB()
            reserved_contact = users.get_item_value(message.chat.id, "contact")

            users.change_item(chat_id, "request", "3")

            if not reserved_contact:
                k_wargs = {"reply_markup": service.render_keyboard({f'private_{chat_id}': "Спросить контакты"})}
            else:
                k_wargs = {}
            bot.send_message(settings.get_env_value('admin'),
                             f'❌ ПОЛЬЗОВАТЕЛЬ НЕ ПОЛУЧИЛ КОНСУЛЬТАЦИЮ!\n'
                             f'Заявка №: {chat_id}_{users.get_item_value(chat_id, "last_message_id")}"\n'
                             f'Пользователь: @{users.get_item_value(chat_id, "username")}\n'
                             f'Имя: {users.get_item_value(chat_id, "name")}\n'
                             f'Статус (верующий/неверующий): {constants.STATUS.get(users.get_item_value(chat_id, "status"))}\n'
                             f'Доп. контакт: {reserved_contact}\n'
                             f'Тема: {users.get_item_value(chat_id, "action_type")}\n'
                             f'Дата обращения: {users.get_item_value(chat_id, "last_message_date")}\n'
                             f'Сообщение: {users.get_item_value(chat_id, "last_message")}', **k_wargs)
            bot.forward_message(settings.get_env_value("admin"), chat_id,
                                message_id=users.get_item_value(chat_id, "last_message_id"))

            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.id, reply_markup=None)
            answer = 'Ваше обращение отправлено специалисту повторно. Просим прощения за задержку консультации 😔🌷'
            bot.send_message(chat_id, answer, reply_markup=service.returntomainmenu_keyboard(show_website=True))
            logging.warning(f'{datetime.now} - Ignored Button - processed')

        elif call.data == 'answered':
            chat_id = call.message.chat.id
            users = models.RDB()
            users.change_item(chat_id, "request", "2")
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.id, reply_markup=None)
            answer = ('Благодарим за доверие к нам в Вашей ситуации! 🙏'
                      'При возникновении вопросов всегда готовы Вам помочь! 💒\n\n'
                      'Пусть Господь благословит Вас!')
            bot.send_message(chat_id, answer, reply_markup=service.returntomainmenu_keyboard(show_website=True))
            logging.warning(f'{datetime.now} - Answered Button - processed')
        elif call.data.startswith('private_'):
            btn_id = call.data
            manager_chat = call.message.chat.id
            chat_id = btn_id[btn_id.rfind('_') + 1:]
            get_contact = bot.send_message(
                chat_id,
                f'⚠️ Ваш профиль в telegram приватный. \n\nНапишите, пожалуйста, в ответе одним сообщением '
                f'ваш номер телефона или email для связи. 👇👇👇',
            )
            bot.register_next_step_handler(get_contact, additional_contact, manager_chat=manager_chat)
            bot.edit_message_reply_markup(chat_id=manager_chat, message_id=call.message.id, reply_markup=None)
        else:
            pass
    except Exception as err:
        logging.error(f'{datetime.now()} - {service._get_detail_exception_info(err)}')


def additional_contact(message, manager_chat):
    bot.forward_message(manager_chat, message.chat.id, message_id=message.id)
    contact = message.text
    users = models.RDB()
    users.change_item(message.chat.id, "contact", contact)
    bot.reply_to(message,
                 f'Спасибо, {users.get_item_value(message.chat.id, "name")}! Ваш контакт передан, скоро с Вами свяжутся 📲',
                 reply_markup=service.returntomainmenu_keyboard())


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logging.warning(f'{datetime.now} - clicked start Button')

    if message.from_user.is_bot:
        return
    # bot.reply_to(message, greeting_message(), reply_markup=standart_keyboard())
    bot.reply_to(message, service.greeting_message())
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
    sleep_time = 1000
    logging.warning(f'{datetime.now()} - start feedback_checker')
    while True:
        logging.warning(f'{datetime.now()} - start feedback_checker cycle')
        for chat_id in models.db.scan_iter('*'):
            users = models.RDB()
            # obj = users.get_object(chat_id)
            request_status = users.get_item_value(chat_id, 'request')
            last_message_date = users.get_item_value(chat_id, 'last_message_date')
            name = users.get_item_value(chat_id, 'name')

            if request_status == '1' and last_message_date:
                dt_format = '%Y-%m-%d %H:%M:%S.%f'
                dt = datetime.strptime(last_message_date, dt_format)
                if abs(datetime.now() - dt).days >= 1:
                    # if abs(datetime.now() - dt).days < 1:
                    bot.send_message(chat_id.decode(), f'Здравствуйте, {name}! '
                                                       f'Недавно Вы оставляли обращение для консультации.\n\n'
                                                       f'С Вами связались по Вашему обращению? (выберите соответствующий вариант ниже 👇)',
                                     reply_markup=service.render_keyboard(constants.FEEDBACK))
                    users.change_item(chat_id.decode(), "request", "4")
                    logging.warning(
                        f'{datetime.now()} - asking for feedback - USER_ID {users.get_item_value(chat_id, "tm_id")} - '
                        f'CHAT_ID - {chat_id.decode()}')
        logging.warning(
            f'{datetime.now()} - sleep for {sleep_time} seconds')
        sleep(sleep_time)


if __name__ == '__main__':
    logging.warning(f'{datetime.now()} - starting THREAD')
    Thread(target=feedback_checker).start()
    logging.warning(f'{datetime.now()} - starting BOT')
    bot.polling(none_stop=True)
    # bot.polling()
