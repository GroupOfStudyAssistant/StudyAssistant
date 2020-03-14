import pymysql
from elasticsearch import Elasticsearch, helpers

def create_concept(es):
    # 为防止插入部分数据后失败，每次运行时如果索引已存在则删除重新创建
    es.indices.delete(index='conceptlist', ignore=[400, 404]) 
    es.indices.create(index='conceptlist', ignore=400)

    li = []
    print("loading data from mysql...")
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

def create_mooc(es):

    es.indices.delete(index='mooc', ignore=[400, 404]) 
    es.indices.create(index='mooc', ignore=400)

    li = []
    print("loading data from mysql...")
    pdformysql = "7h43rmd2" # 数据库密码
    dbname = "testforsa" # 数据库名称
    db = pymysql.connect("localhost", "root", pdformysql, dbname)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM MOOC")
    data = cursor.fetchall()

    i = 0
    for d in data:
        i += 1
        action = {
            "_index": "mooc",
            "_type": "mooccourse",
            "_source": {
                "id": d[0],
                "name": d[1],
                "chinese_name": d[2],
                "duration": d[3],
                "platform": d[4],
                "school": d[5],
                "blackboard": d[7],
                "depts": d[8]
            }
        }
        li.append(action)
    helpers.bulk(es, li)
    db.close()

if __name__ == "__main__":
    es = Elasticsearch()
    # create_concept(es)
    create_mooc(es)
    print("begin query, see if create_mooc() is succussful...")
    dsl = {
        # '_source': {"id"}
        'query': {
            'multi_match': {
                'query':'programming',
                'fields': ['name', 'blackboard']
            }
        }
    }
    result = es.search(index='mooc', body=dsl)
    print(result)
