# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import time
import MySQLdb
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.i = 0
        self.conn = MySQLdb.connect(
            host='localhost', user='root', passwd='Gold7789@',
            db='article_spider', charset='utf8', use_unicode=True
        )
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        start_time = time.time()  # 计时开始

        insert_sql = """
            INSERT INTO jobbole_article(title, url, url_object_id, front_image_path,
                                       front_image_url, parise_nums, comment_nums,
                                       fav_nums, tags, content, create_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title=VALUES(title),
                front_image_path=VALUES(front_image_path),
                front_image_url=VALUES(front_image_url),
                parise_nums=VALUES(parise_nums),
                comment_nums=VALUES(comment_nums),
                fav_nums=VALUES(fav_nums),
                tags=VALUES(tags),
                content=VALUES(content),
                create_date=VALUES(create_date)
        """

        params = [
            item.get('title', ""),
            item.get('url', ""),
            item.get('url_object_id', ""),
            item.get('front_image_path', ""),
            ",".join(item.get('front_image_url', [])),
            item.get('parise_nums', 0),
            item.get('comment_nums', 0),
            item.get('fav_nums', 0),
            item.get('tags', ""),
            item.get('content', ""),
            item.get('create_date', "1970-01-01")
        ]

        try:
            self.cursor.execute(insert_sql, tuple(params))
            self.conn.commit()
        except Exception as e:
            spider.logger.error(f"MySQL写入异常: {e}")

        elapsed = time.time() - start_time
        self.i += 1
        spider.logger.info(f"MySQL写入第 {self.i} 条 耗时: {elapsed:.4f}秒, 文章标题: {item.get('title', '')[:20]}")

        return item

    def spider_closed(self, spider):
        self.conn.close()


class ArticleImgPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for img_url in item.get("front_image_url", []):
            if not img_url or not isinstance(img_url, str):  # 过滤 None 和非字符串
                continue
            img_url = self.normalize_url(img_url)
            if not img_url:
                continue
            yield Request(
                img_url,
                headers={
                    "Referer": item.get("url", ""),
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/138.0.0.0 Safari/537.36"
                },
                meta={
                    "start_time": time.time(),
                    "title": item.get("title", "No Title")
                }
            )

    def item_completed(self, results, item, info):
        image_paths = [x["path"] for ok, x in results if ok]
        if image_paths:
            item["front_image_path"] = image_paths[0]
        return item

    def normalize_url(self, url):
        if not url or not isinstance(url, str):
            return None
        if url.startswith("//"):
            return "https:" + url
        return url



# class JsonWithEncodingPipeline(object):
#     def __init__(self):
#         self.file = codecs.open('article.json', 'a', encoding='utf-8')
#
#     def process_item(self, item, spider):
#         line = json.dumps(dict(item), ensure_ascii=False) + "\n"
#         self.file.write(line)
#         return item
#
#     def spider_closed(self, spider):
#         self.file.close()

# class JsonExportPipeline(object):
#     def __init__(self):
#         self.file = open('articleexport.json', 'wb')
#         self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8')
#         self.exporter.start_exporting()
#
#     def process_item(self, item, spider):
#         self.exporter.export_item(item)
#         return item
#
#     def spider_closed(self, spider):
#         self.exporter.finish_exporting()
#         self.file.close()

