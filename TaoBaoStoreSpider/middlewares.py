# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests
import sys
import logging
import configparser
import time
import conf
from random import choice
import json

class TaobaostorespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TaobaostorespiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleware(object):
    proxy_cf = ''
    cf =''
    db = ''
    cursor = ''
    get_proxy_url = ""
    def __init__(self):
        self.proxy_cf = configparser.ConfigParser()
        self.cf = conf.conf()
        self.proxy_cf.read(self.cf.get_proxy_conf(), encoding="utf-8")

    def get_proxy_ip(self):
        proxy_ip = self.proxy_cf.get('proxy', 'ip')
        if proxy_ip == '':
            proxy_ip = self.get_ip_by_url()

        # 检查代理是否失效
        try:
            proxies = {"http": proxy_ip}
            response = requests.get('http://www.baidu.com', proxies=proxies)
            if response.status_code != 200:
                logging.debug('代理'+proxy_ip+'失效,重新获取')
                proxy_ip = self.get_ip_by_url()
        except Exception as e:
            logging.error(e)
            proxy_ip = self.get_ip_by_url()
        return proxy_ip

    def get_ip_by_url(self):
        url = self.proxy_cf.get('proxy', 'url')
        try:
            response = requests.get(url)
            if response.status_code == 200:
                if "code" in response.text:
                    logging.error(response.text)
                    sys.exit(0)
                else:
                   if "code" in response.text:
                       proxy_ip = self.get_ip_by_url()
                   else:
                    proxy_ip = response.text.strip()
                    self.proxy_cf.set('proxy', 'ip', proxy_ip)
                    self.proxy_cf.set('proxy', 'get_ip_time', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                    with open(self.cf.get_proxy_conf(), "w+") as f:
                            self.proxy_cf.write(f)
            else:
                proxy_ip = ''
                logging.error('代理IP获取失败1')
        except Exception as e:
            logging.error('代理IP获取失败2；'+e)
            proxy_ip = ''
        return proxy_ip

    def process_request(self, request, spider):
        proxy_ip = self.get_proxy_ip()
        if proxy_ip:
            if request.url.startswith("http://"):
                request.meta['proxy'] = "http://" + str(proxy_ip)
            elif request.url.startswith("https://"):
                request.meta['proxy'] = "https://" + str(proxy_ip)
        else:
            logging.debug("未设置代理IP")
            sys.exit(0)
        logging.info('使用的代理:'+proxy_ip)


class RandomUserAgentMiddleware(object):
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
    def process_request(self, request, spider):
        ua = choice(self.user_agent_list)
        request.headers.setdefault('User-Agent', ua)
        request.headers.setdefault('Accept', '*/*')
        request.headers.setdefault('cookie', 'cna=tZ3zFZ6GUksCAQ4SlGJNqRr/; hng=CN%7Czh-CN%7CCNY%7C156; lid=ydyxfc; enc=cB6OUnSPrsisxZ0UzwbFbNogpLwRnR9Ry6936jftcyCWGtzUdMr6vSPv1YdxXPhtZL%2BESio2RxS1wJ4r3iL7Vg%3D%3D; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; dnk=ydyxfc; _m_h5_tk=e6ef1a69d89b9983e0629af8a7c738bd_1575617118355; _m_h5_tk_enc=77177ba950da58a59ccf426218b6f069; uc4=nk4=0%40GINykxWkHKzDS3d3h9Oobn4%3D&id4=0%40UO6QoO1NXNuDPAcMqXFU%2BEwSDThV; cookie2=16fe9705625ff6b9f1c6061ef27d0f9a; t=f0e599b3af0b72018e96d629904b0ae1; csg=77126f2f; _tb_token_=e316fe59137bb; l=dB_Q490rqyLFYf--BOCZlurza77TAIRfguPzaNbMi_5dt1L_DkbOkhG1fep6cjWcGVYB4dH2-seTxecYWPTaHkb4znvGongWBef..; x5sec=7b227477736d3b32223a223433336636353239633965626262353232323533656363643732623133323466434b2f41702b3846454e4b4c684c364469654c363567453d227d; isg=BBMTRQ9yStOxuwYeeU-Ny7Vfopc9yKeK1qPdtsUwbzJpRDPmTZg32nHWevKPZP-C')