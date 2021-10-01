from bs4 import BeautifulSoup
import scrapy, json, math
from datetime import datetime, timedelta
from ..items import *
from ..configure import *


API_URL = 'https://api.github.com'
HTML_URL = 'https://github.com'
class GithubSpider(scrapy.Spider):
    name = 'github'

    def __init__(self, ids='', **kwargs):
        self.ids = ['BigDannyK']
        self.hd = {
            'Authorization' : f'token {OAUTH_TOKEN}'
        }
        if ids != '' :
            self.ids = ids.split(',')

    def start_requests(self):
        for id in self.ids :
            yield self.api_get(f'users/{id}', self.parse_user)
    
    def __end_of_month(self, now: datetime) :
        next_month = now.month % 12 + 1
        next_year = now.year + now.month // 12
        return datetime(next_year, next_month, 1) - timedelta(seconds=1)

    def api_get(self, endpoint, callback, metadata={}, page=1, per_page=100) :
        req = scrapy.Request(
                f'{API_URL}/{endpoint}?page={page}&per_page={per_page}',
                callback,
                headers=self.hd,
                meta=metadata)
        
        return req

    def parse_user(self, res) :
        user_json = json.loads(res.body)
        github_id = user_json['login']
        user_item = User()
        user_item['github_id'] = github_id
        user_item['followers'] = user_json['followers']
        user_item['following'] = user_json['following']
        user_item['total_repos'] = user_json['public_repos']
        user_item['total_commits'] = 0
        user_item['total_PRs'] = 0
        user_item['total_issues'] = 0
        user_item['stars'] = 0
        user_item['request_cnt'] = 1 + math.ceil(user_json['public_repos'] / 100)

        created_date = user_json['created_at'][:7]
        updated_date = user_json['updated_at'][:7]
        pivot_date = datetime.strptime(created_date, '%Y-%m')
        end_date = datetime.strptime(updated_date, '%Y-%m')
        end_date = self.__end_of_month(end_date)
        while pivot_date < end_date :
            pivot_date = self.__end_of_month(pivot_date) + timedelta(days=1)
            user_item['request_cnt'] += 1
        yield user_item


        yield self.api_get(
            f'users/{github_id}/repos', 
            self.parse_user_repo,
            {'github_id': github_id, 'page': 1}
            )

        pivot_date = datetime.strptime(created_date, '%Y-%m')
        while pivot_date < end_date :
            from_date = pivot_date.strftime('%Y-%m-%d')
            to_date = self.__end_of_month(pivot_date).strftime('%Y-%m-%d')
            yield scrapy.Request(
                f'{HTML_URL}/{github_id}/?tab=overview&from={from_date}&to={to_date}',
                self.parse_user_update,
                meta={'github_id':github_id},
            )
            pivot_date = self.__end_of_month(pivot_date) + timedelta(days=1)
        
        yield scrapy.Request(
            f'{HTML_URL}/{user_json["login"]}', 
            self.parse_user_page,
            meta={'github_id':github_id}
        )

    def parse_user_update(self, res):
        github_id = res.meta['github_id']
        soup = BeautifulSoup(res.body, 'html.parser')
        user_update = UserUpdate()
        user_update['github_id'] = github_id
        user_update['target'] = 'activity'
        user_update['total_commits'] = 0
        user_update['total_PRs'] = 0
        user_update['total_issues'] = 0
        for event in soup.select('.TimelineItem-body'):
            summary = event.select_one('summary')
            if summary == None :
                summary = event.select_one('h4')
                if summary == None:
                    pass
                else:
                    summary = ' '.join(summary.text.strip().split())
                    if 'Opened their first issue' in summary :
                        user_update['total_issues'] += 1
                    if 'Opened their first pull request' in summary :
                        user_update['total_PRs'] += 1
                    if 'Created an issue' in summary :
                        user_update['total_issues'] += 1
                    if 'Created an pull request' in summary :
                        user_update['total_PRs'] += 1
                continue
            summary = summary.text.strip().split()
            if summary[0] == 'Created':
                # Create Commit
                if summary[2] == 'commit' or summary[2] == 'commits':
                    commit_list = event.select('li')
                    for commit in commit_list :
                        detail = commit.select('a')
                        commit_cnt = int(detail[1].text.strip().split()[0])
                        user_update['total_commits']  += commit_cnt
            elif summary[0] == 'Opened' :
                # Open Issues
                if 'issue' in summary or 'issues' in summary :
                    issue_list = event.select('li')
                    user_update['total_issues'] += len(issue_list)
                # Open Pull Requests
                elif 'request' in summary or 'requests' in summary :
                    pr_list = event.select('li')
                    user_update['total_PRs'] += len(pr_list)
        yield user_update

    def parse_user_page(self, res):
        soup = BeautifulSoup(res.body, 'html.parser')
        info_list = [tag.parent for tag in soup.select('h2.h4.mb-2')]
        user_data = UserUpdate()
        user_data['github_id'] = res.meta['github_id']
        user_data['target'] = 'badge'
        user_data['achievements'] = None
        user_data['highlights'] = None
        for info in info_list :
            if info.h2.text == 'Achievements' :
                user_data['achievements'] = ', '.join(
                    [tag['alt'] for tag in info.select('img')]
                    )
            if info.h2.text == 'Highlights' :
                user_data['highlights'] = ', '.join(
                    [tag.text.strip() for tag in info.select('li')]
                )
        yield user_data
    
    def parse_user_repo(self, res):
        json_data = json.loads(res.body)
        user_data = UserUpdate()
        github_id = res.meta['github_id']
        user_data['github_id'] = github_id
        user_data['target'] = 'repo_star'
        user_data['stars'] = 0
        for repo_data in json_data:
            user_data['stars'] += repo_data['stargazers_count']
        yield user_data
        
        if len(json_data) == 100 :
            metadata = res.meta
            metadata['page'] += 1
            yield self.api_get(
                f'users/{github_id}/repos',
                self.parse_user_repo,
                metadata,
                page = metadata['page']
                )

    def parse_repo(self, res):
        pass