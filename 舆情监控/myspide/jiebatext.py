# # -*- coding:utf-8 -*-
import jieba
from gensim import corpora, models
import numpy as np
import re

import os
import re
import  json
import datetime
import sys

sys.path.append("myspide")
import mysql_write
# 停用词
# 创建停用词列表
def get_stopwords_list():
    stopwords = [line.strip() for line in open('中文停用词.txt',encoding='UTF-8').readlines()]
    return stopwords

# 对句子进行中文分词
def seg_depart(sentence):
    # 对文档中的每一行进行中文分词
    sentence_depart = jieba.lcut(sentence.strip())
    return sentence_depart

def remove_digits(input_str):
    punc = u'0123456789.'
    output_str = re.sub(r'[{}]+'.format(punc), '', input_str)
    return output_str

# 去除停用词
def move_stopwords(sentence_list, stopwords_list):
    # 去停用词
    out_list = []
    for word in sentence_list:
        if word not in stopwords_list:
            if not remove_digits(word):
                continue
            if word != '\t':
                out_list.append(word)
    return out_list

# 去除重复关键词
def move_repet(sentence_depart):
    sentence_depart.sort()  # 列表排序
    s = set(sentence_depart)  # 将列表转化为集合，去重
    sentence_depart = list(s)  # 集合重新变成列表
    return sentence_depart

# LDA模型
def LDA_learn(item,num_topic):
    dictionary = corpora.Dictionary(item)
    # print(dictionary.token2id)
    # 基于词典，使【词】→【稀疏向量】，并将向量放入列表，形成【稀疏向量集】
    corpus = [dictionary.doc2bow(words) for words in item]
    # lda模型，num_topics设置主题的个数
    lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topic)
    # 打印所有主题，每个主题显示5个词
    # for topic in lda.print_topics(num_words=10):
    #     print(topic)
    # # 主题推断
    # print(lda.inference(corpus))
    return lda.inference(corpus),lda.print_topics(num_words=10)
# 给json内的键加上双引号
def jsonPropt(astr):
    return astr.replace(' ', '').replace('\n', '').replace('\r', '') \
            .replace("'", '"')
def wangyi_lda():
    list_hanshu = []
    for i in range(1, 6):
        if i == 1:
            menu = open('netease/wj-cm_yaowen20200213.html', 'r')
            menu_content = jsonPropt(menu.read())
            menu_content = json.loads(menu_content)
            list_hanshu = list_hanshu+menu_content
        else:
            menu = open('netease/wj-cm_yaowen20200213_0{}.html'.format(i), 'r')
            menu_content = jsonPropt(menu.read())
            menu_content = json.loads(menu_content)
            list_hanshu = list_hanshu + menu_content

    if len(list_hanshu) != 0:
        print(list_hanshu)
        a, b = LDA_yuqing(list_hanshu, 'netease', '.')
        mysql_write.guanjianci_mysql(a)
        mysql_write.bianhao_mysql(b)
    else:
        print('无数据')
def sina_lda():
    list_hanshu = []
    for i in range(1, 10):
            menu = open('sina/wj-page={page}.html'.format(page=i), 'r')
            menu_content = jsonPropt(menu.read())
            menu_content = json.loads(menu_content)
            list_hanshu = list_hanshu + menu_content
    if len(list_hanshu)!=0:
        a ,b= LDA_yuqing(list_hanshu,'sina','.')
        mysql_write.guanjianci_mysql(a)
        mysql_write.bianhao_mysql(b)
    else:
        print('无数据')
def tencent_lda():
    list_hanshu = []
    for i in range(1, 17):
            menu = open('tencent/wj-page={page}.html'.format(page=i), 'r')
            menu_content = jsonPropt(menu.read())
            menu_content = json.loads(menu_content)
            list_hanshu = list_hanshu + menu_content
    if len(list_hanshu)!=0:
        a ,b= LDA_yuqing(list_hanshu,'tencent','.')
        mysql_write.guanjianci_mysql(a)
        mysql_write.bianhao_mysql(b)
    else:
        print('无数据')
def tianya_lda():
    list_hanshu = []
    for i in range(1, 10):
            menu = open('tianya/wj-pageNum={page}.html'.format(page=i), 'r')
            menu_content = jsonPropt(menu.read())
            menu_content = json.loads(menu_content)
            list_hanshu = list_hanshu + menu_content
    if len(list_hanshu) != 0:
        a, b = LDA_yuqing(list_hanshu, 'tianya', '-')
        mysql_write.guanjianci_mysql(a)
        mysql_write.bianhao_mysql(b)
    else:
        print('无数据')
