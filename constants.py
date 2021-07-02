import settings

STATUS = {"1": 'Я прихожанин Христианской Церкви Барнаула',
          "2": 'Я неверующий',
          "3": 'Я верующий, но не посещаю церковь',
          "4": 'Я верующий, но посещаю другую церковь',
          "5": 'Нет моего варианта'
          }  # 0, 'Неизвестно'


FEEDBACK = {"answered": "✅  Да, со мной связались",
            "ignored":"❌  Нет, я не получил ответа"
            }


request = ((0, 'Нет активных обращений'),  # конечный статус
           (1, 'Обращение передано'),
           (2, 'Обращение отвечено (вопрос решён)'),  # конечный статус
           (3, 'Обращение не отвечено (вопрос не решён)'),
           (4, 'Не получен ответ о завершении вопроса'),  # конечный статус
           )

CONTACTS = (f'<u><b>НАШИ КОНТАКТЫ</b></u> 👇\n\n'
           f'Сайт: {settings.get_env_value("website")}\nАдрес: {settings.get_env_value("address")}\n\n'
           f'<b>Подпишись на наши группы!</b> 😉 \n\n'
           f'YouTube: {settings.get_env_value("yt")} \n'
           f'ВКонтакте: {settings.get_env_value("vk")} \n'
           f'Instagram: {settings.get_env_value("ig")} \n'
           f'Одноклассники: {settings.get_env_value("ok")} \n'
           f'Telegram: {settings.get_env_value("tg")} \n'
           f'Tik Tok: {settings.get_env_value("tt")} \n'
           f'Facebook: {settings.get_env_value("fb")} \n'
            )

'''
structure = {"987654":
                 {"tm_id": 123456,
                  "username": "uname",  # optional
                  "name": "Ivan",
                  "status": 1,
                  "contact": "891231231223",  # optional
                  "chat_id": 987654,
                  "last_message_id": 48,  # optional
                  "last_message":"123", # optional
                  "last_message_date":datetime,
                  "action_type":action),        # ACTIONS['action'] #optional
                  "request": 0},  # optional
             }
             '''

