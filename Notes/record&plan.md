# 20200220
确定工作分工

目前需要做：
加标签页(tab)、学习代码结构调整和部署上线部分的内容并完成
学习记录分享：以后每两天讨论一次，并上传这两天的学习文档

下一步工作如何需要咨询老师：明天上午跟老师讨论



# 20200211

确定一下学习的分工：
- html+css+bootstrap 樊雨萱 胡文博
- javascript 黄文诚 胡文博
- python+flask 樊雨萱 黄文诚
- neo4j 数据库（问老师）
- elastic search怎么用（问老师）

尽快问老师数据接口的事情


# 20200117 寒假开工
寒假整体规划：
- 每3天集中讨论一次（暂定晚8点），期间在微信随时交流。<br>

0117-0120安排：<br>
- fyx整理模板，hwc hwb继续学习flask<br>
- 学习使用Git,参见[廖雪峰的教程](https://www.liaoxuefeng.com/wiki/896043488029600 "liaoxuefeng")

最终的页面设计图：
[view](./view.jpg "view")



# 20191115 找老师
1.用bootstrap提供的模板，一周内完成前端的设计<br>
2.页面设计图可以，资源展示框不用悬浮框，而用tab
3.用elasticsearch堆各种数据进行索引，索引到id然后去数据库里取。

<br>
<br>

# 20191025 week2 讨论记录
## 需求文档

大致结构：
1. 一个搜索框处理所有输入（而非查小知识点在页面A，查学习路径规划在页面B）
2. 对于小知识点，返回：
    - 知识点的解释
    - 一个多层的图，分层展示和此知识点相关的上层概念、下层概念、所属课程、所属书籍、相关信息等。
        - 点击图中任何一个结点，则该结点变成中心结点，知识点解释中的文字也对应新中心结点的解释。
    - 悬浮框：当鼠标悬停/点击左图中某一结点时，分类展示知识点的相关资源：慕课、书籍、大学课程、论文列表
        - 每一类资源只展示TOP1-2的项目，防止用户由于选择过多而不知道该看哪一项。
        - 有readmore选项，可以展开或者跳转去看更多相关资源
        - 悬停在每一个资源项目上，会展示相关项目的特点（如吴恩达的《机器学习》课程适合初学者，数学公式推导少）
        - 点击每一个资源项目，都可以跳转到相应的课程、相应的书籍电子书、论文的地址
3. 对于大概念，返回：
    - 概念的解释
        - 这里增添对大概念整体的描述及学习指导（e.g.数据结构这门课程解决了什么问题，问什么要学这门课）
    - 概念的前置课程、后续课程图
    - 概念的内部结构图，按照纵向的学习时间线展示，每一个结点都链接有相关资源，用于快速跳转
    - 悬浮框：作用同上
4. 后台记录用户查询各个知识点的次数等搜索信息，有搜索记录、收藏知识点、收藏资源列表等选项。

最终的页面设计图：
[view](./view.jpg "view")

## 一些问题
1. 知识图谱中文本的格式，纯文本？markdown？html?
2. 怎么在后台分辨大概念与小概念。
3. 知识图谱中文本的格式，纯文本？markdown？html?（公式怎么展现）

## 功能分析：

一个搜索框处理所有输入。

学习路线规划怎样展示？

以查询词汇“机器学习”为例：  
**首先简明扼要地展示为了学习机器学习，需要学那些前置知识，而学了机器学习，又可以进一步学习哪些后置知识。**  
**然后通过纵向的时间线展示，每一个节点是一个部分**（例如，机器学习中的提升算法）**。每一个部分都分类列出资源。节点之间的组织需要整理。**
对于每一类资源，我们通过某些排序算法选出rank为1的推荐给用户，防止选花眼了（不过展开可看见其他的）  
【待讨论】资源按类别怎么展示。不能单纯梳树状结构。

需求有两种，详细的和概论性的，用户可选

**详细的指导包括对学科进行模块的分割，标记处哪一模块讲了什么问题，对每一模块提供资源。**
资源怎么获取？对于基础的，成熟的课程（数据结构），有现成的网课，论文，课程结构等资源。对于前沿的课程（没有成熟的学科体系），需要通过知识图谱来构建课程结构，据此查找资源，然后进行展示。


**概论性的指导包括对学科整体的描述，学习的整体指导**（如数据结构这门学科解决了什么问题），**学科结构的展示，不需要展示资源。**  
【待讨论】这个的实现方法、是否可行

知识点搜索结果怎么展示：

概念文本+节点网络

节点网络应该展示子概念与父概念以及平级概念。当点击网络中的其他节点时，概念文本随之改变。<br>
<br>
<br>

# 20191022 week1 找老师

## 科研路上的小小进展
- 如何进行下一步的研究？
    - 我们需要做什么
    - 怎么做
    - 找什么资料

## 关于老师的知识图谱
-  图谱中有什么
    - 中英文的概念
    - 概念的解释
    - 概念的父概念子概念
    - 概念的部分先修关系（不是100%准确，概率关系，如80%有这个先修关系）
    - 学院有服务器，校内调试可以用，校内外不通
- 图谱用neo4j的图数据库存储


## 我们要做什么事情
- 不做APP了，做一个适配手机的网页就行。
- 功能：
    - **查询一个概念，展示概念定义，相关概念，在哪些大学课程、慕课课程中出现，在哪些前沿论文中出现，将这些信息综合起来提给用户**。
    - 注：不能在一个页面上展示，组织形式要新颖一些，不能把一堆课全扔给他，规划学习路线（修读顺序、课程先修关系）
    - 实现方式：  
    如学无人驾驶：去知识图谱中找到无人驾驶的概念——无人驾驶是关于xx，xx的学科 =>  
    从一个个概念延伸去找包含这些概念包含在哪些书籍、课程、论文中 =>  
    用户点中一个课程，就展现课程结构、有哪些知识点，学这门课要先学什么再学什么
- **要做一个类似知识引擎的东西，所有的资源都建立跟概念图谱的链接，从概念图谱的概念出发，再找与之相关的课程、书籍、资料，综合地展现给用户**。
- **This week : 写需求文档，列to do list和需求分析、界面设计，然后找老师确定技术路线**。


## 我们可以利用的资源
- 维基百科的知识库
- 慕课/网课
- 图书目录（京东）
- 各大会议论文的paper list【未做】
- 国内（清北）国外大学的课程体系【待做】
    - 课程的描述
        - 用老师的工具,识别一段描述里面的概念,链接到知识图谱上  
    - 课程和课程的先修关系
    - 概念和概念的先修关系
        - 可结合老师抓取的京东书籍目录
- =>**梳理资源、信息的展现形式**。