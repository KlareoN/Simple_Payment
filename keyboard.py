from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_keyboard(send_url):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(
            text='Ссылка на оплату 👁',
            url=f'{send_url}'
        ),
        InlineKeyboardButton(
            text='Проверить оплату 🔎',
            callback_data='check'
        )
    )
    return markup