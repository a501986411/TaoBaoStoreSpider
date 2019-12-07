# -*- coding: utf-8 -*-

class conf:
    # conf_dir = "D:\\project\\TaobaoStoreSpider\\config\\"
    conf_dir = "/www/TaoBaoStoreSpider/config/"
    def get_db_conf(self):
        return self.conf_dir+"db.ini"

    def get_proxy_conf(self):
        return self.conf_dir + "proxy.ini"
