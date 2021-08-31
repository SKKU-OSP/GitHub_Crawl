import requests
from configure import OAUTH_TOKEN
from datetime import datetime

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
                params={'page': page, 'per_page': per_page})
        return res.json()