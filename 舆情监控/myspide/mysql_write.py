# # -*- coding:utf-8 -*-
import pymysql

# data = {'title': '葡萄牙14岁少年因新冠肺炎去世 为欧洲最年轻死者',
#         'docurl': 'https://news.163.com/20/0330/15/F8VP4BHS00019B3E.html',
#         'commenturl': 'http://comment.tie.163.com/F8VP4BHS00019B3E.html',
#         'label': '其它',
#         'time': '03/30/2020 15:15:54',
#         'source': '海外网'}
# key = 'F8VO1CL50001899O'

def netease_mysql(dic_content):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    for data in dic_content:
        sql = "INSERT INTO netease_content(title,docurl,label,time_t,commenturl,source,key_c)" \
              "VALUES ('%s','%s','%s','%s','%s','%s','%s')"%(data['title'],data['docurl'],data['label'],data['time'],data['commenturl'],data['source'],data['key'])

        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 执行sql语句
        print('chenggong')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')
    # 关闭数据库连接
    db.close()

def netease_comment_mysql(dic_content):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    for data in dic_content:
        sql = "INSERT INTO netease_comment(key_c,against,content,createTime,location,nickname,vote,minganci)" \
              "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')"%(data['key'],data['against'],data['content'],data['createTime'],data['location'],data['nickname'],data['vote'],data['minganci'])

        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 执行sql语句
        print('评论成功存入数据库')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')
    # 关闭数据库连接
    db.close()

def sina_mysql(dic_content):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    for data in dic_content:
        sql = "INSERT INTO sina_content(key_c,title,docurl,label,source,time_t)" \
              "VALUES ('%s','%s','%s','%s','%s','%s')"%(data['key'],data['title'],data['docurl'],data['label'],data['source'],data['time'])

        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 执行sql语句
        print('评论成功存入数据库')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')
    # 关闭数据库连接
    db.close()
def sina_comment_mysql(dic_content):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    for data in dic_content:
        sql = "INSERT INTO sina_comment(key_c,content,createTime,location,nickname,vote,minganci)" \
              "VALUES ('%s','%s','%s','%s','%s','%s','%s')"%(data['key'],data['content'],data['createTime'],data['location'],data['nickname'],data['vote'],data['minganci'])

        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 执行sql语句
        print('评论成功存入数据库')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')
    # 关闭数据库连接
    db.close()

def tencent_content_mysql(dic_content):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    for data in dic_content:
        sql = "INSERT INTO tencent_content(key_c,title,docurl,label,source,time_t,comment_id)" \
              "VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (
              data['key'], data['title'], data['docurl'], data['label'], data['source'],data['time'],data['comment_id'])
        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 执行sql语句
        print('评论成功存入数据库')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')
    # 关闭数据库连接
    db.close()

def tencent_comment_mysql(dic_content):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    for data in dic_content:
        sql = "INSERT INTO tencent_comment(key_c,content,createTime,nickname,vote,minganci)" \
              "VALUES ('%s','%s','%s','%s','%s','%s')"%(data['key'],data['content'],data['createTime'],data['nickname'],data['vote'],data['minganci'])

        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 执行sql语句
        print('评论成功存入数据库')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')
    # 关闭数据库连接
    db.close()

def tianya_content_mysql(dic_content):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    for data in dic_content:
        sql = "INSERT INTO tianya_content(key_c,title,docurl,label,source,time_t)" \
              "VALUES ('%s','%s','%s','%s','%s','%s')" % (
              data['key'], data['title'], data['docurl'], data['label'], data['source'],data['time'])
        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 执行sql语句
        print('评论成功存入数据库')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')
    # 关闭数据库连接
    db.close()

def tianya_comment_mysql(dic_content):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    for data in dic_content:
        sql = "INSERT INTO tianya_comment(key_c,content,createTime,nickname,minganci)" \
              "VALUES ('%s','%s','%s','%s','%s')"%(data['key'],data['content'],data['createTime'],data['nickname'],data['minganci'])

        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 执行sql语句
        print('评论成功存入数据库')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')
    # 关闭数据库连接
    db.close()
def guanjianci_mysql(dic_content):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    for data in dic_content:
        sql = "INSERT INTO guanjianci_table(bianhao,guanjianci,time_t,source)" \
              "VALUES ('%s','%s','%s','%s')" % (data['Lda_bianhao'], data['LDA_key'], data['time'], data['source'])

        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 执行sql语句
        print('评论成功存入数据库')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')
    # 关闭数据库连接
    db.close()
def bianhao_mysql(dic_content):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    for data in dic_content:
        sql = "INSERT INTO guilei_table(key_k,bianhao,time_t,jishu)" \
              "VALUES ('%s','%s','%s','%s')" % (data['id'], data['bianhao'],data['time'],data['jishu'])

        cursor.execute(sql)  # 执行sql语句
        db.commit()  # 执行sql语句
        # print('评论成功存入数据库')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')
    # 关闭数据库连接
    db.close()
