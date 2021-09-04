import requests
from datetime import datetime
from bs4 import BeautifulSoup

GITHUB_API_URL = 'https://api.github.com/'

class GitHubException(Exception) :
    def __init__(self, message):
        self.message = message
    def __str__(self) :
        return self.message

class GitHub_API():
    def __init__(self, token):
        self.auth = {
            'Authorization': f'token {token}'
        }
        res = requests.get(GITHUB_API_URL, headers=self.auth)
        if res.status_code != 200 :
            raise GitHubException(f'Error in Authentication: status code {res.status_code} / {res.json()["message"]}')

    def check_quota(self):
        res = requests.get(GITHUB_API_URL, headers=self.auth)
        limit = {}
        limit['limit'] = res.headers['X-RateLimit-Limit']
        limit['remaining'] = res.headers['X-RateLimit-Remaining']
        limit['reset'] = datetime.fromtimestamp(int(res.headers['X-RateLimit-Reset']))
        limit['reset_remaining'] = limit['reset'] - datetime.now()
        limit['used'] = res.headers['X-RateLimit-Used']
        return limit

    def get(self, endpoint, page=1, per_page=100) :
        res = requests.get(
                f'{GITHUB_API_URL}{endpoint}', 
                params={'page': page, 'per_page': per_page},
                headers=self.auth)
        if res.status_code != 200 :
            raise GitHubException(f'Error: status code {res.status_code}')
        return res.json()

    def get_user(self, github_id) :
        json_data = self.get(f'users/{github_id}')
        data = {'type':'user'}
        data['github_id'] = github_id
        data['followers'] = json_data['followers']
        data['following'] = json_data['following']
        data['total_of_repos'] = json_data['public_repos']

        # Highlights and Achievements
        res = requests.get(f'http://github.com/{github_id}')
        soup = BeautifulSoup(res.text, 'html.parser')
        info_list = [tag.parent for tag in soup.select('h2.h4.mb-2')]
        
        for info in info_list :
            if info.h2.text == 'Achievements' :
                data['achievements'] = ', '.join(
                    [tag['alt'] for tag in info.select('img')]
                    )
            if info.h2.text == 'Highlights' :
                data['highlights'] = ', '.join(
                    [tag.text.strip() for tag in info.select('li')]
                )

        return data
    
    def get_repos_of_user(self, github_id) :
        repo_list = []
        while True:
            json_data = self.get(f'users/{github_id}/repos', page=1)
            for repo_data in json_data:
                repo_list.append(repo_data['name'])
            if len(json_data) < 100 :
                break
        return repo_list
        
    def get_repo(self, github_id, repo_name) :
        json_data = self.get(f'repos/{github_id}/{repo_name}')
        repo = {
            'type': 'repo',
            'github_id': json_data['owner']['login'], 
            'repo_name': json_data['name']
        }
        repo['stargazers_count'] = json_data['stargazers_count']
        repo['forks_count'] = json_data['forks_count']
        repo['watchers'] = None if not 'subscribers_count' in json_data else json_data['subscribers_count']
        repo['create_date'] = json_data['created_at']
        repo['update_date'] = json_data['updated_at']
        repo['language'] = json_data['language']
        repo['proj_short_desc'] = not json_data['description'] is None
        repo['license'] = None if json_data['license'] is None else json_data['license']['name']
        
        repo['release_ver'] = None
        repo['release_count'] = 0
        release_data = self.get(f'repos/{github_id}/{repo_name}/releases')
        if len(release_data) > 0 :
            repo['release_ver'] = release_data[0]['name']
            while True :
                repo['release_count'] += len(release_data)
                if len(release_data) < 100 :
                    break

        repo['contributors'] = 0
        try :
            contributor_data = self.get(f'repos/{github_id}/{repo_name}/contributors')
            while True :
                repo['contributors'] += len(contributor_data)
                if len(contributor_data) < 100 :
                    break
        except GitHubException :
            repo['contributors'] = 999

        repo['readme'] = 0
        content_data = self.get(f'repos/{github_id}/{repo_name}/contents')
        for content in content_data:
            if 'readme' in content['name'] or 'README' in content['name']:
                repo['readme'] = content['size']

        return repo