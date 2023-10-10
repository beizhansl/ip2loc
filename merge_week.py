from datetime import datetime
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import time
from util import get_websites_from_file, store_file_with_retry

def logging_fun():
    logging.basicConfig(level=logging.INFO)
    log_handle = RotatingFileHandler("./log/merge_log.txt", maxBytes=1024 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s - %(process)d")
    log_handle.setFormatter(formatter)
    logging.getLogger().addHandler(log_handle)

def merge_week(end):
    website_list = get_websites_from_file()
    oneday = 24*60*60*1*(10**9)
    dirname = f'./loc/'
    for web in website_list:
        ip_loc_dict = {}
        ip_count_dict = {}
        loc_dict = {}
        log_num = 0
        for i in range(7):
            filename = dirname + web['name'] + '_' + str(end - i*oneday) + '_day.json'
            if not os.path.exists(filename):
                logging.error(f"{filename} not exists.")
                break
            with open (filename,'r') as f:
                json_str = f.read()
            locmsg = json.loads(json_str)
            log_num += locmsg['log_num']
            data = locmsg['data']
            for loc in data:
                for ip in loc['ip']:
                    ip_count_dict[ip[0]] = ip_count_dict.get(ip[0],0) + ip[1]
                    ip_loc_dict[ip[0]] = (loc['latitude'], loc['longitude'])

        
        for ip_str, count in ip_count_dict.items():
            loc_tuple = ip_loc_dict[ip_str]
            if loc_dict.get(loc_tuple, None) is None:
                loc_dict[loc_tuple] = [0,]
            loc_dict[loc_tuple][0] += count
            loc_dict[loc_tuple].append([ip_str, count])

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
            continue
        loc_json:dict = {}
        loc_json['website'] = web['name']
        loc_json['creation_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        loc_json['loc_num'] = loc_num
        loc_json['log_num'] = log_num
        loc_json['range'] = 'day'  
        loc_json['id'] = web['id']
        loc_json['data'] = loc_msg_list
        weekdirname = f'./loc/week/'
        filename = weekdirname + web['name'] + '_' + str(end) + '_week.json'
        store_file_with_retry(filename=filename, data=loc_json)


if __name__ == '__main__':
    logging_fun()
    yes = datetime.now()
    end = datetime(yes.year, yes.month, yes.day - 2)
    end = int(end.timestamp()) * (10**9)
    
    merge_week(end)
