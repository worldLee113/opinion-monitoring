# -*- coding:utf-8 -*-
import requests

s = requests

data={"minganci":"美国"}
r = s.post('http://127.0.0.1:5000/reci_his', data)

print (r.status_code)
# print (r.headers['content-type'])
# print (r.encoding)
print (r.text)
# import datetime
# date_str = '2020-04-13 11:09:57.403'
# date_ = datetime.datetime.strptime(date_str,'%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d')
# print(date_)