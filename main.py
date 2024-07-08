import requests
from bs4 import BeautifulSoup
import fake_useragent
import sqlite3
import telebot

bot = telebot.TeleBot("""Введите сюда ваш токен для бота""")


@bot.message_handler(commands="start")
def start_bot(message):
    bot.send_message(message.chat.id, f"\tПриветствую тебя, {message.from_user.first_name}!\nВведи профессию, которую ты ищешь")

@bot.message_handler()
def input_vacancy(message):
    with sqlite3.connect("vacancy_app.db") as con:
        con.execute("""CREATE TABLE IF NOT EXISTS vacancy (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        link TEXT,
        info TEXT,
        location TEXT )""")
    con.commit()
    cur = con.cursor()

    user = fake_useragent.UserAgent().random
    header = { "user-agent": user }

    search = str(message.text)
    link = f"https://career.avito.com/vacancies/?q={search}&action=filter"
    response = requests.get(link, headers=header)
    soup = BeautifulSoup(response.text, "lxml")


    all_vacancy = soup.find_all("div", class_ = "vacancies-section__item")

    counter = 0

    for x in all_vacancy:
        vacancy_name = x.find("span", class_= "vacancies-section__item-link-name").text
        vacancy_links = "https://career.avito.com" + x.find("a", class_= "vacancies-section__item-link").get("href")
        try:
            info = x.find("span", class_ ="vacancies-section__item-format").text
        except:
            info = ""
        try:
            location = x.find("span", class_ ="vacancies-section__item-city").text
        except AttributeError:
            location = ""
        counter += 1
        cur.execute("INSERT OR REPLACE INTO vacancy(id, name, link, info, location) VALUES (?, ?, ?, ?, ?)", (counter, vacancy_name, vacancy_links, info,location))
        con.commit()
        bot.send_message(message.chat.id, f"{counter}) {vacancy_name}\n\t\t\t\t{info} | {location}\n{vacancy_links}",disable_web_page_preview = True) 

bot.infinity_polling()