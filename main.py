import telebot

import requests
import json
import random

import config
import keyboard

bot = telebot.TeleBot(config.telegram_token, parse_mode='HTML')

class other_func():
	output = {}
	url_pay = {}
	qiwi_transfer = {}

@bot.message_handler(commands = ['start'])
def start_message(message):
	other_func.output[message.from_user.id] = []
	other_func.url_pay[message.from_user.id] = []
	other_func.qiwi_transfer[message.from_user.id] = []

	amount = config.price # цена
	temp_code = random.randint(1000000, 9999999)

	# temp_code,|,amount
	other_func.output[
		message.from_user.id
	].append(
		f'{temp_code},|,{amount}'.split(',|,')
	)

	# выглядит кошмарно, но на деле очень простая система.
	if config.qiwi_transfer_anonim == 1:
		other_func.qiwi_transfer[
			message.from_user.id
		].append(
			f'Киви Ник,|,{config.qiwi_nick}'.split(',|,')
		)

		url_qiwi = f'https://qiwi.com/payment/form/99999?extra%5B%27account%27%5D={config.qiwi_nick}&amountInteger={other_func.output[message.from_user.id][0][1]}&amountFraction=0&blocked%5B0%5D=comment&blocked%5B1%5D=account&blocked%5B2%5D=sum'

		other_func.url_pay[
			message.from_user.id
		].append(
			f'{config.qiwi_number},|,{url_qiwi}'.split(',|,')
		)

		show_nick = 'Внимание! Не забудьте вставить комментарий к переводу.'
	else:
		other_func.qiwi_transfer[
			message.from_user.id
		].append(
			f'Номер телефона,|,{config.qiwi_number}'.split(',|,')
		)

		url_qiwi = f'https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={config.qiwi_number}&extra%5B%27comment%27%5D={other_func.output[message.from_user.id][0][0]}&amountInteger={other_func.output[message.from_user.id][0][1]}&amountFraction=0&blocked%5B0%5D=comment&blocked%5B1%5D=account&blocked%5B2%5D=sum'
		other_func.url_pay[message.from_user.id].append(
			f'{config.qiwi_number},|,{url_qiwi}'.split(',|,')
		)

		show_nick = ''


	bot.send_message(
		message.chat.id,
		'👋'
	)

	bot.send_message(
		message.chat.id,
		f'<b>Привет</b>, я выставил тебе счёт!\n\n'
		f'<b>{other_func.qiwi_transfer[message.from_user.id][0][0]}:</b> <code>{other_func.qiwi_transfer[message.from_user.id][0][1]}</code>\n'
		f'<b>Сумма: </b><code>{other_func.output[message.from_user.id][0][1]} ₽</code>\n'
		f'<b>Комментарий: </b><code>{other_func.output[message.from_user.id][0][0]} </code>\n'
		f'<i>{show_nick}</i>',
		reply_markup=keyboard.main_keyboard(
			other_func.url_pay[message.from_user.id][0][1]
		)
	)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	if call.data == 'check':
		s = requests.Session()
		s.headers['authorization'] = 'Bearer ' + config.qiwi_token
		parameters = {'rows': '10'}
		h = s.get(f'https://edge.qiwi.com/payment-history/v1/persons/{config.qiwi_number}/payments', params=parameters)
		req = json.loads(h.text)

		for i in range(len(req['data'])):
			if req['data'][i]['comment'] == f'{other_func.output[call.message.chat.id][0][0]}' and req['data'][i]['sum']['amount'] == int(other_func.output[call.message.chat.id][0][1]) and req['data'][i]['sum']['currency'] == int(643):
				bot.edit_message_text(
					chat_id=call.message.chat.id,
					message_id=call.message.message_id-1,
					text=f'👍'
				)
				bot.edit_message_text(
					chat_id=call.message.chat.id,
					message_id=call.message.message_id,
					text=f'<b>Спасибо</b>, ваш платёж на сумму <code>{other_func.output[call.message.chat.id][0][1]} ₽</code> был <b>успешно обработан!</b>'
				)

				other_func.output[
					call.message.chat.id
				].append(
					f'-1,|,{int(other_func.output[call.message.chat.id][0][1])}'.split(',|,'))
				break

bot.polling()
