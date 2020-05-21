# 存放处理搜索词的函数
import os 

from Web import app, es, graph

# 这一部分还没有改太好
# 获取概念解释?
def get_concepts(textforsearch):
    key = "_".join(x.lower() for x in textforsearch.split())
    dsl_concept_1 = {
        'query': {
            'multi_match': {
                'query': key,
                'fields': ['concept', 'definition']
            }
        }
    }
    qresult_concept = es.search(index="conceptlist", body=dsl_concept_1)
    concepts = qresult_concept["hits"]["hits"][0:min(3, len(qresult_concept["hits"]["hits"]))]
    
    """
    if qresult_concept["hits"]["hits"][0]["concept"].lower != key:
        dsl_concept_2 = {
            'query': {
                'multi_match': {
                    'query': textforsearch,
                    'fields': ['concept', 'definition']
                }
            }
        }
        qresult_concept = es.search(index="conceptlist", body=dsl_concept)
        concepts = qresult_concept["hits"]["hits"][0:min(3, len(qresult_concept["hits"]["hits"]))]
    """
    return concepts


# 获取概念图谱(需要改进模糊搜索)
def get_relations(textforsearch):
    relations = graph.getAll(textforsearch)
    return json.dumps(relations)


# 使用ES搜索课程
def get_moocs(textforsearch):
    dsl_mooc = {
        'query': {
            'multi_match': {
                'query': textforsearch,
                'fields': ['name', 'blackboard']
            }
        }
    }
    qresult_mooc = es.search(index="mooc", body=dsl_mooc)
    moocs = qresult_mooc["hits"]["hits"][0:min(5, len(qresult_mooc["hits"]["hits"]))]
    return moocs

    
# 获取课程先修关系
def get_prereqs(textforsearch):
    dsl_uni_course = {
        'query': {
            'match_phrase': {'name': textforsearch} # 短语匹配可以让短语不分开
        }
    }
    qresult_course = es.search(index="uni_course", body = dsl_uni_course)
    if qresult_course["hits"]["total"]["value"]: # match_phrase有结果的话
        print("hits num:", qresult_course["hits"]["total"]["value"])
        course = qresult_course["hits"]["hits"][0] # 暂时取第一个作为展示的结果图，后续可以筛选。
    else: # 否则，重新按照match查询
        dsl_uni_course = {
            'query': {
                'multi_match': {
                    'query': textforsearch,
                    'fields': ['name', 'descript']}
            }
        }
        qresult_course = es.search(index="uni_course", body = dsl_uni_course)

        if qresult_course["hits"]["total"]["value"]:
            print("hits num:", qresult_course["hits"]["total"]["value"])
            course = qresult_course["hits"]["hits"][0]# 暂时取第一个作为展示的结果图，后续可以筛选。
        else:
            course = {"_source": {}}

    with open(os.path.join(os.path.dirname(app.root_path), 'resources/result.json') , 'w') as f:
        json.dump(course["_source"]["children"], f) # 读取时使用json.load(f)
    return course
    