
import telebot
import sqlite3
from telebot import types
bot = telebot.TeleBot('') # Токен бота

db = sqlite3.connect('base.db', check_same_thread=False) # Открываем базу данных
sql = db.cursor()

chat = [] # Список chat_id которые подали заявку и ожидают от нас ответа
keyboard2 = types.ReplyKeyboardMarkup(row_width=1)

button1 = types.KeyboardButton("Меню📋")
button2 = types.KeyboardButton("Бронирование столика📃")
button3 = types.KeyboardButton("Контакты☎️")
keyboard2.add(button1,button2,button3)

keyboard4 = types.ReplyKeyboardMarkup(row_width=1)
button4 = types.KeyboardButton("Пожеланий нет")
keyboard4.add(button4)

@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.chat.id, "Приветственное сообщение", reply_markup=keyboard2)
    elif message.text.lower() == "меню📋":
        bot.send_photo(message.chat.id, 'https://mir-s3-cdn-cf.behance.net/project_modules/fs/64157148005935.588b67f6e5135.jpg')
    elif message.text.lower() == "контакты☎️":
        bot.send_message(message.chat.id, "тут контакты в виде картинки или текста")
    elif message.text.lower() == "бронирование столика📃":
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard1 = telebot.types.InlineKeyboardButton(text='📩Подать заявку.', callback_data='application')
        keyboard.add(keyboard1)
        bot.send_message(message.chat.id, '☑Нажмите, чтобы подать заявку на бронирование.☑', reply_markup=keyboard) 
        sql.execute('SELECT * FROM users WHERE user_id = ?', (message.chat.id,))

        if sql.fetchone() == None:
            sql.execute('INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?)', (message.chat.id, 'none', 'none', 'none', message.from_user.username, 0))
            db.commit()
            
@bot.callback_query_handler(func=lambda call:True)
def question(call):
    if call.data == 'application':
        sql.execute(f'SELECT * FROM users WHERE user_id = {call.message.chat.id}')
        ans = sql.fetchone()
        status = 0
        if status == 0:
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="1) Напишите Ваше имя и фамилию") # Первый вопрос
            bot.register_next_step_handler(msg, question2)
    elif call.data == 'sent':
        sql.execute(f"""UPDATE users SET status = 1 WHERE user_id = {call.message.chat.id}""")
        db.commit()
        if (call.message.chat.id in chat):
            print(chat)
        else:
            chat.append(call.message.chat.id)
            print(chat)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="☑Заявка отправлена, ожидайте ответа от администратора!☑") # Ответ когда пользователь отправил заявку
        sql.execute(f'SELECT * FROM users WHERE id = 1')
        ans = sql.fetchone()
        msm = ans[1]
        sql.execute(f'SELECT * FROM users WHERE user_id = {call.message.chat.id}')
        anss = sql.fetchone()
        ans1 = anss[2]
        ans2 = anss[3]
        ans3 = anss[4]
        username = anss[5]
        key = telebot.types.InlineKeyboardMarkup()
        key1 = telebot.types.InlineKeyboardButton(text='Подтвердить бронь✅', callback_data='accepted')
        key2 = telebot.types.InlineKeyboardButton(text='Отклонить бронь❌', callback_data='reject')
        key.add(key1, key2)
        bot.send_message(msm, f'Поступила новая заявка от @{username}:\n'
                              f'Имя Фамилия: {ans1}\n'
                              f'Время и дата: {ans2}\n'
                              f'Пожелания: {ans3}', reply_markup=key) # Сообщения об поступившей заявке
    if call.data == 'accepted':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Вы приняли заявку✅") # Ответ если вы приняли заявку
        msm = chat[0]
        bot.send_message(msm, 'Столик успешно забронирован!✅') # Ответ тому кого вы приняли
        del chat[0]
    elif call.data == 'reject':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Вы отклонили заявку❌") # Ответ если вы отклонили заявку
        msm = chat[0]
        bot.send_message(msm, 'Извините, но мест на это время нет. Попробуйте забронировать на другое время❌') # Ответ тому кого вы отклонили
        del chat[0]

def question2(message):
    question1 = message.text
    sql.execute(f"""UPDATE users SET answer = '{question1}' WHERE user_id = {message.chat.id}""")
    db.commit()
    msg = bot.send_message(message.chat.id, '2) Напишите желаемое время и дату') # Второй вопрос
    bot.register_next_step_handler(msg, question3)

def question3(message):
    question2 = message.text
    sql.execute(f"""UPDATE users SET answer2 = '{question2}' WHERE user_id = {message.chat.id}""")
    db.commit()
    msg = bot.send_message(message.chat.id, '3) Есть ли у вас пожелания?', reply_markup=keyboard4) # Третий вопрос
    bot.register_next_step_handler(msg, finish)

def finish(message):
    keyboards = telebot.types.InlineKeyboardMarkup()
    keyboard2 = telebot.types.InlineKeyboardButton(text='Отправить заявку💬', callback_data='sent')
    keyboard3 = telebot.types.InlineKeyboardButton(text='Заполнить заново🌀', callback_data='application')
    keyboards.add(keyboard2, keyboard3)
    question3 = message.text
    sql.execute(f"""UPDATE users SET answer3 = '{question3}' WHERE user_id = {message.chat.id}""")
    db.commit()
    sql.execute(f'SELECT * FROM users WHERE user_id = {message.chat.id}')
    ans = sql.fetchone()
    ans1 = ans[2]
    ans2 = ans[3]
    ans3 = ans[4]
    bot.send_message(message.chat.id, f'Все верно?:\n 1) {ans1} '
                                      f'\n 2) {ans2}'
                                      f'\n 3) {ans3}', reply_markup=keyboards)

bot.polling()