def LDA_yuqing(menu_content,str_content,xiaocanshu):
    # 调用get_stopwords_list方法，获取中文停用词
    stopwords = get_stopwords_list()
    items = []
    id_value_list = []
    id_values = []
    # 参数menu_content其实就是新闻属性，遍历的目的是为了寻找每个新闻的ID
    for i in menu_content:
        # 每个新闻的ID，可以从docurl中截取出来
        id_url = i['docurl']
        id_value_mid = id_url.split('/')[-1]
        id_value = id_value_mid.split(xiaocanshu)[-2]
        item = {}
        # 判定相关路径下是否存在这个新闻ID的文件
        if os.access(str_content+'/wj-%s-content.html' % id_value, os.F_OK):
            # 获取文件内容
            f = open(str_content+'/wj-%s-content.html' % id_value, 'r')
            print(id_value)

            m = ''
            content_item = []
            # 去除新闻中的特殊字符
            for n in re.findall(r'[\u4e00-\u9fff]+', f.read()):
                m = m + str(n)
            # 调用下面这三个函数完成中文分词的操作
            sentence_depart = seg_depart(m)
            sentence_depart = move_stopwords(sentence_depart, stopwords)
            sentence_depart = move_repet(sentence_depart)
            # 生成可以进行LDA主题的dic数据
            if len(sentence_depart) != 0:
                item['content_key'] = sentence_depart
                item['key'] = id_value
                # print(item)
        items.append(item)
        content_list = []
        for i in items:
            if len(i) != 0:
                content_list.append(i['content_key'])
                id_value_list.append(i['key'])
    print(len(content_list))
        # 执行LDA主题分类的模型，输入新闻词，输出五个分类
    a, b = LDA_learn(content_list, 5)
    content_list_mysql = []
    # 整理输出的结果，便于后续存入数据库
    for i in b:
        content_dic = {}
        y = ''
        for n in re.findall(r'[\u4e00-\u9fff]+', i[1]):
            if len(y) == 0:
                y = y + str(n)
            else:
                y = y + ',' + str(n)
        content_dic['Lda_bianhao'] = str(i[0])
        content_dic['LDA_key'] = y
        content_dic['time'] = str(datetime.datetime.now().strftime('%Y-%m-%d'))
        content_dic['source'] = str_content
        content_list_mysql.append(content_dic)
    x = a[0]
    index_max = np.argmax(x, axis=1)  # 其中，axis=1表示按行计算
    topic_content = index_max.tolist()
    for i in range(len(id_value_list)):
        id_value ={}
        id_value['id'] = str(id_value_list[i])
        id_value['bianhao'] = str(topic_content[-1])
        id_value['time'] = str(datetime.datetime.now().strftime('%Y-%m-%d'))
        id_value['jishu'] = str_content
        id_values.append(id_value)
    print(id_values)
    return content_list_mysql,id_values
if __name__ == "__main__":
    wangyi_lda()
    # sina_lda()
    # tencent_lda()
    # tianya_lda()
    # menu = open('myspide/netease/wj-cm_yaowen20200213.html', 'r')
    # # print(menu.read())
    # menu_content = jsonPropt(menu.read())
    # menu_content = json.loads(menu_content)
    # stopwords = get_stopwords_list()
    # items = []
    # id_value_list = []
    # id_values = {}
    #
    # for i in menu_content:
    #     id_url = i['docurl']
    #     id_value_mid = id_url.split('/')[-1]
    #     id_value = id_value_mid.split('.')[-2]
    #     item = {}
    #     if os.access('myspide/netease/wj-%s-content.html'%id_value, os.F_OK):
    #         f = open('myspide/netease/wj-%s-content.html'%id_value, 'r')
    #         print(id_value)
    #
    #         m = ''
    #         content_item = []
    #         for n in re.findall(r'[\u4e00-\u9fff]+', f.read()):
    #             m = m + str(n)
    #         # LDA_yuqing(m)
    #         content_depart = seg_depart(m)
    #         content_depart = move_stopwords(content_depart, stopwords)
    #         content_depart = move_repet(content_depart)
    #         if len(content_depart) != 0:
    #             item['content_key'] = content_depart
    #             item['key'] = id_value
    #             print(item)
    #         # print(content_depart)
    # #     if os.access('myspide/netease/wj-%s-comment.html' % id_value, os.F_OK):
    # #         e = open('myspide/netease/wj-%s-comment.html' % id_value, 'r')
    # #         comment_content = jsonPropt(e.read())
    # #         comment_content = json.loads(comment_content)
    # #         comment_items = []
    # #         for i in comment_content:
    # #             comment = i['content']
    # #             for n in re.findall(r'[\u4e00-\u9fff]+', comment):
    # #                 n = n + str(n)
    # #             sentence_depart = seg_depart(n)
    # #             sentence_depart = move_stopwords(sentence_depart, stopwords)
    # #             sentence_depart = move_repet(sentence_depart)
    # #             # print(sentence_depart)
    # #             comment_items.append(sentence_depart)
    # #         item['comment_key'] = comment_items
    #     items.append(item)
    # # # print(items)
    #
    # content_list = []
    # for i in items:
    #     if len(i) !=0 :
    #         content_list.append(i['content_key'])
    #         id_value_list.append(i['key'])
    # a,b = LDA_learn(content_list,5)
    #
    # content_list_mysql = []
    # for i in b:
    #     content_dic = {}
    #     y = ''
    #     for n in re.findall(r'[\u4e00-\u9fff]+', i[1]):
    #         if y == 0 :
    #             y = y + str(n)
    #         else:
    #             y = y + ','+str(n)
    #     content_dic['Lda_bianhao'] = str(i[0])
    #     content_dic['LDA_key'] = y
    #     content_dic['time'] = int(time.time())
    #     content_list_mysql.append(content_dic)
    # print(content_list_mysql)




