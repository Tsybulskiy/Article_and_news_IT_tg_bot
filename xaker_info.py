import aiohttp
import asyncio
from bs4 import BeautifulSoup
import aiomysql
import json


async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()


async def insert_link_into_db(connection, category, title, link, author, author_link, finally_text, date):
    async with connection.cursor() as cursor:
        try:
            syntax = """Insert into links (Category, Title, link, Author, Author_link, Text, DATE) values (%s, %s, %s, %s, %s, %s, %s);"""
            await cursor.execute(syntax, (category, title, link, author, author_link, finally_text, date))
            await connection.commit()
        except aiomysql.Error as err:
            if err.args[0] == 1062:  # Duplicate entry error code
                print("Duplicate entry found.")
            else:
                raise err


async def get_xaker_info(loop):
    urls = ['https://xakep.ru/category/hack/page/', 'https://xakep.ru/category/privacy/page/',
            'https://xakep.ru/category/tricks/page/', 'https://xakep.ru/category/coding/page/',
            'https://xakep.ru/category/admin/page/', 'https://xakep.ru/category/geek/page/']
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    }

    # Setup database connection
    connection = await aiomysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="12345678",
        db="bot",
        loop=loop
    )

    async with aiohttp.ClientSession() as session:
        for url in urls:
            initial_page_html = await fetch(session, url + '1', headers)
            initial_page_soup = BeautifulSoup(initial_page_html, 'html.parser')
            amount_pages = int(initial_page_soup.find('span', class_='pages').text.split('из')[-1])
            category = initial_page_soup.find('h4', 'block-title').text

            for page in range(1, amount_pages + 1):
                page_html = await fetch(session, url + str(page), headers)
                page_soup = BeautifulSoup(page_html, 'html.parser')
                cards = page_soup.find_all('div', class_='block-article-content-wrapper')

                for card in cards:
                    try:
                        title = card.find('h3', class_='entry-title').text.strip()
                        link = card.find('h3', class_='entry-title').find('a').get('href')
                        list_url = link.split('/')
                        date = list_url[3] + '-' + list_url[4] + '-' + list_url[5]
                        article_html = await fetch(session, link, headers)
                        article_soup = BeautifulSoup(article_html, 'html.parser')
                        author = article_soup.find('div', class_='bdaia-post-author-name').find('a').text
                        author_link = article_soup.find('div', class_='bdaia-post-author-name').find('a').get('href')
                        text = article_soup.find('div', class_='bdaia-post-content').text.replace('­', '')
                        finally_text = ' '.join(text.splitlines())
                        finally_text = finally_text.replace('"', '\\"').replace("'", "\\'")

                        await insert_link_into_db(connection, category, title, link, author, author_link, finally_text,
                                                  date)
                    except Exception as ex:
                        print(ex)
                        continue

                    await asyncio.sleep(5)
                await asyncio.sleep(5)

    await connection.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(get_xaker_info(loop))
