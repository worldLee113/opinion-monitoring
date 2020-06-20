#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 导入Flask类
from flask import Flask,request
from flask_cors import CORS
import pymysql
import json
import os
import sys
import datetime
print (sys.argv[0])
db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
cursor = None
# 实例化，可视为固定格式
app = Flask(__name__)
# route()方法用于设定路由；类似spring路由配置
# 测试用的API
@app.route('/helloworld')
def hello_world():
    return 'Hello, World!'
# 敏感词单个查询历史记录API
@app.route('/reci_his',methods=['POST'])
def reci_his():
    time_t = request.form.get('minganci')
    print(time_t)
    sql = "SELECT e.createTime,count(*) as geshu,'netease' as laiyuan " \
          "FROM netease_comment e " \
          "where e.minganci like '%{}%' group by e.createTime " \
          "UNION " \
          "SELECT e.createTime,count(*) as geshu,'sina' as laiyuan " \
          "FROM sina_comment e " \
          "where e.minganci like '%{}%' group by e.createTime " \
          "UNION " \
          "SELECT e.createTime,count(*) as geshu,'tencent' as laiyuan " \
          "FROM tencent_comment e " \
          "where e.minganci like '%{}%' group by e.createTime " \
          "UNION " \
          "SELECT e.createTime,count(*) as geshu,'tianya' as laiyuan " \
          "FROM tianya_comment e " \
          "where e.minganci like '%{}%' group by e.createTime ".format(time_t,time_t,time_t,time_t)

    print(sql)
    try:
        cursor = db.cursor()
        cursor.execute(sql)
    except:
        db.ping()
        cursor = db.cursor()
        cursor.execute(sql)
    # cursor = db.cursor()
    # cursor.execute(sql)  # 执行sql语句
    row_headers = [x[0] for x in cursor.description]
    results = cursor.fetchall()
    print(results)
    json_data = []
    for result in results:
        json_data.append(dict(zip(row_headers, result)))
    print(json_data)
    # _db.commit()
    db.rollback()
    cursor.close()


    return json.dumps(json_data)
# 敏感词查询API
@app.route('/reci_chaxun',methods=['GET'])
def reci_chaxun():
    data = {}
    with open("C:/Users/Administrator/Desktop/舆情监控/myspide/热词.txt", "r") as f:
        lines = f.read().splitlines()
    data['data'] = lines
    print(data)
    return json.dumps(data)
# 敏感词删除API
@app.route('/reci_shanchu',methods=['POST'])
def reci_shanchu():
    shanchu_canshu = request.form.get('minganci')
    with open("C:/Users/Administrator/Desktop/舆情监控/myspide/热词.txt","r") as f:
        data = f.read().splitlines()
    with open("C:/Users/Administrator/Desktop/舆情监控/myspide/热词.txt","w") as f_w:
        for line in data:
            if shanchu_canshu in line:
                continue
            f_w.write(line + '\n')
    return '删除成功'

# 添加敏感词API
@app.route('/reci',methods=['POST'])
def reci():
    reci_canshu = request.form.get('minganci')
    with open("C:/Users/Administrator/Desktop/舆情监控/myspide/热词.txt","a") as f:
        f.write(reci_canshu + '\n')
    return '添加成功'

# 查询屏蔽词API
@app.route('/chaxunpingbi/',methods=['GET'])
def chaxunhuifu():
    data = {}
    with open("C:/Users/Administrator/Desktop/舆情监控/myspide/敏感词停用.txt", "r") as f:
        lines = f.read().splitlines()
    data['data'] = lines
    print(data)
    return json.dumps(data)

# 屏蔽词恢复API
@app.route('/huifu/',methods=['POST'])
def huifu():
    huifu = request.form.get('minganci')
    print(huifu)
    with open("C:/Users/Administrator/Desktop/舆情监控/myspide/敏感词停用.txt", "r") as f:
        lines = f.read().splitlines()
        # print(lines)
    with open("C:/Users/Administrator/Desktop/舆情监控/myspide/敏感词停用.txt", "w") as f_w:
        for line in lines:
            if huifu in line:
                continue
            f_w.write(line+'\n')
    return '恢复成功'

