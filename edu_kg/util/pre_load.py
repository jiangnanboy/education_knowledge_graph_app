# -*- coding: utf-8 -*-
from pyhanlp import HanLP
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import pickle

from Model.neo4j_models import Neo4j_Handle

def init_hanlp():
    segment = HanLP.newSegment().enableNameRecognize(True).enableOrganizationRecognize(True).enablePlaceRecognize(True).enableCustomDictionaryForcing(True)
    print("init hanlp...")
    return segment

def init_neo4j():
    neo4jconn = Neo4j_Handle()
    neo4jconn.connectNeo4j()
    print('init neo4j...')
    return neo4jconn

def init_course_kp():
    '''
    小学语文 -> 小学语文综合库
    小学数学 -> 小学数学综合库
    小学英语 -> 小学英语综合库
    初中语文 -> 初中语文综合库
    初中数学 -> 初中数学综合库
    初中英语 -> 初中英语综合库
    初中历史 -> 初中历史综合库
    初中生物 -> 初中生物综合库
    初中化学 -> 初中化学综合库
    初中地理 -> 初中地理综合库
    初中物理 -> 初中物理综合库
    初中政治 -> 初中政治综合库
    初中信息技术 -> 初中信息技术综合库
    高中语文 -> 高中语文综合库
    高中英语 -> 高中英语综合库
    高中数学 -> 高中数学综合库
    高中历史 -> 高中历史综合库
    高中生物 -> 高中生物综合库
    高中化学 -> 高中化学综合库
    高中地理 -> 高中地理综合库
    高中物理 -> 高中物理综合库
    高中政治 -> 高中政治综合库
    高中信息技术 -> 高中信息技术综合库
    高中通用技术 -> 高中通用技术综合库
    '''
    course_dict = {}
    course_dict['小学语文'] = '小学语文综合库'
    course_dict['小学数学'] = '小学数学综合库'
    course_dict['小学英语'] = '小学英语综合库'
    course_dict['初中语文'] = '初中语文综合库'
    course_dict['初中数学'] = '初中数学综合库'
    course_dict['初中英语'] = '初中英语综合库'
    course_dict['初中历史'] = '初中历史综合库'
    course_dict['初中生物'] = '初中生物综合库'
    course_dict['初中化学'] = '初中化学综合库'
    course_dict['初中地理'] = '初中地理综合库'
    course_dict['初中物理'] = '初中物理综合库'
    course_dict['初中政治'] = '初中政治综合库'
    course_dict['初中信息技术'] = '初中信息技术综合库'
    course_dict['高中语文'] = '高中语文综合库'
    course_dict['高中英语'] = '高中英语综合库'
    course_dict['高中数学'] = '高中数学综合库'
    course_dict['高中历史'] = '高中历史综合库'
    course_dict['高中生物'] = '高中生物综合库'
    course_dict['高中化学'] = '高中化学综合库'
    course_dict['高中地理'] = '高中地理综合库'
    course_dict['高中物理'] = '高中物理综合库'
    course_dict['高中政治'] = '高中政治综合库'
    course_dict['高中信息技术'] = '高中信息技术综合库'
    course_dict['高中通用技术'] = '高中通用技术综合库'

    print('init course dict...')
    return course_dict

# 初始化模型
def init_model():
    words_path = os.path.join(os.getcwd() + '/util', "words.pkl")
    with open(words_path, 'rb') as f_words:
        words = pickle.load(f_words)

    # 构建分类模型
    class TextCNN(nn.Module):
        def __init__(self, vocab_size, embedding_dim, output_size, filter_num=100, filter_size=(3, 4, 5), dropout=0.5):
            '''
            vocab_size:词典大小
            embedding_dim:词维度大小
            output_size:输出类别数
            filter_num:卷积核数量
            filter_size(3,4,5):三种卷积核，size为3,4,5，每个卷积核有filter_num个，卷积核的宽度都是embedding_dim
            '''
            super(TextCNN, self).__init__()
            self.embedding = nn.Embedding(vocab_size, embedding_dim)
            # conv2d(in_channel,out_channel,kernel_size,stride,padding),stride默认为1，padding默认为0
            self.convs = nn.ModuleList([nn.Conv2d(1, filter_num, (k, embedding_dim)) for k in filter_size])
            self.dropout = nn.Dropout(dropout)
            self.fc = nn.Linear(filter_num * len(filter_size), output_size)

        '''
        以下forward中的卷积和池化计算方式如下：

        1.卷积
        卷积后的shape公式计算简化为:np.floor((n + 2p - f)/s + 1)
        输入shape:(batch, in_channel, hin, win) = (163, 1, 20, 300)，20为句子长度，300为embedding大小
        输出shape:
        hout=(20 + 2 * 0 - 1 * (3 - 1) - 1)/1 + 1 = 18
        wout=(300 + 2 * 0 - 1 * (300 - 1) -1)/1 + 1 = 1
        =>
        output:(batch, out_channel, hout, wout) = (163, 100, 18, 1)

        2.max_pool1d池化
        简化公式：np.floor((l + 2p - f)/s + 1)
        输入shape:(N,C,L):(163, 100, 18, 1) -> squeeze(3) -> (163, 100, 18)
        输出shape:
        lout = (18 + 2*0 - 18)/18 +1 = 1 -> (163, 100, 1)
        '''

        def forward(self, x):
            # x :(batch, seq_len) = (163, 20)
            x = self.embedding(x)  # [batch,word_num,embedding_dim] = [N,H,W] -> (163, 20, 300)
            x = x.unsqueeze(1)  # [batch, channel, word_num, embedding_dim] = [N,C,H,W] -> (163, 1, 20, 300)
            x = [F.relu(conv(x)).squeeze(3) for conv in
                 self.convs]  # len(filter_size) * (N, filter_num, H) -> 3 * (163, 100, 18)
            # MaxPool1d(kernel_size, stride=None, padding=0, dilation=1, return_indices=False, ceil_mode=False),stride默认为kernal_size
            x = [F.max_pool1d(output, output.shape[2]).squeeze(2) for output in
                 x]  # len(filter_size) * (N, filter_num) -> 3 * (163, 100)
            x = torch.cat(x, 1)  # (N, filter_num * len(filter_size)) -> (163, 100 * 3)
            x = self.dropout(x)
            x = self.fc(x)
            return x

    model = TextCNN(len(words), 300, 9)
    model_path = os.path.join(os.getcwd() + '/util', "model.h5")
    model.load_state_dict(torch.load(model_path))
    return model,words

# 初始化
segment = init_hanlp()

# 初始化
neo4jconn = init_neo4j()

# 初始化学科名
course_dict = init_course_kp()

# 初始化意图分类模型
model_dict = init_model()