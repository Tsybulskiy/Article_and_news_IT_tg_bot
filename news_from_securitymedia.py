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

def get_news_from_securitymedia():
    for page in range(1,3):
        resp = get(f'https://securitymedia.org/news/?PAGEN_2={page}',headers=headers)
        bs = BeautifulSoup(resp.text,'html.parser')
        cards = bs.find_all('div', class_='news-card mb-4')
        for card in cards:
            title = card.find('div',class_='h4').text
            link = 'https://securitymedia.org' + card.find('a',class_='text-dark').get('href')
            date_list = card.find('div',class_='py-3 date_time font-weight-light').text.strip().split('.')
            date = date_list[2] + '-' + date_list[1] + '-' + date_list[0]
            description = card.find('div',class_='col-md-8')
            div_tags = description.find_all('div')
            for tag in div_tags:
                tag.decompose()
            description_list = description.text.strip().split()
            description = ' '.join(description_list)
            text=description
            insert_link_into_bd(title,link,text,date)
            print(title)
            print(link)
            print(date)
            print(description)
            print('------')
        time.sleep(3)

get_news_from_securitymedia()