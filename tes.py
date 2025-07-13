# @Time    : 2025/7/13 17:51
# @Author  : libaojin
# @File    : tes.py
import re

a = "2025-07-13 15:36"
b = re.match(r'\".*"', a)
print(b)
