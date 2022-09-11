# 教育学科知识图谱及问答
    功能主要包括学科知识图谱以及题目知识点追踪、关系查询、问答及知识点预测等。
    前端页面参考：https://github.com/qq547276542/Agriculture_KnowledgeGraph，在此表示非常感谢。
    此项目也参考了作者之前的电影图谱：https://github.com/jiangnanboy/movie_knowledge_graph_app，具体细节可参考此项目。
    
## 准备数据及构建实体及关系
    数据为知识点和题目，利用neo4j进行构建。构建方式如https://github.com/jiangnanboy/movie_knowledge_graph_app。
    
## 项目结构
```
.
│
│       
├── edu_kg     // django项目路径
│   ├── Model  // 模型层，用于和neo4j交互，实现查询等核心功能
│   ├── edu_kg   // 用于写页面的逻辑(View)
│   ├── static    // 静态资源
│   ├── templates   // html页面
│   └── util   // 预加载一些数据和模型
.
```

## 功能模块

本地启动django命令：python manage.py runserver (或 edu_kg\run.bat)

打开：http://127.0.0.1:8000/

### 一.学科知识点图谱
    输入学科名将展示整个学科知识体系
![image](https://raw.githubusercontent.com/jiangnanboy/education_knowledge_graph_app/master/img/course.png)

### 二.题目知识点追踪
    输入题目id，可追踪该题目所包含的所有知识点(子知识点 -> 父知识点 -> 根知识点)
![image](https://raw.githubusercontent.com/jiangnanboy/education_knowledge_graph_app/master/img/question.png)

### 三.关系查询
    展示两个知识点间的关系
![image](https://raw.githubusercontent.com/jiangnanboy/education_knowledge_graph_app/master/img/relation.png)

### 四.学知问答

    1.利用分类模型对用户输入的问题进行意图识别
    
    (1).模型的构建及训练见https://github.com/jiangnanboy/intent_classification
    
    (2).总共9个意图类别，如下：
        0:知识点A包含哪些知识点？
        1:包含知识点A的知识点是什么？
        2:知识点A的定义(概念)是什么？(暂无数据)
        3:知识点A怎么计算的(计算方式)？(暂无数据)
        4:包含知识点A的题目有哪些？
        5:包含知识点A的题目还包含哪些知识点?
        6:包含知识点A的题目题型有哪些？
        7:包含知识点A的题目的复杂度如何？
        8:知识点A的知识路径是什么？
    
    (3).意图识别
        这里使用textcnn进行意图识别，具体训练代码见https://github.com/jiangnanboy/intent_classification/tree/master/textcnn
        训练好的model及加载方式在本项目edu_kg/util下。

    2.意图识别后，利用pyhanlp进行实体识别(槽填充)。
    
    3.将识别的意图以及提取的槽位(即识别的实体)转为cypher语言，在neo4j中进行查询得到答案
        利用分类模型预测用户提问的意图类别，将不同的意图类别转换为不同的cypher语言，从neo4j中查询得到答案。
![image](https://raw.githubusercontent.com/jiangnanboy/education_knowledge_graph_app/master/img/qa.png)

### 五.知识点预测

    1.利用多标签分类模型对输入的题目进行知识点标注
    
    (1).多标签模型的构建及训练见https://github.com/jiangnanboy/knowledge-automatic-tagging。
    
    (2).训练好的model及加载方式在edu_kg/util下。
    
![image](https://raw.githubusercontent.com/jiangnanboy/education_knowledge_graph_app/master/img/kp_predict.png)    

  
### `作者的qq，如您有什么想法可以和作者联系：2229029156。`

### `如果您支持作者继续开发更加完善的功能，请动一动手为此项目打个星吧或fork此项目，这是对作者最大的鼓励。` 

### Requirements
    requirement.txt

### References
* https://github.com/jiangnanboy/movie_kg
* https://github.com/qq547276542/Agriculture_KnowledgeGraph
* https://github.com/jiangnanboy/movie_knowledge_graph_app
* https://github.com/jiangnanboy/intent_classification
    
### contact

如有搜索、推荐、nlp以及大数据挖掘等问题或合作，可联系我：

1、我的github项目介绍：https://github.com/jiangnanboy

2、我的博客园技术博客：https://www.cnblogs.com/little-horse/

3、我的QQ号:2229029156
