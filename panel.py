import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters import Text
from aiogram import types
from bs4 import BeautifulSoup
import requests
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
import random
from pyqiwip2p import QiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime, PaymentMethods
from datetime import datetime, date, time
import re
import string
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import keyboards_panel as kb
import config_panel as config
import db_config as db
from datetime import datetime, date, time
import time

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.token, parse_mode='html')
dp = Dispatcher()

conn= psycopg2.connect(user=db.user,
                                  # пароль, который указали при установке PostgreSQL
                                  password=db.password,
                                  host=db.host,
                                  port=db.port,
                                  database=db.database)
    # Курсор для выполнения операций с базой данных
cur = conn.cursor()




cur.execute("""CREATE TABLE IF NOT EXISTS product(
	id TEXT PRIMARY KEY,
	category TEXT,
	podcategory TEXT,
	name TEXT,
	description TEXT,
	price TEXT);
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS product_remains(
	id TEXT,
	product TEXT);
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS promocod_tovar(
	promocod TEXT,
	tovar TEXT);
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS promocod_money(
	promocod TEXT PRIMARY KEY,
	sum TEXT);
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS promocod_skidka(
	promocod TEXT,
	skidka TEXT);
""")

cur.execute("""CREATE TABLE IF NOT EXISTS prize_fortuna(
	category TEXT,
	promocod TEXT);
""")
conn.commit()

conn.commit()
class AdPromoMoney(StatesGroup):
	ad_promo_money = State() 
class AdPromoTovar(StatesGroup):
	ad_promo_tovar = State() 
class AdPromoSkidka(StatesGroup):
	ad_promo_skidka = State() 
class AdPromoTovar(StatesGroup):
	ad_promo_tovar = State() 
class AdCategory(StatesGroup):
	ad_category = State() 
class AdPodcategory(StatesGroup):
	ad_podcategory = State() 
class AdName(StatesGroup):
	ad_name = State()
class AdDescription(StatesGroup):
	ad_description = State()  
class AdPrice(StatesGroup):
	ad_price = State()  
class AdLinks(StatesGroup):
	ad_links = State()
class UpdLinks(StatesGroup):
	upd_links = State()    
class AddPrize(StatesGroup):
	add_prize = State()    
class GenMoney(StatesGroup):
	gen_money = State()  
class GenSkidka(StatesGroup):
	gen_skidka = State()  
class GenTovar(StatesGroup):
	gen_tovar = State()  
class JobUser(StatesGroup):
    cat2=State()
    job = State() 
    kod=State()
    but=State()
    qiwi=State()
    proverka=State()
    podcat=State()
def generate_random_string(length):
	letters = string.ascii_lowercase
	rand_string = ''.join(random.choice(letters) for i in range(length))
	print(rand_string)
	return rand_string

