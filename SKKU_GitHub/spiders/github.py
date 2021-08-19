import scrapy, json, math
from ..items import *


API_URL = 'https://api.github.com'
class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ['api.github.com']

    def __init__(self, ids='', **kwargs):
        self.ids = ['torvalds']
        if ids != '' :
            self.ids = ids.split(',')

    def start_requests(self):
        for id in self.ids :
            yield scrapy.Request(f'{API_URL}/users/{id}', self.parse_user)

    def parse_user(self, res) :
        data = json.loads(res.body)
        user_item = User()
        user_item['name'] = data['name']
        user_item['repos_cnt'] = data['public_repos']
        user_item['followers'] = data['followers']
        user_item['following'] = data['following']
        user_item['created_at'] = data['created_at']
        user_item['updated_at'] = data['updated_at']
        yield user_item

        for i in range(math.ceil(user_item['repos_cnt'] / 100)) :
            yield scrapy.Request(
                f'{data["repos_url"]}?page={i + 1}&per_page=100',
                self.get_user_repos
            )

    def get_user_repos(self, res) :
        data = json.loads(res.body)
        for repo in data :
            yield scrapy.Request(repo['url'], self.parse_repo)
    
    def parse_repo(self, res) :
        repo = json.loads(res.body)
        repo_item = Repository()
        repo_item['name'] = repo['name']
        repo_item['owner'] = repo['owner']['login']
        repo_item['forked'] = repo['fork']
        repo_item['star'] = repo['stargazers_count']
        repo_item['subs'] = repo['subscribers_count']
        repo_item['fork'] = repo['forks_count']
        repo_item['created_at'] = repo['created_at']
        repo_item['updated_at'] = repo['updated_at']
        repo_item['pushed_at'] = repo['pushed_at']
        yield repo_item