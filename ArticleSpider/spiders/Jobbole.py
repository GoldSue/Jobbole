import re
import json
import time
import scrapy
from urllib import parse
from ArticleSpider.items import Jobbole
from ArticleSpider.utils import common

class JobboleSpider(scrapy.Spider):
    name = "Jobbole"
    start_urls = ["https://news.cnblogs.com"]
    custom_settings = {
        'COOKIES_ENABLED': True
    }

    def get_login_cookies(self):
        import undetected_chromedriver as uc
        import time

        options = uc.ChromeOptions()
        options.add_argument('--disable-crash-reporter')
        options.add_argument('--disable-breakpad')
        browser = uc.Chrome(options=options)

        try:
            start = time.time()
            browser.get('https://account.cnblogs.com/signin')
            time.sleep(3)
            browser.find_element('id', 'mat-input-0').send_keys('q15136522267@gmail.com')
            browser.find_element('id', 'mat-input-1').send_keys('Gold7789')
            time.sleep(1)
            browser.find_element('xpath', '//span[text()=" 登录 "]').click()
            time.sleep(1)
            browser.find_element('id', 'SM_BTN_1').click()
            time.sleep(5)
            browser.find_element('xpath', '//li/a[text()="新闻"]').click()
            time.sleep(2)
            cookies = {c['name']: c['value'] for c in browser.get_cookies()}
            self.logger.info(f"get_login_cookies took {time.time() - start:.2f} seconds")
        finally:
            browser.quit()
        return cookies

    def start_requests(self):
        cookies_dict = self.get_login_cookies()
        for url in self.start_urls:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/138.0.0.0 Safari/537.36'
            }
            yield scrapy.Request(
                url, cookies=cookies_dict, headers=headers, dont_filter=True
            )

    def parse(self, response):
        start = time.time()
        items = response.xpath('//div[@class="content"]')
        self.logger.info(f"parse list page got {len(items)} items")

        for item in items:
            href = item.xpath('.//h2[@class="news_entry"]/a/@href').get()
            full_url = response.urljoin(href)

            img_url = item.xpath('.//img[@class="topic_img"]/@src').get()
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_detail,
                meta={'img_url': img_url}
            )
        self.logger.info(f"parse list page took {time.time() - start:.2f} seconds")

        next_page = response.xpath('//a[text()="Next >"]/@href').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_detail(self, response):
        start_time = time.time()
        match = re.match(r'.*?(\d+)', response.url)
        if match:
            article_item = Jobbole()
            news_id = match.group(1)
            title = response.css('#news_title a::text').get(default='').strip()
            create_date = response.css('.time::text').get(default='').strip()
            content = ''.join(response.css('#news_body ::text').getall()).strip()
            tag_list = response.css('#link_source2::text').getall()
            tags = ",".join(tag.strip() for tag in tag_list)

            article_item['title'] = title
            article_item['create_date'] = create_date
            article_item['url'] = response.url
            image_url = [response.meta['img_url']]
            article_item['front_image_url'] = image_url
            article_item['content'] = content
            article_item['tags'] = tags
            article_item['url_object_id'] = common.get_md5(response.url)


            ajax_url = parse.urljoin(response.url, f"/NewsAjax/GetAjaxNewsInfo?contentId={news_id}")
            yield scrapy.Request(
                url=ajax_url,
                callback=self.parse_num,
                meta={"article_item": article_item}
            )

    def parse_num(self, response):
        data = json.loads(response.text)
        article_item = response.meta.get('article_item', '')
        praise_nums = data.get('DiggCount', 0)
        fav_nums = data.get('ViewCount', 0)
        comment_nums = data.get('CommentCount', 0)

        article_item['praise_nums'] = praise_nums
        article_item['fav_nums'] = fav_nums
        article_item['comment_nums'] = comment_nums
        article_item['url_object_id'] = common.get_md5(article_item['url'])


        yield article_item
