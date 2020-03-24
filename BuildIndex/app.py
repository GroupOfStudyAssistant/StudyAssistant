import pymysql
from elasticsearch import Elasticsearch, helpers
from py2neo import Graph, Node, Relationship

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

def init_es():
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

class GraphSearch:

    def __init__(self):
        self.graph = Graph(
            "http://localhost:7474", 
            username = "neo4j", 
            password = "123456"
        )

    # 转化为全小写下划线，与数据库中lowwer_label一致
    @staticmethod # 静态方法装饰器
    def reg(query_str):
        return "_".join(x.lower() for x in query_str.split())

    # 匹配，返回节点数组
    def graph_match(self, keyword, rel_type):
        result = []
        keyword = self.reg(keyword)
        gql = "MATCH (start:WikiConcept)-[rel:" + rel_type + "]->(end:WikiConcept) " \
            "WHERE start.lowwer_label = \"" + keyword + "\" RETURN end"
        match_result = self.graph.run(gql).data()
        for item in match_result:
            label = item['end'].get("label")
            result.append(label)
        return result

    def search_isa(self, keyword):
        res1 = self.graph_match(keyword, "Wibi_IsA")
        res2 = self.graph_match(keyword, "Wordnet_Hypernyms")
        res3 = self.graph_match(keyword, "WikiData_InstanceOf")
        res = list(set(res1 + res2 + res3)) # 合并，去重
        return res
    
    def search_subclassof(self, keyword):
        return self.graph_match(keyword, "WikiData_SubclassOf")

    def search_prerequisite(self, keyword):
        return self.graph_match(keyword, "KGBnu_Ref")

    def search_relatedto(self, keyword):
        return self.graph_match( keyword, "KGBnu_RelatedTo")

    def getAll(self, keyword):
        entityRelation = [] # 返回格式按照wangluo.html中的entityRelation的格式

        isa_res = self.search_isa(keyword)
        res = [{"r": {"name": "IsA"}, "m": {"name": nodename}} for nodename in isa_res]
        entityRelation.extend(res)

        subclassof_res = self.search_subclassof(keyword)
        res = [{"r": {"name": "IsA"}, "m": {"name": nodename}} for nodename in subclassof_res]
        entityRelation.extend(res)
        
        prerequisite_res = self.search_prerequisite(keyword)
        res = [{"r": {"name": "Prerequisite"}, "m": {"name": nodename}} for nodename in prerequisite_res]
        entityRelation.extend(res)

        relatedto_res = self.search_relatedto(keyword)
        res = [{"r": {"name": "RelatedTo"}, "m": {"name": nodename}} for nodename in relatedto_res]
        entityRelation.extend(res)

        return entityRelation

def init_neo4j():
    graph = GraphSearch()


if __name__ == "__main__":
    # init_es()
    init_neo4j()