@dp.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
	if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
		await message.answer("Привет👋\n\n<b>Добро пожаловать в админ-панель магазина.</b> \n\n<em>Что будем делать?</em>", reply_markup=kb.keyboard_inital,  parse_mode="html")
	
	@dp.message(Text(text="📈 Статистика"))
	async def get_text_messages(message: types.Message):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			cur.execute('SELECT * FROM users ')
			user_info=cur.fetchall()
			conn.commit()
			cur.execute('SELECT * FROM pokupki ')
			pokupki_info=cur.fetchall()
			conn.commit()
			zarabotok=0
			for i in range(len(user_info)):
				zarabotok=zarabotok+float(user_info[i][1])
			print(user_info)
			print(zarabotok)
			zarabotok1=str(zarabotok)
			print(zarabotok1)
			await message.answer('👤 <b>Пользователей в боте: </b>'+str(len(user_info))+'\n💰 <b>Капитал магазина:</b> '+ str(zarabotok1) +' руб. '+'\n<b>📦 Всего покупок: </b> '+str(len(pokupki_info))+' \n  ⊢<b>Сегодня:</b> '+' \n  ⊢<b>Вчера:</b> '+' \n  ⊢<b>Неделя:</b> '+' \n  ⊢<b>Месяц:</b> '+' \n  ⊢<b>Квартрал:</b> '+' \n  ⊢<b>Год:</b> ',reply_markup=kb.keyboard_stat)
		
	@dp.message(Text(text="🔙 Назад"))
	async def get_text_messages(message: types.Message):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await message.answer("Привет👋\n\n<b>Добро пожаловать в админ-панель магазина.</b> \n\n<em>Что будем делать?</em>", reply_markup=kb.keyboard_inital,  parse_mode="html")

	@dp.message(Text(text="🏷️ Промокоды"))
	async def get_text_messages(message: types.Message):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await message.answer('🏷️<b>На что будем делать промокод?</b>',reply_markup=kb.keyboard_kupon)
	
	@dp.message(Text(text="📦 Товар"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await message.answer('📦<b>Что получит пользователь, когда ведёт промокод?</b>')
			await state.set_state(AdPromoTovar.ad_promo_tovar)
		
	@dp.message(state=AdPromoTovar.ad_promo_tovar)
	async def ad_category_text(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(ad_category=message.text)
			promo=generate_random_string(16)
			promo='T'+promo
			promo_tovar_add=((str(promo,),str(message.text)))
			cur.execute('INSERT INTO "promocod_tovar" VALUES (%s, %s)', promo_tovar_add)
			conn.commit()
			await message.answer('🏷️ <b>Вот промокод на товар:</b> '+'<pre>'+promo+'</pre>'+'\n<b>📦 Товар в промокоде: </b>\n'+message.text)
			await state.clear() 

	@dp.message(Text(text="💲 Деньги"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await message.answer('💲<b>Какой номинал промокода?</b>')
			await state.set_state(AdPromoMoney.ad_promo_money)
	
	@dp.message(state=AdPromoMoney.ad_promo_money)
	async def ad_category_text(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(ad_category=message.text)
			promo=generate_random_string(16)
			promo='M'+promo
			promo_tovar_add=((str(promo,),str(message.text)))
			cur.execute("INSERT INTO promocod_money VALUES (%s, %s)", promo_tovar_add)
			conn.commit()
			await message.answer('🏷️ <b>Вот промокод на деньги:</b> '+'<pre>'+promo+'</pre>'+'\n<b>💲 Номинал промокода: </b>\n'+message.text+' руб.')
			await state.clear() 
		
	@dp.message(Text(text="💯 Скидка"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await message.answer('💯 <b>Процент скидки?</b>')
			await state.set_state(AdPromoSkidka.ad_promo_skidka)
		
	@dp.message(state=AdPromoSkidka.ad_promo_skidka)
	async def ad_category_text(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(ad_category=message.text)
			promo=generate_random_string(16)
			promo='S'+promo
			promo_tovar_add=((str(promo,),str(message.text)))
			cur.execute('INSERT INTO "promocod_skidka" VALUES (%s, %s)', promo_tovar_add)
			conn.commit()
			await message.answer('🏷️ <b>Вот промокод на скидку:</b> '+'<pre>'+promo+'</pre>'+'\n<b>💯 Размер скидки: </b>'+message.text +' процентов')
			await state.clear() 

	@dp.message(Text(text="👤 Пользователи"))
	async def get_text_messages(message: types.Message):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			cur.execute('SELECT * FROM users ')
			user_info=cur.fetchall()
			conn.commit()
			for i in range(len(user_info)):
				await message.answer('<b>⚙ ID пользователя:</b> '+'<pre>'+str(user_info[i][0]+'</pre>'+'\n\n💰 <b>Баланс пользователя:</b> '+str(user_info[i][1])))
				time.sleep(1)
	@dp.message(Text(text="📦 Добавить новый товар"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await message.answer('🗃️<b> Какая категория товара?</b>\n\n<b>⚠️ Отменить ввод и перейти в главное меню: введи</b> "<pre>stop</pre>"')
			await state.set_state(AdCategory.ad_category)

	@dp.message(state=AdCategory.ad_category)
	async def ad_category_text(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(ad_category=message.text)
			if message.text=='stop':
				await message.answer("Привет👋\n\n<b>Добро пожаловать в админ-панель магазина.</b> \n\n<em>Что будем делать?</em>", reply_markup=kb.keyboard_inital,  parse_mode="html")
				return await state.clear()
			global category
			category=message.text
			await message.answer('Запомнил.\n\n<b>🗃️ Категория:</b> '+category+ '\n\n<em>Идём дальше.</em> \n\n🗃️ <b>Какая подкатегория?</b>\n\n<b>⚠️ Отменить ввод и перейти в главное меню: введи</b> "<pre>stop</pre>"')   
			await state.clear() 
			await state.set_state(AdPodcategory.ad_podcategory)
	
	@dp.message(state=AdPodcategory.ad_podcategory)
	async def ad_podcategory_text(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(ad_category=message.text)
			if message.text=='stop':
				await message.answer("Привет👋\n\n<b>Добро пожаловать в админ-панель магазина.</b> \n\n<em>Что будем делать?</em>", reply_markup=kb.keyboard_inital,  parse_mode="html")
				return await state.clear()
			global podcategory
			podcategory=message.text
			await message.answer('Запомнил.\n\n<b>🗃️ Категория:</b> '+category+ '\n\n<b>🗃️ Подкатегория:</b> '+podcategory+ '\n\n<em>Идём дальше.</em> \n\n📝 <b>Как назовем товар?</b>\n\n<b>⚠️ Отменить ввод и перейти в главное меню: введи</b> "<pre>stop</pre>"')   
			await state.clear() 
			await state.set_state(AdName.ad_name)

	@dp.message(state=AdName.ad_name)
	async def ad_name(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(ad_name=message.text)
			if message.text=='stop':
				await message.answer("Привет👋\n\n<b>Добро пожаловать в админ-панель магазина.</b> \n\n<em>Что будем делать?</em>", reply_markup=kb.keyboard_inital,  parse_mode="html")
				return await state.clear()
			global name
			name=message.text
			await message.answer('Запомнил.\n\n<b>🗃️ Категория:</b> '+category+ '\n\n<b>🗃️ Подкатегория:</b> '+podcategory+ '\n\n<b>📝 Название:</b> '+name+'\n\n<em>Идём дальше.</em> \n\n✏️ <b>Какое описание товара?</b>\n\n<b>⚠️ Отменить ввод и перейти в главное меню: введи</b> "<pre>stop</pre>"')   
			await state.clear()
			await state.set_state(AdDescription.ad_description)

	@dp.message(state=AdDescription.ad_description)
	async def ad_description(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(ad_description=message.text)
			if message.text=='stop':
				await message.answer("Привет👋\n\n<b>Добро пожаловать в админ-панель магазина.</b> \n\n<em>Что будем делать?</em>", reply_markup=kb.keyboard_inital,  parse_mode="html")
				return await state.clear()
			global description
			description=message.text
			await message.answer('Запомнил.\n\n<b>🗃️ Категория:</b> '+category+ '\n\n<b>🗃️ Подкатегория:</b> '+podcategory+ '\n\n<b>📝 Название:</b> '+name+'<b>\n\n✏️ Описание:</b> '+description+'\n\n<em>Идём дальше.</em> \n\n💰​ <b>Сколько будет стоить?</b>\n\n<b>⚠️ Отменить ввод и перейти в главное меню: введи</b> "<pre>stop</pre>"')   
			await state.clear()
			await state.set_state(AdPrice.ad_price)

	@dp.message(state=AdPrice.ad_price)
	async def ad_price(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(ad_price=message.text)
			if message.text=='stop':
				await message.answer("Привет👋\n\n<b>Добро пожаловать в админ-панель магазина.</b> \n\n<em>Что будем делать?</em>", reply_markup=kb.keyboard_inital,  parse_mode="html")
				await state.clear()
			global price
			price=message.text
			await message.answer('Запомнил.\n\n<b>🗃️ Категория:</b> '+category+ '\n\n<b>🗃️ Подкатегория:</b> '+podcategory+ '\n\n<b>📝 Название:</b> '+name+'<b>\n\n✏️ Описание:</b> '+description+'\n\n<b>💰​ Стоимость:</b> '+price+'\n\n<em>Идём дальше.</em> \n\n🌐 <b>Отправь файл с товарами\nили сообщение, где товары разделены знаком ";"</b>\n\n<b>⚠️ Отменить ввод и перейти в главное меню: введи</b> "<pre>stop</pre>"')   
			await state.clear()
			await state.set_state(AdLinks.ad_links)

	@dp.message(content_types=types.ContentType.ANY,state=AdLinks.ad_links)
	async def ad_links(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(ad_links=message.text)
			if message.text=='stop':
				await message.answer("Привет👋\n\n<b>Добро пожаловать в админ-панель магазина.</b> \n\n<em>Что будем делать?</em>", reply_markup=kb.keyboard_inital,  parse_mode="html")
				return await state.clear()
			global links
			conn.commit()
			ids=(str(random.randint(1,1000000)))
			print(ids)
			tovar=((ids),(category),(podcategory),(name),(description),(price))
			print(tovar)
			post_jobs = []
			if message.document:
				print("downloading document")
				file_id = message.document.file_id
				file = await bot.get_file(file_id)
				await bot.download_file(file.file_path, "tovar.txt")
				print('Успешно')
				file1 = open("tovar.txt", "r")
				while True:
					line = file1.readline()
					if not line:
						break
					post_jobs.append(line.strip())
				print('Вот товары: ')
				print(post_jobs)
				links=' '
				for i in range(len(post_jobs)):
					product_tabble=(ids,post_jobs[i])
					cur.execute('INSERT INTO product_remains VALUES (%s,%s)', (product_tabble))
					conn.commit()
					print('Добавил товар: '+post_jobs[i])
					links=links+'\n'+post_jobs[i]
			if message.text:
				post_jobs=message.text.split(";")
				print(post_jobs)
				links=''
				for i in range(len(post_jobs)):
					product_tabble=(ids,post_jobs[i])
					cur.execute('INSERT INTO product_remains VALUES (%s,%s)', (product_tabble))
					conn.commit()
					print('Добавил товар: '+post_jobs[i])
					links=links+'\n'+post_jobs[i]
			cur.execute("INSERT INTO product VALUES (%s, %s, %s, %s, %s, %s)", tovar)
			conn.commit()
			await message.answer('Запомнил.\n\n<b>🗃️ Категория:</b> '+category+'\n\n<b>🗃️ Подкатегория:</b> '+podcategory+'\n\n<b>📝 Название:</b> '+name+'<b>\n\n✏️ Описание:</b> '+description+'\n\n<b>💰​ Стоимость:</b> '+price+'\n\n🌐 <b>Товары:\n\n</b>'+links+'\n\n<b>✅ Товар добавлен!</b>')   
			await state.clear()
	
	@dp.message(Text(text="📝 Редактирование товаров"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(jobs=message.text)
			user_ids=message.from_user.id
			print('Вот ID: '+ str(user_ids))
			cur.execute("SELECT * FROM product;")
			all_results = cur.fetchall()
			kol=len(all_results)
			cat=[]
			for i in range(kol):
				print(all_results[i][1])
				cat1=all_results[i][1]
				cat.append(cat1)
			ints_list1 = list(set(cat))
			print(ints_list1)

			kolvo=len(ints_list1)
			markup =InlineKeyboardBuilder() # создаём клавиатуру
			markup.row(width=1)
			menu=markup.add(*[InlineKeyboardButton(text=ints_list1[x], callback_data=str(ints_list1[x])) for x in range(kolvo)]) #Создаём кнопки, i[1] - название, i[2] - каллбек дата	
			markup2= menu.adjust(2).as_markup()
			msg = await message.answer('📖 <b>Выбери нужный раздел:</b>', reply_markup=markup2)
			await state.clear()
			return await state.set_state(JobUser.kod)
	
	@dp.callback_query(state=JobUser.kod)
	async def stoptopupcall(callback_query: types.CallbackQuery, state: FSMContext):
		if str(callback_query.from_user.id)=='567660912'or str(callback_query.from_user.id)=='733672052':
			cur.execute('SELECT * FROM product WHERE category = %s', (callback_query.data, ))
			all_results = cur.fetchall()
			kol=len(all_results)
			cat=[]
			for i in range(kol):
				print(all_results[i][2])
				cat1=all_results[i][2]
				cat.append(cat1)
			ints_list1 = list(set(cat))
			kolvo=len(ints_list1)
			print('Вот подкатегории:'+str(ints_list1))
			user_ids=callback_query.from_user.id
			print('Вот ID: '+ str(user_ids))
			cur.execute('SELECT * FROM product WHERE category = %s', (callback_query.data, ))
			tovarinfo = cur.fetchall()
			print(tovarinfo)
			kolvo2=len(tovarinfo)
			markup3 =InlineKeyboardBuilder() # создаём клавиатуру
			markup3.row(width=1)
			menu2=markup3.add(*[InlineKeyboardButton(text=ints_list1[x], callback_data=str(ints_list1[x])) for x in range(kolvo)]) #Создаём кнопки, i[1] - название, i[2] - каллбек дата	
			markup3= menu2.adjust(2).as_markup()
			keyboard2 = InlineKeyboardBuilder.as_markup(menu2)
			global msg1
			msg1 = await callback_query.message.answer('📖 <b>Выбери подкатегорию:</b>', reply_markup=markup3)
			await callback_query.answer()
			await state.clear()
			return await state.set_state(JobUser.podcat)
	
	@dp.callback_query(state=JobUser.podcat)
	async def stoptopupcall(callback_query: types.CallbackQuery, state: FSMContext):
		if str(callback_query.from_user.id)=='567660912'or str(callback_query.from_user.id)=='733672052':
			user_ids=callback_query.from_user.id
			print('Вот ID: '+ str(user_ids))
			cur.execute('SELECT * FROM product WHERE podcategory = %s', (callback_query.data, ))
			tovarinfo = cur.fetchall()
			print(tovarinfo)
			kolvo2=len(tovarinfo)
			markup3 =InlineKeyboardBuilder() # создаём клавиатуру
			markup3.row(width=1)
			menu2=markup3.add(*[InlineKeyboardButton(text=tovarinfo[x][3], callback_data=str(tovarinfo[x][0])) for x in range(kolvo2)]) #Создаём кнопки, i[1] - название, i[2] - каллбек дата	
			markup3= menu2.adjust(2).as_markup()
			keyboard2 = InlineKeyboardBuilder.as_markup(menu2)
			global msg1
			msg1 = await callback_query.message.answer('📖 <b>Выбери товар:</b>', reply_markup=markup3)
			await callback_query.answer()
			await state.clear()
			return await state.set_state(JobUser.job)
	
	@dp.callback_query(state=JobUser.job)
	async def stoptopupcall(callback_query: types.CallbackQuery, state: FSMContext):
		if str(callback_query.from_user.id)=='567660912'or str(callback_query.from_user.id)=='733672052':
			await state.update_data(jobs=callback_query.data)
			user_ids=callback_query.from_user.id
			global tab_name
			tab_name=callback_query.data
			print('Вот ID: '+ str(user_ids))
			global tovarinfo1
			cur.execute('SELECT * FROM product WHERE id = %s', (str(callback_query.data), ))
			tovarinfo1=cur.fetchone()
			print(callback_query.data)
			print(tovarinfo1)
			markup_buy =InlineKeyboardBuilder() # создаём клавиатуру
			cur.execute('SELECT * FROM product_remains WHERE id = %s', (str(tovarinfo1[0]), ))
			tovary5= cur.fetchall()
			kolvo_tovarov=(len(tovary5))
			button_buy=markup_buy.add(InlineKeyboardButton(text='❌ Удалить', callback_data='delete_tovar'))#Создаём кнопки, i[1] - название, i[2] - каллбек дата	
			button_buy=markup_buy.add(InlineKeyboardButton(text='📲 Добавить', callback_data='add_link'))#Создаём кнопки, i[1] - название, i[2] - каллбек дата	
			buy_kb= button_buy.adjust(2).as_markup()
			await callback_query.message.answer(f'<b>📝 Название:</b> {tovarinfo1[3]}\n\n<b>✏️ Описание:</b>{tovarinfo1[4]}\n\n<b>📦 Остаток:</b>{str(kolvo_tovarov)} шт.\n\n<b>📄 Товары: \n</b>{str(tovary5)}',reply_markup=buy_kb)
			await callback_query.answer()
			await state.clear()
			return await state.set_state(JobUser.but)
	@dp.callback_query(state=JobUser.but)
	async def stoptopupcall(callback_query: types.CallbackQuery, state: FSMContext):
		if str(callback_query.from_user.id)=='567660912'or str(callback_query.from_user.id)=='733672052':
			await state.update_data(jobs=callback_query.data)
			if callback_query.data=='delete_tovar':
				#tab_info = cur.execute('SELECT * FROM shop WHERE name = ?', (str(tab_name), )).fetchone()
				cur.execute('DELETE from product WHERE id = %s', (str(tab_name), ))
				conn.commit()
				await callback_query.message.answer('❌ <b>Товар удален</b>')
				await callback_query.answer()
				return await state.set_state(JobUser.but)
			if callback_query.data=='add_link':
				await callback_query.message.answer('<b>📝 Отправь файл с товарами в формате txt \nили сообщение, разделив товары символом: ";"</b>')
				await callback_query.answer()
				return await state.set_state(UpdLinks.upd_links)
	
	@dp.message(content_types=types.ContentType.ANY, state=UpdLinks.upd_links)
	async def upd_links(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912'or str(message.from_user.id)=='733672052':
			await state.update_data(upd_links=message.text)
			if message.document:
				file_id = message.document.file_id
				file = await bot.get_file(file_id)
				await bot.download_file(file.file_path, "tovar.txt")
				post_jobs = []
				file1 = open("tovar.txt", "r")

				while True:
					line = file1.readline()
					if not line:
						break
					post_jobs.append(line.strip())
				for i in range(len(post_jobs)):
					product_tabble=(tovarinfo1[0],post_jobs[i])
					cur.execute('INSERT INTO product_remains VALUES (%s,%s)', (product_tabble))
					conn.commit()
					print('Добавил товар: '+post_jobs[i])

				await message.answer('<b>Добавлено ✅</b>')
				print(post_jobs)
			if message.text:
				post_jobs=message.text.split(";")
				print(post_jobs)
				for i in range(len(post_jobs)):
					product_tabble=(tovarinfo1[0],post_jobs[i])
					cur.execute('INSERT INTO product_remains VALUES (%s,%s)', (product_tabble))
					conn.commit()
					print('Добавил товар: '+post_jobs[i])
				await message.answer('<b>Добавлено ✅</b>')
	
	@dp.message(Text(text="⚙️ Генерация промокодов"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		await message.answer('<b>❓ На что генерируем промокоды?</b>\n\n⚙️ <em>Когда нажмешь на одну из кнопок ниже, сгененируется промокоды определенной категории </em>', reply_markup=kb.keyboard_generation)
	
	@dp.message(Text(text="💲 Генерация на деньги"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		await message.answer('<b>❓ На какую сумму генерируем промокоды?</b> \n\n Введи сумму промокода (интервал) и количество промокодов через пробел.\n\n<em>Например: 5 10 50. Бот создаст 50 промокодов с суммой от 5 до 10</em>')
		return await state.set_state(GenMoney.gen_money)
	
	@dp.message(state=GenMoney.gen_money)
	async def gen_money(message: types.Message, state: FSMContext):	
		sum_promicaA=message.text.split()[0]
		sum_promicaB=message.text.split()[1]
		kolvo_promicov=message.text.split()[2]
		promici=''
		for i in range(int(kolvo_promicov)):
			promo=generate_random_string(16)
			promo='M'+promo
			promici=promici+promo+'\n'
			sum_promica=random.randint(int(sum_promicaA), int(sum_promicaB))
			promo_money_add=((str(promo,),str(sum_promica)))
			cur.execute("INSERT INTO promocod_money VALUES (%s, %s)", promo_money_add)
			conn.commit()
			fortuna_money_add=(('money'),str(promo,))
			cur.execute("INSERT INTO prize_fortuna VALUES (%s, %s)", fortuna_money_add)
			conn.commit()
		await message.answer('➕ <b>Добавил в базу:</b> \n' + promici)	

	@dp.message(Text(text="💯 Генерация на скидку"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		await message.answer('<b>❓ На какую скидку генерируем промокоды?</b> \n\n Введи скидку промокода и количество промокодов через пробел.\n\n<em>Например: 10 50</em>')
		return await state.set_state(GenSkidka.gen_skidka)
	
	@dp.message(state=GenSkidka.gen_skidka)
	async def gen_money(message: types.Message, state: FSMContext):	
		skidka_promica=message.text.split()[0]
		kolvo_promicov=message.text.split()[1]
		promici=''
		for i in range(int(kolvo_promicov)):
			promo=generate_random_string(16)
			promo='S'+promo
			promici=promici+promo+'\n'
			promo_skidka_add=((str(promo,),str(skidka_promica)))
			cur.execute("INSERT INTO promocod_skidka VALUES (%s, %s)", promo_skidka_add)
			conn.commit()
			fortuna_skidka_add=(('skidka'),str(promo,))
			cur.execute("INSERT INTO prize_fortuna VALUES (%s, %s)", fortuna_skidka_add)
			conn.commit()
		await message.answer('➕ <b>Добавил в базу:</b> \n' + promici)	

	@dp.message(Text(text="📦 Генерация на товар"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		await message.answer('<b>📁 Отправь файл с товарами и я из них сделаю промокоды</b>')
		return await state.set_state(GenTovar.gen_tovar)

	@dp.message(content_types=types.ContentType.ANY,state=GenTovar.gen_tovar)
	async def gen_tovar(message: types.Message, state: FSMContext):	
		post_jobs = []
		if message.document:
			print("downloading document")
			file_id = message.document.file_id
			file = await bot.get_file(file_id)
			await bot.download_file(file.file_path, "promo_tovar.txt")
			print('Успешно')
			file1 = open("promo_tovar.txt", "r")
			while True:
				line = file1.readline()
				if not line:
					break
				post_jobs.append(line.strip())
			print('Вот товары: ')
			print(post_jobs)
			links=' '
			promici=''
			for i in range(len(post_jobs)):
				promo=generate_random_string(16)
				promo='T'+promo
				promici=promici+promo+'\n'
				promo_tovar_add=((str(promo,),str(post_jobs[i])))
				cur.execute("INSERT INTO promocod_tovar VALUES (%s, %s)", promo_tovar_add)
				conn.commit()
				fortuna_tovar_add=(('tovar'),str(promo,))
				cur.execute("INSERT INTO prize_fortuna VALUES (%s, %s)", fortuna_tovar_add)
				conn.commit()
			await message.answer('➕ <b>Добавил в базу:</b> \n' + promici)	
async def main():
    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())