# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import logging
import configparser
import conf
import sys


class TaobaostorespiderPipeline(object):
    db = ''
    cursor = ''
    db_cnf = ''
    cf = ''

    def __init__(self):
        self.db_cnf = configparser.ConfigParser()
        self.cf = conf.conf()
        self.db_cnf.read(self.cf.get_db_conf(), encoding="utf-8")
        self.db = pymysql.connect(self.db_cnf.get('db', 'db_host'), self.db_cnf.get('db', 'db_user'), self.db_cnf.get('db', 'db_pwd'), self.db_cnf.get('db', 'db_database'))

    def process_item(self, item, spider):
        if item['result'] != False:
            self.save_data(item)
        else:
            pass

    def save_data(self, item):
        cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            # 执行更新语句
            if self.goods_is_exist(item['goods_id']):
                u_sql = "update etb_goods set title='%s', cover_img='%s', detail_url='%s' where goods_id=%s" % \
                        (item['title'], item['cover_img'], item['detail_url'], item['goods_id'])
                cursor.execute(u_sql)
            else:
                i_sql = "INSERT INTO etb_goods (goods_id, title, detail_url, monthly_sales, cover_img, shop_id, seller_id)  VALUES (%s, '%s', '%s', %s, '%s', %s, %s)" % \
                        (item['goods_id'], item['title'], item['detail_url'], item['monthly_sales'], item['cover_img'], item['shop_id'], item['seller_id'])
                cursor.execute(i_sql)
            self.db.commit()
        except Exception as e:
            logging.error(e)
            self.db.rollback()

    def goods_is_exist(self, goods_id):
        sql = "select * from etb_goods where goods_id=%s" % \
              (goods_id)
        cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql)
        row = cursor.fetchone()
        if not row:
            return False
        else:
            return True
