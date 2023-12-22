import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import undetected_chromedriver as uc
import mysql.connector

db = mysql.connector.connect(
                        host="127.0.0.1",
                        user="root",
                        password="12345678",
                        port="3306",
                        database="prefinal",
                        option_files='my.conf',
                        get_warnings=True
                    )

def insert_link_into_bd (category,title,link,author,author_link,finally_text,date):
    cursor = db.cursor(buffered=True)
    try:
        syntext = """Insert into links (Category,Title,Article_link,Author,Author_link,Text, DATE) values (%s,%s,%s,%s,%s,%s,%s);"""
        value = ((category),(title),(link),(author),(author_link),(finally_text),(date))
        cursor.execute(syntext,value)
        db.commit()
    except mysql.connector.Error as err:
            if err.sqlstate == '23000': raise err

def get_itsec_ru_info():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.1.1138 Yowser/2.5 Safari/537.36"
    }

    unique_sites = []
    all_site = []
    urls = ['https://www.itsec.ru/articles/page/']
    for k in urls:
        for i in range(1, 34):
            url = f"{k}{i}"
            print(url)
            r = requests.get(url=url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            articles_cards = soup.find_all("div", class_="span12 widget-span widget-type-cell content-card-text")
            for card in articles_cards:
                try:
                    title = card.find('h3').find('a').text
                except Exception as ex:
                    print(ex)
                    title = "Заголовок отсутствует"
                try:
                    category = card.find('a', class_="topic-button theme").text
                except Exception as ex:
                    print(ex)
                    category = "Категория отсутствует"
                try:
                    link = card.find('h3').find('a').get('href')
                except Exception as ex:
                    print(ex)
                    link = "Ссылка отсутствует"
                try:
                    resp = requests.get(url=link, headers=headers)
                    soup = BeautifulSoup(resp.text, "html.parser")
                    text = soup.find('div', class_='clear').text
                    finally_text = r''' '''
                    for tag in text:
                        finally_text += ' '.join(tag.splitlines())
                    finally_text = finally_text.replace('"', '\"')
                    for i in finally_text:
                        i = i.replace("'", "\\'")
                except Exception as ex:
                    print(ex)
                    finally_text = "Текс отсутствует"
                try:
                    author = soup.find('a', class_='strong').text
                except Exception as ex:
                    print(ex)
                    author = "Автор отсутствует"
                try:
                    author_link = soup.find('p').find('a').get('href')
                except Exception as ex:
                    print(ex)
                    author_link = "Cсылка на автора отсутствует"
                try:
                    date = card.find('div', class_='span12 widget-span widget-type-raw_jinja').text.strip('\n')
                    date_list = date.split('/')
                    day, month, year = date_list[0], date_list[1], '20' + date_list[2]
                    date_time_obj = datetime.strptime((day + '/' + month + '/' + year), '%d/%m/%Y').date()
                except Exception as ex:
                    print(ex)
                    date_time_obj = " "
                date=date_time_obj
                insert_link_into_bd(category, title, link, author, author_link, finally_text, date)
                print('Заголовок -', title)
                print('Категория -', category)
                print('Ссылка -', link)
                print("Текст статьи:", finally_text)
                print('Автор:', author)
                print('Ссылка на автора:', author_link)
                print('Дата статьи -', date_time_obj)
                print('===============')
                all_site.append({'Category': category,
                                 'Title': title,
                                 'Article_link': link,
                                 'Author': author,
                                 'Author_link': author_link,
                                 'Text': finally_text,
                                 'Date': str(date_time_obj)
                                 })
                time.sleep(7)
    for site in all_site:
        if site not in unique_sites:
            unique_sites.append(site)
    with open('itsec_ru.json', 'w', encoding="utf-8") as file:
        json.dump(all_site, file, indent=4, ensure_ascii=False)


get_itsec_ru_info()