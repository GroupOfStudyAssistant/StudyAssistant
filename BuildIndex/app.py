import pymysql
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch()
# 为防止插入部分数据后失败，每次运行时如果索引已存在则删除重新创建
# es.indices.delete(index='conceptlist', ignore=[400, 404]) 
es.indices.create(index='conceptlist', ignore=400)

li = []
pdformysql = "123456" # 数据库密码
dbname = "concept_graph" # 数据库名称
db = pymysql.connect("localhost", "root", pdformysql, dbname)
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
        print("Successfully adding data: %d ~ %d..." % (i - 999, i))
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
