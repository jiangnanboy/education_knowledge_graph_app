# -*- coding: utf-8 -*-
from py2neo import Graph,NodeMatcher

class KnowledgePoint():
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Question():
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Neo4j_Handle():
	graph = None
	matcher = None
	def __init__(self):
		pass

	def connectNeo4j(self):
		self.graph = Graph("http://127.0.0.1:7474", username="neo4j", password="123")
		self.matcher = NodeMatcher(self.graph)

	# 一.科目知识点大全
	def course_knowledgepoint(self, name) -> list:
		'''
        查找该course包含的所有知识点
        :param name:
        :return:
        '''
		data = self.graph.run(
			"match path=(source:KnowledgePoint)-[:BELONG_TO*..]->(target:KnowledgePoint)  where target.name = $name " +
			"return relationships(path) as relationships", name=name)
		knowledgePointDict = {}  # 知识点
		course_to_knowledgepoint = {}  # 三元组
		while data.forward():
			cursor = data.current
			for relation in cursor['relationships']:

				# source node
				source_node = relation.start_node
				source_node_id = source_node['id']
				#source_node_label = str(source_node.labels).strip(":")
				source_node_name = source_node['name']

				# relationship type
				relation_type = list(relation.types())[0]

				# target node
				target_node = relation.end_node
				target_node_id = target_node['id']
				#target_node_label = str(target_node.labels).strip(":")
				target_node_name = target_node['name']

				# 三元组关系
				if source_node_id in course_to_knowledgepoint.keys():
					target_dict = course_to_knowledgepoint.get(source_node_id)
					target_dict.setdefault(target_node_id, relation_type)
				else:
					target_dict = {target_node_id: relation_type}
					course_to_knowledgepoint[source_node_id] = target_dict
				# 节点
				if source_node_id not in knowledgePointDict.keys():
					knowledgePoint = KnowledgePoint(source_node_id, source_node_name)
					knowledgePointDict[source_node_id] = knowledgePoint
				if target_node_id not in knowledgePointDict.keys():
					knowledgePoint = KnowledgePoint(target_node_id, target_node_name)
					knowledgePointDict[target_node_id] = knowledgePoint
		# 三元组以dict形式存储，便于转为json格式
		json_list = []
		for source_key, value in course_to_knowledgepoint.items():
			for target_key, rel_type in value.items():
				knowledgepoint_dict = {}
				knowledgepoint_dict['source'] = knowledgePointDict.get(source_key).name
				knowledgepoint_dict['rel_type'] = rel_type
				knowledgepoint_dict['target'] = knowledgePointDict.get(target_key).name
				json_list.append(knowledgepoint_dict)

		'''
        print("关系数：{}".format(len(josn_list)))
        #打印
        [print('{}-[{}]->{}'.format(knowledgePointDict.get(source_key).name, rel_type, knowledgePointDict.get(target_key).name))
        for source_key,value in course_to_knowledgepoint.items() for target_key, rel_type in value.items()]
        '''
		return json_list

	# 二.题目所包含知识点追溯
	def question_knowledgepoint(self, question_id) -> list:
		'''
        查找该题目包含的所有知识点以及知识点的父知识点
        :param graph:
        :param question_id:
        :return:
        '''
		data = self.graph.run(
			"match path=(q:Question)-[include:INCLUDE_A]->(k1:KnowledgePoint)-[belong_to:BELONG_TO*..]->(k2:KnowledgePoint) "
			"where q.id = $id return relationships(path) as relationships",
			id=question_id)

		knowledgePointDict = {}  # 知识点
		questionDict = {}  # 题目
		question_to_knowledgepoint = {}  # 三元组
		while data.forward():
			cursor = data.current
			for relation in cursor['relationships']:
				source_node = relation.start_node
				target_node = relation.end_node
				source_node_id = source_node['id']
				target_node_id = target_node['id']
				relation_type = list(relation.types())[0]
				source_node_label = str(source_node.labels).strip(":")
				#target_node_label = str(target_node.labels).strip(":")
				source_node_name = source_node['name']
				target_node_name = target_node['name']
				# 存储三元组关系
				if source_node_id in question_to_knowledgepoint.keys():
					target_dict = question_to_knowledgepoint.get(source_node_id)
					target_dict.setdefault(target_node_id, relation_type)
				else:
					target_dict = {target_node_id: relation_type}
					question_to_knowledgepoint[source_node_id] = target_dict
				# 存储节点
				if ("Question" == source_node_label) and (source_node_id not in questionDict.keys()):
					question = Question(source_node_id, source_node_name)
					questionDict[source_node_id] = question
				elif ("KnowledgePoint" == source_node_label) and (source_node_id not in knowledgePointDict.keys()):
					knowledgePoint = KnowledgePoint(source_node_id, source_node_name)
					knowledgePointDict[source_node_id] = knowledgePoint
				if target_node_id not in knowledgePointDict.keys():
					knowledgePoint = KnowledgePoint(target_node_id, target_node_name)
					knowledgePointDict[target_node_id] = knowledgePoint
		# 三元组以dict形式存储，便于转为json格式
		json_list = []
		# 打印
		for source_key, value in question_to_knowledgepoint.items():
			for target_key, rel_type in value.items():
				if "INCLUDE_A" == rel_type:  # 题目包含
					question_dict = {}
					question_dict['source'] = questionDict.get(source_key).name
					question_dict['rel_type'] = rel_type
					question_dict['target'] = knowledgePointDict.get(target_key).name
					json_list.append(question_dict)
				# print('{} - [{}] -> {}'.format(questionDict.get(source_key).name, rel_type, knowledgePointDict.get(target_key).name))
				elif "BELONG_TO" == rel_type:  # 知识点属于
					knowledgepoint_dict = {}
					knowledgepoint_dict['source'] = knowledgePointDict.get(source_key).name
					knowledgepoint_dict['rel_type'] = rel_type
					knowledgepoint_dict['target'] = knowledgePointDict.get(target_key).name
					json_list.append(knowledgepoint_dict)
				# print('{} - [{}] -> {}'.format(knowledgePointDict.get(source_key).name, rel_type, knowledgePointDict.get(target_key).name))
		'''
        print("关系数：{}".format(len(json_list)))
        for i in range(len(json_list)):
            print("{}-[{}]->{}".format(json_list[i]['source'], json_list[i]['rel_type'], json_list[i]['target']))
        '''
		return json_list

	# 三.关系查询为1度关系
	# 1.关系查询:实体1(与实体1有直接关系的实体与关系)
	def findRelationByEntity1(self,entity1):
		answer = self.graph.run(
			"match (source:KnowledgePoint)-[rel]-(target)  where source.name = $name " +
			"return rel ", name=entity1).data()

		answer_list = []
		for an in answer:
			result = {}
			rel = an['rel']
			relation_type = list(rel.types())[0]
			start_name = rel.start_node['name']
			end_name = rel.end_node['name']
			result["source"] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)

		return answer_list

	# 2.关系查询：实体2
	def findRelationByEntity2(self,entity1):
		answer = self.graph.run(
			"match (source)-[rel]-(target:KnowledgePoint)  where target.name = $name " +
			"return rel ", name=entity1).data()

		answer_list = []
		for an in answer:
			result = {}
			rel = an['rel']
			relation_type = list(rel.types())[0]
			start_name = rel.start_node['name']
			end_name = rel.end_node['name']
			result["source"] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)

		return answer_list

	# 3.关系查询：实体1+关系
	def findOtherEntities(self,entity1,relation):
		answer = self.graph.run(
			"match (source:KnowledgePoint)-[rel:" + relation + "]->(target)  where source.name = $name " +
			"return rel ", name=entity1).data()

		answer_list = []
		for an in answer:
			result = {}
			rel = an['rel']
			relation_type = list(rel.types())[0]
			start_name = rel.start_node['name']
			end_name = rel.end_node['name']
			result["source"] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)

		return answer_list

	# 4.关系查询：关系+实体2
	def findOtherEntities2(self,entity2,relation):

		answer = self.graph.run(
			"match (source)-[rel:" + relation + "]->(target:KnowledgePoint)  where target.name = $name " +
			"return rel ", name=entity2).data()

		answer_list = []
		for an in answer:
			result = {}
			rel = an['rel']
			relation_type = list(rel.types())[0]
			start_name = rel.start_node['name']
			end_name = rel.end_node['name']
			result["source"] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)

		return answer_list

	# 5.关系查询：实体1+实体2
	def findRelationByEntities(self,entity1,entity2):
		answer = self.graph.run(
			"match (source:KnowledgePoint)-[rel]-(target:KnowledgePoint)  where source.name= $name1 and target.name = $name2 " +
			"return rel ", name1=entity1,name2=entity2).data()

		answer_list = []
		for an in answer:
			result = {}
			rel = an['rel']
			relation_type = list(rel.types())[0]
			start_name = rel.start_node['name']
			end_name = rel.end_node['name']
			result["source"] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)

		return answer_list

	# 6.关系查询：实体1+关系+实体2 (实体1 - 关系 -> 实体2)
	def findEntityRelation(self,entity1,relation,entity2):
		answer = self.graph.run(
			"match (source:KnowledgePoint)-[rel:" + relation + "]->(target:KnowledgePoint)  where source.name= $name1 and target.name = $name2 " +
			"return rel ", name1=entity1, name2=entity2).data()

		answer_list = []
		for an in answer:
			result = {}
			rel = an['rel']
			relation_type = list(rel.types())[0]
			start_name = rel.start_node['name']
			end_name = rel.end_node['name']
			result["source"] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)

		return answer_list

	# 四.问答

	# 意图识别+槽填充，试着采用联合建模进行识别。
	'''
		1.知识点A包含哪些知识点？
		2.包含知识点A的知识点是什么？
		3.知识点A的定义(概念)是什么？(暂无数据)
		4.知识点A怎么计算的(计算方式)？(暂无数据)
		5.包含知识点A的题目有哪些？
		6.包含知识点A的题目还包含哪些知识点?
		7.包含知识点A的题目题型有哪些？
		8.包含知识点A的题目的复杂度如何？
	    9.知识点A的知识路径是什么？
	'''
	# 1.知识点A包含哪些知识点？
	def kp_contain(self, name):
		answer = self.graph.run(
			"match (source:KnowledgePoint)-[rel:BELONG_TO]->(target:KnowledgePoint)  where target.name = $name " +
			"return rel ", name=name).data()

		answer_dict = {}
		answer_name = []
		answer_list = []
		for an in answer:
			result = {}
			rel = an['rel']
			relation_type = list(rel.types())[0]
			start_name = rel.start_node['name']
			end_name = rel.end_node['name']
			result["source"] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)
			answer_name.append(start_name)
		answer_dict['answer'] = answer_name
		answer_dict['list'] = answer_list

		if len(answer_name) == 0:
			return []

		return answer_dict

	# 2.包含知识点A的知识点是什么？
	def contain_kp(self, name):
		answer = self.graph.run("match (source:KnowledgePoint)-[rel:BELONG_TO]->(target:KnowledgePoint) where source.name=$name return rel",name=name).data()
		answer_dict = {}
		answer_name = []
		answer_list = []
		for an in answer:
			result = {}
			rel = an['rel']
			relation_type = list(rel.types())[0]
			start_name = rel.start_node['name']
			end_name = rel.end_node['name']
			result['source'] = {'name':start_name}
			result['type'] = relation_type
			result['target'] = {'name':end_name}
			answer_list.append(result)
			answer_name.append(end_name)
		answer_dict['answer'] = answer_name
		answer_dict['list'] = answer_list

		if len(answer_name) == 0:
			return []

		return answer_dict

	# 3.知识点A的定义(概念)是什么？(暂缺数据)
	def kp_definition(self, name):
		pass

	# 4.知识点A怎么计算的(计算方式)？(暂缺数据)
	def kp_computation(self, name):
		pass

	# 5.包含知识点A的题目有哪些？
	def question_contain_kp(self, name):
		answer = self.graph.run("match (source:Question)-[rel:INCLUDE_A]->(target:KnowledgePoint) where target.name=$name return rel limit 10",name=name).data()

		answer_dict = {}
		answer_name = []
		answer_list = []
		for an in answer:
			result = {}
			rel = an['rel']
			relation_type = list(rel.types())[0]
			start_name = rel.start_node['name']
			end_name = rel.end_node['name']
			result['source'] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)
			answer_name.append(start_name)
		answer_dict['answer'] = answer_name
		answer_dict['list'] = answer_list

		if len(answer_name) == 0:
			return []

		return answer_dict

	# 6.包含知识点A的题目还包含哪些知识点?
	def question_kp_contain_kp(self, name):
		answer = self.graph.run("match (target2:KnowledgePoint)<-[rel2:INCLUDE_A]-(source:Question)-[rel1:INCLUDE_A]->(target1:KnowledgePoint) where target1.name=$name return rel2 limit 10",name=name).data()

		answer_dict = {}
		answer_name = set()
		answer_list = []
		for an in answer:
			result = {}
			rel = an['rel2']
			relation_type = list(rel.types())[0]
			start_name = rel.start_node['name']
			end_name = rel.end_node['name']
			result['source'] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)
			answer_name.add(end_name)
		answer_dict['answer'] = list(answer_name)
		answer_dict['list'] = answer_list

		if len(answer_name) == 0:
			return []

		return answer_dict

	# 7.包含知识点A的题目题型有哪些？
	def question_type_contain_kp(self, name):
		answer = self.graph.run("match (source:Question)-[rel:INCLUDE_A]->(target:KnowledgePoint) where target.name=$name return target.name as name, source.questionType as questionType limit 10", name=name).data()

		answer_dict = {}
		answer_name = set()
		answer_list = []
		for an in answer:
			result = {}
			relation_type = '题型'
			start_name = an['name']
			end_name = an['questionType']
			result["source"] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)
			answer_name.add(end_name)
		answer_dict['answer'] = list(answer_name)
		answer_dict['list'] = answer_list

		if len(answer_name) == 0:
			return []

		return answer_dict

	# 8.包含知识点A的题目的复杂度如何？
	def queston_complexity_contain_kp(self, name):
		answer = self.graph.run("match (source:Question)-[rel:INCLUDE_A]-(target:KnowledgePoint) where target.name=$name return target.name as name, source.complexity as complexity", name=name).data()

		answer_dict = {}
		answer_name = set()
		answer_list = []
		for an in answer:
			result = {}
			relation_type = '复杂度'
			start_name = an['name']
			end_name = an['complexity']
			result["source"] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)
			answer_name.add(end_name)
		answer_dict['answer'] = list(answer_name)
		answer_dict['list'] = answer_list

		if len(answer_name) == 0:
			return []

		return answer_dict

	# 9.学习知识点A的路径是什么？(知识点A的路径追踪)
	def path_learning_kp(self, name):
		answer = self.graph.run("match (source:KnowledgePoint)-[rel:BELONG_TO*..]->(target:KnowledgePoint) where source.name=$name return rel", name=name).data()

		answer_dict = {}
		answer_name = set()
		answer_list = []
		answer = answer[-1]['rel']
		for an in answer:
			result = {}
			relation_type = list(an.types())[0]
			start_name = an.start_node['name']
			end_name = an.end_node['name']
			result['source'] = {'name': start_name}
			result['type'] = relation_type
			result['target'] = {'name': end_name}
			answer_list.append(result)
			answer_name.add(end_name)
		answer_dict['answer'] = list(answer_name)
		answer_dict['list'] = answer_list

		if len(answer_name) == 0:
			return []

		return answer_dict

