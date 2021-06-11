import json
import os

from dotenv import load_dotenv
import telebot

load_dotenv()
# TODO ddos check
# TODO get name
# TODO edit message
# TODO greeting message with photo or video

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

ACTIONS = json.loads(os.environ.get('ACTIONS'))
website = os.environ.get('website')


def get_trouble(message, action):
    bot.send_message(message.chat.id,
                     'Ваше обращение принято в обработку. С вами свяжутся в ближайшее время! Благодарим за обращение!',
                     reply_markup=returntomainmenu_keyboard())
    bot.send_message(f"{os.environ.get(action)}",
                     f'Пользователь: @{message.from_user.username}\nТема: {ACTIONS[action]}\nСообщение: {message.text}')
    bot.forward_message(f"{os.environ.get(action)}", message.chat.id, message_id=message.id)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    answer = ''
    if call.data == 'contact':
        answer = f'Сайт: {website}\nАдрес: пр. Комсомольский, 80, офис 304\n'
        bot.send_message(call.message.chat.id, answer, reply_markup=returntomainmenu_keyboard(show_website=True))
    elif call.data in ACTIONS.keys():
        answer = 'Опишите свою ситуацию в ответе одним сообщением, пожалуйста.'
        sent = bot.send_message(call.message.chat.id, answer)
        bot.register_next_step_handler(sent, get_trouble, action=call.data)
    elif call.data == 'menu':
        bot.send_message(call.message.chat.id, 'Выберите действие', reply_markup=standart_keyboard())
    else:
        pass


def returntomainmenu_keyboard(show_website=False):
    kboard = telebot.types.InlineKeyboardMarkup()
    if show_website:
        kboard.add(telebot.types.InlineKeyboardButton(text='Перейти на сайт', url=website))
    kboard.add(telebot.types.InlineKeyboardButton(text='Вернуться к действиям', callback_data='menu'))
    return kboard


def standart_keyboard():
    kboard = telebot.types.InlineKeyboardMarkup(row_width=6)
    kboard.add(telebot.types.InlineKeyboardButton(text='Контакты', callback_data='contact'))
    for k, v in ACTIONS.items():
        kboard.add(telebot.types.InlineKeyboardButton(text=v, callback_data=k))
    return kboard


def greeting_message(message):
    return (f'Я могу ответить на самые частые вопросы: показать контакты, рассказать об основных направлениях, '
            f'мероприятиях и принять обращение.\n\n'
            f'{message.from_user.first_name}, какое действие вы хотите выполнить?')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, greeting_message(message), reply_markup=standart_keyboard())


@bot.message_handler(commands=['about', ])
def send_welcome(message):
    bot.send_message(message.chat.id, greeting_message(message), reply_markup=standart_keyboard())


if __name__ == '__main__':
    # bot.polling(none_stop=True)
    bot.polling()
