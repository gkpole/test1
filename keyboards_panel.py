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
			types.KeyboardButton(text="📦 Добавить новый товар"),
	],
	[
			types.KeyboardButton(text="📝 Редактирование товаров"),
	], 
	[
			types.KeyboardButton(text="📈 Статистика"),
			types.KeyboardButton(text="🏷️ Промокоды")
	],
	]
keyboard_inital = types.ReplyKeyboardMarkup(
		keyboard=initalkb,
		resize_keyboard=True,
		input_field_placeholder="Выберите раздел"
	)
	
statkb = [
	[
		types.KeyboardButton(text="👤 Пользователи"),
	], 
	[
		types.KeyboardButton(text="🔙 Назад"),
	],
	]
keyboard_stat = types.ReplyKeyboardMarkup(
		keyboard=statkb,
		resize_keyboard=True,
		input_field_placeholder="Выберите раздел"
	)
kuponkb = [
	[
		types.KeyboardButton(text="💲 Деньги"),
		types.KeyboardButton(text="📦 Товар"),
	], 
	[
		types.KeyboardButton(text="💯 Скидка"),
	],
	[
		types.KeyboardButton(text="⚙️ Генерация промокодов"),
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
generationkb = [
	[
		types.KeyboardButton(text="💲 Генерация на деньги"),
	], 
	[
		types.KeyboardButton(text="💯 Генерация на скидку"),
	],
	[
		types.KeyboardButton(text="📦 Генерация на товар"),
	],
	[
		types.KeyboardButton(text="🔙 Назад"),
	],
	]
keyboard_generation = types.ReplyKeyboardMarkup(
		keyboard=generationkb,
		resize_keyboard=True,
		input_field_placeholder="Выберите раздел"
	)