import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters import Text
from aiogram import types
from aiogram.types import FSInputFile
from aiogram.types import URLInputFile
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from aiogram.methods.send_animation import SendAnimation
from aiogram.methods import SendAnimation
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router


initalkb = [
		[
			types.KeyboardButton(text="📖 Лавка"),
		], 
		[
			types.KeyboardButton(text="💰 Баланс"),
			types.KeyboardButton(text="📧 Поддержка"),
		],
		[
			types.KeyboardButton(text="▶️ Дополнительно"),
			types.KeyboardButton(text="🎲 Испытать удачу"),
		],
		[
			types.KeyboardButton(text="➕ Пригласить друга"),
		],

	]
keyboard_inital = types.ReplyKeyboardMarkup(
		keyboard=initalkb,
		resize_keyboard=True,
		input_field_placeholder="Выберите раздел"
	)


balance_kb = [
		[
		types.KeyboardButton(text="💰 Пополнить баланс"),
		], 
		[
			types.KeyboardButton(text="🔙 Назад"),
		], 
	]
keyboard_balance = types.ReplyKeyboardMarkup(
		keyboard=balance_kb,
		resize_keyboard=True,
		input_field_placeholder="Выберите раздел"
	)

profil_kb = [
		[
			types.KeyboardButton(text="💰 Пополнить баланс"),
		],
		[
			types.KeyboardButton(text="🛒 Покупки"),
			types.KeyboardButton(text="💳 Пополнения"),
		], 
		[
			types.KeyboardButton(text="👥 Мои рефералы"),
		],
		[
			types.KeyboardButton(text="🔙 Назад"),
		], 
	]
keyboard_profil = types.ReplyKeyboardMarkup(
		keyboard=profil_kb,
		resize_keyboard=True,
		input_field_placeholder="Выберите раздел"
	)


all_kb = [
		[
			types.KeyboardButton(text="👤 Профиль"),
			types.KeyboardButton(text="🎁 Акции")
		],
		[
			types.KeyboardButton(text="⚠️ Помощь"),
			types.KeyboardButton(text="📖 Отзывы"),
		],
		[
			types.KeyboardButton(text="🏷️ Промокоды"),
		],  
		[
			types.KeyboardButton(text="🔙 Назад"),
		], 
	]
keyboard_all = types.ReplyKeyboardMarkup(
		keyboard=all_kb,
		resize_keyboard=True,
		input_field_placeholder="Выберите раздел"
	)

adminkb = [
		[
		types.KeyboardButton(text="📩 Массовая рассылка")        
		],
		[
		types.KeyboardButton(text="➕ Пополнить баланс по ID")        
		],
		[
		types.KeyboardButton(text="📨 Отправка сообщения по ID")        
		],
		[
			types.KeyboardButton(text="🔙 Назад"),
		], 
		]
keyboard_inital_adminkb = types.ReplyKeyboardMarkup(
		keyboard=adminkb,
		resize_keyboard=True,
		input_field_placeholder="Админ-панель"
		)

referalskb = [
		[
		types.KeyboardButton(text="👥 Показать моих рефералов")        
		],
		[
		types.KeyboardButton(text="💰 Доход с рефералов")        
		],
		[
			types.KeyboardButton(text="🔙 Назад"),
		], 
		]
keyboard_referals = types.ReplyKeyboardMarkup(
		keyboard=referalskb,
		resize_keyboard=True,
		input_field_placeholder="Ваши рефералы"
		)

kuponkb = [
	[
		types.KeyboardButton(text="🏷️ Активировать промокод"),
	], 
	[
		types.KeyboardButton(text="🔙 Назад"),
	],
	]
keyboard_kupon = types.ReplyKeyboardMarkup(
		keyboard=kuponkb,
		resize_keyboard=True,
		input_field_placeholder="Выберите раздел"
	)

nazadpopolkb = [
	[
		types.KeyboardButton(text="🔙 Назад"),
	],
	]
keyboard_nazadpopol = types.ReplyKeyboardMarkup(
		keyboard=nazadpopolkb,
		resize_keyboard=True,
		input_field_placeholder="Выберите раздел"
	)

def get_otzyv():
	buttons1 = [
	[
		types.InlineKeyboardButton(text="📄 Оставить отзыв", callback_data="otzyv", url='https://t.me/gandalf_otzyv')
	],

	]
	keyboard1 = types.InlineKeyboardMarkup(inline_keyboard=buttons1)
	return keyboard1

def get_help():
	buttons1 = [
	[
		types.InlineKeyboardButton(text="📄 Правила", callback_data="pravila", url='https://telegra.ph/Obshchij-svod-pravil-12-12'),
		types.InlineKeyboardButton(text="❓ FAQ", callback_data="faq", url='https://telegra.ph/FAQ-12-17-12')
	],
	[
		types.InlineKeyboardButton(text="📦 Поставщикам", callback_data="postavshik", url='https://telegra.ph/Postavshchikam-12-11'),
		types.InlineKeyboardButton(text="🔁 Замена", callback_data="zamena", url='https://telegra.ph/Zamena-tovara-12-17')
	],
	]
	keyboard1 = types.InlineKeyboardMarkup(inline_keyboard=buttons1)
	return keyboard1
def get_fortuna():
	buttons1 = [
	[
		types.InlineKeyboardButton(text="🎰 Крутить барабан", callback_data="game")
	],

	]
	keyboard1 = types.InlineKeyboardMarkup(inline_keyboard=buttons1)
	return keyboard1