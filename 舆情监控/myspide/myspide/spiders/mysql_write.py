# # -*- coding:utf-8 -*-
import pymysql

# data = {'title': '葡萄牙14岁少年因新冠肺炎去世 为欧洲最年轻死者',
#         'docurl': 'https://news.163.com/20/0330/15/F8VP4BHS00019B3E.html',
#         'commenturl': 'http://comment.tie.163.com/F8VP4BHS00019B3E.html',
#         'label': '其它',
#         'time': '03/30/2020 15:15:54',
#         'source': '海外网'}
# key = 'F8VO1CL50001899O'

def netease_mysql(data):
    db = pymysql.connect(host='127.0.0.1',
             port=3306,
             user='root',
             passwd='123456',
             db='yuqing',
             charset='utf8mb4',  )
    cursor = db.cursor()
    sql = "INSERT INTO netease_content(title,docurl,label,time_t,commenturl,source,key_t)" \
          "VALUES ('%s','%s','%s','%s','%s','%s','%s')"%(data['title'],data['docurl'],data['label'],data['time'],data['commenturl'],data['source'],data['key'])

    cursor.execute(sql)  # 执行sql语句
    db.commit()  # 执行sql语句
    print('chenggong')
    # except:
    #     db.rollback()  # 发生错误时回滚
    #     print('cuowu')

    # 关闭数据库连接
    db.close()

