import asyncio
import aiomysql

async def fetch_categories_and_texts(pool):
    categories = []
    texts = []

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT DISTINCT Category FROM links")
            result = await cur.fetchall()
            categories = [x[0] for x in result]

            await cur.execute("SELECT text FROM links")
            result2 = await cur.fetchall()
            texts = [z[0] for z in result2]

            await cur.execute("TRUNCATE tags")
            await conn.commit()

    return categories, texts

async def insert_tags(pool, categories, texts):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SET FOREIGN_KEY_CHECKS=0")

            for l in categories:
                tag = l if len(l) <= 10 else l[:len(l) // 2 + 4]
                for g in texts:
                    if tag in g:
                        print(tag, texts.index(g) + 1)
                        query = "INSERT INTO tags (tag,linkid) VALUES (%s,%s)"
                        values = (l, texts.index(g) + 1)
                        await cur.execute(query, values)
            await conn.commit()

            await cur.execute("SET FOREIGN_KEY_CHECKS=1")
            await conn.commit()

async def main():
    pool = await aiomysql.create_pool(
        host="127.0.0.1",
        user="root",
        password="12345678",
        port=3306,
        db="bot"
    )

    categories, texts = await fetch_categories_and_texts(pool)
    await insert_tags(pool, categories, texts)

    pool.close()
    await pool.wait_closed()

asyncio.run(main())
