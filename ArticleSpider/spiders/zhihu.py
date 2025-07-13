# @Time    : 2025/7/12 18:38
# @Author  : libaojin
# @File    : zhihu.py
import scrapy


class JobboleSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ["https://www.zhihu.com"]
    custom_settings = {
        'COOKIES_ENABLED': True
    }

    def start_requests(self):
        #从这里模拟登录知乎获取cookie
        #两种识别滑动验证方法：1.使用opencv识别。2.使用机器学习识别。
        pass