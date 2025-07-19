import time
import MySQLdb
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy import signals


def clean_url_list(urls):
    """过滤 None、空字符串、非字符串，并返回 strip 后的列表"""
    if isinstance(urls, str):
        urls = [urls]
    return [url.strip() for url in urls if isinstance(url, str) and url.strip()]


class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.i = 0
        self.insert_success_count = 0
        self.duplicate_count = 0
        self.fail_count = 0
        self.has_printed_duplicate = False
        self.has_printed_failed = False

        self.conn = MySQLdb.connect(
            host='localhost', user='root', passwd='Gold7789@',
            db='article_spider', charset='utf8', use_unicode=True
        )
        self.cursor = self.conn.cursor()

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline

    def process_item(self, item, spider):
        insert_sql = """
            INSERT INTO jobbole_article(title, url, url_object_id, front_image_path,
                                       front_image_url, parise_nums, comment_nums,
                                       fav_nums, tags, content, create_date,insert_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,NOW())
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

        image_urls = clean_url_list(item.get("front_image_url", []))
        joined_urls = ",".join(image_urls)

        params = [
            item.get('title', ""),
            item.get('url', ""),
            item.get('url_object_id', ""),
            item.get('front_image_path', ""),
            joined_urls,
            item.get('praise_nums', 0),
            item.get('comment_nums', 0),
            item.get('fav_nums', 0),
            item.get('tags', ""),
            item.get('content', ""),
            item.get('create_date', "1970-01-01")
        ]

        try:
            affected_rows = self.cursor.execute(insert_sql, tuple(params))
            self.conn.commit()

            if affected_rows == 1:
                self.insert_success_count += 1
            elif affected_rows == 2:
                self.duplicate_count += 1
                if not self.has_printed_duplicate:
                    spider.logger.info(f"MySQL处理，重复更新 1 条❌ 文章标题: {item.get('title', '')[:25]}")
                    self.has_printed_duplicate = True

        except Exception as e:
            self.fail_count += 1
            if not self.has_printed_failed:
                spider.logger.error(f"MySQL处理，插入失败 文章标题: {item.get('title', '')[:25]}")
                self.has_printed_failed = True
            spider.logger.error(f"MySQL写入异常: {e}")

        self.i += 1
        elapsed = time.time() - getattr(item, "_start_time", time.time())
        spider.logger.info(f"MySQL写入第 {self.i} 条 , 耗时 {elapsed:.2f} 秒，文章标题: {item.get('title', '')[:25]}")
        return item

    def spider_closed(self, spider):
        self.conn.close()
        spider.logger.info(
            f"MySQL处理完成，共处理 {self.i} 条，成功插入 {self.insert_success_count} 条，重复更新 {self.duplicate_count} 条，失败 {self.fail_count} 条"
        )


class ArticleImgPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        image_urls = item.get("front_image_url", [])
        if isinstance(image_urls, str):
            image_urls = [image_urls]

        valid_urls = [self.normalize_url(url) for url in image_urls
                      if isinstance(url, str) and url.strip()]

        for img_url in valid_urls:
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
        else:
            item["front_image_path"] = ""
        return item

    def normalize_url(self, url):
        if not url or not isinstance(url, str):
            return None
        if url.startswith("//"):
            return "https:" + url
        return url.strip()
