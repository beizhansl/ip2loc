import requests
import json
import logging
import time


def get_websites_from_url(category_url):
    try:
        cookie = {'csrftoken':'ZsLyt9MfI3LMKMCClNWjdtInkYs7i6PxTGGFEkrKCJKZmZZC4A29Nx7CGS8TiISK', 'sessionid':'mijnznoj0w5wcug7iwaidcvhzfagbj2s'}
        re = requests.get(category_url, cookies=cookie, params={'page':1, 'page_size' : 1000})
        service_list = re.json()['results']
        website_list = []
        for service in service_list:
            website_list.extend(service['website'])
    except Exception as e:
        print("get websites error, ", e)
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


if __name__ == '__main__':
    cate_url = 'https://aiopsbackend.cstcloud.cn/api/v1/log/http-log/category/'
    get_websites_from_url(cate_url)
