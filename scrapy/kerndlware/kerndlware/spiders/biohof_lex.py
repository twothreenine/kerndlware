# -*- coding: utf-8 -*-
import scrapy
from kerndlware.items import *
import re

class BiohofLexSpider(scrapy.Spider):
    name = "biohof_lex"
    allowed_domains = ["shop.biohof-lex.de"]
    start_urls = ['http://shop.biohof-lex.de/']

    def __init__(self):
        super(BiohofLexSpider,self).__init__()
        self.page_counter = 1

    def parse(self, response):
        total_pages = int(response.css("#pages a:last-child::text").extract_first())
        for i in range(1, total_pages):
            yield scrapy.Request("http://shop.biohof-lex.de/?p=productsList&iPage=" + str(i), callback=self.parse_entries)

    def parse_entries(self, response):
        entries = response.css(".entry")
        for e in entries:
            i = OfferItem()
            i["offer_category"] = e.css("h5 a::text").extract_first()
            original_id_href = e.css("h2 a::attr(href)").extract_first()
            m = re.search('(.+?)(\d+)', original_id_href)
            i["offer_original_id"] = m.group(2)
            name_and_amount = e.css("h2 a::text").extract_first()
            m = re.search('(Bio-)?(.+?) (\d+) ?(g|kg|ml|l)?', name_and_amount)         #         old:    (.+?) (\d+) ?(g|kg)?
            if m:
                i["offer_name"] = m.group(2)
                i["offer_amount"] = m.group(3)
                i["offer_unit"] = m.group(4)
            else:
                i["offer_name"] = name_and_amount   # check
            i["offer_description"] = e.css("p::text").extract_first()
            i["offer_total_price"] = e.css("a.cart::text").extract_first()
            yield i