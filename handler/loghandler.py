from datetime import datetime
import json
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


    def check_log(self, url, start=None, end=None):
        attempts = 0
        max_attempts = 3
        date_object = datetime.utcfromtimestamp(end)
        end_str = date_object.strftime("%Y-%m-%d-%H:%M:%S")
        url_check = str.split(url, '{')[0] + 'count_over_time({' + str.split(url, '{')[1] + '[1h])'
        logging.info(f"checking for {url} {end_str}...")
        while attempts < max_attempts: 
            try:
                re = requests.get(url_check, params={'start':end, 'end':end, 'step':3600}, timeout=30, headers=self.get_header())
                re.raise_for_status()
                result  = re.json()['data']['result']
                if len(result) == 0 or result[0]['values'][0][1] == "0":
                    return False
                else: 
                    return True
            except json.decoder.JSONDecodeError as e:
                logging.error(f"Check error for {e} url {url} end={end_str} response is {re.text}...")
            except requests.exceptions.ConnectionError as e:
                logging.error(f"Check error for {e} url {url} end={end_str}...")
                exit(0)
            except requests.exceptions.HTTPError as e:
                logging.error(f"Check error for {e} url {url} end={end_str}...")
                exit(0)
            except requests.exceptions.RequestException as e:
                logging.error(f"Check error for {e} url {url} end={end_str}...")
                exit(0)    
            except Exception as e:
                logging.error(f"Check error for {e} url {url} end={end_str}...")
            finally:
                attempts += 1
                if attempts == 3:
                    return False
    
    
    def get_log(self, url=None, start = None, end = None, limit = None):
        log_list = []
        attempts = 0
        max_attempts = 3
        ok = True
        date_object = datetime.utcfromtimestamp(end)
        end_str = date_object.strftime("%Y-%m-%d-%H:%M:%S")
        logging.info(f"geting log for url {url} end {end_str}")
        while attempts < max_attempts: 
            try:
                re = requests.get(url, params={'start':start, 'end':end, 'limit':limit}, timeout=30, headers=self.get_header())
                re.raise_for_status()
                log_res = re.json()
                log_res = log_res['data']['result']
                if len(log_res) != 0 and 'values' in log_res[0]:
                    log_list = log_res[0]['values']
                ok = True
                return log_list, ok
            except json.decoder.JSONDecodeError as e:
                logging.error(f"Get error for {e} url {url} end={end_str} response is {re.text}...")
            except requests.exceptions.ConnectionError as e:
                logging.error(f"Get error for {e} url {url} end={end_str}...")
                exit(0)
            except requests.exceptions.HTTPError as e:
                logging.error(f"Get error for {e} url {url} end={end_str}...")
                exit(0)
            except requests.exceptions.RequestException as e:
                logging.error(f"Get error for {e} url {url} end={end_str}...")
                exit(0)  
            except Exception as e:
                logging.error(f"Get error for {e} url {url} end={end_str}...")
            finally:
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
