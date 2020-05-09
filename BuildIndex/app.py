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

def create_course(es):
    es.indices.delete(index='conceptlist', ignore=[400, 404]) 
    es.indices.create(index='conceptlist', ignore=400)

    li = []
    print("loading data from mysql...")
    pdformysql = "123456" # 数据库密码
    dbname = "all_course" # 数据库名称
    db = pymysql.connect("localhost", "root", pdformysql, dbname)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM COURSES")
    data = cursor.fetchall()

    i = 0
    for d in data:
        i += 1
        action = {
            "_index": "uni_course",
            "_type": "course",
            "_source": {
                "id": d[0],
                "name": d[1],
                "url": d[2],
                "school": d[3],
                "instructor": d[4],
                "descript": d[5],
                "topics": d[6],
                "prerequisites": d[7],
                "related_course": d[8],
                "related_course_link": d[9],
                "reference_name": d[10],
                "reference_link": d[11],
                "bianhao": d[12],
                "prereq_name": d[13],
                "children": d[14]
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


def init_es():
    es = Elasticsearch()
    """
    分别将concept, mooc, 我们的course放入es.运行过的再运行可能会重复
    下面的es.search代码是用来验证是否插入成功的
    """
    # create_concept(es)
    # create_mooc(es)
    create_course(es) # 20200509 用于把all_course导入es
    print("begin query, see if create_course() is succussful...")
    dsl = {
        # '_source': {"id"}
        'query': {
            'multi_match': {
                'query':'machine learning',
                'fields': ['name','descript']
            }
        }
    }
    result = es.search(index='uni_course', body=dsl)
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
    def graph_match(self, keyword, rel_type, head = True, limit = 2):
        result = []
        keyword = self.reg(keyword)
        start_node = "start"
        end_node = "end"
        if not head:
            start_node = "end"
            end_node = "start"
        gql = "MATCH (start:WikiConcept)-[rel:" + rel_type + "]->(end:WikiConcept) " \
            "WHERE " + start_node + ".lowwer_label = \"" + keyword + "\" RETURN " + end_node + " LIMIT " + str(limit)
        match_result = self.graph.run(gql).data()
        for item in match_result:
            label = item[end_node].get("lowwer_label")
            if label != keyword:
                result.append(label)
        return result

    def search_isa(self, keyword, limit = 2):
        res1 = self.graph_match(keyword, "Wibi_IsA", limit = limit)
        #res2 = self.graph_match(keyword, "Wordnet_Hypernyms")
        #res3 = self.graph_match(keyword, "WikiData_InstanceOf")
        #res = list(set(res1 + res2 + res3)) # 合并，去重
        return res1

    def search_be_isa_of(self, keyword, limit = 2):
        res1 = self.graph_match(keyword, "Wibi_IsA", head = False, limit = limit)
        #res2 = self.graph_match(keyword, "Wordnet_Hypernyms", head = False)
        #res3 = self.graph_match(keyword, "WikiData_InstanceOf", head = False)
        #res = list(set(res1 + res2 + res3)) # 合并，去重
        return res1

    def search_subclassof(self, keyword, limit = 2):
        return self.graph_match(keyword, "WikiData_SubclassOf", limit = limit)

    def search_superclassof(self, keyword, limit = 2):
        return self.graph_match(keyword, "WikiData_SubclassOf", head = False, limit = limit)

    def search_prerequisite(self, keyword, limit = 5):
        return self.graph_match(keyword, "KGBnu_Ref", limit = limit)

    def search_be_prerequisite_of(self, keyword, limit = 2):
        return self.graph_match(keyword, "KGBnu_Ref", head = False, limit = limit)

    def search_relatedto(self, keyword, limit = 5):
        return self.graph_match( keyword, "KGBnu_RelatedTo", limit = limit)

    @staticmethod
    def pack(keyword, result, rel_type):
        if result is not None:
            return [{"n": {"name": keyword}, "r": {"name": rel_type}, "m": {"name": nodename}} for nodename in result]
        else:
            return None

    def getAll(self, keyword):
        entityRelation = [] # 返回格式按照wangluo.html中的entityRelation的格式,(起始节点n)-[关系r]->(终止节点m)
        _keyword = self.reg(keyword)
        
        be_isa_of_res = self.search_be_isa_of(_keyword) 
        res = [{"n": {"name": nodename.replace("_", " ")}, "r": {"name": "IsA"}, "m": {"name": keyword}} for nodename in be_isa_of_res]
        entityRelation.extend(res)
        be_prerequisite_of_res = self.search_be_prerequisite_of(_keyword) 
        res = [{"n": {"name": nodename.replace("_", " ")}, "r": {"name": "Prerequisite"}, "m": {"name": keyword}} for nodename in be_prerequisite_of_res]
        entityRelation.extend(res)
        
        isa_res = self.search_isa(_keyword)
        res = [{"n": {"name": keyword}, "r": {"name": "IsA"}, "m": {"name": nodename.replace("_", " ")}} for nodename in isa_res]
        entityRelation.extend(res)

        """
        subclassof_res = self.search_subclassof(_keyword)
        res = [{"n": {"name": keyword}, "r": {"name": "SubclassOf"}, "m": {"name": nodename.replace("_", " ")}} for nodename in subclassof_res]
        entityRelation.extend(res)
        superclassof_res = self.search_superclassof(_keyword) 
        res = [{"n": {"name": nodename.replace("_", " ")}, "r": {"name": "SubclassOf"}, "m": {"name": keyword}} for nodename in superclassof_res]
        entityRelation.extend(res)
        """
        prerequisite_res = self.search_prerequisite(_keyword) 
        res = [{"n": {"name": keyword}, "r": {"name": "Prerequisite"}, "m": {"name": nodename.replace("_", " ")}} for nodename in prerequisite_res]
        entityRelation.extend(res)
        
        relatedto_res = self.search_relatedto(_keyword) 
        res = [{"n": {"name": keyword}, "r": {"name": "RelatedTo"}, "m": {"name": nodename.replace("_", " ")}} for nodename in relatedto_res]
        entityRelation.extend(res)

        return entityRelation

def init_neo4j():
    graph = GraphSearch()


if __name__ == "__main__":
    """
    在服务器上初始化时两者都应取消注释
    """
    init_es()
    # init_neo4j()