# 屏蔽词添加API
@app.route('/shanchu/',methods=['POST'])
def shanchu():
    minganci_shanchu = request.form.get('minganci')
    print(minganci_shanchu)
    print(os.path.isfile("敏感词停用.txt"))
    with open("C:/Users/Administrator/Desktop/舆情监控/myspide/敏感词停用.txt", "r") as f:
        lines = f.read().splitlines()
    if minganci_shanchu not in lines:
        with open("C:/Users/Administrator/Desktop/舆情监控/myspide/敏感词停用.txt", "a") as f:
            f.write(minganci_shanchu+'\n')
        return '删除成功'
    else:
        return '有重复'

# 用户评论溯源API
@app.route('/suyuan/',methods=['POST'])
def suyuan():
    guanjianci = request.form.get('minganci')
    sql = "SELECT d.content,d.createTime,d.nickname,e.docurl " \
          "FROM netease_content e,netease_comment d " \
          "where e.key_c = d.key_c and d.minganci like '%{page}%' " \
          "UNION " \
          "SELECT d.content,d.createTime,d.nickname,e.docurl " \
          "FROM sina_content e,sina_comment d " \
          "where e.key_c = d.key_c and d.minganci like '%{page}%' " \
          "UNION " \
          "SELECT d.content,d.createTime,d.nickname,e.docurl " \
          "FROM tianya_content e,tianya_comment d " \
          "where e.key_c = d.key_c and d.minganci like '%{page}%' " \
          "UNION " \
          "SELECT b.content,b.createTime,b.nickname,a.docurl " \
          "FROM tencent_content a,tencent_comment b " \
          "where a.key_c = b.key_c and b.minganci like '%{page}%' ".format(page = guanjianci)
    try:
        cursor = db.cursor()
        cursor.execute(sql)
    except:
        db.ping()
        cursor = db.cursor()
        cursor.execute(sql)
    # cursor = db.cursor()
    # cursor.execute(sql)  # 执行sql语句
    row_headers = [x[0] for x in cursor.description]
    results = cursor.fetchall()
    print(results)
    json_data = []
    for result in results:
        json_data.append(dict(zip(row_headers, result)))
    print(json_data)
    # _db.commit()
    db.rollback()
    cursor.close()
    return json.dumps(json_data)

# 热词查询API
@app.route('/minganci/',methods=['POST'])
def minganci():
    time_t = request.form.get('time')
    sql = "select (minganci) from netease_comment where createTime = '{page}' " \
          "union all select (minganci) from sina_comment where createTime = '{page}'" \
          " union all select (minganci) from tencent_comment where createTime = '{page}'" \
          " union all select (minganci) from tianya_comment where createTime = '{page}'".format(page = time_t)
    try:
        cursor = db.cursor()
        cursor.execute(sql)
    except:
        db.ping()
        cursor = db.cursor()
        cursor.execute(sql)
    row_headers = [x[0] for x in cursor.description]
    results = cursor.fetchall()
    print(results)
    json_data = []
    for result in results:
        json_data.append(dict(zip(row_headers, result)))
    print(json_data)
    # _db.commit()
    db.rollback()
    cursor.close()
    return json.dumps(json_data)

