import json
from requests import get
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import undetected_chromedriver as uc
import mysql.connector

headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.4.778 Yowser/2.5 Safari/537.36"
    }


db = mysql.connector.connect(
                        host="127.0.0.1",
                        user="root",
                        password="12345678",
                        port="3306",
                        database="bot",
                        option_files='my.conf',
                        get_warnings=True
                    )

def insert_link_into_bd (title,link,text,date):
    cursor = db.cursor(buffered=True)
    try:
        syntext = """Insert into news (Link,Title,Text,Date) values (%s,%s,%s,%s);"""
        value = (link, title, text, date)
        cursor.execute(syntext,value)
        db.commit()
    except mysql.connector.Error as err:
        if err.sqlstate == '23000': raise err

def get_news_from_cisoclub():
    for page in range(1, 4):
        r = get(url=f'https://cisoclub.ru/category/news/page/{page}', headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        articles_cards = soup.find_all("div", class_="content-wrap")
        for card in articles_cards:
            try:
                link = card.find('h3').find('a').get('href')
            except Exception as ex:
                print(ex)
                link = "Ссылка отсутсвует"
            try:
                title = card.find('h3').find('a').text
            except Exception as ex:
                print(ex)
                title = "Заголовок отсутствует"
            try:
                description = card.find('div', class_='entry-content').find('p').text
            except Exception as ex:
                print(ex)
                description = "Текст отсутствует"
            try:
                date_one = card.find('span', class_='posted-date').text
                date_list = date_one.split('.')
                day, month, year = date_list[0], date_list[1], date_list[2]
                date = datetime.strptime((day + '/' + month + '/' + year), '%d/%m/%Y').date()
            except Exception as ex:
                continue
                date = "Дата отсутствует"
            text=description
            insert_link_into_bd (title,link,text,date)
            print("Заголовок -", title)
            print("Ссылка -", link)
            print("Дата:", date)
            print("Аннотация:", description)
            print("--------")
        time.sleep(3)

get_news_from_cisoclub()