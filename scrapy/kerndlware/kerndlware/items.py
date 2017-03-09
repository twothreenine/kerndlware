# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OfferItem(scrapy.Item):
    # define the fields for your item here like:
    general_offer_count = scrapy.Field() # for lists/shops which sort specific offers by general offers
    offer_category = scrapy.Field() # category from list/shop
    offer_original_id = scrapy.Field() # art no from list/shop to compare it in the future
    offer_name = scrapy.Field()
    offer_description = scrapy.Field()
    offer_unit = scrapy.Field()
    offer_total_price = scrapy.Field()
    offer_parcel = scrapy.Field()
    offer_quantity = scrapy.Field()