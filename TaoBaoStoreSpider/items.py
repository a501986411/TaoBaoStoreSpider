# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TaobaostorespiderItem(scrapy.Item):
    title = scrapy.Field()
    # 商品id
    goods_id = scrapy.Field()
    # 月销量
    monthly_sales = scrapy.Field()
    # 首图
    cover_img = scrapy.Field()
    # 结果标识
    result = scrapy.Field()
    pass
