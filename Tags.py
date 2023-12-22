import mysql.connector
db = mysql.connector.connect(
                        host="127.0.0.1",
                        user="root",
                        password="12345678",
                        port="3306",
                        database="bot"
                    )
cursor = db.cursor(buffered=True)
category = "SELECT Distinct Category FROM links "
cursor.execute(category)
result = cursor.fetchall()
categories = []
for x in result:
    for c in x:
        categories.append(c)
text="select text from links"
cursor.execute(text)
result2 = cursor.fetchall()
texts = []
query2="Truncate tags"
cursor.execute((query2))
for z in result2:
    for v in z:
        texts.append(v)
for l in categories:
    tag=l
    if len(l)>10:
        long=len(l)//2+4
        tag=l[:long]
    for g in texts:
        if tag in g:
            print(tag,texts.index(g)+1)
            foreign_checks_zero="SET FOREIGN_KEY_CHECKS=0"
            cursor.execute(foreign_checks_zero)
            query="Insert into tags (tag,linkid) values (%s,%s)"
            values=(l,texts.index(g)+1)
            cursor.execute(query, values)
            db.commit()
foreign_checks_one="SET FOREIGN_KEY_CHECKS=1"
cursor.execute(foreign_checks_one)