# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sys, pymysql
from .items import *
from .configure import *

class SkkuGithubPipeline:
    def __init__(self) -> None:
        try :
            self.crawlDB = pymysql.connect(
                user=SQL_USER,
                passwd=SQL_PW,
                host=SQL_HOST,
                port=SQL_PORT,
                db=SQL_DB
            )
            self.cursor = self.crawlDB.cursor()
        except :
            print('ERROR: DB connection failed')
            sys.exit(1)
        self.wait = {}

    def process_item(self, item, spider):
        insert = False
        if type(item) == User:
            self.wait[item['github_id']] = item
        elif type(item) == UserUpdate:
            prev = self.wait[item['github_id']]
            if item['target'] == 'badge':
                prev['achievements'] = item['achievements']
                prev['highlights'] = item['highlights']
            elif item['target'] == 'activity':
                prev['total_commits'] += item['total_commits']
                prev['total_PRs'] += item['total_PRs']
                prev['total_issues'] += item['total_issues']
            elif item['target'] == 'repo_star':
                prev['stars'] += item['stars']
            prev['request_cnt'] -= 1
            self.wait[item['github_id']] = prev
            if prev['request_cnt'] == 0 :
                self.wait.pop(item['github_id'])
                insert = True
                data = prev
                print(prev)
        
        if insert:
            if type(data) == User:
                insert_sql = 'INSERT IGNORE INTO github_crawl.github_overview('
                insert_sql+= 'github_id, stars, followers, followings, total_repos, '
                insert_sql+= 'total_commits, total_PRs, total_issues, achievements, highlights) '
                insert_sql+= 'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                insert_data = (
                        data['github_id'], data['stars'], data['followers'], data['following'], 
                        data['total_repos'], data['total_commits'], data['total_PRs'], 
                        data['total_issues'], data['achievements'], data['highlights']
                    )

            try:
                self.cursor.execute(insert_sql, insert_data)
                self.crawlDB.commit()
            except:
                print(insert_sql)
                print(insert_data)
                sys.exit(1)

        return item
