import scrapy

class User(scrapy.Item) :
    github_id = scrapy.Field()
    stars = scrapy.Field()
    followers = scrapy.Field()
    following = scrapy.Field()
    total_repos = scrapy.Field()
    total_commits = scrapy.Field()
    total_PRs = scrapy.Field()
    total_issues = scrapy.Field()
    achievements = scrapy.Field()
    highlights = scrapy.Field()
    stars = scrapy.Field()
    request_cnt = scrapy.Field()

class UserUpdate(scrapy.Item) :
    github_id = scrapy.Field()
    target = scrapy.Field()
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
    stars = scrapy.Field()
    num_of_cr_repos = scrapy.Field()
    num_of_co_repos = scrapy.Field()
    num_of_commits = scrapy.Field()
    num_of_PRs = scrapy.Field()
    num_of_issues = scrapy.Field()

class Repo(scrapy.Item):
    github_id = scrapy.Field()
    repo_name = scrapy.Field()
    path = scrapy.Field()
    target = scrapy.Field()
    stargazers_count = scrapy.Field()   # API
    forks_count = scrapy.Field()        # API
    watchers = scrapy.Field()           # API
    create_date = scrapy.Field()        # API
    update_date = scrapy.Field()        # API
    language = scrapy.Field()           # API
    proj_short_desc = scrapy.Field()    # API
    license = scrapy.Field()            # API
    release_ver = scrapy.Field()        # Main Page
    release_count = scrapy.Field()      # Main Page
    contributors = scrapy.Field()       # Main Page
    readme = scrapy.Field()             # Main Page
    commits_count = scrapy.Field()      # Main Page
    code_edits = scrapy.Field()         # Commit API
    prs_count = scrapy.Field()          # PR Page
    open_issue_count = scrapy.Field()   # Issue Page
    close_issue_count = scrapy.Field()  # Issue Page
    request_cnt = scrapy.Field()

class RepoUpdate(scrapy.Item):
    path = scrapy.Field()
    target = scrapy.Field()
    release_ver = scrapy.Field()
    release_count = scrapy.Field()
    contributors = scrapy.Field()
    readme = scrapy.Field()
    commits_count = scrapy.Field()
    code_edits = scrapy.Field()
    prs_count = scrapy.Field()
    open_issue_count = scrapy.Field()
    close_issue_count = scrapy.Field()
    request_cnt = scrapy.Field()

class RepoContribute(scrapy.Item):
    github_id = scrapy.Field()
    owner_id = scrapy.Field()
    repo_name = scrapy.Field()