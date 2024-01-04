import asyncio
import aiomysql
import aiohttp
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.4.778 Yowser/2.5 Safari/537.36"
}


async def insert_link_into_bd(pool, title, link, text, date):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                syntext = """Insert into news (Link, Title, Text, Date) values (%s, %s, %s, %s);"""
                value = (link, title, text, date)
                await cursor.execute(syntext, value)
                await conn.commit()
            except aiomysql.Error as err:
                if err.args[0] == 1062:  # Duplicate entry error code
                    print("Duplicate entry, skipping...")
                else:
                    raise


async def fetch_page(session, url):
    async with session.get(url, headers=headers) as response:
        return await response.text()


async def parse_and_insert_news(pool, html_content):
    bs = BeautifulSoup(html_content, 'html.parser')
    cards = bs.find_all('div', class_='news-card mb-4')
    for card in cards:
        title = card.find('div', class_='h4').text
        link = 'https://securitymedia.org' + card.find('a', class_='text-dark').get('href')
        date_list = card.find('div', class_='py-3 date_time font-weight-light').text.strip().split('.')
        date = f"{date_list[2]}-{date_list[1]}-{date_list[0]}"
        description = card.find('div', class_='col-md-8')
        div_tags = description.find_all('div')
        for tag in div_tags:
            tag.decompose()
        text = ' '.join(description.text.strip().split())
        await insert_link_into_bd(pool, title, link, text, date)
        print(title, link, date, text, sep='\n')
        print('------')


async def get_news_from_securitymedia(pool):
    async with aiohttp.ClientSession() as session:
        for page in range(1, 3):
            url = f'https://securitymedia.org/news/?PAGEN_2={page}'
            html_content = await fetch_page(session, url)
            await parse_and_insert_news(pool, html_content)
            await asyncio.sleep(3)


async def main():
    pool = await aiomysql.create_pool(
        host="127.0.0.1",
        user="root",
        password="12345678",
        port=3306,
        db="bot",
        autocommit=True,
        loop=asyncio.get_event_loop()
    )

    await get_news_from_securitymedia(pool)

    pool.close()
    await pool.wait_closed()


asyncio.run(main())
