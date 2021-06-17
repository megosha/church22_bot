from datetime import datetime

import telebot
import settings
import models
import constants

# TODO ddos check
# TODO edit message
# TODO greeting message with photo or video
# TODO опрос статуса ответа на обращение - фоновый таск
# TODO если вопрос не решён, напомнить ответственному - фоновый таск
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
        db_item = models.RDB()
        chat_id = message.chat.id
        tm_id = message.from_user.id
        name = message.text.strip()
        m_id = message.id
        if service.name_is_valid(name):
            body = db_item.init_item(chat_id, tm_id, name, m_id)
            db_item.set_item(chat_id, body)
            bot.send_message(message.chat.id, f"❓ {name}, являетесь ли Вы верующим человеком?",
                             reply_markup=service.render_keyboard(constants.status))
        else:
            get_name(message, True)
    else:
        send_welcome(message)


def get_trouble(message, action):
    user = models.RDB()
    bot.send_message(message.chat.id,
                     f'{user.get_item(message.chat.id, "name")}, Ваше обращение принято в обработку. С Вами свяжутся в ближайшее время!🕐 Благодарим за обращение!',
                     reply_markup=service.returntomainmenu_keyboard())
    bot.forward_message(settings.get_env_value(action), message.chat.id, message_id=message.id)
    bot.send_message(settings.get_env_value(action),
                     f'Заявка №: f"{message.chat.id}{message.id}"\n'
                     f'Пользователь: @{message.from_user.username}\n'
                     f'Имя: {user.get_item(message.chat.id, "name")}\n'
                     f'Статус: {constants.status.get(user.get_item(message.chat.id, "status"))}\n'
                     f'Тема: {settings.ACTIONS[action]}\n'
                     f'Сообщение: {message.text}')
    user.change_item(message.chat.id, "status", "1")
    user.change_item(message.chat.id, "last_message_id", f"{message.id}")
    user.change_item(message.chat.id, "last_message", message.text)
    user.change_item(message.chat.id, "last_message_date", f"{datetime.now()}")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    # answer = ''
    if call.data == 'contact':
        answer = f'Сайт: {settings.get_env_value("website")}\nАдрес: пр. Комсомольский, 80, офис 304\n'
        bot.send_message(call.message.chat.id, answer, reply_markup=service.returntomainmenu_keyboard(show_website=True))
    elif call.data in settings.ACTIONS.keys():
        answer = '📨 Опишите свою ситуацию в ответе одним сообщением, пожалуйста. 👇'
        sent = bot.send_message(call.message.chat.id, answer)
        bot.register_next_step_handler(sent, get_trouble, action=call.data)
    elif call.data == 'menu':
        bot.send_message(call.message.chat.id, 'Выберите действие',
                         reply_markup=service.render_keyboard(settings.ACTIONS, True))
    elif call.data in constants.status.keys():
        chat_id = call.message.chat.id
        db_item = models.RDB()
        db_item.change_item(chat_id, "status", str(call.data))

        bot.send_message(chat_id,
                         f'Приятно познакомиться, {db_item.get_item(chat_id, "name")}! Спасибо, что уделили время и ответили на вопросы! 🙏\n\n'
                         f'Какое направление Вас интересует? 👇\nКонсультации бесплатны 🔥 ',
                         reply_markup=service.render_keyboard(settings.ACTIONS, True))
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
    if not models.RDB().get_item(message.chat.id, 'name'):
        get_name(message)


from threading import Thread
from time import sleep

def feedback_checker():
    pass
    while True:

        sleep(100)

if __name__ == '__main__':
    # bot.polling(none_stop=True)
    Thread(target=feedback_checker).start()
    bot.polling()
