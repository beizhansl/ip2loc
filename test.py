import requests
cookie = {'csrftoken':'ZsLyt9MfI3LMKMCClNWjdtInkYs7i6PxTGGFEkrKCJKZmZZC4A29Nx7CGS8TiISK', 'sessionid':'tc5p94yt9zdujg067htcupywk6i6x13q'}

# re = requests.get('https://aiopsbackend.cstcloud.cn/api/v1/log/http-log/category/',cookies=cookie, params={'page':1, 'page_size' : 1000})

# data = re.json()
# url = data['results'][0]['website'][0]['api_url']
# print(url)

# import re

# log = "223.193.36.4 [26/Sep/2023:16:37:16 +0800] 159.226.33.12 200 102 972 service.cstcloud.cn \"GET / HTTP/1.1\" \"-\""

# # 使用正则表达式提取第二个IP地址
# ip_pattern = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
# match = re.findall(ip_pattern, log)

# if len(match) >= 2:
#     second_ip = match[1]
#     print("第二个IP地址：", second_ip)
# else:
# #     print("日志中没有足够的IP地址")
# import json
# re = requests.get('http://159.226.91.149:34135/loki/api/v1/query_range?query={job="service"}', params={'start':'1695680611','end':'1695819432', 'limit': 500000, 'direction':'forward'}, timeout=1000)
# with open('data.json','w+') as p:
#     json.dump(re.json(),fp=p, indent=2)
#print(re.json()['data']['result'][0]['values'])

# import datetime
# import time
# print(time.time_ns())
# print(type(time.time_ns()))
# t =(1695818370806111500 - 1695213570806111500) / 1e9
# du = datetime.timedelta(seconds=t)
# print(str(du))

#from datetime import datetime, timedelta
#yesterday = datetime.now()
#end = datetime(yesterday.year, yesterday.month, yesterday.day)
# print(end.timestamp())
#nsend = int(end.timestamp()) 
#print(nsend)
#print(end)
import os 
filename = f'./loc/day/000000'
if not os.path.exists(filename):
    os.makedirs(filename)