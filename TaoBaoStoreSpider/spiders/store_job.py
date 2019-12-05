# -*- coding: utf-8 -*-
import scrapy
import pymysql
import configparser
import conf
import requests
from lxml import etree
import logging
import sys
class StoreJobSpider(scrapy.Spider):
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    name = 'store_job'
    allowed_domains = ['taobao.com', 'tmall.com']
    start_urls = ['http://taobao.com/']
    db = ''
    cf = configparser.ConfigParser()
    conf = conf.conf()
    type_tb = 1
    type_tm = 2
    def __init__(self):
        super().__init__(scrapy.Spider)
        self.set_db()

    def parse(self, response):
        response.xpath("//text()").extract_first().replace("jsonp_73411981(","").replace(")","")
        logging.debug(response)
        sys.exit(0)
        pass

    def set_start_urls(self):
        sql = "select fs.id,fs.domain,fs.seller_id,fs.shop_id,fs.type from etb_user_store us LEFT JOIN etb_follow_store fs on us.follow_store_id = fs.id where us.is_follow = 1"
        cursor = self.db.cursor(cursor = pymysql.cursors.DictCursor)
        cursor.execute(sql)
        urls = []
        for row in cursor.fetchall():
            if not row['seller_id'] or not row['shop_id']:
                tmp = self.get_store_info(row['id'], row['domain'], row['type'])
                if tmp == False:
                    continue
                row['seller_id'] = tmp['seller_id']
                row['shop_id'] = tmp['shop_id']
            if row['type'] == self.type_tb:
                pass
            else:
                tmp_url = "https://"+row['domain']+".m.tmall.com/shop/shop_auction_search.do?suid="+row['seller_id']+"&sort=d&p=1&page_size=12&from=h5&shop_id="+row['shop_id']+"&ajson=1&_tm_source=tmallsearch&callback=jsonp_73411981"
                urls.append(tmp_url)
        self.start_urls = urls


    def get_store_info(self, store_id, store_domain, store_type):
        if store_type == self.type_tb:
            pass
        else:
            url = "https://"+ store_domain +".m.tmall.com/"
            res = requests.get(url)
            html = etree.HTML(res.text)
            seller_id = html.xpath('//input[@id="sid"]')[0].get('value')
            shop_id = html.xpath('//input[@id="shop_id"]')[0].get('value')
            name = html.xpath('//title/text()')[0]
        if self.save_store_info(store_id, seller_id, shop_id, name):
            return False
        else:
            return {"seller_id":seller_id, "shop_id":shop_id}

    def save_store_info(self, store_id, seller_id, shop_id, name):
        try:
            sql = "update etb_follow_store set seller_id=%s, shop_id=%s, name='%s' where id=%s" % \
                  (seller_id, shop_id, name, store_id)
            c = self.db.cursor(cursor = pymysql.cursors.DictCursor)
            c.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            logging.error("更新关注店铺信息失败")
            return False


    def set_db(self):
        db_conf = self.cf.read(self.conf.get_db_conf(), encoding="utf-8")
        self.db = pymysql.connect(db_conf.get('db','db_host'), db_conf.get('db','db_user'),db_conf.get('db','db_pwd'), db_conf.get('db','db_database'))

