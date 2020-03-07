import pymysql
from elasticsearch import Elasticsearch

user_query = "ethnic group"

es = Elasticsearch()
es.indices.create(index='conceptlist', ignore=400)

db = pymysql.connect("localhost", "root", "123456", "concept_graph")
cursor = db.cursor()
cursor.execute("SELECT * FROM CONCEPT")
data = cursor.fetchall()
i = 0
for d in data:
    print(i)
    i += 1
    dict = {}
    dict['concept'] = d[1]
    dict['definition'] = d[2]
    result = es.index(index='conceptlist', doc_type='condef', body=dict)
    #print(result)
db.close()


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

