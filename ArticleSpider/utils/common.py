# @Time    : 2025/7/14 23:23
# @Author  : libaojin
# @File    : common.py
import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)

    return m.hexdigest()

def clean_text( text):
    text = text.replace('\xa0', '').replace('\u3000', '').replace('\u200b', '').replace('\u2002','').replace('\n','').replace('\r', '').replace(' ','')
    return text

if __name__ == '__main__':
    print(get_md5("https://news.cnblogs.com"))