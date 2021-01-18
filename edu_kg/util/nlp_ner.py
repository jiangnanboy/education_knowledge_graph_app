# -*- coding: utf-8 -*-
# import sys

# sys.path.append("..")

from util.pre_load import course_dict
'''
人名:nr
地名:ns
机构名:nt
知识点:kp
'''

#获取实体信息
def get_ner_info(nature):

	if nature == 'nr':
		return 'nr'
	if nature == 'ns':
		return 'ns'
	if nature == 'nt':
		return 'nt'
	if nature == 'kp':
		return 'kp'

def get_detail_ner_info(nature):
	if nature == 'nr':
		return '人物'
	if nature == 'ns':
		return '地名'
	if nature == 'nt':
		return '机构'
	if nature == 'kp':
		return '知识点'

def get_ner(word_nature):
	ner_list = []
	for term in word_nature:
		word = term.word
		pos = str(term.nature)
		if word in course_dict.keys():
			ner_list.append([word, 'kp'])
			continue
		if pos.startswith('nr'):
			ner_list.append([word, 'nr'])
		elif pos.startswith('ns'):
			ner_list.append([word, 'ns'])
		elif pos.startswith('nt'):
			ner_list.append([word, 'nt'])
		#elif pos.startswith('kp'):
			#ner_list.append([word, 'kp'])
		else:
			ner_list.append([word, 0])
	return ner_list

# 获取知识点
def get_kp(word_nature):
	ner_list = []
	for term in word_nature:
		word = term.word
		pos = str(term.nature)
		if word in course_dict.keys():
			ner_list.append(course_dict.get(word))
			continue
		if pos.startswith('kp'):
			ner_list.append(word)
	return ner_list