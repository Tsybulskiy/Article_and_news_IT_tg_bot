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
        syntext = """Insert into links (Category,Title,Article_link,Author,Author_link,Text, DATE) values (%s,%s,%s,%s,%s,%s,%s);"""
        value = ((category),(title),(link),(author),(author_link),(finally_text),(date))
        cursor.execute(syntext,value)
        db.commit()
    except mysql.connector.Error as err:
        if err.sqlstate == '23000': raise err

def get_codeby_net_data():

    unique_sites = []
    all_site = []
    urls = ['https://codeby.net/articles/categories/informac-bezopasnost.5/page-',
            'https://codeby.net/articles/categories/ctf.18/page-',
            'https://codeby.net/articles/categories/kali-linux.15/page-',
            'https://codeby.net/articles/categories/lotus.25/page-',
            'https://codeby.net/articles/categories/metasploit-framework.24/page-',
            'https://codeby.net/articles/categories/anonimnost-v-seti.3/page-',
            'https://codeby.net/articles/categories/audit-bezopasnosti.13/page-',
            'https://codeby.net/articles/categories/darknet.1/page-',
            'https://codeby.net/articles/categories/zaschita-informacii.4/page-',
            'https://codeby.net/articles/categories/kiberataka.6/page-',
            'https://codeby.net/articles/categories/kriptografija.16/page-',
            'https://codeby.net/articles/categories/mobilnyj-pentest.14/page-',
            'https://codeby.net/articles/categories/nastrojka-linuks.21/page-',
            'https://codeby.net/articles/categories/ni-webom-edinym.22/page-',
            'https://codeby.net/articles/categories/novosti-ib.26/page-',
            'https://codeby.net/articles/categories/pentest.2/page-',
            'https://codeby.net/articles/categories/programmirovanie.20/page-',
            'https://codeby.net/articles/categories/programmirovanie-python.10/page-',
            'https://codeby.net/articles/categories/sbor-informacii-osint.12/page-',
            'https://codeby.net/articles/categories/ujazvimosti-wifi.23/page-',
            'https://codeby.net/articles/categories/forenzika-forensics.8/page-',
            'https://codeby.net/articles/categories/shifrovanie-dannyx.11/page-']
    try:
        # driver = uc.Chrome(headless=True)
        chrome_options = uc.ChromeOptions()  # добавить юзер-агент
        # chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
        #chrome_options.add_argument('--proxy-server=ip:port')
        driver = uc.Chrome(options=chrome_options, version_main=111) #,headless=True
        time.sleep(15)
        for url in urls:
            driver.get(url+str(1))
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, "html.parser")
            page_elem = soup.find('a', class_='pageNavSimple-el pageNavSimple-el--current')
            if page_elem is not None:
                page_count = int(page_elem.text.split('из')[-1])
            else:
                page_count = 2
            category = soup.find('h1', class_='p-title-value').text
            for i in range(1, page_count + 1):
                driver.get(url+str(i))
                time.sleep(3)
                html_source = driver.page_source
                soup = BeautifulSoup(html_source, "html.parser")
                all_cards = soup.find_all('div', class_='porta-article-item')
                for card in all_cards:
                    link = 'https://codeby.net' + (card.find('h2', class_='block-header').find('a').get('href'))
                    title_a = card.find('h2', class_='block-header').find('a')
                    span = title_a.find('span')
                    if span is not None:
                        span.decompose()
                        title = title_a.text.strip()
                    else:
                        title = title_a.text.strip()
                    try:
                        date = card.find('time', class_='u-dt').get('data-date-string')
                        date_list = date.split('.')
                        day, month, year = date_list[0], date_list[1], date_list[2]
                        date_time_obj = datetime.strptime((day + '/' + month + '/' + year), '%d/%m/%Y').date()
                    except Exception as ex:
                        date_time_obj = " "
                    driver.get(link)
                    html_source_state = driver.page_source
                    soup_state = BeautifulSoup(html_source_state, "html.parser")
                    author = soup_state.find('div', class_='p-description').find('a').text
                    author_link = 'https://codeby.net'+ soup_state.find('div', class_='p-description').find('a').get('href')
                    text = soup_state.find('div', class_='bbWrapper').text
                    finally_text = r''' '''
                    for tag in text:
                        finally_text += ' '.join(tag.splitlines())
                        # print(tag)
                    finally_text = finally_text.replace('"', '\"')
                    for i in finally_text:
                        i = i.replace("'", "\\'")
                    date=date_time_obj
                    try:
                        insert_link_into_bd(category, title, link, author, author_link, finally_text, date)
                    except mysql.connector.Error as err:
                        if err.sqlstate == '23000': raise err
                    print('Текст статьи -', finally_text)
                    print('Автор -', author)
                    print('Ссылка на автора -', author_link)
                    print('Категория статьи -', category)
                    print('Заголовок статьи -', title)
                    print('Ссылка на статью -', link)
                    print('Дата статьи -', date_time_obj)
                    print('='*10)
                    all_site.append({'Category': category,
                                     'Title': title,
                                     'Article_link': link,
                                     'Author': author,
                                     'Author_link': author_link,
                                     'Text': finally_text,
                                     'Date': date_time_obj
                                     })
                time.sleep(5)
            time.sleep(5)
    except Exception as ex:...
    finally:
        driver.quit()

    for site in all_site:
        if site not in unique_sites:
            unique_sites.append(site)
    with open('codeby_net.json', 'w', encoding="utf-8") as file:
        json.dump(all_site, file, indent=4, ensure_ascii=False)
get_codeby_net_data()