import asyncio
import aiomysql
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import json


async def fetch(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.text()


async def insert_link_into_db(pool, category, title, link, author, author_link, finally_text, date):
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            try:
                syntax = """Insert into links (Category, Title, link, Author, Author_link, Text, DATE) values (%s, %s, %s, %s, %s, %s, %s);"""
                await cursor.execute(syntax, (category, title, link, author, author_link, finally_text, date))
                await connection.commit()
            except aiomysql.Error as err:
                if err.args[0] == 1062:  # Duplicate entry error code
                    print("Duplicate entry found.")
                else:
                    raise


async def get_safe_surf_ru_data(loop):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.1.1138 Yowser/2.5 Safari/537.36"
    }

    all_site = []

    urls = ['https://safe-surf.ru/article/?PAGEN_1=']
    pool = await aiomysql.create_pool(
        host="127.0.0.1",
        user="root",
        password="12345678",
        port=3306,
        db="bot",
        loop=loop
    )

    async with aiohttp.ClientSession() as session:
        for base_url in urls:
            for i in range(1, 8):
                url = f"{base_url}{i}"
                print(url)
                page_html = await fetch(session, url, headers)

                soup = BeautifulSoup(page_html, "html.parser")
                articles_cards = soup.find_all("article", class_="articles__card change-shadow")

                for card in articles_cards:
                    category = card.find('div', class_="articles__tags tags") \
                        .find('a', class_="articles__tag tag").text \
                        if card.find('div', class_="articles__tags tags") else "Категория отсутствует"
                    title = card.find('h2').find('a').text if card.find('h2') else "Заголовок отсутствует"
                    link = 'https://safe-surf.ru' + card.find('h2').find('a').get('href') if card.find(
                        'h2') else "Ссылка отсутсвует"

                    article_html = await fetch(session, link, headers)
                    article_soup = BeautifulSoup(article_html, "html.parser")
                    text = article_soup.find('div', class_='container article__container').text if article_soup.find(
                        'div', class_='container article__container') else "Текст отсутствует"
                    cleaned_text = ' '.join(text.splitlines()).replace('"', '\\"').replace("'", "\\'")

                    author = article_soup.find('a', class_='articles__author-link').text if article_soup.find('a',
                                                                                                              class_='articles__author-link') else "Автор отсутствует"
                    author_link = 'https://safe-surf.ru' + article_soup.find('a', class_="articles__author-link").get(
                        'href') if article_soup.find('a',
                                                     class_='articles__author-link') else "Cсылка на автора отсутствует"

                    date_text = card.find('div', class_='item__date').text.strip('\n') if card.find('div',
                                                                                                    class_='item__date') else None
                    date_list = date_text.split('.') if date_text else None
                    date_time_obj = datetime.strptime('/'.join(date_list), '%d/%m/%Y').date() if date_list else None

                    await insert_link_into_db(pool, category, title, link, author, author_link, cleaned_text,
                                              date_time_obj)

                    print('Заголовок:', title)
                    print('Категория:', category)
                    print('Ссылка:', link)
                    print('Текст статьи:', cleaned_text)
                    print('Автор:', author)
                    print('Ссылка на автора:', author_link)
                    print('Дата статьи:', date_time_obj)
                    print('===============')

                    data = {
                        'Category': category.capitalize(),
                        'Title': title,
                        'Article_link': link,
                        'Author': author,
                        'Author_link': author_link,
                        'Text': cleaned_text,
                        'Date': date_time_obj.strftime('%Y-%m-%d') if date_time_obj else None
                    }
                    all_site.append(data)

                    await asyncio.sleep(7)
    pool.close()
    await pool.wait_closed()

    with open('safe-surf_ru.json', 'w', encoding="utf-8") as file:
        json.dump(all_site, file, indent=4, ensure_ascii=False)


loop = asyncio.get_event_loop()
loop.run_until_complete(get_safe_surf_ru_data(loop))
