import telebot
from telebot import types
import wikipedia
import aiogram
from aiogram.types import ReplyKeyboardRemove


wikipedia.set_lang('ru')  # использует русский язык

bot = telebot.TeleBot("5979199325:AAGZHSL1MkKiufHOG3LMjHq5_NBNI428cr0")  # подключение токена бота

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Привет, я ваш персональный словарь. Чтобы я смог вам помочь, введите интересующее вас слово.')

@bot.message_handler(content_types=['text'])
def send_keyboard(message, call = 'Выберете, что вы хотели бы получить:'):
    keyboard = types.ReplyKeyboardMarkup()  # создание клавиатуры
    item1 = types.KeyboardButton('Значение слова ' + str(message.text))  # создание кнопки 'Значение слова'
    item2 = types.KeyboardButton('Фото по запросу ' + str(message.text))  # создание кнопки 'Фото'
    keyboard.add(item1)  # добавление кнопки 'Значение слова' на клавиатуру
    keyboard.add(item2)  # добавление кнопки 'Фото' на клавиатуру

    # отправлет сообщение в чат и запоминает информацию о нем
    message_1 = bot.send_message(message.from_user.id, text=call, reply_markup=keyboard)

    # отправляет информацию о сообщении в функцию
    bot.register_next_step_handler(message_1, answer)


def definition(word):
    try:
        get_page = wikipedia.page(word)    # возвращает данные со страницы в википедии
        definition_1 = get_page.content[:2000]  # возвращает первые 1000 текстовых символа
        sentences = definition_1.split('.')  # создаем массив из предложений
        sentences = sentences[:-1]  # срезает последнее предложение
        short_definition = ''   # пустая строчка
        for sentence in sentences:   # добавим все предложения до символа ==
            if not('==' in sentence):
                short_definition = short_definition + sentence + '.'
            else:
                break
        return short_definition
    except Exception as e:   # не найдена страница
        if len(wikipedia.search(word)) > 1:
            return 'В Википедии нет такой страницы, но есть несколько страниц, содержащих данное слово: ' + \
                   ', '.join(wikipedia.search(word)) + '. Если один из них вы имели в виду, пожалуйста, введите интересующий вас вариант.'
        return 'К сожалению, в Википедии нет информации об этом.'

def photo(word):
    try:
        get_page = wikipedia.page(word)  # возвращает данные со страницы в википедии
        get_photo = get_page.images  # возвращает фото
        for i in range(len(get_photo)):
            if get_photo[i][-3:] != 'svg':
                return get_photo[i]
    except Exception as e:  # не найдена страница
        if len(wikipedia.search(word)) > 1:
            return 'В Википедии нет такой страницы, но есть несколько страниц, содержащих данное слово: ' + \
           ', '.join(wikipedia.search(word)) + '. Если один из них вы имели в виду, пожалуйста, введите интересующий вас вариант.'
        return 'В Википедии нет информации об этом или страницы, содержащей данное фото.'


@bot.message_handler(content_types=['text'])
def answer(call):
    if call.text[:15] == 'Значение слова ':
        try:
            new_call = call.text[15:]
            bot.send_message(call.chat.id, definition(new_call))  # отправит сообщение со значением функции в чат
            if definition(new_call)[:84] == 'В Википедии нет такой страницы, но есть несколько страниц, содержащих данное слово: ':
                bot.send_message(call.from_user.id,
                         text='Пожалуйста, введите интересующий вас вариант (не совпадающий с введенным ранее)',
                         reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.send_message(call.from_user.id, text='Если хотите узнать что-то еще, введите интересующее вас слово.',
                                          reply_markup=types.ReplyKeyboardRemove())
        except Exception as e:
            bot.send_message(call.chat.id, 'К сожалению, я ничего не смог найти по вашему запросу.')
    if call.text[:16] == 'Фото по запросу ':
        try:
            new_call = call.text[16:]
            if photo(new_call)[:84] == 'В Википедии нет такой страницы, но есть несколько страниц, содержащих данное слово: ':
                bot.send_message(call.chat.id, photo(new_call))  # отправит сообщение об ошибке в чат
                bot.send_message(call.from_user.id,
                            text='Пожалуйста, введите интересующий вас вариант (не совпадающий с введенным ранее)',
                            reply_markup=types.ReplyKeyboardRemove())
            else:
                if photo(new_call)[:71] == 'В Википедии нет информации об этом или страницы, содержащей данное фото':
                    bot.send_message(call.chat.id, photo(new_call))  # отправит сообщение об ошибке в чат
                else:
                    bot.send_photo(call.chat.id, photo(new_call))  # отправит фото
                bot.send_message(call.from_user.id, text='Если хотите узнать что-то еще, введите интересующее вас слово.',
                                      reply_markup=types.ReplyKeyboardRemove())
        except Exception as e:
            bot.send_message(call.chat.id, 'К сожалению, я ничего не смог найти по вашему запросу.')

bot.infinity_polling()