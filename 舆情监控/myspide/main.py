#!/usr/bin/env python
#-*- coding:utf-8 -*-

from scrapy.cmdline import execute
import os
import sys
import jiebatext


#添加当前项目的绝对地址
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


#执行 scrapy 内置的函数方法execute，  使用 crawl 爬取并调试，最后一个参数jobbole 是我的爬虫文件名
# while True:
# execute(['scrapy', 'crawlall'])
# jiebatext.wangyi_lda()
# jiebatext.sina_lda()
# jiebatext.tencent_lda()
# jiebatext.tianya_lda()

# execute(['scrapy', 'crawl', 'sinaspider'])
# execute(['scrapy', 'crawl', 'tencentspider'])
execute(['scrapy', 'crawl', 'tianyaspider'])