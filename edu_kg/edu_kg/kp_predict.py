# -*- coding:utf-8 -*-
from django.shortcuts import render
import jieba
from util.pre_load import  kp_predict_model_dict
import torch
import torch.nn.functional as F
import re

# 模型、词典、知识点、停词
kp_predict_model,kp_words,knowledge_points,stopwords_set = kp_predict_model_dict

# 测试模式
kp_predict_model.eval()

# 知识点预测
def kp_predict(request):
	context = {'ctx':''}
	if(request.GET):
		question = request.GET['question']
		question = question[:200]
		# 移除空格
		question = question.strip()

		result_predict = predict(question)

		answer_dict = {}
		answer_name = []
		answer_list = []

		result_predict = result_predict[0]
		for index in range(len(result_predict)):
			result = {}
			if result_predict[index] == 1:
				answer_name.append(knowledge_points[index])
				result["source"] = {'name': question}
				result['type'] = 'contain'
				result['target'] = {'name': knowledge_points[index]}
				answer_list.append(result)

		answer_dict['answer'] = answer_name
		answer_dict['list'] = answer_list

		if(len(answer_dict)!=0):
			return render(request,'kp_predict.html',{'ret':answer_dict})

		return render(request, 'kp_predict.html', {'ctx':'暂未找到答案'})

	return render(request, 'kp_predict.html', context)

def content_preprocess(content):
    # 去标点
    r = re.compile("[^\u4e00-\u9fa5]+|题目")
    content = r.sub("", content)  # 删除所有非汉字字符
    # jieba分词
    words = jieba.cut(content, cut_all=False)
    words = [w for w in words if w not in stopwords_set]
    # words = ' '.join(words)
    return words

def bow(sentence):
	sentence_words = content_preprocess(sentence)
	indexed = [kp_words.stoi[t] for t in sentence_words]
	src_tensor = torch.LongTensor(indexed)
	src_tensor = src_tensor.unsqueeze(0)
	return src_tensor

def predict_class(sentence):
	sentence_bag = bow(sentence)
	with torch.no_grad():
		outputs = kp_predict_model(sentence_bag)

	predicts = F.sigmoid(outputs).data.numpy() > 0.5
	predicts = predicts.astype(int)

	return predicts

def predict(text):
	predict_result = predict_class(text)
	return predict_result