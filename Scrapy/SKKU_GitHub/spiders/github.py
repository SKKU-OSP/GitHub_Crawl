import scrapy, json, math
from ..items import *
from ..configure import *


API_URL = 'https://api.github.com'
class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ['api.github.com']

    def __init__(self, ids='', **kwargs):
        self.ids = ['tsfo1489']
        self.hd = {
            'Authorization' : f'token {OAUTH_TOKEN}'
        }
        if ids != '' :
            self.ids = ids.split(',')

    def start_requests(self):
        for id in self.ids :
            yield scrapy.Request(
                f'{API_URL}/users/{id}', 
                self.parse_user,
                headers=self.hd
                )

    def parse_user(self, res) :
        user_json = json.loads(res.body)
        user_item = User()
        user_item['github_id'] = user_json['name']
        #user_item['stars'] = user_json['name']
        user_item['followers'] = user_json['followers']
        user_item['following'] = user_json['following']
        user_item['total_of_repos'] = user_json['public_repos']
        yield user_item