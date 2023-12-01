from datetime import datetime
import requests


# re = requests.get("http://159.226.91.149:34135/loki/api/v1/query_range?query=count_over_time({job=%22obs%22})", params={'start':1695715452, 'end':1695715452}, timeout=30)
# print(re.text)

yes = datetime.now() 
end = datetime(yes.year, yes.month, yes.day)
# 当天去获取一周前的  确保数据到位
print(end.timestamp())
end = int(end.timestamp()) - 2*24*60*60
start = end - 60*60
print(end)
date_object = datetime.utcfromtimestamp(end)
end_str = date_object.strftime("%Y-%m-%d")
print(end_str)
url = "http://159.226.91.149:34135/loki/api/v1/query_range?query={job=\"obs\"}"
url_check = str.split(url, '{')[0] + 'count_over_time({' + str.split(url, '{')[1] + '[60m])'

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
                    'Connection':'close', 'Accept-Encoding':'gzip,deflate'}

re = requests.get(url_check, params={'start':end, 'end':end, 'step':3600}, timeout=30, headers=headers)
print(re.text)