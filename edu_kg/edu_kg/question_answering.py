# -*- coding:utf-8 -*-
from django.shortcuts import render
from util.pre_load import segment, neo4jconn, model_dict
from util.nlp_ner import get_kp
import torch
import torch.nn.functional as F

# 模型和词典
model, words = model_dict

# 测试模式
model.eval()

# qa
def question_answering(request):
	context = {'ctx':''}
	if(request.GET):
		question = request.GET['question']
		question = question[:100]
		# 移除空格
		question = question.strip()

		word_nature = segment.seg(question)
		print('word_nature:{}'.format(word_nature))
		classfication_num = predict(word_nature)
		print('类别：{}'.format(classfication_num))

		# 实体识别
		ner_list = get_kp(word_nature)

		# 返回格式：答案和关系图{‘answer':[], 'result':[]}
		if classfication_num == 0:
			ret_dict = neo4jconn.kp_contain(ner_list[0])
			if len(ret_dict) == 0:
				ret_dict = {}

		elif classfication_num == 1:
			ret_dict = neo4jconn.contain_kp(ner_list[0])
			if len(ret_dict) == 0:
				ret_dict = {}

		elif classfication_num == 2:
			ret_dict = {}

		elif classfication_num == 3:
			ret_dict = {}

		elif classfication_num == 4:
			ret_dict = neo4jconn.question_contain_kp(ner_list[0])
			if len(ret_dict) == 0:
				ret_dict = {}

		elif classfication_num == 5:
			ret_dict = neo4jconn.question_kp_contain_kp(ner_list[0])
			if len(ret_dict) == 0:
				ret_dict = {}

		elif classfication_num == 6:
			ret_dict = neo4jconn.question_type_contain_kp(ner_list[0])
			if len(ret_dict) == 0:
				ret_dict = {}

		elif classfication_num == 7:
			ret_dict = neo4jconn.queston_complexity_contain_kp(ner_list[0])
			if len(ret_dict) == 0:
				ret_dict = {}

		elif classfication_num == 8:
			ret_dict = neo4jconn.path_learning_kp(ner_list[0])
			if len(ret_dict) == 0:
				ret_dict = {}

		if(len(ret_dict)!=0):
			return render(request,'question_answering.html',{'ret':ret_dict})

		return render(request, 'question_answering.html', {'ctx':'暂未找到答案'})

	return render(request, 'question_answering.html', context)

def sentence_segment(word_nature):
	sentence_words = []
	for term in word_nature:
		if str(term.nature) == 'kp':
			sentence_words.append('kp')
		else:
			sentence_words.extend(list(term.word))
	return sentence_words

def bow(sentence, words):
	sentence_words = sentence_segment(sentence)
	indexed = [words.stoi[t] for t in sentence_words]
	src_tensor = torch.LongTensor(indexed)
	src_tensor = src_tensor.unsqueeze(0)
	return src_tensor

def predict_class(sentence, model):
	sentence_bag = bow(sentence, words)
	with torch.no_grad():
		outputs = model(sentence_bag)
	predicted_prob, predicted_index = torch.max(F.softmax(outputs, 1), 1)  # 预测最大类别的概率与索引
	results = []
	# results.append({'intent':index_classes[predicted_index.detach().numpy()[0]], 'prob':predicted_prob.detach().numpy()[0]})
	results.append({'intent': predicted_index.detach().numpy()[0], 'prob': predicted_prob.detach().numpy()[0]})
	return results

def get_response(predict_result):
	tag = predict_result[0]['intent']
	return tag

def predict(text):
	predict_result = predict_class(text, model)
	res = get_response(predict_result)
	return res