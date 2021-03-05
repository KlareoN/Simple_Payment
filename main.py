import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests, json, random

import config

bot = telebot.TeleBot(config.telegram_token)

@bot.message_handler(commands = ['start'])
def start_message(message):
	global temp_code
	global amount
	global local_var

	amount = 1 # цена
	temp_code = random.randint(1000000, 9999999)

	local_var = f'Номер телефона: {config.qiwi_number}'

	if config.qiwi_transfer_anonim == 1:
		local_var = f'Киви Ник: {config.qiwi_nick}'
		url_qiwi = f'https://qiwi.com/payment/form/99999?extra%5B%27account%27%5D={config.qiwi_nick}&amountInteger={amount}&amountFraction=0&blocked%5B0%5D=comment&blocked%5B1%5D=account&blocked%5B2%5D=sum'
	else:
		local_var = f'Номер телефона: {config.qiwi_number}'
		url_qiwi = f'https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={config.qiwi_number}&extra%5B%27comment%27%5D={temp_code}&amountInteger={amount}&amountFraction=0&blocked%5B0%5D=comment&blocked%5B1%5D=account&blocked%5B2%5D=sum'

	markup = InlineKeyboardMarkup()
	markup.row_width = 1
	markup.add(InlineKeyboardButton('Ссылка на оплату', url = f'{url_qiwi}'),
			   InlineKeyboardButton('Проверить оплату', callback_data = 'check'))

	bot.send_message(message.chat.id, f'Привет, я выставил тебе счёт!\n'
									  f'{local_var}\n'
									  f'Сумма: {amount} Рублей\n'
									  f'Комментарий: {temp_code}\n'
									  f'ВОЗМОЖНО ВКЛЮЧЕНА ОПЛАТА ПО НИКУ, ВСТАВЬТЕ КОММЕНТАРИЙ КОТОРЫЙ МЫ ВАМ ВЫДАЛИ ВЫШЕ!', reply_markup = markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	if call.data == 'check':
		global temp_code
		global amount
		s = requests.Session()
		s.headers['authorization'] = 'Bearer ' + config.qiwi_token
		parameters = {'rows': '10'}
		h = s.get(f'https://edge.qiwi.com/payment-history/v1/persons/{config.qiwi_number}/payments', params=parameters)
		req = json.loads(h.text)

		for i in range(len(req['data'])):
			if req['data'][i]['comment'] == f'{temp_code}' and req['data'][i]['sum']['amount'] == amount:
				bot.send_message(call.message.chat.id, f'Спасибо, ваш платёж на сумму {amount} был успешно обработан!')
				temp_code = -1 # анти абуз типа
				break

bot.polling()
