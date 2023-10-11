import logging
import time
import requests
import re

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
                log_res = re.json()
                log_res = log_res['data']['result']
                if len(log_res) != 0 and 'values' in log_res[0]:
                    log_list = log_res[0]['values']
                ok = True
                return log_list, ok
            except Exception as e:
                logging.error(f"Get log error for {str(e)} url {url}&start={start}&end={end}")
                # logging.error(re.text)
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
                ip_dict[ip_str] = ip_dict.get(ip_str, 0) + 1
            except Exception as e:
                logging.error("extract ip error, ", str(e))
                pass
        return ip_dict
