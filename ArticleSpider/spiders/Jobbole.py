import re
import json
import scrapy
from urllib import parse


class JobboleSpider(scrapy.Spider):
    name = "Jobbole"
    allowed_domains = ["news.cnblogs.com"]
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
        hrefs = response.xpath('//h2[@class="news_entry"]/a/@href').getall()
        for href in hrefs:
            full_url = response.urljoin(href)
            # print("文章详情 URL：", full_url)
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_detail
            )

        # 提取下一页
        next_page = response.xpath('//a[text()="Next >"]/@href').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            print("下一页 URL：", next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_detail(self, response):
        match = re.match(r'.*?(\d+)', response.url)
        if match:
            news_id = match.group(1)
            title = response.css('#news_title a::text').get(default='').strip()
            create_date = response.css('.time::text').get(default='').strip()
            news_body = ''.join(response.css('#news_body ::text').getall()).strip()
            tag_list = response.css('#link_source2::text').getall()
            tags = ",".join(tag.strip() for tag in tag_list)

            print("文章标题：", title)
            print("文章发布时间：", create_date)
            print("文章标签：", tags)
            print("文章内容：", news_body)


            # 发 Ajax 请求获取数据
            ajax_url = parse.urljoin(response.url, f"/NewsAjax/GetAjaxNewsInfo?contentId={news_id}")
            yield scrapy.Request(
                url=ajax_url,
                callback=self.parse_num,
                meta={
                    "news_id": news_id,
                    "title": title,
                    "create_date": create_date,
                    "news_body": news_body,
                    "tags": tags
                }
            )

    def parse_num(self, response):
        data = json.loads(response.text)
        if data:
            print("文章阅读数：", data.get("TotalView"))
            print("文章评论数：", data.get("CommentCount"))
            print("文章点赞数：", data.get("DiggCount"))

        yield {
            "news_id": response.meta['news_id'],
            "title": response.meta['title'],
            "create_date": response.meta['create_date'],
            "news_body": response.meta['news_body'],
            "tags": response.meta['tags'],
            "read_num": data.get("TotalView"),
            "comment_num": data.get("CommentCount"),
            "digg_num": data.get("DiggCount")
        }
