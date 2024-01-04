import asyncio
import aiohttp
import aiomysql
from bs4 import BeautifulSoup
from datetime import datetime
import json

async def insert_link_into_db(pool, category, title, link, author, author_link, finally_text, date):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                syntax = """Insert into links (Category, Title, link, Author, Author_link, Text, DATE) values (%s, %s, %s, %s, %s, %s, %s);"""
                await cursor.execute(syntax, (category, title, link, author, author_link, finally_text, date))
                await conn.commit()
            except aiomysql.Error as err:
                print(err)
                if err.sqlstate == '23000':
                    raise err

async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def get_itsec_ru_info():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.1.1138 Yowser/2.5 Safari/537.36"}
    db_config = {
        "host": "127.0.0.1",
        "user": "root",
        "password": "12345678",
        "port": 3306,
        "db": "bot"
    }

    pool = await aiomysql.create_pool(**db_config)
    all_site = []

    async with aiohttp.ClientSession() as session:
        for i in range(1, 34):
            url = f"https://www.itsec.ru/articles/page/{i}"
            print(url)
            page_text = await fetch(session, url, headers)
            soup = BeautifulSoup(page_text, "html.parser")
            articles_cards = soup.find_all("div", class_="span12 widget-span widget-type-cell content-card-text")

            for card in articles_cards:
                # Обработка карточек статей асинхронно
                title = card.find('h3').find('a').text if card.find('h3').find('a') else "Заголовок отсутствует"
                category = card.find('a', class_="topic-button theme").text if card.find('a', class_="topic-button theme") else "Категория отсутствует"
                link = card.find('h3').find('a').get('href') if card.find('h3').find('a') else "Ссылка отсутствует"

                article_text = await fetch(session, link, headers)
                soup_article = BeautifulSoup(article_text, "html.parser")
                text = soup_article.find('div', class_='clear').text if soup_article.find('div', class_='clear') else "Текст отсутствует"
                finally_text = ' '.join(text.splitlines()).replace('"', '\"').replace("'", "\\'")

                author = soup_article.find('a', class_='strong').text if soup_article.find('a', class_='strong') else "Автор отсутствует"
                author_link = soup_article.find('p').find('a').get('href') if soup_article.find('p').find('a') else "Ссылка на автора отсутствует"

                date_str = card.find('div', class_='span12 widget-span widget-type-raw_jinja').text.strip('\n') if card.find('div', class_='span12 widget-span widget-type-raw_jinja') else " "
                date_time_obj = datetime.strptime(date_str, '%d/%m/%y').date() if date_str.strip() else None

                await insert_link_into_db(pool, category, title, link, author, author_link, finally_text, date_time_obj)

                all_site.append({
                    'Category': category,
                    'Title': title,
                    'Article_link': link,
                    'Author': author,
                    'Author_link': author_link,
                    'Text': finally_text,
                    'Date': str(date_time_obj)
                })

                await asyncio.sleep(7)  # Искусственная задержка для соблюдения вежливости

    pool.close()
    await pool.wait_closed()

    with open('itsec_ru.json', 'w', encoding="utf-8") as file:
        json.dump(all_site, file, indent=4, ensure_ascii=False)

# Запуск асинхронного сборщика информации
asyncio.run(get_itsec_ru_info())