# 热词出现频率统计API
@app.route('/jishu/',methods=['POST'])
def jishu():
    time_t = request.form.get('time')
    print(time_t)
    sql = "SELECT " \
          "count(CASE WHEN jishu = 'tianya' and time_t = '{page}'and bianhao = '1'THEN 1 END) AS tianya01," \
          "count(CASE WHEN jishu = 'tianya' and time_t = '{page}'and bianhao = '2'THEN 1 END) AS tianya02," \
          "count(CASE WHEN jishu = 'tianya' and time_t = '{page}'and bianhao = '3'THEN 1 END) AS tianya03," \
          "count(CASE WHEN jishu = 'tianya' and time_t = '{page}'and bianhao = '4'THEN 1 END) AS tianya04," \
          "count(CASE WHEN jishu = 'tianya' and time_t = '{page}'and bianhao = '0'THEN 1 END) AS tianya00," \
          "count(CASE WHEN jishu = 'netease' and time_t = '{page}'and bianhao = '1'THEN 1 END) AS netease01," \
          "count(CASE WHEN jishu = 'netease' and time_t = '{page}'and bianhao = '2'THEN 1 END) AS netease02," \
          "count(CASE WHEN jishu = 'netease' and time_t = '{page}'and bianhao = '3'THEN 1 END) AS netease03," \
          "count(CASE WHEN jishu = 'netease' and time_t = '{page}'and bianhao = '4'THEN 1 END) AS netease04," \
          "count(CASE WHEN jishu = 'netease' and time_t = '{page}'and bianhao = '0'THEN 1 END) AS netease00," \
          "count(CASE WHEN jishu = 'tencent' and time_t = '{page}'and bianhao = '1'THEN 1 END) AS tencent01," \
          "count(CASE WHEN jishu = 'tencent' and time_t = '{page}'and bianhao = '2'THEN 1 END) AS tencent02," \
          "count(CASE WHEN jishu = 'tencent' and time_t = '{page}'and bianhao = '3'THEN 1 END) AS tencent03," \
          "count(CASE WHEN jishu = 'tencent' and time_t = '{page}'and bianhao = '4'THEN 1 END) AS tencent04," \
          "count(CASE WHEN jishu = 'tencent' and time_t = '{page}'and bianhao = '0'THEN 1 END) AS tencent00," \
          "count(CASE WHEN jishu = 'sina' and time_t = '{page}'and bianhao = '1'THEN 1 END) AS sina01," \
          "count(CASE WHEN jishu = 'sina' and time_t = '{page}'and bianhao = '2'THEN 1 END) AS sina02," \
          "count(CASE WHEN jishu = 'sina' and time_t = '{page}'and bianhao = '3'THEN 1 END) AS sina03," \
          "count(CASE WHEN jishu = 'sina' and time_t = '{page}'and bianhao = '4'THEN 1 END) AS sina04," \
          "count(CASE WHEN jishu = 'sina' and time_t = '{page}'and bianhao = '0'THEN 1 END) AS sina00" \
          " FROM guilei_table".format(page = time_t)
    print(sql)
    try:
        cursor = db.cursor()
        cursor.execute(sql)
    except:
        db.ping()
        cursor = db.cursor()
        cursor.execute(sql)
    # cursor = db.cursor()
    # cursor.execute(sql)  # 执行sql语句
    row_headers = [x[0] for x in cursor.description]
    results = cursor.fetchall()
    print(results)
    json_data = []
    for result in results:
        json_data.append(dict(zip(row_headers, result)))
    print(json_data)
    # _db.commit()
    db.rollback()
    cursor.close()
    return json.dumps(json_data)

# 条形图所需数据的API
@app.route('/tiaoxingtu/',methods=['POST'])
def tiaoxingtu():
    time_t = request.form.get('time')
    print(time_t)
    sql = "SELECT " \
          "count(CASE WHEN jishu = 'tianya' and time_t = '{}'THEN 1 END) AS tianya," \
          "count(CASE WHEN jishu = 'netease' and time_t = '{}'THEN 1 END) AS netease," \
          "count(CASE WHEN jishu = 'tencent' and time_t = '{}'THEN 1 END) AS tencent," \
          "count(CASE WHEN jishu = 'sina' and time_t = '{}'THEN 1 END) AS sina" \
          " FROM guilei_table".format(time_t,time_t,time_t,time_t)
    print(sql)
    try:
        cursor = db.cursor()
        cursor.execute(sql)
    except:
        db.ping()
        cursor = db.cursor()
        cursor.execute(sql)
    # cursor = db.cursor()
    # cursor.execute(sql)  # 执行sql语句
    row_headers = [x[0] for x in cursor.description]
    results = cursor.fetchall()
    print(results)
    json_data = []
    for result in results:
        json_data.append(dict(zip(row_headers, result)))
    print(json_data)
    # _db.commit()
    db.rollback()
    cursor.close()
    return json.dumps(json_data)

