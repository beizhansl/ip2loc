import os
import re
import time
import traceback
import geoip2.database
import json
import requests
from tqdm import tqdm
from multiprocessing import Pool
from datetime import datetime
import random
import logging
from logging.handlers import RotatingFileHandler

def logging_fun():
    # 创建日志的记录等级设
    logging.basicConfig(level=logging.INFO)
    # 创建日志记录器，指明日志保存的路径，每个日志文件的最大值，保存的日志文件个数上限
    log_handle = RotatingFileHandler("/home/code/log.txt", maxBytes=1024 * 1024 * 1024, backupCount=5)
    # 创建日志记录的格式
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s - %(process)d")
    # 为创建的日志记录器设置日志记录格式
    log_handle.setFormatter(formatter)
    # 为全局的日志工具对象添加日志记录器
    logging.getLogger().addHandler(log_handle)


def get_websites_from_url(category_url):
    try:
        cookie = {'csrftoken':'ZsLyt9MfI3LMKMCClNWjdtInkYs7i6PxTGGFEkrKCJKZmZZC4A29Nx7CGS8TiISK', 'sessionid':'tc5p94yt9zdujg067htcupywk6i6x13q'}
        re = requests.get(category_url, cookies=cookie, params={'page':1, 'page_size' : 1000})
        service_list = re.json()['results']
        website_list = []
        for service in service_list:
            website_list.extend(service['website'])
    except Exception as e:
        logging.error("get websites error, ", str(e))
        return None
    filename = "website_list.json"
    with open (filename,'w') as f:
            json.dump(website_list, fp=f, indent=2)
    return website_list

def get_websites_from_file():
    filename = "website_list.json"
    with open (filename,'r') as f:
            json_str = f.read()
    website_list = json.loads(json_str)
    return website_list

class LogHandler:
    # 获得log
    
    def get_header(self):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
                    'Connection':'close', 'Accept-Encoding':'gzip,deflate'}
        return headers

    def get_log(self, url=None, start = None, end = None, limit = None):
        log_list = []
        attempts = 0
        max_attempts = 3
        ok = True
        while attempts < max_attempts: 
            try:
                re = requests.get(url, params={'start':start, 'end':end, 'limit':limit}, timeout=30, headers=self.get_header()) 
                if 'NoSuchKey' in re.text:
                    ok = True
                    return log_list, ok
                log_res = re.json()
                log_res = log_res['data']['result']
                if len(log_res) != 0 and 'values' in log_res[0]:
                    log_list = log_res[0]['values']
                ok = True
                return log_list, ok
            except Exception as e:
                logging.error(f"Get log error for {str(e)} url {url}&start={start}&end={end}")
                logging.error(re.text)
                attempts += 1
                ok = False
                # print(log_res)
        return log_list, ok
    
    def extract_ip_from_log(self, log_list:list):
        ip_dict:dict = {}
        ip_pattern = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        for log in log_list:
            try:
                log_str:str = log[1]
                match = re.findall(ip_pattern, log_str)
                ip_str = match[1]
                ip_dict[ip_str] = ip_dict.get(ip_str,0) + 1
            except Exception as e:
                logging.error("extract ip error, ", str(e))
                pass
        return ip_dict


class IPHandler:
    def __init__(self, filename=None):
        self.filename = filename if filename else './GeoLite2-City.mmdb'
        self.reader = None
        self.get_reader()
        
    def get_reader(self):
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts:
            try:
                self.reader = geoip2.database.Reader(self.filename)
                return
            except Exception as e:        
                logging.error("open geoip2 reader error, ", str(e))
                attempts += 1
                self.reader = None

    def ip2loc(self, ip_dict: dict):
        if self.reader is None:
            return 
        loc_dict:dict = {}
        loc_dict['Unknown'] = [0,]
        for ip_str, count in ip_dict.items():
            try:
                res = self.reader.city(ip_str)
                if res is None or res.location.latitude is None or res.location.longitude is None:
                    raise Exception("cannot get city latitude or longitude")
                loc_tuple = (res.location.latitude, res.location.longitude)
                if loc_dict.get(loc_tuple, None) is None:
                    loc_dict[loc_tuple] = [0,]
                loc_dict[loc_tuple][0] += count
                loc_dict[loc_tuple].append([ip_str, count])
            except Exception as e:
                logging.warning("translate ip to loc error, ", str(e))
                loc_dict['Unknown'][0] += count
                loc_dict['Unknown'].append([ip_str, count])
                pass
        self.close_reader()
        return loc_dict

    def close_reader(self):
        if self.reader is not None:
            self.reader.close()

