# @Time    : 2025/7/6 15:11
# @Author  : libaojin
# @File    : nain.py
import os
import sys
from scrapy.cmdline import execute
(sys.path.append(os.path.dirname(os.path.abspath(__file__))))
execute(['scrapy', 'crawl', 'Jobbole'])