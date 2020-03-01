import pymysql
from elasticsearch import Elasticsearch

db = pymysql.connect("localhost", "root", "123456", "concept_graph")
cursor = db.cursor()
cursor.execute("SELECT * FROM CONCEPT LIMIT 5")
data = cursor.fetchall()
#print(type(data))
#print(data)

#json_data = json.dumps(data)
#print(json_data)

#for d in data:
    # print(d[0], d[1], d[2])
db.close()

es = Elasticsearch()
result = es.indices.create(index='concept', ignore=400)
print(result)