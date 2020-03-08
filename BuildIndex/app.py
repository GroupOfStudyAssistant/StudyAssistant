import pymysql
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch()
es.indices.create(index='conceptlist', ignore=400)

li = []
db = pymysql.connect("localhost", "root", "123456", "concept_graph")
cursor = db.cursor()
cursor.execute("SELECT * FROM CONCEPT")
data = cursor.fetchall()

i = 0
for d in data:
    i += 1
    action = {
        "_index": "conceptlist",
        "_type": "condef",
        "_source": {
            "concept": d[1],
            "definition": d[2]
        }
    }
    li.append(action)
    if i % 1000 == 0:

        # 批量插入数据到es
        helpers.bulk(es, li)
        li = []
        #time.sleep(1)
helpers.bulk(es, li)

db.close()

"""
# 查询，应放在views.py中
user_query = "adobe"
dsl = {
    'query': {
        'multi_match': {
            'query': user_query,
            'fields': ['concept', 'definition']
        }
    }
}
result = es.search(index='conceptlist', doc_type='condef', body=dsl)
print(result)
"""