# 查询模块API
@app.route('/search_content/',methods=['POST'])
def search_content():
    address = request.form.get('address')
    keyword = request.form.get('keyword')
    with open("C:/Users/Administrator/Desktop/舆情监控/myspide/敏感词停用.txt") as f:  # 不需要自己关闭 文件句柄  f.close()不需要 默认 r
        datas = f.read().splitlines()
    if keyword not in datas:
        print(address)
        print(keyword)
        sql = "select * from {} where title like '%{}%'".format(address,keyword)
        try:
            cursor = db.cursor()
            cursor.execute(sql)
        except:
            db.ping()
            cursor = db.cursor()
            cursor.execute(sql)
        # cursor = db.cursor()
        # cursor.execute(sql)  # 执行sql语句
        row_headers = [x[0] for x in cursor.description]
        results = cursor.fetchall()
        print(results)
        json_data = []
        for result in results:
            json_data.append(dict(zip(row_headers, result)))
        print(json_data)
        # _db.commit()
        db.rollback()
        cursor.close()
        return json.dumps(json_data)
    else:
        data = {}
        data['request'] = '关键词已被屏蔽'
        return json.dumps(data)

# 查询评论及相关数据API
@app.route('/search_comment/',methods=['POST'])
def search_comment():
    address = request.form.get('address')
    keyword = request.form.get('id')
    print(address)
    print(keyword)
    sql = "select * from {} where key_c = '{}'".format(address,keyword)
    try:
        cursor = db.cursor()
        cursor.execute(sql)
    except:
        db.ping()
        cursor = db.cursor()
        cursor.execute(sql)
    # cursor = db.cursor()
    # cursor.execute(sql)  # 执行sql语句
    row_headers = [x[0] for x in cursor.description]
    results = cursor.fetchall()
    print(results)
    json_data = []
    for result in results:
        json_data.append(dict(zip(row_headers, result)))
    print(json_data)
    # _db.commit()
    db.rollback()
    cursor.close()
    return json.dumps(json_data)

# LDA新闻分类的API
@app.route('/search_guilei/',methods=['POST'])
def search_guilei():
    address = request.form.get('address')
    time_t = request.form.get('time')
    if time_t!=None:
        if address != None:
            sql = "select * from guilei_table where jishu = '{}' and time_t = '{}'".format(address,time_t)
        else:
            sql = "select * from guilei_table where time_t = '{}'".format(time_t)

    print(sql)
    try:
        cursor = db.cursor()
        cursor.execute(sql)
    except:
        db.ping()
        cursor = db.cursor()
        cursor.execute(sql)
    # cursor = db.cursor()
    # cursor.execute(sql)  # 执行sql语句
    row_headers = [x[0] for x in cursor.description]
    results = cursor.fetchall()
    print(results)
    json_data = []
    for result in results:
        json_data.append(dict(zip(row_headers, result)))
    print(json_data)
    # _db.commit()
    db.rollback()
    cursor.close()
    return json.dumps(json_data)

# 每个评论的关键词查询API
@app.route('/search_guanjianci/',methods=['POST'])
def search_guanjianci():
    address = request.form.get('address')
    time_t = request.form.get('time')
    print(address)
    print(time_t)
    sql = "select * from guanjianci_table where source = '{}' AND time_t = '{}'".format(address,time_t)
    cursor = db.cursor()
    cursor.execute(sql)  # 执行sql语句
    row_headers = [x[0] for x in cursor.description]
    results = cursor.fetchall()
    print(results)
    json_data = []
    for result in results:
        json_data.append(dict(zip(row_headers, result)))
    print(json_data)
    # _db.commit()
    db.rollback()
    cursor.close()
    return json.dumps(json_data)


if __name__ == '__main__':
    CORS(app, supports_credentials=True)
    # app.run(host, port, debug, options)
    # 默认值：host="127.0.0.1", port=5000, debug=False
    app.run(host="0.0.0.0", port=5000)