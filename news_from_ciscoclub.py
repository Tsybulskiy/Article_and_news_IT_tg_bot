import asyncio
import aiohttp
import aiomysql
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.4.778 Yowser/2.5 Safari/537.36"
}


async def insert_link_into_db(pool, title, link, text, date):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                syntext = "Insert into news (Link, Title, Text, Date) values (%s, %s, %s, %s);"
                value = (link, title, text, date)
                await cursor.execute(syntext, value)
                await conn.commit()
            except aiomysql.Error as err:
                if err.args[0] == 1062:  # Код ошибки дубликации записи
                    print("Duplicate entry, skipping...")
                else:
                    raise


async def fetch(session, url):
    async with session.get(url, headers=headers) as r:
        return await r.text()


async def get_news_from_cisoclub(pool):
    async with aiohttp.ClientSession() as session:
        for page in range(1, 4):
            response = await fetch(session, f'https://cisoclub.ru/category/news/page/{page}')
            soup = BeautifulSoup(response, "html.parser")
            articles_cards = soup.find_all("div", class_="content-wrap")

            for card in articles_cards:
                link = card.find('h3').find('a').get('href', "Ссылка отсутствует")
                title = card.find('h3').find('a').text.strip() or "Заголовок отсутствует"
                description = card.find('div', class_='entry-content').find('p').text.strip() or "Текст отсутствует"

                try:
                    date_one = card.find('span', class_='posted-date').text.strip()
                    day, month, year = date_one.split('.')
                    date = datetime.strptime((day + '/' + month + '/' + year), '%d/%m/%Y').date()
                except Exception as ex:
                    print(ex)
                    continue

                await insert_link_into_db(pool, title, link, description, date)

                print("Заголовок -", title)
                print("Ссылка -", link)
                print("Дата:", date)
                print("Аннотация:", description)
                print("--------")

            # Ожидаем 3 секунды перед следующим запросом
            await asyncio.sleep(3)


async def main():
    pool = await aiomysql.create_pool(
        host="127.0.0.1",
        user="root",
        password="12345678",
        db="bot",
        port=3306,
        charset="utf8mb4",
        autocommit=True,
        loop=asyncio.get_event_loop()
    )

    try:
        await get_news_from_cisoclub(pool)
    finally:
        pool.close()
        await pool.wait_closed()


asyncio.run(main())
