import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

GITHUB_API_URL = 'https://api.github.com/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47'
TYPE_DEFINE = {
    'user': [
        'github_id', 'followers', 'following', 
        'total_of_repos', 'highlights', 'achievements'
    ],
    'user_period': [
        'github_id', 'start_yymm', 'end_yymm', 'stars', 
        'num_of_commits', 'num_of_prs', 'num_of_issues',
        'num_of_cr_repos'
    ],
    'repo': [
        'github_id', 'repo_name', 'stargazers_count', 'forks_count',
        'watchers', 'create_date', 'update_date', 'language', 
        'proj_short_desc', 'license', 'release_ver', 'release_count',
        'contributors', 'readme', 'commits_count', 'code_edits', 
        'prs_count', 'open_issue_count', 'close_issue_count'
    ],
    'repo_period': [
        'github_id', 'repo_name', 'start_yymm', 'end_yymm',
        'stargazer_count', 'forks_count', 'commits_count',
        'code_edits', 'prs_count', 'open_issue_count', 
        'close_issue_count', 'watchers_count', 'update_date', 
        'update_count', 'contributors_count', 'release_ver', 
        'release_count'
    ]
}

class GitHubException(Exception) :
    def __init__(self, message):
        self.message = message
    def __str__(self) :
        return self.message