def store_file_with_retry(filename, data, max_retries=3, retry_delay=1):
    retries = 0
    while retries < max_retries:
        try:
            with open(filename, 'w+') as f:
                json.dump(data, f, indent=2)
            logging.info(f"{filename} created successfully")
            return  # 存储成功，结束函数并返回

        except Exception as e:
            logging.error(f"Failed to create {filename}: {e}")
            retries += 1
            if retries < max_retries:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

    logging.error(f"Unable to create {filename} after {max_retries} retries.")

def is_file_exists(filename):
    return os.path.exists(filename)

def web2json(web, start, end):
    start_w = start
    limit = 100
    end_w = end
    log_num = 0
    all_ip_dict = {}
    last_time = end_w
    logh = LogHandler()
    url = web['api_url']
    filename = '/home/code/loc/'
    filename += web['name']
    filename += '_'
    filename += str(end) 
    filename +='_day.json'
    if is_file_exists(filename):
        logging.info(f"{filename} already exists.")
        return 

    logging.info(f"Starting get log of day {str(end)} from {web['name']}")
    count = 0
    while(True):
        count += 1
        if count % 100 == 0:
            logging.info(f"getting log... of day {str(end)} from {web['name']} log num is {log_num}")
        # print(f"start time is {start_w}, end time is {end_w}")
        logs, ok = logh.get_log(url, start_w, end_w, limit)
        if ok is True:
            if len(logs) != 0:
                last_time = int(logs[-1][0]) - 1
            else:
                break
        else:
            break
        log_num += len(logs)
        # print(f"log length is {len(logs)}, now log_num is {log_num}")
        ip_dict = logh.extract_ip_from_log(logs)
        for ip_str, num in ip_dict.items():
            all_ip_dict[ip_str] = all_ip_dict.get(ip_str,0) + num
        end_w = last_time
        if start_w >= end_w:
            break
    
    if log_num == 0:
        logging.error(f"The log num is 0, get log failed.")
        return

    logging.info(f"Starting handle ip of day {str(end)} from {web['name']}")
    iph = IPHandler()
    loc_dict = iph.ip2loc(all_ip_dict)
    loc_msg_list = []
    loc_num = 0
    for loc_tuple, ip_list in loc_dict.items():
        try:
            loc_msg = { 'latitude':loc_tuple[0],
                        'longitude':loc_tuple[1],
                        'ip_num':ip_list[0],
                        'ip':ip_list[1:]}
            loc_msg_list.append(loc_msg)
            loc_num += 1
        except Exception as e:
            logging.error("add new loc error, ", str(e))
            pass

    logging.info(f"Starting store msg of day {str(end)} from {web['name']}")
    if len(loc_msg_list) == 0:
        return
    loc_json:dict = {}
    loc_json['website'] = web['name']
    loc_json['creation_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    loc_json['loc_num'] = loc_num
    loc_json['log_num'] = log_num
    loc_json['range'] = 'day'  
    loc_json['id'] = web['id']
    loc_json['data'] = loc_msg_list

    store_file_with_retry(filename=filename, data=loc_json)

if __name__ == '__main__':
    logging_fun()
    pool = Pool(processes=16)
    # 获得今天零点的时间戳
    yes = datetime.now()
    end = datetime(yes.year, yes.month, yes.day)
    end = int(end.timestamp()) * (10**9)
    # end = int(time.time_ns())
    for i in range(30):
        start = end - 24*60*60*1*(10**9)
        # cate_url = 'https://aiopsbackend.cstcloud.cn/api/v1/log/http-log/category/'
        # website_list = get_websites_from_url(cate_url)
        website_list = get_websites_from_file()
        for web in website_list:
            result = pool.apply_async(web2json,(web,start,end,))
        end = end - 24*60*60*1*(10**9)
    pool.close()
    pool.join()
    logging.info("----All task finished----")
