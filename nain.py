# @Time    : 2025/7/6 15:11
# @Author  : libaojin
# @File    : nain.py
# import os
# import sys
# from scrapy.cmdline import execute
# (sys.path.append(os.path.dirname(os.path.abspath(__file__))))
# execute(['scrapy', 'crawl', 'Jobbole'])

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ArticleSpider.spiders.Jobbole import JobboleSpider

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(JobboleSpider)
    process.start()
