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
    total_of_repos = scrapy.Field()
    total_commits = scrapy.Field()
    total_PRs = scrapy.Field()
    total_issues = scrapy.Field()
    achievements = scrapy.Field()
    highlights = scrapy.Field()