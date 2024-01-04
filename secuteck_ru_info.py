import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import asyncio
import aiomysql
import json

config = {
    'host': "127.0.0.1",
    'user': "root",
    'password': "12345678",
    'port': 3306,
    'db': "bot",
}


async def insert_link_into_db(pool, category, title, link, author, author_link, finally_text, date):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute(
                    "Insert into links (Category, Title, Link, Author, Author_link, Text, DATE) "
                    "values (%s, %s, %s, %s, %s, %s, %s);",
                    (category, title, link, author, author_link, finally_text, date)
                )
            except aiomysql.Error as err:
                print(err)
                if err.args[0] == 1062:
                    print("Duplicate entry, skipping...")
                    return
            await conn.commit()


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.text()


async def get_secuteck_ru_info(pool):
    headers = {
        "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.4.778 Yowser/2.5 Safari/537.36")
    }

    unique_sites = []
    all_site = []
    urls = ['https://www.secuteck.ru/articles/tag/комплексная-безопасность/page/']
    async with aiohttp.ClientSession(headers=headers) as session:
        for k in urls:
            for i in range(1, 11):
                url = f"{k}{i}"
                print(url)
                html = await fetch(url, session)
                soup = BeautifulSoup(html, "html.parser")
                articles_cards = soup.find_all("div", class_="span4 widget-span widget-type-cell mb30")

                for card in articles_cards:
                    title = card.find('h3').find('a').text if card.find('h3') else "Заголовок отсутствует"
                    category = card.find('a', class_="topic-button theme").text if card.find('a',
                                                                                             class_="topic-button theme") else "Категория отсутствует"
                    link = card.find('h3').find('a').get('href') if card.find('h3') else "Ссылка отсутствует"
                    date = card.find('div', class_='span12 widget-span widget-type-raw_jinja')
                    date = date.text.strip('\n') if date else " "


                    try:
                        date_list = date.split('/')
                        day, month, year = date_list[0], date_list[1], '20' + date_list[2]
                        date_time_obj = datetime.strptime((day + '/' + month + '/' + year), '%d/%m/%Y').date()
                    except ValueError:
                        print(f"Error parsing date: {date}")
                        date_time_obj = None


                    article_response = await fetch(link, session)
                    article_soup = BeautifulSoup(article_response, "html.parser")
                    text = article_soup.find('div', class_='clear').text if article_soup.find('div',
                                                                                              class_='clear') else "Текст отсутствует"
                    finally_text = ' '.join(text.splitlines()).replace('"', '\"').replace("'", "\\'")

                    author = article_soup.find('a', class_='strong').text if article_soup.find('a',
                                                                                               class_='strong') else "Автор отсутствует"
                    author_link = article_soup.find('p').find('a').get('href') if article_soup.find('p').find(
                        'a') else "Ссылка на автора отсутствует"

                    date = date_time_obj

                    await insert_link_into_db(pool, category, title, link, author, author_link, finally_text, date)

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
                    await asyncio.sleep(7)

    for site in all_site:
        if site not in unique_sites:
            unique_sites.append(site)

    with open('secuteck_ru.json', 'w', encoding="utf-8") as file:
        json.dump(all_site, file, indent=4, ensure_ascii=False)


async def main():
    pool = await aiomysql.create_pool(**config)
    try:
        await get_secuteck_ru_info(pool)
    finally:
        pool.close()
        await pool.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
