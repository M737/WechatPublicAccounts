# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import json
import re
import time
from wechat.items import WechatItem
from scrapy.spiders import CrawlSpider

class PubSpider(CrawlSpider):
    name = 'pub'
    choice = input('搜公众号请输入1，搜文章请输入2：')
    content = input('请输入关键字：')
    headers = {'Host': 'weixin.sogou.com',
               'Referer': 'http://weixin.sogou.com/weixin?type=2&s_from=input&query=%E6%B5%85%E5%B1%B1%E5%B0%8F%E7%AD%91&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=5109&sst0=1513697178371&lkt=0%2C0%2C0',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
    # start_urls = ['http://weixin.sogou.com/weixin']
    page = 1
    def start_requests(self):
        if self.choice == '1':
            return [scrapy.FormRequest(url='http://weixin.sogou.com/weixin',
                                    formdata={'type':'1',
                                            's_from':'input',
                                            'query':self.content,
                                            'ie':'utf8',
                                            '_sug_':'n',
                                            '_sug_type_':''},
                                    method='get',
                                    callback=self.parse1)]

        elif self.choice == '2':
            return [scrapy.FormRequest(url='http://weixin.sogou.com/weixin',
                                    formdata={'type':'2',
                                            'ie':'utf8',
                                            'query':self.content,
                                            'tsn':'1',
                                            'ft':'',
                                            'et':'',
                                            'interation':'',
                                            'sst0': str(int(time.time()*1000)),
                                            'page': str(self.page),
                                            'wxid':'',
                                            'usip':''},
                                    method='get',
                                    meta={'page':self.page},
                                    headers=self.headers,
                                    callback=self.parse2)]
        else:
            print('输入有误，程序退出')
            return

    def parse1(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        pub_url = soup.find('a', attrs={'uigs': 'account_name_0'})['href']
        yield scrapy.Request(pub_url,callback=self.pub_parse)

    def parse2(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        node_soup = soup.find('ul', attrs={'class': 'news-list'})
        for node in node_soup.findAll('li'):
            url = node.select('div h3 a')[0]['href']
            yield scrapy.Request(url, callback=self.article_parse)
        page = response.meta['page']
        while page < 5:
            page += 1
            yield scrapy.FormRequest(url='http://weixin.sogou.com/weixin',
                                 formdata={'type': '2',
                                         'ie': 'utf8',
                                         'query': self.content,
                                         'tsn': '1',
                                         'ft': '',
                                         'et': '',
                                         'interation': '',
                                         'sst0': str(int(time.time() * 1000)),
                                         'page': str(page),
                                         'wxid': '',
                                         'usip': ''},
                                 method='get',
                                 meta={'page':page},
                                 headers=self.headers,
                                 callback=self.parse2)

    def pub_parse(self, response):
        patt = re.compile(r'var msgList = (\{.*?\});')
        result = patt.search(response.text)
        url_list = json.loads(result.group(1))['list']
        for data in url_list:
            article_url = data['app_msg_ext_info']['content_url']
            url = 'https://mp.weixin.qq.com' + article_url.replace(r'amp;', '')
            yield scrapy.Request(url, callback=self.article_parse)

    def article_parse(self, response):
        item = WechatItem()
        soup = BeautifulSoup(response.text, 'lxml')
        item['title'] = soup.find('h2', attrs={'class':'rich_media_title'}).get_text()
        item['pubdate'] = soup.find('em', attrs={'id':'post-date'}).get_text()
        item['article'] = soup.find('div', attrs={'class':'rich_media_content '}).get_text()
        # print(item['title'])
        yield item






