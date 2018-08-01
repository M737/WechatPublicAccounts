# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html



import json
import pymysql
class  WechatPipeline(object):
    def __init__(self):
        config = {'host': '127.0.0.1','user': 'root','port': 3306,'database': 'test','charset': 'utf8'}
        self.cnn = pymysql.connect(**config)
        self.cursor = self.cnn.cursor()
        
    def process_item(self, item, spider):
        sql = "insert into xxx (title, pubdate, article) values(item['title'], item['pubdate'],item['article'])"
        self.cursor.execute(sql)
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.cnn.close()