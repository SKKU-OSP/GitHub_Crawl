# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class User(scrapy.Item) :
    name = scrapy.Field()
    repos_cnt = scrapy.Field()
    followers = scrapy.Field()
    following = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()

class Repository(scrapy.Item) :
    name = scrapy.Field()
    owner = scrapy.Field()
    forked = scrapy.Field()
    fork = scrapy.Field()
    star = scrapy.Field()
    subs = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    pushed_at = scrapy.Field()

class Event(scrapy.Item) :
    type = scrapy.Field()
    actor = scrapy.Field()
    created_at = scrapy.Field()