# -*- coding: utf-8 -*-
import scrapy
import re
import sys
sys.path.append("myspide/spiders")
import mysql_write
import jieba
import re
import datetime
import os


from scrapy.selector import Selector

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
class NetspiderSpider(scrapy.Spider):

    name = 'netspider'
    allowed_domains = ['163.com']
    # start_urls = ['https://temp.163.com/special/00804KVA/cm_yaowen20200213.js?']

    # 动态生成初始 URL
    def start_requests(self):
        # start_urls = []
        # 遍历网易网站的API
        for i in range(1, 6):
            if i == 1:
                url='https://temp.163.com/special/00804KVA/cm_yaowen20200213.js?callback=data_callback'
            else:
                url = 'https://temp.163.com/special/00804KVA/cm_yaowen20200213_0{page}.js?callback=data_callback'.format(
                page=i)
            # 执行scrapy爬虫，把url和parse函数作为参数输入
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split('/')[-1]
        # 取文件名
        page = page.split('.')[-2]
        filename = 'wj-%s.html' % page
        # 改变爬取到的数据的编码方式，编码方式gbk
        a = bytes.decode(response.body,encoding='gbk')
        a = a.encode('gbk', 'ignore').decode('gbk', 'ignore')
        # 执行正则表达式，提取有用的信息
        b = re.findall(r'"title":"(.*?)",'
                       r'.*?"docurl":"(.*?)",'
                       r'.*?"commenturl":"(.*?)",'
                       r'.*?"label":"(.*?)",'
                       r'.*?"time":"(.*?)",'
                       r'.*?"source":"(.*?)",',a,re.S)
        print(b)
        # 获取历史ID记录，用于后续的查重步骤
        ID_menu = [line.strip() for line in open('netease/net_ID.txt', encoding='UTF-8').readlines()]
        items = []
        # 整理正则表达式提取出的内容，存入items
        for i in range(len(b)):
            item = {}
            page = b[i][1].split('/')[-1]  # 取文件名
            page = page.split('.')[-2]
            if page not in ID_menu:
                item['key'] = page
                item['title'] = b[i][0]
                item['docurl'] = b[i][1]
                item['commenturl'] = b[i][2]
                item['label'] = b[i][3]
                date_ = datetime.datetime.strptime(b[i][4], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d')
                item['time'] = date_
                item['source'] = b[i][5]
                items.append(item)
            else:
                print('目标数据已存在')
        print(items)
        # 将数据写入数据库
        mysql_write.netease_mysql(items)
        with open('netease/'+filename, 'w') as f:
            f.write(str(items))  # 写文件
        # open('/netease/filename','wb').write(response.body)#写文件
        self.log('保存文件: %s' % filename)  # 打印日志
        for i in items:
            content_url = i['docurl']
            # 获取每个新闻页面的新闻内容页面，调取新闻内容爬虫函数
            yield scrapy.Request(content_url, callback=self.parse_content)
    def parse_content(self,response):
        # 取文件名
        page = response.url.split('/')[-1]
        page = page.split('.')[-2]
        ID_menu = [line.strip() for line in open('netease/net_ID.txt', encoding='UTF-8').readlines()]
        # 考虑到新闻内容页面的特殊性，调用scrapy的selector函数，根据html5的特征提取相关信息
        with open('netease/net_ID.txt', 'a')as f:
            f.write(page+'\n')
        selector = Selector(response)
        a = selector.xpath('//*[@id="endText"]/p').extract()
        if len(a) == 0:
            a = selector.xpath('//*[@id="content"]/p').extract()
        b = ''
        for i in a:
            b = b+str(i)
        # 将新闻内容写入本地文件
        filename = 'wj-%s-content.html' % page
        with open('netease/'+filename, 'w') as f:
            f.write(str(b))  # 写文件
        self.log('保存文件: %s' % filename)  # 打印日志
        url_1 = 'http://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/'
        url_2 = '/comments/hotList?limit=40'
        # 获取新闻页面用户评论的API，并执行爬取用户评论API的爬虫
        comment_url = url_1+page+url_2
        yield scrapy.Request(comment_url, callback=self.parse_comment)
    def parse_comment(self,response):
        # 获取中文停用词文档中的所有停用词
        stopwords = get_stopwords_list()
        page = response.url.split('/')[-3]  # 取文件名
        filename = 'wj-%s-comment.html' % page
        # 改变爬取到的数据的编码方式
        a = bytes.decode(response.body)
        a =a.encode('gbk', 'ignore').decode('gbk', 'ignore')
        # 调用正则表达式re模块，提取用户评论中的有用信息
        b = re.findall(r'"against":(.*?),'
                       r'.*?"content":"(.*?)",'
                       r'.*?createTime":"(.*?)",'
                       r'.*?"location":"(.*?)",'
                       r'.*?"nickname":"(.*?)",'
                       r'.*?,"vote":(.*?)},', a, re.S)
        if len(b) != 0:
            items = []
            for i in range(len(b)):
                item = {}
                item['key'] = page
                item['against'] = b[i][0]
                item['content'] = b[i][1]
                # 对用户评论进行中文分词（粗粒度）
                sentence_depart = seg_depart(item['content'])
                # 去重停用词
                sentence_depart = move_stopwords(sentence_depart, stopwords)
                # 敏感词去重
                sentence_depart = move_repet(sentence_depart)
                item['minganci'] = ",".join(sentence_depart)
                date_ = datetime.datetime.strptime(b[i][2], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                item['createTime'] = date_
                item['location'] = b[i][3]
                item['nickname'] = b[i][4]
                item['vote'] = b[i][5]
                items.append(item)
            print(items)
            # 将整理好的数据写入数据库
            mysql_write.netease_comment_mysql(items)
            # 将整理好的数据存入本地文件中
            with open('netease/'+filename, 'w') as f:
                f.write(str(items))  # 写文件
            self.log('保存文件: %s' % filename)  # 打印日志

class SinaspiderSpider(scrapy.Spider):

    name = 'sinaspider'
    allowed_domains = ['sina.com.cn']
    # start_urls = ['https://feed.sina.com.cn/api/roll/get?pageid=121&lid=1356&num=20&page=1']

    # 动态生成初始 URL
    def start_requests(self):
        # start_urls = []
        for i in range(1, 11):
            if i == 1:
                url='https://feed.sina.com.cn/api/roll/get?pageid=121&lid=1356&num=20&page=1'
            else:
                url = 'https://feed.sina.com.cn/api/roll/get?pageid=121&lid=1356&num=20&page={page}'.format(
                page=i)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split('&')[-1]  # 取文件名
        filename = 'wj-%s.html' % page
        a = bytes.decode(response.body,encoding='unicode_escape')
        print(a)
        print(type(a))
        b = re.findall(r'.*?"url":"(.*?)",'
                       r'.*?"title":"(.*?)",'
                       r'.*?"keywords":"(.*?)",'
                       r'.*?"media_name":"(.*?)",',a,re.S)
        print(b)

        items = []
        for i in range(len(b)):
            page = b[i][0].replace('\\','').split('/')[-1]  # 取文件名
            page = page.split('.')[-2]
            ID_menu = [line.strip() for line in open('sina/sina_ID.txt', encoding='UTF-8').readlines()]
            if page not in ID_menu:
                with open('sina/sina_ID.txt', 'a')as f:
                    f.write(page + '\n')
                item = {}
                item['key'] = page
                item['title'] = b[i][1].replace('"','')
                item['docurl'] = b[i][0].replace('\\','')
                item['label'] = b[i][2]
                item['source'] = b[i][3]
                date_=datetime.datetime.now().strftime('%Y-%m-%d')
                item['time'] = date_
                items.append(item)
            else:
                print('目标网址已爬过了')
        mysql_write.sina_mysql(items)
        with open('sina/'+filename, 'w') as f:
            f.write(str(items))  # 写文件
        # open('/netease/filename','wb').write(response.body)#写文件
        self.log('保存文件: %s' % filename)  # 打印日志
        for i in items:
            content_url = i['docurl']
            yield scrapy.Request(content_url, callback=self.parse_content)

    def parse_content(self,response):
        page = response.url.split('/')[-1]  # 取文件名
        page = page.split('.')[-2]

        selector = Selector(response)
        a = selector.xpath('//*[@id="article"]/p').extract()
        filename = 'wj-%s-content.html' % page
        with open('sina/'+filename, 'w') as f:
            f.write(str(a))  # 写文件
        self.log('保存文件: %s' % filename)  # 打印日志
        url_1 = 'http://comment.sina.com.cn/page/info?channel=gn&newsid=comos-'
        page = page.split('-i')[-1]
        url_3 = '&page=1'
        url = url_1+page+url_3
        yield scrapy.Request(url, callback=self.parse_comment)

    def parse_comment(self,response):
        stopwords = get_stopwords_list()
        page = response.url.split('-')[-1]
        page = page.split('&')[-2]  # 取文件名
        a = bytes.decode(response.body)
        b = re.findall(r'"vote": "(.*?)",'
                       r'.*?"area": "(.*?)",'
                       r'.*?"content": "(.*?)",'
                       r'.*?"nick": "(.*?)",'
                       r'.*?"time": "(.*?)",', a, re.S)
        if len(b) != 0:
            items = []
            for i in range(len(b)):
                item = {}
                item['key'] = 'doc-i'+page
                item['content'] = eval("'"+b[i][2]+"'")
                sentence_depart = seg_depart(item['content'])
                sentence_depart = move_stopwords(sentence_depart, stopwords)
                sentence_depart = move_repet(sentence_depart)
                item['minganci'] = ",".join(sentence_depart)
                date_ = datetime.datetime.strptime(b[i][4], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                item['createTime'] = date_
                item['location'] = eval("'"+b[i][1]+"'")
                item['nickname'] = eval("'"+b[i][3]+"'")
                item['vote'] = b[i][0]
                items.append(item)
            print(items)
            mysql_write.sina_comment_mysql(items)
            filename = 'wj-%s-comment.html' % page
            with open('sina/'+filename, 'w') as f:
                f.write(str(items))  # 写文件
            self.log('保存文件: %s' % filename)  # 打印日志
class TencentspiderSpider(scrapy.Spider):

    name = 'tencentspider'
    allowed_domains = ['qq.com']
    # start_urls = ['https://pacaio.match.qq.com/irs/rcd?cid=137&token=d0f13d594edfc180f5bf6b845456f3ea&ext=top&page=1']

    # 动态生成初始 URL
    def start_requests(self):
        # start_urls = []
        for i in range(1, 18):
            url = 'https://pacaio.match.qq.com/irs/rcd?cid=137&token=d0f13d594edfc180f5bf6b845456f3ea&ext=top&page={page}'.format(
            page=i)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split('&')[-1]  # 取文件名
        filename = 'wj-%s.html' % page
        a = bytes.decode(response.body)

        b = re.findall(r'.*?"comment_id":"(.*?)",'
                       r'.*?"keywords":"(.*?)",'
                       r'.*?"publish_time":"(.*?)",'
                       r'.*?"source":"(.*?)",'
                       r'.*?"title":"(.*?)",'
                       r'.*?"vurl":"(.*?)"}',a,re.S)
        print(b)

        items = []
        ID_menu = [line.strip() for line in open('tencent/tencent_ID.txt', encoding='UTF-8').readlines()]
        for i in range(len(b)):
            item = {}
            if '?' in b[i][5]:
                continue
            page = b[i][5].replace('\\','').split('/')[-1]  # 取文件名
            page = page.split('.')[-2]
            if page not in ID_menu:
                with open('tencent/tencent_ID.txt', 'a')as f:
                    f.write(page + '\n')
                item['key'] = page
                item['title'] = b[i][4]
                item['docurl'] = b[i][5].replace('\\','')
                item['label'] = b[i][1]
                item['source'] = b[i][3]
                date_ = datetime.datetime.strptime(b[i][2], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                item['time'] = date_
                item['comment_id'] = b[i][0]
                items.append(item)
            else:
                print('已经爬过了')
        mysql_write.tencent_content_mysql(items)
        with open('tencent/'+filename, 'w') as f:
            f.write(str(items))  # 写文件
        # open('/netease/filename','wb').write(response.body)#写文件
        self.log('保存文件: %s' % filename)  # 打印日志

        for i in items:
            content_url = i['docurl']
            yield scrapy.Request(content_url, callback=self.parse_content)
            url_1 = 'https://coral.qq.com/article/'
            url_2 = i['comment_id']
            url_3 = '/comment/v2?oriorder=o&orirepnum=10'
            url = url_1 + url_2 + url_3
            yield scrapy.Request(url, callback=self.parse_comment)

    def parse_content(self,response):
        page = response.url.split('/')[-1]  # 取文件名
        page = page.split('.')[-2]
        selector = Selector(response)
        a = selector.xpath('//div[@class="content-article"]/p').extract()
        print(a)
        filename = 'wj-%s-content.html' % page
        with open('tencent/'+filename, 'w') as f:
            f.write(str(a))  # 写文件
        self.log('保存文件: %s' % filename)  # 打印日志
    def parse_comment(self,response):
        stopwords = get_stopwords_list()
        a = response.body.decode()
        c = a.encode('gbk', 'ignore').decode('gbk', 'ignore')
        # print(c)
        b = re.findall(r'.*?"time":"(.*?)",'
                       r'.*?"userid":"(.*?)",'
                       r'.*?"content":"(.*?)",'
                       r'.*?"up":"(.*?)",', c, re.S)
        # print(b)

        if len(b) != 0:
            items = []
            d = re.findall(r'"nid\\":\\"(.*?)\\"}', c, re.S)
            for i in range(len(b)):
                item = {}
                item['key'] = d[0]
                item['content'] = b[i][2]
                sentence_depart = seg_depart(item['content'])
                sentence_depart = move_stopwords(sentence_depart, stopwords)
                sentence_depart = move_repet(sentence_depart)
                item['minganci'] = ",".join(sentence_depart)
                dateArray = datetime.datetime.utcfromtimestamp(int(b[i][0]))
                otherStyleTime = dateArray.strftime("%Y-%m-%d")
                item['createTime'] = otherStyleTime
                item['nickname'] = b[i][1]
                item['vote'] = b[i][3]
                items.append(item)
            mysql_write.tencent_comment_mysql(items)
            filename = 'wj-%s-comment.html' % d[0]
            with open('tencent/' + filename, 'w') as f:
                f.write(str(items))  # 写文件
            self.log('保存文件: %s' % filename)  # 打印日志
class TianyaspiderSpider(scrapy.Spider):

    name = 'tianyaspider'
    allowed_domains = ['tianya.cn']
    # start_urls = ['https://bbs.tianya.cn/api?method=bbs.ice.getHotArticleList&params.pageSize=40&params.pageNum=1']

    # 动态生成初始 URL
    def start_requests(self):
        # start_urls = []
        for i in range(1, 11):
            url = 'https://bbs.tianya.cn/api?method=bbs.ice.getHotArticleList&params.pageSize=40&params.pageNum={page}'.format(
            page=i)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

            page = response.url.split('.')[-1]  # 取文件名
            filename = 'wj-%s.html' % page
            print(response.body)
            a = bytes.decode(response.body)
            a = a.encode('gbk', 'ignore').decode('gbk', 'ignore')
            # print(a)
            b = re.findall(r'.*?"item_name":"(.*?)",'
                           r'.*?"title":"(.*?)",'
                           r'.*?"url":"(.*?)",'
                           r'.*?"author_name":"(.*?)",'
                           r'.*?"time":"(.*?)",', a, re.S)
            # print(b)
            ID_menu = [line.strip() for line in open('tianya/tianya_ID.txt', encoding='UTF-8').readlines()]
            items = []
            for i in range(len(b)):
                item = {}
                page = b[i][2].replace('\\', '').split('-')[-2]
                if page not in ID_menu:
                    with open('tianya/tianya_ID.txt', 'a')as f:
                        f.write(page + '\n')
                    item['key'] = page
                    item['title'] = b[i][1]
                    item['docurl'] = b[i][2].replace('\\', '')
                    item['label'] = b[i][0]
                    date_ = datetime.datetime.strptime(b[i][4], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d')
                    item['time'] =date_
                    item['source'] = b[i][3]
                    items.append(item)
                else:
                    print('已经爬过了')
            mysql_write.tianya_content_mysql(items)
            with open('tianya/' + filename, 'w') as f:
                f.write(str(items))  # 写文件
            # open('/netease/filename','wb').write(response.body)#写文件
            self.log('保存文件: %s' % filename)  # 打印日志
            for i in items:
                url = i['docurl']
                yield scrapy.Request(url=url, callback=self.parse_content)
    def parse_content(self,response):
        selector = Selector(response)
        a = selector.xpath('//div[@class="bbs-content clearfix"]').extract()
        b = selector.xpath('//div[@class="atl-pages"]/form/@onsubmit').extract()
        print(b)
        if len(b) == 0:
            comment_page_total = 1
        else:
            comment_page = b[0].split(',')[-1].split(')')[-2]
            comment_page_total = int(comment_page)
        print(comment_page_total)
        page = response.url.split('/')[-1]  # 取文件名
        page = page.split('-')[-2]
        filename = 'wj-%s-content.html' % page
        with open('tianya/' + filename, 'w') as f:
            a = str(a).encode('gbk', 'ignore').decode('gbk', 'ignore')
            f.write(a)  # 写文件
        # open('/netease/filename','wb').write(response.body)#写文件
        self.log('保存文件: %s' % filename)  # 打印日志
        comment_items = []
        for i in range(1,comment_page_total+1):
            url_1 = response.url.split('1.sh')[-2]
            url_2 = str(i)
            url_3 = '.shtml'
            url = url_1+url_2+url_3
            # print(url)
            yield scrapy.Request(url, callback=self.parse_comment)
        #     comment_items.append(comment_item)
        # print(comment_items)
        # filename = 'wj-%s-comment.html' % page
        # with open('tianya/' + filename, 'w') as f:
        #
        #     f.write(str(comment_items))  # 写文件
        # # open('/netease/filename','wb').write(response.body)#写文件
        # self.log('保存文件: %s' % filename)  # 打印日志
    def parse_comment(self,response):
        stopwords = get_stopwords_list()
        comment = bytes.decode(response.body)
        comment = comment.encode('gbk', 'ignore').decode('gbk', 'ignore')
        selector = Selector(response)
        a = selector.xpath('//div[@class="atl-item"]/@_host').extract()
        b = selector.xpath('//div[@class="atl-item"]/@js_restime').extract()
        c = re.findall(r'div class="bbs-content">(.*?)</div>', comment, re.S)
        items = []
        page = response.url.split('/')[-1]  # 取文件名
        page01 = page.split('-')[-2]
        page02 = page.split('-')[-1].split('.')[-2]
        page = page01 + '-' + page02
        for i in range(len(c)):
            item = {}
            item["key"] = page01
            item["content"] = c[i]
            sentence_depart = seg_depart(item['content'])
            sentence_depart = move_stopwords(sentence_depart, stopwords)
            sentence_depart = move_repet(sentence_depart)
            item['minganci'] = ",".join(sentence_depart)
            date_ = datetime.datetime.strptime(b[i], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            item["createTime"] = date_
            item["nickname"] = a[i]
            items.append(item)
        mysql_write.tianya_comment_mysql(items)
        filename = 'wj-%s-comment.html' % page
        last_comment_list = []
        last_comment_list.append(items)
        print(last_comment_list)
        with open('tianya/' + filename, 'w') as f:
            f.write(str(last_comment_list))  # 写文件
def jsonPropt(astr):  # 给json内的键加上双引号
    return astr.replace(' ', '').replace('\n', '').replace('\r', '') \
            .replace("'", '"').replace('{', '{"').replace(':', '":') \
            .replace('],', '],"').replace('",', '","')