import os
import sys

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


def _get_detail_exception_info(exception_object: Exception):
    """
    Returns the short occurred exception description.
    :param exception_object:
    :return:
    """
    type, value, traceback = sys.exc_info()
    if traceback:
        # import traceback as tb
        # tb.print_tb(traceback, file=sys.stdout)

        return '{message} ({code} in {file}: {line})'.format(
            message=str(exception_object),
            code=exception_object.__class__.__name__,
            file=os.path.split(sys.exc_info()[2].tb_frame.f_code.co_filename)[1],
            line=sys.exc_info()[2].tb_lineno,
        )
    else:
        return f'{str(exception_object)} ({exception_object.__class__.__name__})'