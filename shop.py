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
from datetime import timedelta
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import re
import keyboards_shop as kb
import config_shop as config
import db_config as db
import traceback
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

QIWI_PRIV_KEY = config.qiwi_token

p2p = QiwiP2P(auth_key=QIWI_PRIV_KEY)

balance_chanel_id=config.balance
pokupka_chanel_id=config.pokupka
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token, parse_mode='html')
dp = Dispatcher()
conn= psycopg2.connect(user=db.user,
                                  # пароль, который указали при установке PostgreSQL
                                  password=db.password,
                                  host=db.host,
                                  port=db.port,
                                  database=db.database)
    # Курсор для выполнения операций с базой данных
cur = conn.cursor()
image = URLInputFile(
    config.image_link,
    filename=config.image_name
    )
class JobUser(StatesGroup):
    cat2=State()
    job = State() 
    kod=State()
    but=State()
    qiwi=State()
    proverka=State()
    podcat=State()
    rass=State()
    popolid=State()
    mesid=State()
    mesmes=State()
    proverpodpis=State()

class AdBalance(StatesGroup):
	ad_balance = State() 
class AdPromoMoney(StatesGroup):
	ad_promo_money = State() 
class AdPromoTovar(StatesGroup):
	ad_promo_tovar = State() 
class AdFortuna(StatesGroup):
	fortuna = State() 
cur.execute("""CREATE TABLE IF NOT EXISTS users(
	id TEXT PRIMARY KEY,
	balance INT,
	referer TEXT);
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS referals(
	id TEXT PRIMARY KEY,
	referer TEXT);
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS fortuna(
	id TEXT,
	data TEXT);
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS skidka(
	id TEXT,
	skidka TEXT);
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS pokupki(
		id TEXT,
		name_pokupka TEXT,
		tovar TEXT,
		summa TEXT,
		data TEXT);
		""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS popolneniya(
		id TEXT,
		id_platech TEXT,
		summa TEXT,
		data TEXT);
		""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS zarabotok(
			id_referera TEXT,
			id_referala TEXT,
			dohod TEXT,
			data TEXT,
			opisanie TEXT);
			""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS qiwi(
		id TEXT,
		balik TEXT,
		bils TEXT,
		new_bill TEXT,
		status TEXT,
		url_check TEXT);
		""")
conn.commit()
def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"
async def proveka_platezhek(dp: Dispatcher):
	cur.execute('SELECT * FROM qiwi')
	info_pay=cur.fetchall()
	if len(info_pay)>0:
		for i in range(len(info_pay)):
			print('Есть платежка от: ' + info_pay[i][0])
			balik=info_pay[i][1]
			bils=info_pay[i][2]
			url_check=info_pay[i][5]
			if len(info_pay)>0:
				status=p2p.check(bill_id=bils).status
				print(status)
				if status =='PAID':
					print(status)
					cur.execute('SELECT * FROM users WHERE id = %s', (str(info_pay[i][0]), ))
					user_info = cur.fetchone()
					conn.commit()
					bal=user_info[1]
					bal=float(user_info[1])
					bal=float(bal)+int(balik)
					us_b=(info_pay[i][0],bal)
					sql = """UPDATE users SET balance = %s WHERE id = %s"""
					cur.execute(sql, (float(bal),str(info_pay[i][0])))
					conn.commit()
					data_popolneniya=datetime.now()
					popolneniya_info=(str(user_ids),str(bils),str(balik),str(data_popolneniya))
					await bot.send_message(info_pay[i][0],'<b>➕ Вижу пополнение на сумму:</b> ' + str(balik) + '\n\n💰​ <b>Текущий баланс:</b> '+ str(toFixed(bal,2))+'\n\n<em>😎 За покупками?</em>')
					cur.execute('INSERT INTO popolneniya VALUES (%s, %s, %s, %s)', popolneniya_info)
					conn.commit()
					await bot.send_message(balance_chanel_id,'<b>Пополнение баланса ✅</b>\n\nПользователь: \n<b>🔐 ID</b>: '+str(info_pay[i][0])+'\n<b>⚙ ID платежа:</b> '+str(bils)+'\n<b>💰​Сумма:</b> '+str(balik)+' руб.')
					cur.execute('DELETE FROM qiwi WHERE bils = %s', (str(info_pay[i][2]),))
					conn.commit()
					
					print(status)
				if status == 'EXPIRED':
					await bot.send_message(info_pay[i][0],'<b>❌ Платёж с уникальным идентификатором: </b>'+str(bils)+' был отменен. \n\n<b>Причина:</b> <em>истёк срок, за который нужно было оплатить.</em>')
					cur.execute('DELETE FROM qiwi WHERE bils = %s', (str(info_pay[i][2]),))
					conn.commit()
		
	else:		
		print('Нет платежек')
scheduler.add_job(proveka_platezhek, "interval", seconds=10, args=(dp,))


