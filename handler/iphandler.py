import logging
import geoip2
import time
import json
from handler.xdbSearcher import XdbSearcher

class IPHandler:
    def __init__(self, filename=None):
        self.filename = filename if filename else './GeoLite2-City.mmdb'
        self.reader = None
        self.xdbsearcher = None
        self.loc = None
        self.init_reader()
        
    def init_reader(self):
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts:
            try:
                self.reader = geoip2.database.Reader(self.filename)
                return
            except Exception as e:
                self.close_reader()        
                logging.error("open geoip2 reader error, ", str(e))
                attempts += 1
                time.sleep(1)
                self.reader = None
    
    def init_xdbsearcher(self):
        dbPath = "./ip2region.xdb"
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts:
            try:
                cb = XdbSearcher.loadContentFromFile(dbfile=dbPath)
                self.xdbsearcher = XdbSearcher(contentBuff=cb)
                with open('./loc.json', 'r', encoding='utf-8') as f:
                    self.loc = json.load(fp=f,)
            except Exception as e:
                self.close_reader()        
                logging.error("open geoip2 reader error, ", str(e))
                attempts += 1
                time.sleep(1)
                self.xdbsearcher = None

    def close_reader(self):
        if self.reader is not None:
            self.reader.close()

    def close_xdbsearcher(self):
        if self.xdbsearcher is not None:
            self.xdbsearcher.close()


    def ip2loc(self, ip_dict: dict):
        if self.reader is None:
            self.init_reader() 
        loc_dict:dict = {}
        loc_dict['Unknown'] = [0,]
        for ip_str, count in ip_dict.items():
            try:
                res = self.reader.city(ip_str)
                if res is None or res.location.latitude is None or res.location.longitude is None or (res.location.latitude==34.7732 and res.location.longitude == 113.722):
                    logging.info("translate ip to loc failed, trying xdbSearch...", str(e))
                    region_str = self.searcher.searchByIPStr(ip_str)
                    regeion = region_str.split('|')
                    loc_l = []
                    if regeion[2] in self.loc:
                        loc_l = self.loc[regeion[2]]
                    else:
                        loc_l = self.loc[regeion[0]]
                    loc_tuple = (loc_l[1], loc_l[0])
                else:
                    # use geolite
                    loc_tuple = (res.location.latitude, res.location.longitude)
                if loc_dict.get(loc_tuple, None) is None:
                    loc_dict[loc_tuple] = [0,]
                loc_dict[loc_tuple][0] += count
                loc_dict[loc_tuple].append([ip_str, count])
            except Exception as e:
                logging.warning("translate ip to loc error.", str(e))
                loc_dict['Unknown'][0] += count
                loc_dict['Unknown'].append([ip_str, count])

        self.close_reader()
        self.close_xdbsearcher()
        return loc_dict