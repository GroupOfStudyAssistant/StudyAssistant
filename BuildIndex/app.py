import pymysql
from elasticsearch import Elasticsearch, helpers

user_query = "ethnic group"

es = Elasticsearch()
es.indices.create(index='conceptlist', ignore=400)

db = pymysql.connect("localhost", "root", "123456", "concept_graph")
cursor = db.cursor()
cursor.execute("SELECT * FROM CONCEPT")
data = cursor.fetchall()
for d in data:
    action = {
        "_index": "conceptlist",
        "_type": "condef",
        "_source": {
            "concept": d[1],
            "definition": d[2]
        }
    }
    li.append(action)
db.close()

# 批量插入数据到es
helpers.bulk(es, li)

# 查询
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

