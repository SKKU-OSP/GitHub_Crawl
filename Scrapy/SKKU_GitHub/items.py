# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class User(scrapy.Item) :
    github_id = scrapy.Field()
    stars = scrapy.Field()
    followers = scrapy.Field()
    following = scrapy.Field()
    request_cnt = scrapy.Field()
    total_repos = scrapy.Field()
    total_commits = scrapy.Field()
    total_PRs = scrapy.Field()
    total_issues = scrapy.Field()
    achievements = scrapy.Field()
    highlights = scrapy.Field()
    stars = scrapy.Field()

class UserUpdate(scrapy.Item) :
    github_id = scrapy.Field()
    total_commits = scrapy.Field()
    total_PRs = scrapy.Field()
    total_issues = scrapy.Field()
    achievements = scrapy.Field()
    highlights = scrapy.Field()
    stars = scrapy.Field()

class UserPeriod(scrapy.Item):
    github_id = scrapy.Field()
    start_yymm = scrapy.Field()
    end_yymm = scrapy.Field()