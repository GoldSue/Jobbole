# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline,Request

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item


class ArticleImgPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for img_url in item.get("front_image_url", []):
            img_url = self.normalize_url(img_url)
            yield Request(
                img_url,
                headers={
                    "Referer": item.get("url", ""),  # 页面来源，防止服务器拦截
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/138.0.0.0 Safari/537.36"
                }
            )

    def item_completed(self, results, item, info):
        if results:
            image_paths = [x["path"] for ok, x in results if ok]
            if image_paths:
                item["front_image_path"] = image_paths[0]  # 或者保留全部路径 image_paths
        return item

    def normalize_url(self, url):
        if url.startswith("//"):
            return "https:" + url
        return url