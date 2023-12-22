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
                        database="bot",
                        option_files='my.conf',
                        get_warnings=True
                    )

def insert_link_into_bd (category,title,link,author,author_link,finally_text,date):
    cursor = db.cursor(buffered=True)
    try:
        syntext = """Insert into links (Category,Title,link,Author,Author_link,Text, DATE) values (%s,%s,%s,%s,%s,%s,%s);"""
        value = ((category),(title),(link),(author),(author_link),(finally_text),(date))
        cursor.execute(syntext,value)
        db.commit()
    except mysql.connector.Error as err:
        if err.sqlstate == '23000':
            raise err
def get_xaker_info():
    urls = ['https://xakep.ru/category/hack/page/','https://xakep.ru/category/privacy/page/','https://xakep.ru/category/tricks/page/','https://xakep.ru/category/coding/page/','https://xakep.ru/category/admin/page/','https://xakep.ru/category/geek/page/']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    }
    all_site = []
    unique_sites = []
    for url in urls:
        r = requests.get(url=url+'1', headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        amount_pages = int(soup.find('span', class_='pages').text.split('из')[-1])
        category = soup.find('h4', 'block-title').text
        for page in range(1,amount_pages+1):
            r = requests.get(url=url+str(page), headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.find_all('div', class_='block-article-content-wrapper')
            for card in cards:
                try:
                    title = card.find('h3', class_='entry-title').text
                    link = card.find('h3', class_='entry-title').find('a').get('href')
                    list_url = link.split('/')
                    date = list_url[3]+'-'+list_url[4]+'-'+list_url[5]
                    resp = requests.get(url=link, headers=headers)
                    soup_state = BeautifulSoup(resp.text, "html.parser")
                    author = soup_state.find('div', class_='bdaia-post-author-name').find('a').text
                    author_link = soup_state.find('div', class_='bdaia-post-author-name').find('a').get('href')
                    text = soup_state.find('div', class_='bdaia-post-content').text.replace('­','')
                    # if
                    finally_text = r''' '''
                    for tag in text:
                        finally_text += ' '.join(tag.splitlines())
                    finally_text = finally_text.replace('"', '\"')
                    for i in finally_text:
                        i = i.replace("'", "\\'")

                    print('Текст - ',finally_text)
                    print('Автор -', author)
                    print('Ссылка на автора -', author_link)
                    print('Категория -',category)
                    print('Дата статьи -',date)
                    print('Название статьи -',title)
                    print('Ссылка на статью -',link)
                    print('========')
                except Exception as ex:
                    print(ex)
                    continue

                all_site.append({'Category': category,
                                 'Title': title,
                                 'Article_link': link,
                                 'Author': author,
                                 'Author_link': author_link,
                                 'Text': finally_text,
                                 'Date': date
                                 })
                insert_link_into_bd(category, title, link, author, author_link, finally_text, date)
                time.sleep(5)
            time.sleep(5)

    for site in all_site:
        if site not in unique_sites:
            unique_sites.append(site)
    with open('xaker_ru.json', 'w', encoding="utf-8") as file:
        json.dump(unique_sites, file, indent=4, ensure_ascii=False)

get_xaker_info()