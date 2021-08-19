import requests, json

API_URL = 'https://api.github.com'
class User :
    def __init__(self, github_id):
        self.github_id = github_id
        res = requests.get(f'{API_URL}/users/{github_id}')
        user_data = json.loads(res.content)
        
        self.repos = []
        res = requests.get(user_data['repos_url'])
        repo_data = json.loads(res.content)
        print(len(repo_data))
    

class Repository :
    def __init__(self, owner, repo_name):
        self.owner = owner
        self.name = repo_name
        res = requests.get(f'{API_URL}/repos/{owner}/{repo_name}')
        repo_data = json.loads(res.content)
        print(repo_data)
        self.star = repo_data['stargazers_count']
        self.subs = repo_data['subscribers_count']

if __name__ == '__main__':
    User('mit-pdos')
    Repository('mit-pdos', 'xv6-public')