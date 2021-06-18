import telebot

import settings


def greeting_message():
    return (f'Здравствуйте! Я бот-помощник Христианской Церкви Барнаула. 💒✝️\n\n'
            f'Наша церковь образовалась в 2009 году. В Барнаул приехали миссионеры Артём и Анастасия Торопчины и начали служить людям евангелием и добрыми делами.\n\n'
            f'‼️ Мы помогаем решить проблемы:\n'
            f' 🟢 Социальные\n'
            f' 🟢 Финансовые\n'
            f' 🟢 Семейные\n'
            f' 🟢 Душевные\nУже более 1000 человек получили нашу помощь. 🤝🙏\n\n'
            f'📝 Я могу принять Ваше обращение для консультации с соответствующим служителем церкви. И он сам свяжется с Вами. Это абсолютно бесплатно!🙂'
            )


def name_is_valid(name: str):
    return name.replace('-', '').isalpha() and len(name) <= 100


def render_keyboard(params: dict, standart=False):
    kboard = telebot.types.InlineKeyboardMarkup(row_width=6)
    for k, v in params.items():
        kboard.add(telebot.types.InlineKeyboardButton(text=v, callback_data=k))
    if standart:
        kboard.add(telebot.types.InlineKeyboardButton(text='Показать контакты', callback_data='contact'))
    return kboard


def returntomainmenu_keyboard(show_website=False):
    kboard = telebot.types.InlineKeyboardMarkup()
    if show_website:
        kboard.add(telebot.types.InlineKeyboardButton(text='Перейти на сайт', url=settings.get_env_value("website")))
    kboard.add(telebot.types.InlineKeyboardButton(text='Показать другие функции', callback_data='menu'))
    return kboard
