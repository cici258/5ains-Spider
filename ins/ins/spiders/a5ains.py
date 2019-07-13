# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.spiders import Rule
import urllib
from copy import deepcopy

class A5ainsSpider(RedisCrawlSpider):
    handle_httpstatus_list = [404, 500]
    name = '5ains'
    allowed_domains = ['5ains.com']
    # start_urls = ['https://www.5ains.com/Start']
    redis_key = "5ains"

    rules = (
        # 明星列表的url地址
        Rule(LinkExtractor(restrict_xpaths=("//div[@class='card-image']/a",)), callback="parse_user_page", follow=True),
        # 明星post的url地址
        Rule(LinkExtractor(restrict_xpaths=("//div[@class='card-image']/a",)), callback="parse_detail_url",follow=True)
    )

    # def parse(self, response):
    #     div_list = response.xpath("//div[@class='col s4 m2']")
    #     for div in div_list:
    #         item = {}
    #         item["user_url"] = div.xpath(".//a[1]/@href").extract_first()
    #         item["user_url"] = urllib.parse.urljoin(response.url,item["user_url"])
    #
    #         if item["user_url"] is not None:
    #             yield scrapy.Request(
    #                 item["user_url"],
    #                 callback=self.parse_user_page,
    #                 meta={"item":deepcopy(item)}
    #             )


    def parse_user_page(self,response):
        item = {}
        item["user_name"] = response.xpath("//div[@class='col s10']//p[1]/span[4]/text()").extract_first()
        item["user_avatar"] = response.xpath("//div[@class='row valign-wrapper']//img/@src").extract_first()
        item["user_id"] = response.xpath("//div[@class='col s10']//p[1]/span[2]/text()").extract_first()
        item["user_post_num"] = response.xpath("//div[@class='col s10']//p[2]/span[2]/text()").extract_first()
        item["user_fans_num"] = response.xpath("//div[@class='col s10']//p[2]/span[4]/text()").extract_first()
        post_list = response.xpath("//div[@class='col s6 m3']")
        for post in post_list:
            item["user_post_date"] = post.xpath("./div/div[2]/p[2]/text()").extract_first()
            item["user_post_content"] = post.xpath("normalize-space(./div/div[2]/p[3]/text())").extract_first()

            item["user_post_url"] = post.xpath(".//div[@class='card-image']/a/@href").extract_first()
            item["user_post_url"] = urllib.parse.urljoin(response.url, item["user_post_url"])

            yield scrapy.Request(
                item["user_post_url"],
                callback=self.parse_detail_url,
                meta={"item":deepcopy(item)}
            )

        # 翻页
        next_url = response.xpath("//ul[@class='pagination']/li[last()]/a/@href").extract_first()

        if next_url is not None:
            next_url = urllib.parse.urljoin(response.url, next_url)

            yield scrapy.Request(
                next_url,
                callback=self.parse_user_page,
                meta={"item":deepcopy(item)}
            )

    def parse_detail_url(self,response):
        item = deepcopy(response.meta["item"])
        item_type = response.xpath("//div[@class='col s12 m9 offset-m2']/div[1]//@type").extract_first()

        if item_type == "video/mp4":
            item["user_post_video"] = response.xpath("//div[@class='col s12 m9 offset-m2']/div[1]//@src").extract_first()
            yield item
        else:
            item["user_post_img"] = response.xpath("//div[@class='col s12 m9 offset-m2']/div[1]//@src").extract()
            yield item

