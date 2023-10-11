import os
import time
from multiprocessing import Pool
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from handler.iphandler import IPHandler
from handler.loghandler import LogHandler
from util import get_websites_from_file, store_file_with_retry


def logging_fun():
    logging.basicConfig(level=logging.INFO)
    log_handle = RotatingFileHandler("/home/ip2loc/log/log.txt", maxBytes=1024 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s - %(process)d")
    log_handle.setFormatter(formatter)
    logging.getLogger().addHandler(log_handle)


def get_log_by_time(logh, web, start, end):
    start_w = start
    end_w = end
    limit = 1000
    url = web['api_url']
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
            logging.error("get log failed of day, trying next min...")
            last_time -= 60 * (10**9)
            end_w = last_time
            continue
        log_num += len(logs)
        ip_dict = logh.extract_ip_from_log(logs)
        for ip_str, num in ip_dict.items():
            all_ip_dict[ip_str] = all_ip_dict.get(ip_str,0) + num
        if log_num % 10000 == 0:
            logging.info(f"getting log... time {end_w} from {web['name']} log num is {log_num}")
            # print(f"log length is {len(logs)}, now log_num is {log_num}")
        end_w = last_time
    return log_num, all_ip_dict


def ip2json(web, start, end, range_time):
    filename = f'/home/ip2loc/loc/day/'
    if not os.path.exists(filename):
        os.makedirs(filename)
    filename += web['name']
    filename += '_'
    filename += str(end) 
    filename +='_day.json'
    if os.path.exists(filename):
        logging.info(f"{filename} already exists.")
        return 

    start_w = end - range_time
    end_w = end
    log_num = 0
    all_ip_dict = {}
    logh = LogHandler()
    
    logging.info(f"Starting get log of day {str(end)} from {web['name']}")
    
    # split get log by time -- 1d
    while start_w >= start:
        logging.info(f"getting log... time {end_w} from {web['name']} log num is {log_num}")
        lognum, ip_dict = get_log_by_time(logh=logh, web=web, start=start_w, end=end_w)
        log_num += lognum
        for ip_str, num in ip_dict.items():
            all_ip_dict[ip_str] = all_ip_dict.get(ip_str,0) + num
        end_w = start_w
        start_w = end_w - range_time
    
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
    logging_fun()
    # range_time
    oneday = 24*60*60*1*(10**9)
    tenmin = 10*60*1*(10**9)
    pool = Pool(processes=8)
    yes = datetime.now()
    end = datetime(yes.year, yes.month, yes.day)
    end = int(end.timestamp()) * (10**9)
    start = end - oneday
    website_list = get_websites_from_file()
    for i in range(1):
        for web in website_list:
            result = pool.apply_async(ip2json, (web, start, end, tenmin,))
        end = start
        start = end - oneday
    pool.close()
    pool.join()
    logging.info("----All task finished----")