@dp.message(Command(commands=["start"]))
async def command_start_handler(message: Message, state: FSMContext) -> None:
	try:
		users1=((str(message.from_user.id)),('1'),('no referer'))
		cur.execute("INSERT INTO users VALUES (%s, %s, %s)ON CONFLICT  (id) DO NOTHING", users1)
		conn.commit()
		user_channel_status = await bot.get_chat_member(chat_id=config.channel_popdiska, user_id=message.chat.id)
		user_channel_status = re.findall(r"\w*", str(user_channel_status))
		print(user_channel_status[3])
		if user_channel_status[3] == 'left':
			def get_keyboard1():
				buttons1 = [
				[
					types.InlineKeyboardButton(text="📲 Подписаться", callback_data="popdisatsa", url='https://t.me/gandalf_news')
				],
				[
					types.InlineKeyboardButton(text="♻️ Проверить подписку", callback_data="proveritpodpis")
				],
				]
				keyboard1 = types.InlineKeyboardMarkup(inline_keyboard=buttons1)
				return keyboard1

			await message.answer('<b>🫵 Ты не пройдешь!</b> \n\n<em>(если не подпишешься на канал)</em>\n\n<b>🚪 Подпишись на канал и двери в лавку Гэндальфа откроются</b>',reply_markup=get_keyboard1())  #Пользователь не подписан
			await state.set_state(JobUser.proverpodpis)
		else:
			cur.execute('SELECT * FROM skidka WHERE id = %s', (str(message.from_user.id), ))
			user_skidka_info=cur.fetchone()
			conn.commit()
			await bot.send_photo(message.from_user.id, image, caption="<b>🏠 Приветствую, странник!\n\n🧙 Ты находишься в лавке Гэндальфа</b>\n\n🗃️ Здесь собрано огромное количество цифровых товаров, среди которых каждый сможет найти то, что нужно!\n\n <b>😎 На все товары распространяется гарантия. </b>\n\n<b>🤫 Все сделки проходят на условиях полной конфиденциальности. </b>", reply_markup=kb.keyboard_inital,  parse_mode="html")
			if user_skidka_info!=None:
				await message.answer('<b>❗ У вас активна скидка </b>'+'<pre>'+user_skidka_info[1]+' процентов '+'</pre>'+'<b>на одну покупку</b>')
	except:
		await bot.send_message(config.error,('<b>❗Ошибка при запуске бота❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(message.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(message.from_user.username)+'</pre>'))	

	@dp.callback_query(state=JobUser.proverpodpis)
	async def stoptopupcall(callback_query: types.CallbackQuery, state: FSMContext):
		try:
			print(1)
			if callback_query.data=='proveritpodpis':
				user_channel_status = await bot.get_chat_member(chat_id=config.channel_popdiska, user_id=callback_query.from_user.id)
				user_channel_status = re.findall(r"\w*", str(user_channel_status))
				print(user_channel_status[3])
				if user_channel_status[3] == 'left':
					await bot.send_message(callback_query.from_user.id, '❌ <b>Ты еще не подписался</b>')  #Пользователь не подписан
					await callback_query.answer()
				else:
					cur.execute('SELECT * FROM skidka WHERE id = %s', (str(callback_query.from_user.id), ))
					user_skidka_info=cur.fetchone()
					conn.commit()
					await bot.send_photo(callback_query.from_user.id, image, caption="<b>🏠 Приветствую, странник!\n\n🧙 Ты находишься в лавке Гэндальфа</b>\n\n🗃️ Здесь собрано огромное количество цифровых товаров, среди которых каждый сможет найти то, что нужно!\n\n <b>😎 На все товары распространяется гарантия. </b>\n\n<b>🤫 Все сделки проходят на условиях полной конфиденциальности. </b>", reply_markup=kb.keyboard_inital,  parse_mode="html")
					if user_skidka_info!=None:
						await message.answer('<b>❗ У вас активна скидка </b>'+'<pre>'+user_skidka_info[1]+' процентов '+'</pre>'+'<b>на одну покупку</b>')
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при проверке подписки на канал❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(callback_query.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(callback_query.from_user.username)+'</pre>'))	
	try:
		user_id = message.from_user.id
		referrer = None
		if " " in message.text:
			user_id=str(user_id)
			referrer_candidate = message.text.split()[1]
			cur.execute('SELECT * FROM users WHERE id = %s', (user_id, ))
			referer_results = cur.fetchone()
			print(len(referer_results))
			if referer_results[2]=='no referer' and str(referrer_candidate)!=str(message.from_user.id):
				datas=datetime.now()
				refererals_add_table=((str(message.from_user.id,),str(referrer_candidate)))
				zar='5'
				opisan='Приглашение в систему'
				zarobotok_table=(str(referrer_candidate),str(message.from_user.id),zar,str(datas),opisan)
				sql2 = """UPDATE users SET referer = %s WHERE id = %s"""
				cur.execute(sql2, (referrer_candidate,user_id))
				conn.commit()
				cur.execute('INSERT into referals VALUES (%s, %s)', refererals_add_table)
				conn.commit()
				cur.execute('INSERT into zarabotok VALUES (%s, %s, %s, %s, %s)', zarobotok_table)
				conn.commit()
				cur.execute('SELECT * FROM users WHERE id = %s', (str(referrer_candidate), ))
				balanceinfo=cur.fetchone()
				conn.commit()
				raznica=float(balanceinfo[1]) + 5
				sql = """UPDATE users SET balance = %s WHERE id = %s"""
				cur.execute(sql, (raznica,referrer_candidate))
				conn.commit()
				await bot.send_message(referrer_candidate, ('<b>➕ К вам присоединился реферал с ID:' +str(message.from_user.id)+'</b>\n\n<b>💰 На ваш счёт зачислено 5 рублей</b>'))
				await message.answer('<b>👤 Вас пригласил: </b>'+str(referrer_candidate))
	except:
		await bot.send_message(config.error,('<b>❗Ошибка при добавлении реферала❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'))	
	user_ids=message.from_user.id
	conn.commit()

	async def send_message(channel_id: int, text: str):
		await bot.send_message(channel_id, text)
		return await state.set_state(JobUser.cat2)
	
	@dp.message(Text(text="📖 Лавка", state=JobUser.cat2))
	async def get_text_messages(message: types.Message, state: FSMContext):
		try:
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
			global markup_glav
			markup_glav= menu.adjust(2).as_markup()
			msg = await message.answer('📖 <b>Выбери нужный раздел:</b>', reply_markup=markup_glav)
			await state.clear()
			return await state.set_state(JobUser.kod)
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при открытии категорий❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(message.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(message.from_user.username)+'</pre>'))
	
	@dp.callback_query(state=JobUser.kod)
	async def stoptopupcall(callback_query: types.CallbackQuery, state: FSMContext):
		try:		
			await callback_query.message.delete()
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
			tovarinfo=cur.fetchall()
			print(tovarinfo)
			kolvo2=len(tovarinfo)
			global markuppodcat
			markuppodcat =InlineKeyboardBuilder() # создаём клавиатуру
			menu2=markuppodcat.add(*[InlineKeyboardButton(text=ints_list1[x], callback_data=str(ints_list1[x])) for x in range(kolvo)]) #Создаём кнопки, i[1] - название, i[2] - каллбек дата	
			menu2=(markuppodcat.add(InlineKeyboardButton(text='🔙 Назад', callback_data='nazad')))	
			markuppodcat= menu2.adjust(2).as_markup()
			keyboard2 = InlineKeyboardBuilder.as_markup(menu2)
			msg1 = await callback_query.message.answer('📖 <b>Выбери подкатегорию:</b>', reply_markup=markuppodcat)
			await callback_query.answer()
			await state.clear()
			return await state.set_state(JobUser.podcat)
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при проверке подписки на канал❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(callback_query.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(callback_query.from_user.username)+'</pre>'))	
	@dp.callback_query(state=JobUser.podcat)
	async def stoptopupcall(callback_query: types.CallbackQuery, state: FSMContext):
		try:
			await callback_query.message.delete()
			if callback_query.data=='nazad':
				await callback_query.message.answer('📖 <b>Выбери нужный раздел:</b>', reply_markup=markup_glav)
				return await state.set_state(JobUser.kod)
			print('Вот ID: '+ str(user_ids))
			cur.execute('SELECT * FROM product WHERE podcategory = %s', (callback_query.data, ))
			tovarinfo = cur.fetchall()
			print(tovarinfo)
			kolvo2=len(tovarinfo)
			global markuptovar
			markuptovar =InlineKeyboardBuilder() # создаём клавиатуру
			menu2=markuptovar.add(*[InlineKeyboardButton(text=tovarinfo[x][3], callback_data=str(tovarinfo[x][0])) for x in range(kolvo2)]) #Создаём кнопки, i[1] - название, i[2] - каллбек дата	
			menu2=(markuptovar.add(InlineKeyboardButton(text='🔙 Назад', callback_data='nazad')))
			markuptovar= menu2.adjust(1).as_markup()
			keyboard2 = InlineKeyboardBuilder.as_markup(menu2)
			msg1 = await callback_query.message.answer('📖 <b>Выбери товар:</b>', reply_markup=markuptovar)
			await callback_query.answer()
			await state.clear()
			return await state.set_state(JobUser.job)
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при открытии товаров❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(callback_query.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(callback_query.from_user.username)+'</pre>'))	

	@dp.callback_query(state=JobUser.job)
	async def stoptopupcall(callback_query: types.CallbackQuery, state: FSMContext):
		try:	
			await state.update_data(jobs=callback_query.data)
			user_ids=callback_query.from_user.id
			if callback_query.data=='nazad':
				await callback_query.message.answer('📖 <b>Выбери товар:</b>', reply_markup=markuppodcat)
				return await state.set_state(JobUser.podcat)
			print('Вот ID: '+ str(user_ids))
			cur.execute('SELECT * FROM product WHERE id = %s', (str(callback_query.data), ))
			tovarinfo1 = cur.fetchone()
			print(callback_query.data)
			print(tovarinfo1)
			markup_buy =InlineKeyboardBuilder() # создаём клавиатуру
			cur.execute('SELECT * FROM product_remains WHERE id = %s', (str(tovarinfo1[0]), ))
			tovary5= cur.fetchall()
			cena_tovara=float(tovarinfo1[5])
			cur.execute('SELECT * FROM skidka WHERE id = %s', (str(callback_query.from_user.id), ))
			user_skidka_info=cur.fetchone()
			conn.commit()
			if user_skidka_info!=None:
				skidka_na_tovar=float(user_skidka_info[1])
				raz_cena_tovara=(cena_tovara/100)*skidka_na_tovar
				cena_tovara=cena_tovara-raz_cena_tovara
				kolvo_tovarov=(len(tovary5))
				button_buy=markup_buy.add(InlineKeyboardButton(text='💰​ Со скидкой | '+str(toFixed(cena_tovara,2))+' рублей | Наличие: '+str(kolvo_tovarov)+' шт.', callback_data=str(tovarinfo1[0])))#Создаём кнопки, i[1] - название, i[2] - каллбек дата	
			else:
				kolvo_tovarov=(len(tovary5))
				button_buy=markup_buy.add(InlineKeyboardButton(text='💰​ Купить | '+str(cena_tovara)+' рублей | Наличие: '+str(kolvo_tovarov)+' шт.', callback_data=str(tovarinfo1[0])))#Создаём кнопки, i[1] - название, i[2] - каллбек дата	
			
			if len(tovary5)==0:
				await callback_query.message.answer('<b>😞 Товара нет в наличии</b>\n\n<em>Но мы уже знаем об этом и скоро пополним запасы</em> 😎')
				await callback_query.answer()
				await state.clear()
				return await state.set_state(JobUser.job)
			if len(tovary5)>0:
				buy_kb= button_buy.adjust(1).as_markup()
				await callback_query.message.answer(f'<b>📝 Название:</b> {tovarinfo1[3]}\n\n<b>✏️ Описание:</b>{tovarinfo1[4]}',reply_markup=buy_kb)
				await callback_query.answer()
				await state.clear()
				return await state.set_state(JobUser.but)
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при открытии информации о товаре❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(callback_query.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(callback_query.from_user.username)+'</pre>'))	
	
	@dp.callback_query(state=JobUser.but)
	async def stoptopupcall(callback_query: types.CallbackQuery, state: FSMContext):
		try:
			await state.update_data(jobs=callback_query.data)

			cur.execute('SELECT * FROM skidka WHERE id = %s', (str(callback_query.from_user.id), ))
			user_skidka_info=cur.fetchone()
			conn.commit()
			user_ids=callback_query.from_user.id
			print('Вот ID: '+ str(user_ids))
			cur.execute('SELECT * FROM product WHERE id = %s', (str(callback_query.data), ))
			tovarinfo1 = cur.fetchone()
			conn.commit()
			cena_tovara=float(tovarinfo1[5])
			if user_skidka_info!=None:
				skidka_na_tovar=float(user_skidka_info[1])
				raz_cena_tovara=(cena_tovara/100)*skidka_na_tovar
				cena=cena_tovara-raz_cena_tovara
				cur.execute('DELETE FROM skidka WHERE id = %s', (str(callback_query.from_user.id),))
				conn.commit()
			else:
				cena=tovarinfo1[5]
			print('Вот стоимость товара: '+ str(cena))
			cur.execute('SELECT * FROM users WHERE id = %s', (str(user_ids), ))
			balanceinfo=cur.fetchone()
			conn.commit()
			print('Вот баланс пользователя: '+str(balanceinfo[1]))
			cur.execute('SELECT * FROM product_remains WHERE id = %s', (str(tovarinfo1[0]), ))

			tovary= cur.fetchone()
			print(tovary)
			print(len(tovary))
			datas=datetime.now()
			if float(balanceinfo[1]) >= float(cena):
				print(float(balanceinfo[1]) - float(cena))
				raznica=float(balanceinfo[1]) - float(cena)
				sql = """UPDATE users SET balance = %s WHERE id = %s"""
				cur.execute(sql, (raznica,str(user_ids)))
				conn.commit()
				tovik=str(tovary[1])
				print(tovik)
				await callback_query.message.answer('<b>Успешно!</b>\n\n📦 <b>Вот товар:</b>\n'+'<pre>'+tovik+'</pre>'+'\n\n<b>💰​ Текущий баланс: </b>'+str(raznica))
				await callback_query.message.answer('🧙 Положительные отзывы от таких чудесных клиентов как вы помогают другим людям чувствовать себя уверенно при выборе <b>Gandalf store</b>. \n\nНе могли бы вы потратить 60 секунд, чтобы <b>нажать на кнопку и поделиться своим успешным опытом?</b> ',reply_markup=kb.get_otzyv())
				cur.execute('DELETE FROM product_remains WHERE product = %s', (str(tovary[1]),))
				conn.commit()
				pokupka_info=((user_ids),(tovarinfo1[3]),(str(tovary[0])),(cena),(str(datas)))
				print(pokupka_info)
				cur.execute('INSERT INTO pokupki VALUES (%s, %s, %s, %s, %s)', pokupka_info)
				conn.commit()
				cur.execute('SELECT * FROM users WHERE id = %s', (str(callback_query.from_user.id), ))
				referer_info=cur.fetchone()
				conn.commit()
				if referer_info[2]!='no referer':
					cur.execute('SELECT * FROM referals WHERE referer = %s', (str(referer_info[2]), ))
					referals_results = cur.fetchall()
					conn.commit()
					if len(referals_results)>0:
						cur.execute('SELECT * FROM referals WHERE referer = %s', (str(callback_query.from_user.id), ))
						referals_results = cur.fetchall()
						conn.commit()
						coef=1
						if len(referals_results)>0 and len(referals_results)<20:
							coef=10
						if len(referals_results)>20 and len(referals_results)<40:
							coef=11
						if len(referals_results)>40:
							coef=12
						sum_dohoda=int(cena)/10
						sum_dohoda=sum_dohoda*coef
						print(sum_dohoda+int(cena))
						sum_dohoda=toFixed(sum_dohoda, 2)
						print('Сумма дохода реферала: '+ str(sum_dohoda))
						cur.execute('SELECT * FROM users WHERE id = %s', (str(callback_query.from_user.id), ))
						referer_info=cur.fetchone()
						conn.commit()
						cur.execute('SELECT * FROM users WHERE id = %s', (str(referer_info[2]), ))
						balanceinfo2=cur.fetchone()
						conn.commit()
						print(1)
						raznica=float(balanceinfo2[1]) + float(sum_dohoda)
						sql = """UPDATE users SET balance = %s WHERE id = %s"""
						print(2)
						cur.execute(sql, (raznica,referer_info[2]))
						conn.commit()
						zar=sum_dohoda
						print(3)
						opisan='Покупка товара'
						zarobotok_table=(str(referer_info[2]),str(message.from_user.id),zar,str(datas),opisan)
						print(4)
						cur.execute('INSERT INTO zarabotok VALUES (%s, %s, %s, %s, %s)', zarobotok_table)
						conn.commit()
						await bot.send_message(referer_info[2],'<b>➕ Начисление на баланс за покупку реферала с ID:</b> '+str(callback_query.from_user.id)+'\n<b>💲 Сумма начисления:</b> '+str(sum_dohoda)+' руб.'+'\n<b>💰 Текущий баланс:</b> '+str(toFixed(raznica,2))+' руб.')
				if user_skidka_info!=None:
					cur.execute('DELETE FROM skidka WHERE id = %s', (str(callback_query.from_user.id),))
					conn.commit()

				print('Товар удалил')
				await bot.send_message(pokupka_chanel_id,'<b>Покупка в магазине ✅</b>\n\nПользователь: \n<b>🔐 ID</b>: '+str(callback_query.from_user.id)+'\n<b>⚙ Логин:</b> '+str(callback_query.from_user.username)+'\n<b>📦 Товар:</b> '+tovarinfo1[3]+'\n<b>💰​Стоимость:</b> '+str(cena)+' руб.')
				await callback_query.answer()
				await state.clear()
			if float(balanceinfo[1]) < float(cena):
				await callback_query.message.answer('❌ <b>Недостаточно средств на вашем счете</b> \n\n<b>💰​ Но вы можете легко пополнить:</b>',reply_markup=kb.keyboard_balance)
				await bot.send_message(pokupka_chanel_id,'<b>Неудачная покупка в магазине ❌</b>\n\n<b>Не хватило средств.</b>\n\nПользователь: \n<b>🔐 ID</b>: '+str(callback_query.from_user.id)+'\n<b>⚙ Логин:</b> '+str(callback_query.from_user.username)+'\n<b>📦 Товар:</b> '+tovarinfo1[3]+'\n<b>💰​Стоимость:</b> '+str(cena)+' руб.')
				await callback_query.answer()
				await state.clear()
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при покупке товара❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(callback_query.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(callback_query.from_user.username)+'</pre>'))			
	
	@dp.message(Text(text="💰 Баланс"))
	async def get_text_messages(message: types.Message):
		try:
			user_ids=message.from_user.id
			print('Вот ID: '+ str(user_ids))
			cur.execute('SELECT * FROM users WHERE id = %s', (str(user_ids), ))
			user_info=cur.fetchone()
			conn.commit()
			print(user_info)
			bal=user_info[1]
			print(bal)
			await message.answer('⚙ <b>Ваш ID:</b> '+user_info[0] + '\n\n💰​ <b>Баланс:</b> '+str(bal) + '  руб.', reply_markup=kb.keyboard_balance)
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при открытии раздела -Баланс-❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(message.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(message.from_user.username)+'</pre>'))	
	@dp.message(Text(text="🔙 Назад"))
	async def get_text_messages(message: types.Message):
		await bot.send_photo(message.from_user.id, image, caption="<b>🏠 Приветствую, странник!\n\n🧙 Ты находишься в лавке Гэндальфа</b>\n\n🗃️ Здесь собрано огромное количество цифровых товаров, среди которых каждый сможет найти то, что нужно!\n\n <b>😎 На все товары распространяется гарантия. </b>\n\n<b>🤫 Все сделки проходят на условиях полной конфиденциальности. </b>", reply_markup=kb.keyboard_inital,  parse_mode="html")
	
	@dp.message(Text(text="👤 Профиль"))
	async def get_text_messages(message: types.Message):
		try:
			cur.execute('SELECT * FROM pokupki WHERE id = %s', (str(message.from_user.id), ))
			pokupki=cur.fetchall()
			conn.commit()
			cur.execute('SELECT * FROM zarabotok WHERE id_referera = %s', (str(message.from_user.id), ))
			zarabotok_result = cur.fetchall()
			conn.commit()
			zar=0
			cur.execute('SELECT * FROM users WHERE id = %s', (str(message.from_user.id), ))
			referer_results = cur.fetchone()
			conn.commit()
			cur.execute('SELECT * FROM referals WHERE referer = %s', (str(message.from_user.id), ))
			referals_results = cur.fetchall()
			conn.commit()
			referer_tvoy='нет реферера'
			if referer_results!='no referer':
				referer_tvoy=str(referer_results[2])
			if len(zarabotok_result)>0:
				for i in range(len(zarabotok_result)):
					zar=zar+float(zarabotok_result[i][2])
			kolvo_pokupok=str(len(pokupki))
			print(kolvo_pokupok)
			await message.answer("<b>⚙ ID:</b>"+str(message.from_user.id)+'\n\n<b>🛒 Количество покупок:</b> '+kolvo_pokupok+'\n\n<b>👤 Ваш реферер: </b>'+str(referer_tvoy)+'\n\n<b>👥 У вас рефералов: </b>'+str(len(referals_results))+'\n\n<b>💲 Доход с рефералов:</b> '+str(toFixed(zar,2))+' руб.', reply_markup=kb.keyboard_profil,  parse_mode="html")
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при открытии раздела -Профиль-❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(message.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(message.from_user.username)+'</pre>'))		
	@dp.message(Text(text="👥 Мои рефералы"))
	async def get_text_messages(message: types.Message):
		await message.answer('<b>🤔 Что будем делать?</b>',reply_markup=kb.keyboard_referals)

	@dp.message(Text(text="💰 Доход с рефералов"))
	async def get_text_messages(message: types.Message):
		try:
			cur.execute('SELECT * FROM zarabotok WHERE id_referera = %s', (str(message.from_user.id), ))
			zarabotok_result = cur.fetchall()
			conn.commit()
			if len(zarabotok_result)==0:
				await message.answer('<b>У вас ещё нет рефералов 😞</b>')
			if len(zarabotok_result)>=1:
				for i in range(len(zarabotok_result)):
					vremya=zarabotok_result[i][3]
					await message.answer('<b>👤 Реферал c ID: </b>'+zarabotok_result[i][1]+'\n<b>💲Принёс вам: </b> '+zarabotok_result[i][2]+' руб.'+'<b>\n📅 В это время:</b> '+vremya[:-7]+'\n<b>📲 За действие: </b>'+zarabotok_result[i][4])
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при открытии раздела -Доход с рефералов-❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(message.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(message.from_user.username)+'</pre>'))				
	@dp.message(Text(text="👥 Показать моих рефералов"))
	async def get_text_messages(message: types.Message):
		try:
			cur.execute('SELECT * FROM referals WHERE referer = %s', (str(message.from_user.id), ))
			referals= cur.fetchall()
			conn.commit()
			if len(referals)==0:
				await message.answer('<b>У вас ещё нет рефералов 😞</b>')
			if len(referals)>=1:
				for i in range(len(referals)):
					vremya=referals[i][1]
					await message.answer('<b>👤 Реферал №</b>'+str(i+1)+'<b>\n⚙ ID:</b> '+'<pre>'+referals[i][0]+'</pre>')
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при открытии раздела -Показать моих рефералов-❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(message.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(message.from_user.username)+'</pre>'))				
	
	@dp.message(Text(text="🛒 Покупки"))
	async def get_text_messages(message: types.Message):
		try:
			cur.execute('SELECT * FROM pokupki WHERE id = %s', (str(message.from_user.id), ))
			pokupki=cur.fetchall()
			conn.commit()
			kolvo_pokupok=str(len(pokupki))
			if int(kolvo_pokupok)==0:
				await message.answer('<b>Список покупок пуст 😞</b>')
			if int(kolvo_pokupok)>=1:
				for i in range(int(kolvo_pokupok)):
					vremya=pokupki[i][4]
					await message.answer('📦 <b>Покупка №</b>'+str(i+1)+'\n📝 <b>Наименование:</b> '+pokupki[i][1]+'\n📃 <b>Товар:</b> \n\n'+pokupki[i][2]+'\n\n💰 <b>Стоимость:</b> '+pokupki[i][3]+' руб.'+'\n📅 <b>Дата:</b> '+vremya[:-7])
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при открытии раздела -Покупки-❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(message.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(message.from_user.username)+'</pre>'))	
	@dp.message(Text(text="💳 Пополнения"))
	async def get_text_messages(message: types.Message):
		try:
			cur.execute('SELECT * FROM popolneniya WHERE id = %s', (str(message.from_user.id), ))
			popolnen= cur.fetchall()
			conn.commit()
			kolvo_popolnen=str(len(popolnen))
			if int(kolvo_popolnen)==0:
				await message.answer('<b>Список пополнений пуст 😞</b>')
			if int(kolvo_popolnen)>=1:
				for i in range(int(kolvo_popolnen)):
					vremya=popolnen[i][3]
					await message.answer('💳 <b>Пополнение №</b>'+str(i+1)+'\n\n⚙ <b>ID платежа:</b> '+popolnen[i][1]+'\n💰 <b>Сумма:</b> '+popolnen[i][2]+' руб.'+'\n📅 <b>Дата:</b> '+vremya[:-7])
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при открытии раздела -Пополнения-❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(message.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(message.from_user.username)+'</pre>'))	

	@dp.message(Text(text="⚠️ Помощь"))
	async def get_text_messages(message: types.Message):
		await message.answer('<b>⚠️ В данном разделе собраны часто задаваемые вопросы и ответы на них.</b>',reply_markup=kb.get_help())
	
	@dp.message(Text(text="📖 Отзывы"))
	async def get_text_messages(message: types.Message):
		await message.answer('<b>📖 О нас пишут тут: \n </b>'+config.otzyv_channel)

	@dp.message(Text(text="📧 Поддержка"))
	async def get_text_messages(message: types.Message):
		await message.answer('<b>📧 По любым вопросам \n\nПиши ему: </b>'+config.techpod)

	@dp.message(Text(text="🎁 Акции"))
	async def get_text_messages(message: types.Message):
		await message.answer('<b>😞 Действующих акций пока нет</b>')

	@dp.message(Text(text="💰 Пополнить баланс"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		user_ids=message.from_user.id
		print('Вот ID: '+ str(user_ids))
		await message.answer('<b>💰 Какую сумму будем пополнять?</b>\n\n<b>Мин. сумма пополнения:</b> 1 руб.\n<b>Макс. сумма пополнения:</b> 9999 руб.\n\n<b>⚠️ Отменить ввод и перейти в главное меню: введи</b> "<pre>stop</pre>"',reply_markup=kb.keyboard_nazadpopol)
		await state.set_state(AdBalance.ad_balance)
	
	@dp.message(Text(text="▶️ Дополнительно"))
	async def get_text_messages(message: types.Message):
		await message.answer('<b>❗ Возможно, вам будет полезно</b>',reply_markup=kb.keyboard_all)

	@dp.message(state=AdBalance.ad_balance)
	async def ad_category_text(message: types.Message, state: FSMContext):
		try:
			await state.update_data(ad_balance=message.text)
			if message.text=='stop':
				await bot.send_photo(message.from_user.id, image, caption="<b>🏠 Приветствую, странник!\n\n🧙 Ты находишься в лавке Гэндальфа</b>\n\n🗃️ Здесь собрано огромное количество цифровых товаров, среди которых каждый сможет найти то, что нужно!\n\n <b>😎 На все товары распространяется гарантия. </b>\n\n<b>🤫 Все сделки проходят на условиях полной конфиденциальности. </b>", reply_markup=kb.keyboard_inital,  parse_mode="html")
				return await state.clear()
			if message.text.isdigit()==True:
				if int(message.text)>0 and int(message.text)<10000 :
					user_ids=message.from_user.id
					print('Вот ID: '+ str(user_ids))
					
					balik=int(message.text)
					
					bils=random.randint(1, 100000)
					
					new_bill = p2p.bill(bill_id=bils, amount=balik, lifetime=15)
					print(new_bill.bill_id)
					
					status= bill_id=p2p.check(bill_id=new_bill.bill_id).status
					
					url_check=new_bill.pay_url
					qiwi_info=(str(user_ids),str(balik),str(bils),str(new_bill),str(status),str(url_check))
					print(status)
					markup_buy1 =InlineKeyboardBuilder()
					button_buy1=markup_buy1.add(InlineKeyboardButton(text='💳 Оплатить', callback_data='oplatit',url=new_bill.pay_url)) #Создаём кнопки, i[1] - название, i[2] - каллбек дата	
					buy_kb1= button_buy1.adjust(1).as_markup()
					await message.answer('🔗 Создал ссылку для оплаты. \n\n⌚ Она действует 15 минут. \n\n💲После оплаты деньги автоматически поступят на ваш счёт.',reply_markup=buy_kb1)
					cur.execute('INSERT INTO qiwi VALUES (%s, %s, %s, %s,%s,%s)', qiwi_info)
					conn.commit()
				else:
					await message.answer('<b>❗ Введите число от 1 до 9999</b>\n<em>Пример: </em><pre>100</pre>\n\n<b>⚠️ Отменить ввод и перейти в главное меню: введи </b>"<pre>stop</pre>"')

			if message.text.isdigit()==False:
				await message.answer('<b>❗ Введите число от 1 до 9999</b>\n<em>Пример: </em><pre>100</pre>\n\n<b>⚠️ Отменить ввод и перейти в главное меню: введи </b>"<pre>stop</pre>"')
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при вводе суммы пополнения❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(message.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(message.from_user.username)+'</pre>'))		
	
	@dp.message(Text(text="adminConstruct2$"))
	async def with_puree(message: types.Message):
		if str(message.from_user.id)=='567660912' or str(message.from_user.id)=='733672052':
			cur.execute("SELECT * FROM users;")
			all_results = cur.fetchall()
			conn.commit()
			await message.answer(('🤖 <b>Привет, хозяин!</b> \n\n <b>📈 Пользователей в боте:</b> ' +str(len(all_results))+'\n\n😎 <em>Что будем делать?</em>'), reply_markup=kb.keyboard_inital_adminkb)
		else:		
			await message.answer('<b>☝ Незваный гость хуже татарина</b>')
    
	@dp.message(Text(text="📩 Массовая рассылка"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912' or str(message.from_user.id)=='733672052':
			cur.execute("SELECT * FROM users;")
			global all_results
			all_results = cur.fetchall()
			conn.commit()
			print(all_results)
			await message.answer('Что рассылаем?')
			await state.set_state(JobUser.rass)
		else:
			await message.answer('<b>☝ Незваный гость хуже татарина</b>')
	@dp.message(Text(text="➕ Пополнить баланс по ID"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912' or str(message.from_user.id)=='733672052':
			await message.answer('<b>📝 Введите ID и сумму пополнения через пробел:</b>')
			await state.set_state(JobUser.popolid)
	
	@dp.message(state=JobUser.popolid)
	async def jobs_text(message: types.Message, state: FSMContext):
		await state.update_data(jobs=message.text)
		id_popoln=message.text.split()[0]
		sum_popoln=message.text.split()[1]
		cur.execute('SELECT * FROM users WHERE id = %s', (str(id_popoln), ))
		balanceinfo=cur.fetchone()
		conn.commit()
		raznica=float(balanceinfo[1]) + float(sum_popoln)
		sql = """UPDATE users SET balance = %s WHERE id = %s"""
		cur.execute(sql, (raznica,id_popoln))
		conn.commit()
		await message.answer('<b>✅ Пополнил баланс пользователя \n⚙️ ID: </b>'+str(id_popoln)+'<b>\n➕ На сумму: </b>'+str(sum_popoln)+' руб.'+'\n<b>💰​ Баланс пользователя:</b> '+str(toFixed(raznica,2))+' руб. ')
		await bot.send_message(id_popoln,('➕ <b>Ваш баланс пополнен администратором на сумму:</b> '+str(sum_popoln)+' руб.'+'\n💰​ <b>Текущий баланс:</b> '+str(toFixed(raznica,2))+' руб. '))
		await state.clear() 
	
	@dp.message(Text(text="📨 Отправка сообщения по ID"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		if str(message.from_user.id)=='567660912' or str(message.from_user.id)=='733672052':
			await message.answer('<b>⚙️ Введите ID человека: </b>')
			await state.set_state(JobUser.mesmes)
	
	@dp.message(state=JobUser.mesmes)
	async def get_text_messages(message: types.Message, state: FSMContext):
		await message.answer('<b>📝 Введите текст сообщения: </b>')
		global id_user_sms
		id_user_sms=message.text
		await state.set_state(JobUser.mesid)

	@dp.message(state=JobUser.mesid)
	async def jobs_text(message: types.Message, state: FSMContext):
		await state.update_data(jobs=message.text)
		await message.answer('<b>✅ Отправил сообщение пользователю \n⚙️ ID: </b>'+str(id_user_sms)+'<b>\n📝 Текст сообщения: \n</b>'+str(message.text))
		await bot.send_message(id_user_sms,('📧 <b>Вам сообщение от администратора:</b>\n\n'+str(message.text)))
		await state.clear() 
	
	@dp.message(state=JobUser.rass)
	async def jobs_text(message: types.Message, state: FSMContext):
		await state.update_data(jobs=message.text)
		await bot.send_message(message.chat.id, f"<b>📩 Начинаю рассылку с текстом:</b> \n\n{message.text}\n\n<b>Как всё сделаю, отчитаюсь.</b> ✅")
		for i in range(len(all_results)):
				try:
					await bot.send_message(all_results[i][0],(message.text))
					succes=succes+1
					time.sleep(1)
				except:
					failed=failed+1
					i=i+1
		await message.answer('📩 <b>Рассылка завершена.</b>\n\n✅<em> Успешно отправлено: </em>'+str(succes)+'\n\n<em>❌ Не отправлено: </em>'+str(failed))        
		await state.clear() 
	
	@dp.message(Text(text="➕ Пригласить друга"))
	async def get_ref(message: types.Message):
		ref_baza=config.ref
		ref_link=ref_baza+str(message.from_user.id)
		await message.answer('<b>👥В нашем магазине действует реферальная ссылка.</b>\n\n🔗 Ниже отправили для вас специальную ссылку.\n\n<b>🌎 Делитесь ею со своими друзьями, знакомыми, чтобы получать деньги.</b>\n\n<em>❗ Условия реферальной программы:</em>\n💰 5 руб. на ваш баланс за каждого реферала\n➕ отчисления на ваш баланс за каждую покупку вашего реферала по схеме:\n\n➖ от 0 до 20 рефералов - 10%\n➖ от 20 до 40 рефералов - 11%\n➖ от 40 рефералов - 12%.')
		await message.answer('<b>🔗 Вот твоя реферальная ссылка:</b>' +str(ref_link))

	@dp.message(Text(text="🏷️ Промокоды"))
	async def get_text_messages(message: types.Message):
		await message.answer('<b>Промокоды бывают 3 типов: </b>\n🛍️ cкидочный\n📦 промокод, содержащий в себе какой-то товар\n💲 денежный. \n\n<b>За что их можно получить:</b> \n➖ оставить о нас отзыв \n➖ активно пользоваться магазином \n➖ конкурсы, розыгрыши \n➖ привлечение рефералов \n➖ акции от магазина.',reply_markup=kb.keyboard_kupon)
	
	@dp.message(Text(text="🏷️ Активировать промокод"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		await message.answer('🏷️<b> Введи промокод: </b>')
		await state.set_state(AdPromoMoney.ad_promo_money)

	@dp.message(state=AdPromoMoney.ad_promo_money)
	async def ad_category_text(message: types.Message, state: FSMContext):
		await state.update_data(ad_promo_money=message.text)
		try:
			if message.text[0]=='M':
				cur.execute('SELECT * FROM promocod_money WHERE promocod = %s', (str(message.text), ))
				promo_money_info=cur.fetchall()
				conn.commit()
				if len(promo_money_info)==0:
					await message.answer('<b>❌ Такого промокода нет</b>')
					await state.clear()
				if len(promo_money_info)>0:
					cur.execute('DELETE FROM promocod_money WHERE promocod = %s',(str(message.text),))
					conn.commit()
					cur.execute('SELECT * FROM users WHERE id = %s', (str(message.from_user.id), ))
					balanceinfo=cur.fetchone()
					conn.commit()
					raznica=float(balanceinfo[1]) + float(promo_money_info[0][1])
					sql = """UPDATE users SET balance = %s WHERE id = %s"""
					cur.execute(sql, (float(raznica),str(message.from_user.id)))
					conn.commit()
					await message.answer('<b>✓ Успешное использование промокода</b>'+'\n<b>💲 Баланс пополнен на:</b> '+str(promo_money_info[0][1]+' руб.'+'\n<b>💰 Текущий баланс:</b> '+str(toFixed(raznica,2))+' руб.'))
					await state.clear()
				await state.clear() 
			elif message.text[0]=='T':
				cur.execute('SELECT * FROM promocod_tovar WHERE promocod = %s', (str(message.text), ))
				promo_tovar_info=cur.fetchall()
				conn.commit()
				if len(promo_tovar_info)==0:
					await message.answer('<b>❌ Такого промокода нет</b>')
					await state.clear()
				if len(promo_tovar_info)>0:
					cur.execute('DELETE FROM promocod_tovar WHERE promocod = %s',(str(message.text),))
					conn.commit()
					await message.answer('<b>✓ Успешное использование промокода</b>'+'\n<b>📦 Промокод содержит:</b> \n'+str(promo_tovar_info[0][1]))
					await state.clear()
				await state.clear()
			elif message.text[0]=='S':
				cur.execute('SELECT * FROM promocod_skidka WHERE promocod = %s', (str(message.text), ))
				promo_skidka_info=cur.fetchall()
				conn.commit()
				if len(promo_skidka_info)==0:
					await message.answer('<b>❌ Такого промокода нет</b>')
					await state.clear()
				if len(promo_skidka_info)>0:
					
					skidka_add=((str(message.from_user.id),str(promo_skidka_info[0][1])))
					cur.execute('INSERT INTO skidka VALUES (%s, %s)', skidka_add)
					conn.commit()
					cur.execute('DELETE FROM promocod_skidka WHERE promocod = %s',(str(message.text),))
					conn.commit()
					await message.answer('<b>✓ Скидка в размере:</b> '+'<pre>'+str(promo_skidka_info[0][1]) + ' процентов</pre> <b>на одну покупку - активирована.</b> \n\n<em>😎 За покупками?</em>')
					await state.clear()
				await state.clear() 
			else:
				await message.answer('<b>❌ Такого промокода нет</b>')
		except:
			await bot.send_message(config.error,('<b>❗Ошибка при активации промокода пользователем❗\n\n⚙️ Необходимо проверить работу бота\n\nТекст ошибки:</b> \n\n'+'<pre>'+traceback.format_exc()+'</pre>'+'\n\n<b>👤 Пользователь:</b>\n<em>🔐 ID:</em>'+'<pre>'+str(message.from_user.id)+'</pre>'+'\n<em>⚙️ Логин: </em>'+'<pre>'+str(message.from_user.username)+'</pre>'))	

	@dp.message(Text(text="🎲 Испытать удачу"))
	async def get_text_messages(message: types.Message, state: FSMContext):
		await message.answer('<em>🌄 Каждое утро в столицу прибывала сотня смельчаков, желающих испытать удачу. </em>\n\n<b>🎰 Раз в сутки вы можете бесплатно сыграть в рулетке Гэндальфа</b>\n\n📁 Призы рулетки пополняются ежедневно, добавляются и действительные ценные.\n\n<b>🧙 Поэтому не забывай заглядывать к нам. </b>', reply_markup=kb.get_fortuna())
		await state.set_state(AdFortuna.fortuna)

	@dp.callback_query(state=AdFortuna.fortuna)
	async def stoptopupcall(callback_query: types.CallbackQuery, state: FSMContext): 
		cur.execute('SELECT * FROM fortuna WHERE id = %s', (str(callback_query.from_user.id), ))
		data_info=cur.fetchall()
		conn.commit()
		date_last=''
		date_now =''
		if len(data_info)>0:
			date1=data_info[-1]
			date1=date1[1]
			date1=date1[:-10]
			date_last=datetime.strptime((date1), "%Y-%m-%d %H:%M")
			date_now=datetime.now()
			date_last=date_last+timedelta(hours=24)
		if date_last<date_now or len(data_info)==0:
			print('Прошло больше 5 минут')
			smile=['💰','📦','🏷️']
			light=['🔸','🔹']
			for i in range(random.randint(5,15)):
				try:
					sec1=smile[random.randint(0, 2)]
					sec2=smile[random.randint(0, 2)]
					sec3=smile[random.randint(0, 2)]
					await callback_query.message.edit_text('╔═══╦════╦═══╗\n'+light[random.randint(0,1)]+'<b>Gandalf fortuna</b>'+light[random.randint(0,1)]+'\n╔═══╦════╦═══╗'+'\n    '+sec1+'       '+sec2+'        '+sec3+'   \n╚═══╩════╩═══╝')
					time.sleep(0.5)
				except:
					await callback_query.message.edit_text('╔═══╦════╦═══╗\n'+light[random.randint(0,1)]+'<b>Gandalf fortuna</b>'+light[random.randint(0,1)]+'\n╔═══╦════╦═══╗'+'\n    '+smile[random.randint(0, 2)]+'        '+smile[random.randint(0, 2)]+'        '+smile[random.randint(0, 2)]+'   \n╚═══╩════╩═══╝')
			if sec1==sec2==sec3:
				if sec1=='💰':
					cat='money'
					cur.execute('SELECT * FROM prize_fortuna WHERE category = %s', (cat, ))
					all_results = cur.fetchall()
					conn.commit()
					cur.execute('DELETE from prize_fortuna WHERE promocod = %s', (str(all_results[-1][1]), ))
					conn.commit()
					await callback_query.message.answer('🥳 <b>Поздравляю!</b> \n\n<b>💰 Вы выиграли промокод на деньги.</b>\n\n'+'<pre>'+str(all_results[-1][1])+'</pre>')
				if sec1=='📦':
					cat='tovar'
					cur.execute('SELECT * FROM prize_fortuna WHERE category = %s', (cat, ))
					all_results = cur.fetchall()
					conn.commit()
					cur.execute('DELETE from prize_fortuna WHERE promocod = %s', (str(all_results[-1][1]), ))
					conn.commit()
					await callback_query.message.answer('🥳 <b>Поздравляю!</b> \n\n<b>📦 Вы выиграли промокод на товар.</b>\n\n'+'<pre>'+str(all_results[-1][1])+'</pre>')

				if sec1=='🏷️':
					cat='skidka'
					cur.execute('SELECT * FROM prize_fortuna WHERE category = %s', (cat, ))
					all_results = cur.fetchall()
					conn.commit()
					cur.execute('DELETE from prize_fortuna WHERE promocod = %s', (str(all_results[-1][1]), ))
					conn.commit()
					await callback_query.message.answer('🥳 <b>Поздравляю!</b> \n\n<b>🏷️ Вы выиграли промокод на скидку.</b>\n\n'+'<pre>'+str(all_results[-1][1])+'</pre>')

			else:
				await callback_query.message.answer('😞 <b>К сожалению, удача сегодня не на вашей стороне</b>', reply_markup=kb.get_fortuna())
			dt_now = datetime.now()
			fortuna_table=((str(callback_query.from_user.id,),str(dt_now)))
			cur.execute('INSERT into "fortuna" VALUES (%s, %s)', fortuna_table)
			conn.commit()
			print('Записал в базу')
			await callback_query.answer()

		if date_last>date_now:
			ostalos_do_prokrutki=str(date_last-date_now)
			print('До прокрутки:',ostalos_do_prokrutki[:-4])
			await callback_query.message.answer('😞 <b>Только раз в сутки минут можно крутить барабан.</b>\n\n<em>⌚ До прокрутки осталось: </em>'+ostalos_do_prokrutki[:-4])
			await callback_query.answer()
async def main():
    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
	await bot.delete_webhook(drop_pending_updates=True)
	scheduler.start()
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())
