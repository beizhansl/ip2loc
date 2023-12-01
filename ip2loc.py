import os
import time
from multiprocessing import Pool
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

import requests
from handler.iphandler import IPHandler
from handler.loghandler import LogHandler
from util import get_websites_from_file, store_file_with_retry


def logging_fun():
    logging.basicConfig(level=logging.INFO)
    log_handle = RotatingFileHandler("/home/ip2loc/log/log.txt", maxBytes=1024 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s - %(process)d")
    log_handle.setFormatter(formatter)
    logging.getLogger().addHandler(log_handle)


def get_log_by_time(logh:LogHandler, url, start, end):
    start_w = start
    end_w = end
    limit = 1000
    url = url
    last_time = end_w
    log_num = 0
    all_ip_dict = {}
    while(end_w >= start):
        # print(f"start time is {start_w}, end time is {end_w}")
        logs, ok = logh.get_log(url, start_w, end_w, limit)
        if ok is True:
            if len(logs) != 0:
                last_time = int(logs[-1][0]) - 1
            else:
                break
        else:
            logging.error("get log failed of day, trying next tenmin...")
            last_time -= 60 *10
            end_w = last_time
            time.sleep(2)
            continue
        log_num += len(logs)
        ip_dict = logh.extract_ip_from_log(logs)
        for ip_str, num in ip_dict.items():
            all_ip_dict[ip_str] = all_ip_dict.get(ip_str,0) + num
        # if log_num % 10000 == 0:
        #     logging.info(f"getting log... time {end_str} from {web['name']} log num is {log_num}")
            # print(f"log length is {len(logs)}, now log_num is {log_num}")
        end_w = last_time
    return log_num, all_ip_dict

# 获得某一天的日志
def ip2json(web, start, end, range_time):
    filename = f'/home/ip2loc/loc/day/'
    if not os.path.exists(filename):
        os.makedirs(filename)
    date_object = datetime.utcfromtimestamp(end)
    end_str = date_object.strftime("%Y-%m-%d")
    filename += web['name'] + '_' + str(end_str) + '_day.json'
    if os.path.exists(filename):
        logging.info(f"{filename} already exists.")
        return 
     
    all_ip_dict = {}
    logh = LogHandler()
    url = web['api_url']
    logging.info(f"Starting get log of day {str(end_str)} from {web['name']}")
    
    start_w = end - range_time
    end_w = end
    log_num = 0
    # 分割为1h的数据量
    while start_w >= start:
        # TODO: 获得时间范围内的日志数量，数量为0或网络不可达直接返回0
        # 检查日志量
        ok= logh.check_log(url, start=start_w, end=end_w)
        # 没有数据
        if ok is False:
            end_w = start_w
            start_w = end_w - range_time
            time.sleep(5)
            continue
        lognum, ip_dict = get_log_by_time(logh=logh, url=url, start=start_w, end=end_w)
        log_num += lognum
        for ip_str, num in ip_dict.items():
            all_ip_dict[ip_str] = all_ip_dict.get(ip_str,0) + num
        end_w = start_w
        start_w = end_w - range_time
    
    if log_num == 0:
        logging.error(f"The log num is 0, get log failed url {url} end {str(end_str)} ...")
        return
    
    logging.info(f"Starting handle ip of day {str(end_str)} from {web['name']}")
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

    logging.info(f"Starting store msg of day {str(end_str)} from {web['name']}")
    if len(loc_msg_list) == 0:
        logging.error("The loc num is 0.")
        return
    try:
        loc_json:dict = {}
        loc_json['website'] = web['name']
        loc_json['creation_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        loc_json['loc_num'] = loc_num
        loc_json['log_num'] = log_num
        loc_json['range'] = 'day'  
        loc_json['id'] = web['id']
        loc_json['data'] = loc_msg_list
    except Exception as e:
        logging.error(f"gather msg error. {str(e)}")
    store_file_with_retry(filename=filename, data=loc_json)


if __name__ == '__main__':
    # logging_fun()
    # range_time
    oneday = 24*60*60*1
    onemin = 60
    tenmin = 10*60*1
    onehour = 60*60
    pool = Pool(processes=8)
    yes = datetime.now() 
    end = datetime(yes.year, yes.month, yes.day)
    # 当天去获取一周前的  确保数据到位
    end = int(end.timestamp()) - oneday * 7
    end_sdg = end
    start = end - oneday
    start_sdg = start
    website_list = get_websites_from_file()
    sdg_web = None
    days = 1
    for i in range(days):
        for web in website_list:
            if web["desc_name"] ==  "SDG_OBS":
                sdg_web = web
                continue
            result = pool.apply_async(ip2json, (web, start, end, onehour,))
        end = start
        start = end - oneday

    pool.close()
    pool.join()

    for i in range(days):
        ip2json(sdg_web, start_sdg, end_sdg, onehour)
        end_sdg = start_sdg
        start_sdg = end_sdg - oneday
    logging.info("----All task finished----")
