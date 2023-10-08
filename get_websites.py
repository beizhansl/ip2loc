import requests
import json

def get_websites_from_url(category_url):
    try:
        cookie = {'csrftoken':'ZsLyt9MfI3LMKMCClNWjdtInkYs7i6PxTGGFEkrKCJKZmZZC4A29Nx7CGS8TiISK', 'sessionid':'tc5p94yt9zdujg067htcupywk6i6x13q'}
        re = requests.get(category_url, cookies=cookie, params={'page':1, 'page_size' : 1000})
        service_list = re.json()['results']
        website_list = []
        for service in service_list:
            website_list.extend(service['website'])
    except Exception as e:
        print("get websites error, ", str(e))
        return None
    filename = "website_list.json"
    with open (filename,'w') as f:
            json.dump(website_list, fp=f, indent=2)
    return website_list

if __name__ == '__main__':
    cate_url = 'https://aiopsbackend.cstcloud.cn/api/v1/log/http-log/category/'
    get_websites_from_url(cate_url)