class GitHub_API():
    def __init__(self, token):
        if type(token) == str:
            token_list = [token]
        else:
            token_list = token
        self.tokens = []
        for token in token_list :
            self.auth = {
                'Authorization': f'token {token}'
            }
            res = requests.get(GITHUB_API_URL, headers=self.auth)
            if res.status_code != 200 :
                raise GitHubException(f'Error in Authentication: status code {res.status_code} / {res.json()["message"]}')
            self.tokens.append(token)
        self.now_use_token = 0
        self.auth = {'Authorization': f'token {self.tokens[0]}'}

    def __end_of_month(self, now: datetime) :
        next_month = now.month % 12 + 1
        next_year = now.year + now.month // 12
        return datetime(next_year, next_month, 1) - timedelta(seconds=1)

    def __data_init(self, type) :
        data = dict.fromkeys(TYPE_DEFINE[type], 0)
        data['type'] = type
        return data

    def check_quota(self):
        res = requests.get(GITHUB_API_URL, headers=self.auth)
        limit = {}
        limit['limit'] = res.headers['X-RateLimit-Limit']
        limit['remaining'] = res.headers['X-RateLimit-Remaining']
        limit['reset'] = datetime.fromtimestamp(int(res.headers['X-RateLimit-Reset']))
        limit['reset_remaining'] = limit['reset'] - datetime.now()
        limit['used'] = res.headers['X-RateLimit-Used']
        return limit

    def get_json(self, endpoint, page=1, per_page=100) :
        while True:
            res = requests.get(
                    f'{GITHUB_API_URL}{endpoint}', 
                    params={'page': page, 'per_page': per_page},
                    headers=self.auth)
            if res.status_code != 200:
                if self.now_use_token < len(self.tokens) - 1:
                    self.now_use_token += 1
                    self.auth['Authorization'] = f'token {self.tokens[self.now_use_token]}'
                else :
                    raise GitHubException(f'Error: status code {res.status_code}')
            else :
                break
        return res.json()

    def get_soup(self, endpoint) :
        res = requests.get(f'http://github.com/{endpoint}')
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup

    def get_user(self, github_id) :
        json_data = self.get_json(f'users/{github_id}')
        data = self.__data_init('user')
        data['github_id'] = github_id
        data['followers'] = json_data['followers']
        data['following'] = json_data['following']
        data['total_of_repos'] = json_data['public_repos']

        # Highlights and Achievements
        soup = self.get_soup(github_id)
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
    
    def get_user_period(self, github_id, start_yymm, end_yymm) :
        start_date = datetime.strptime(start_yymm, '%y%m')
        end_date = self.__end_of_month(datetime.strptime(end_yymm, '%y%m'))
        stats = self.__data_init('user_period')
        stats['github_id'] = github_id
        stats['start_yymm'] = start_yymm
        stats['end_yymm'] = end_yymm

        contributed_repo = set()
        page = 1
        while True:
            json_data = self.get_json(f'users/{github_id}/events', page)
            for event in json_data:
                event_date = datetime.fromisoformat(event['created_at'][:-1])
                if event_date < start_date or event_date > end_date :
                    continue
                if event['type'] == 'CreateEvent' :
                    if event['payload']['ref_type'] == 'repository':
                        stats['num_of_cr_repos'] += 1
                if event['type'] == 'WatchEvent' :
                    stats['stars'] += 1
                if event['type'] == 'PushEvent' :
                    repo_name = event['repo']['name']
                    if repo_name[:repo_name.find('/')] != github_id :
                        contributed_repo.add(repo_name)
                    stats['num_of_commits'] += event['payload']['size']
                if event['type'] == 'IssuesEvent' :
                    stats['num_of_issues'] += 1
                if event['type'] == 'PullRequestEvent' :
                    stats['num_of_prs'] += 1
            if len(json_data) < 100 :
                break
            page += 1
        stats['num_of_co_repos'] = len(contributed_repo)
        return stats

    def get_user_period_old(self, github_id, start_yymm, end_yymm) :
        start_date = datetime.strptime(start_yymm, '%y%m')
        end_date = self.__end_of_month(datetime.strptime(end_yymm, '%y%m'))
        stats = self.__data_init('user_period')
        stats['github_id'] = github_id
        stats['start_yymm'] = start_yymm
        stats['end_yymm'] = end_yymm
        contributed_repo = set()
        
        pivot_date = start_date
        while pivot_date < end_date :
            from_date = pivot_date.strftime('%Y-%m-%d')
            to_date = self.__end_of_month(pivot_date).strftime('%Y-%m-%d')
            soup = self.get_soup(f'{github_id}/?tab=overview&from={from_date}&to={to_date}')
            for event in soup.select('.TimelineItem-body'):
                summary = event.select_one('summary')
                if summary == None :
                    continue

                summary = summary.text.strip().split()
                if summary[0] == 'Created':
                    # Create Commit
                    if summary[2] == 'commit' or summary[2] == 'commits':
                        commit_list = event.select('li')
                        for commit in commit_list :
                            detail = commit.select('a')
                            repo = detail[0].text
                            commit_cnt = int(detail[1].text.strip().split()[0])
                            stats['num_of_commits'] += commit_cnt
                            if repo.split('/')[0] != github_id :
                                contributed_repo.add(repo)
                    # Create Repository
                    elif summary[2] == 'repository' or summary[2] == 'repositories':
                        repo_list = event.select('li')
                        for repo in repo_list:
                            stats['num_of_cr_repos'] += 1
                elif summary[0] == 'Opened' :
                    # Open Issues
                    if 'issue' in summary or 'issues' in summary :
                        issue_list = event.select('li')
                        for issue in issue_list:
                            stats['num_of_issues'] += 1
                    # Open Pull Requests
                    elif 'request' in summary or 'requests' in summary :
                        pr_list = event.select('li')
                        for pr in pr_list:
                            stats['num_of_prs'] += 1
                        pass
            pivot_date = self.__end_of_month(pivot_date) + timedelta(days=1)
            
        return stats

    def get_repos_of_user(self, github_id) :
        repo_list = []
        page = 1
        while True:
            json_data = self.get_json(f'users/{github_id}/repos', page)
            for repo_data in json_data:
                repo_list.append(repo_data['name'])
            if len(json_data) < 100 :
                break
            page += 1
        return repo_list
        
    def get_repo(self, github_id, repo_name) :
        json_data = self.get_json(f'repos/{github_id}/{repo_name}')
        repo = self.__data_init('repo')
        repo['stargazers_count'] = json_data['stargazers_count']
        repo['forks_count'] = json_data['forks_count']
        repo['watchers'] = None if not 'subscribers_count' in json_data else json_data['subscribers_count']
        repo['create_date'] = json_data['created_at']
        repo['update_date'] = json_data['updated_at']
        repo['language'] = json_data['language']
        repo['proj_short_desc'] = not json_data['description'] is None
        repo['license'] = None if json_data['license'] is None else json_data['license']['name']
        
        repo['release_ver'] = None
        release_data = self.get_json(f'repos/{github_id}/{repo_name}/releases')
        if len(release_data) > 0 :
            repo['release_ver'] = release_data[0]['name']
            page = 1
            while True :
                repo['release_count'] += len(release_data)
                if len(release_data) < 100 :
                    break
                page += 1
                release_data = self.get_json(f'repos/{github_id}/{repo_name}/releases', page)

        try :
            contributor_data = self.get_json(f'repos/{github_id}/{repo_name}/contributors', page=1)
            page = 1
            while True :
                repo['contributors'] += len(contributor_data)
                if len(contributor_data) < 100 :
                    break
                page += 1
                contributor_data = self.get_json(f'repos/{github_id}/{repo_name}/contributors', page)
        except GitHubException :
            repo['contributors'] = 999

        content_data = self.get_json(f'repos/{github_id}/{repo_name}/contents')
        for content in content_data:
            if 'readme' in content['name'] or 'README' in content['name']:
                repo['readme'] = content['size']

        page = 1
        commit_list = self.get_json(f'repos/{github_id}/{repo_name}/commits')
        while len(commit_list) > 0 :
            repo['commits_count'] += len(commit_list)
            for commit in commit_list :
                stat = self.get_json(f'repos/{github_id}/{repo_name}/commits/{commit["sha"]}')
                repo['code_edits'] += stat['stats']['total']
            page += 1
            commit_list = self.get_json(f'repos/{github_id}/{repo_name}/commits', page)

        soup = self.get_soup(f'{github_id}/{repo_name}/pulls')
        prs_cnt = soup.select_one('a[data-ga-click="Pull Requests, Table state, Open"]').parent
        prs_cnt = [x.text.strip().split() for x in prs_cnt.select('a')]
        repo['prs_counts'] = int(prs_cnt[0][0]) + int(prs_cnt[1][0])

        soup = self.get_soup(f'{github_id}/{repo_name}/issues')
        issue_cnt = soup.select_one('a[data-ga-click="Issues, Table state, Open"]').parent
        issue_cnt = [x.text.strip().split() for x in issue_cnt.select('a')]
        repo['open_issue_count'] = int(issue_cnt[0][0])
        repo['close_issue_count'] = int(issue_cnt[1][0])

        return repo
        
    def get_repo_period(self, github_id, repo_name, start_yymm, end_yymm) :
        start_date = datetime.strptime(start_yymm, '%y%m')
        end_date = self.__end_of_month(datetime.strptime(end_yymm, '%y%m'))
        stats = self.__data_init('repo_period')
        stats['github_id'] = github_id
        stats['repo_name'] = repo_name
        stats['start_yymm'] = start_yymm
        stats['end_yymm'] = end_yymm
        prs_set = set()
        contributor_set = set()
        commit_list = []

        page = 1
        while True:
            json_data = self.get_json(f'repos/{github_id}/{repo_name}/events', page)
            for event in json_data:
                event_date = datetime.fromisoformat(event['created_at'][:-1])
                if event_date < start_date or event_date > end_date :
                    continue
                if event['type'] == 'CreateEvent' :
                    pass
                if event['type'] == 'WatchEvent' :
                    stats['stargazer_count'] += 1
                if event['type'] == 'PushEvent' :
                    if event['actor']['login'] != github_id :
                        contributor_set.add(event['actor']['login'])
                    stats['commits_count'] += event['payload']['size']
                    commit_list += [c['sha'] for c in event['payload']['commits']]
                    if stats['update_date'] == 0 :
                        stats['update_date'] = event['created_at']
                    stats['update_count'] += 1
                if event['type'] == 'IssuesEvent' :
                    if event['payload']['action'] == 'opened' :
                        stats['open_issue_count'] += 1
                    elif event['payload']['action'] == 'closed' :
                        stats['close_issue_count'] += 1
                    if stats['update_date'] == 0 :
                        stats['update_date'] = event['created_at']
                    stats['update_count'] += 1
                if event['type'] == 'IssueCommentEvent' :
                    if stats['update_date'] == 0 :
                        stats['update_date'] = event['created_at']
                    stats['update_count'] += 1
                if event['type'] == 'PullRequestEvent' :
                    prs_set.add(event['payload']['pull_request']['id'])
                    if stats['update_date'] == 0 :
                        stats['update_date'] = event['created_at']
                    stats['update_count'] += 1
                if event['type'] == 'ReleaseEvent' :
                    if stats['release_ver'] == 0 :
                        stats['release_ver'] = event['payload']['release']['tag_name']
                    stats['release_count'] += 1
                    if stats['update_date'] == 0 :
                        stats['update_date'] = event['created_at']
                    stats['update_count'] += 1
                if event['type'] == 'ForkEvent' :
                    stats['forks_count'] += 1
            if len(json_data) < 100 :
                break
            page += 1
        
        stats['prs_count'] = len(prs_set)

        for commit in commit_list :
            stat = self.get_json(f'repos/{github_id}/{repo_name}/commits/{commit}')
            stats['code_edits'] += stat['stats']['total']
        
        return stats