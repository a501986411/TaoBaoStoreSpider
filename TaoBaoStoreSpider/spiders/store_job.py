# -*- coding: utf-8 -*-
import scrapy
import pymysql
import configparser
import conf
import requests
from lxml import etree
import logging
import sys
import time
import json
from urllib import parse
from TaoBaoStoreSpider.items import TaobaostorespiderItem
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
    start_urls = []
    db = ''
    conf = conf.conf()
    type_tb = 1
    type_tm = 2
    tm_url = "https://%s.m.tmall.com/shop/shop_auction_search.do?suid=%s&sort=d&p=%s&page_size=24&from=h5&shop_id=%s&ajson=1&_tm_source=tmallsearch&callback=jsonp_95407611"
    def __init__(self):
        super().__init__(scrapy.Spider)
        self.set_db()
        self.set_start_urls()

    def parse(self, response):
        result = response.xpath("//text()").extract_first().replace("jsonp_95407611(","").replace(")","")
        json_text = json.loads(result)
        #淘宝处理

        # 天猫处理
        if 'items' not in json_text:
            item = TaobaostorespiderItem()
            item['result'] = False
            yield item
        num = 0
        count = len(json_text['items'])
        for row in json_text['items']:
            item = TaobaostorespiderItem()
            item['goods_id'] = row['item_id']
            item['title'] = row['title']
            item['cover_img'] = row['img']
            item['monthly_sales'] = row['sold']
            # item['monthly_sales'] = self.get_monthly_sales_info(item['goods_id'])
            item['detail_url'] = row['url']
            item['price'] = row['price']
            item['shop_id'] = json_text['shop_id']
            item['seller_id'] = json_text['user_id']
            item['result'] = True
            num += 1
            if num == count:
                if count == int(json_text['page_size']):
                    # next_page_url = response.url.replace("p="+json_text['current_page'], "p="+str(int(json_text['current_page']) + 1))
                    # if next_page_url:
                    #     yield scrapy.Request(next_page_url, callback=self.parse)
                    pass
            yield item

    def set_start_urls(self):
        sql = "select fs.id,fs.domain,fs.unique_key,fs.seller_id,fs.shop_id,fs.type from etb_user_store us LEFT JOIN etb_follow_store fs on us.follow_store_id = fs.id where us.is_follow = 1"
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
                tmp_url = self.tm_url % (row['unique_key'], row['seller_id'], 1, row['shop_id'])
                urls.append(tmp_url)
        self.start_urls = urls


    def get_store_info(self, store_id, store_domain, store_type):
        if store_type == self.type_tb:
            pass
        else:
            url = store_domain + '/'
            res = requests.get(url)
            html = etree.HTML(res.text)
            seller_id = html.xpath('//input[@id="sid"]')[0].get('value')
            shop_id = html.xpath('//input[@id="shop_id"]')[0].get('value')
            name = html.xpath('//title/text()')[0]
        if not self.save_store_info(store_id, seller_id, shop_id, name):
            return False
        else:
            return {"seller_id": seller_id, "shop_id": shop_id}

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
        cf = configparser.ConfigParser()
        cf.read(self.conf.get_db_conf(), encoding="utf-8")
        self.db = pymysql.connect(cf.get('db', 'db_host'), cf.get('db', 'db_user'), cf.get('db', 'db_pwd'), cf.get('db', 'db_database'))

    def get_monthly_sales_info(self, goods_id):
        param = {
            "jsv": "2.5.1",
            "appKey": 12574478,
            "t": int(time.time() * 1000),
            # "sign": "08ca47d1bf4ac9d0a8c297fe0980c9b6",
            "api": "mtop.taobao.detail.getdetail",
            "v": "6.0",
            "ttid": "2017@htao_h5_1.0.0",
            "type": "jsonp",
            "dataType": "jsonp",
            "callback": "mtopjsonp1",
            "data": json.dumps({"exParams": "{\"countryCode\":\"CN\"}", "itemNumId": str(goods_id)})
        }
        url = "https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?" + parse.urlencode(param).replace('+', '')
        res = requests.get(url)
        text = res.text.replace("mtopjsonp1(","").replace(")","")
        json_text = json.loads(text)
        monthly_sales = 0
        if 'item' not in json_text['data']:
            return monthly_sales
        else:
            goods_item = json.loads(json_text['data']['apiStack'][0]['value'])
            if 'sellCount' in goods_item['item']:
                monthly_sales = goods_item['item']['sellCount']
            else:
                monthly_sales = goods_item['item']['vagueSellCount']
        return monthly_sales

