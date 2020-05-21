import io, math
import numpy as np
import pymysql
from elasticsearch import Elasticsearch, helpers
from py2neo import Graph, Node, Relationship

vec = {} # 设置为全局变量

# 读取词向量的函数
def load_vectors(fname):
    """
    返回一个dict
    形式是{"word": [1.3, 1.5, ..., 1.9], "next_word": [1.4, 1.5, ..., 2.0], ....}
    """
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, fin.readline().split()) # map()做映射，返回元素的迭代器.读取文件第一行的total_token和vec_size
    data = {}
    i = 0
    for line in fin:
        i += 1
        if i % 1000 == 0:
            print("load %d items..."%i)
        tokens = line.rstrip().split(' ') # split()函数返回列表
        data[tokens[0]] = list(map(float, tokens[1:]))
        #print(tokens[0])
        #print(data[tokens[0]])
    return data

def create_concept(es, dbname, pdformysql): # 特别耗时
    """
    pdformysql = "123456" # 数据库密码
    dbname = "concept_graph" # 数据库名称
    """
    # 为防止插入部分数据后失败，每次运行时如果索引已存在则删除重新创建
    es.indices.delete(index='conceptlist', ignore=[400, 404]) 
    es.indices.create(index='conceptlist', ignore=400)

    li = []
    print("loading data from mysql...")
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

def create_mooc(es, dbname, pdformysql):

    es.indices.delete(index='mooc', ignore=[400, 404]) 
    es.indices.create(index='mooc', ignore=400)

    li = []
    print("loading data from mysql...")
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

def create_course(es, dbname, pdformysql):
    es.indices.delete(index='uni_course', ignore=[400, 404]) 
    es.indices.create(index='uni_course', ignore=400)

    li = []
    print("loading data from mysql...")
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
    create_concept(es, "concept_graph", "123456")
    create_mooc(es, "concept_graph", "123456")
    create_course(es, "all_course", "123456") # 用于把all_course导入es

    # 测试是否导入成功，也可以在kibana-management-index处查看
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

    # 包装格式
    @staticmethod
    def pack(keyword, result, rel_type):
        if result is not None:
            return [{"n": {"name": keyword}, "r": {"name": rel_type}, "m": {"name": nodename}} for nodename in result]
        else:
            return None

    # 相似度计算
    @staticmethod
    def cosine_similarity(x, y):
        # assert len(x) == len(y), "len(x) != len(y)"
        # assuming that x, y are lists with same dimesion
        zero_list = [0] * len(x)
        if x == zero_list or y == zero_list:
            return float(1) if x == y else float(0)
    
        res = np.array([[x[i] * y[i], x[i] * x[i], y[i] * y[i]] for i in range(len(x))])
        cos = sum(res[:, 0]) / (np.sqrt(sum(res[:, 1])) * np.sqrt(sum(res[:, 2])))
    
        return cos
        #return 0.5 * cos + 0.5 if norm else cos 

    @staticmethod
    def phrase_vec(phrase):
        # 返回向量表示的list
        global vec
        total_vec = np.array([0.0]*300) # 需设置成float64类型的
        for word in phrase.split():
            try:
                total_vec += np.array(vec.get(word))
            except: # 如果词表中没有
                total_vec += np.array([0.0]*300)
        return list(np.around(total_vec, decimals=4)) # 按照原数据格式归一到小数点后四位

    @staticmethod
    def cal_sim(phrase1, phrase2):
        vec1 = phrase_vec(phrase1)
        vec2 = phrase_vec(phrase2)
        return cosine_similarity(vec1, vec2)

    @staticmethod
    def wrap_preq(keyword, nodename):
        return [{"n": {"name": keyword}, "r": {"name": "Prerequisite"}, "m": {"name": nodename}}]
    
    @staticmethod
    def wrap_be_preq(keyword, nodename):
        return [{"n": {"name": nodename}, "r": {"name": "Prerequisite"}, "m": {"name": keyword}}]

    def BFS(self, keyword, result, limit = 2, depth = 3, pre = True):
        print("keyword=", keyword, "depth=", depth, "result=",result)
        # keyword有_
        if(depth == 0):
            return None # 什么都不做。
        if pre:
            prerequisite_res = self.search_prerequisite(keyword, limit = 1000000) # 向前扩展, 返回名字的list
        else:
            prerequisite_res = self.search_be_prerequisite_of(keyword,  limit = 1000000) # 向后扩展
        if prerequisite_res is not None:
            #print("preq:", prerequisite_res)
            #sim_list = [cal_sim(i, keyword) for i in prerequisite_res] # 得到每个preq与当前节点的相似度
            #sorted_sim = sorted(range(len(sim_list)), key = lambda x:sim_list[x], reverse=True) # 从大到小排序后的index
            #nodes = [prerequisite_res[sorted_sim[i]] for i in range(limit)] # 返回最相似的limit个节点的list
            nodes = [prerequisite_res[i] for i in range(min(len(prerequisite_res), limit))]
            #print("nodes:", nodes)
            for node in nodes:
                if depth != 3:# 跟中心节点相连的边不重复加入
                    if pre:
                        result.append(self.wrap_preq(keyword.replace("_", " "), node.replace("_", " ")))
                    else:
                        result.append(self.wrap_be_preq(keyword.replace("_", " "), node.replace("_", " ")))
                #print("result:", result)
                # 所有的节点都要继续BFS
                self.BFS(node, result, depth = depth-1)
        # 如果搜索结果为空，则自动返回上一层传进来的result            
        return result # None就行

    def getBFSPre(self, keyword, limit = 2,depth = 3):
        """
        对每个节点，向前取三层(depth)先修节点，向后取三层后置节点，每一层只保留相似度最大的两个(limit)并从这两个扩展
        最终return也应该是一个list，包含若干(起始节点n)-[关系r]->(终止节点m)形式的字典
        问题：如何使用vec？先假设现在有vec了吧
        """
        global vec
        _keyword = self.reg(keyword) # 搜索输入无_，neo4j中有_，输出到无_
        print("begin prenodes:")
        prenodes = self.BFS(_keyword, [])
        print("begin afternodes:")
        afternodes = self.BFS(_keyword, [], pre = False)
        print("prenodes:", prenodes)
        print("afternodes:", afternodes)
        return prenodes + afternodes

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

"""
# 词向量数据，读取需要10分钟
print("start loading word vectors, may takes 10 minutes...")
fname = r'E:\KGProject\wiki-news-300d-1M\wiki-news-300d-1M.vec'
vec = load_vectors(fname)
"""
if __name__ == "__main__":
    """
    在服务器上直接运行本文件进行初始化时两者都应取消注释
    import本文件时init_es()代码不会被执行
    """
    # init_es()
    init_neo4j() # 其实没用，__init__.py中引用的是类而非实例
