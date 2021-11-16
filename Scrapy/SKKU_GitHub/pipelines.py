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
        self.lost = {}

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
                del data['request_cnt']
        elif type(item) == Repo:
            self.wait[item['path']] = item
            if item['path'] in self.lost:
                for prev_item in self.lost[item['path']]:
                    if prev_item['target'] == 'main_page':
                        self.wait[prev_item['path']].update(prev_item)
                    else:
                        self.wait[prev_item['path']].update(prev_item)
                        self.wait[prev_item['path']]['request_cnt'] -= 1
                    if self.wait[prev_item['path']]['request_cnt'] == 0:
                        insert = True
                        data = self.wait[prev_item['path']]
                        self.wait.pop(prev_item['path'])
                        del data['request_cnt']
                        del data['path']
                        del data['target']
                del self.lost[item['path']]
        elif type(item) == RepoUpdate:
            if item['path'] not in self.wait:
                if item['path'] not in self.lost:
                    self.lost[item['path']] = [item]
                else:
                    self.lost[item['path']].append(item)
            else:
                if item['target'] == 'main_page':
                    if 'request_cnt' in self.wait[item['path']]:
                        self.wait[item['path']]['request_cnt'] += item['request_cnt']
                        del item['request_cnt']
                    self.wait[item['path']].update(item)

                else:
                    self.wait[item['path']].update(item)
                    if 'request_cnt' not in self.wait[item['path']]:
                        self.wait[item['path']]['request_cnt'] = 0
                    self.wait[item['path']]['request_cnt'] -= 1
                if self.wait[item['path']]['request_cnt'] == 0:
                    insert = True
                    data = self.wait[item['path']]
                    self.wait.pop(item['path'])
                    del data['request_cnt']
                    del data['path']
                    del data['target']
        elif type(item) == UserPeriod:
            insert = True
            data = item
        elif type(item) == RepoContribute:
            insert = True
            data = item
        elif type(item) == RepoCommit:
            insert = True
            data = item
        
        if insert:
            if type(data) == User:
                table_name = 'github_overview'
                key_col = ['github_id']
                data_col = list(set(data.keys()) - set(key_col))
            if type(data) == UserPeriod:
                table_name = 'github_stats_yymm'
                key_col = ['github_id', 'start_yymm', 'end_yymm']
                data_col = list(set(data.keys()) - set(key_col))
            if type(data) == Repo:
                table_name = 'github_repo_stats'
                key_col = ['github_id', 'repo_name']
                data_col = list(set(data.keys()) - set(key_col))
            if type(data) == RepoContribute:
                table_name = 'github_repo_contributor'
                key_col = ['github_id', 'owner_id', 'repo_name']
                data_col = list(set(data.keys()) - set(key_col))
            if type(data) == RepoCommit:
                table_name = 'github_repo_commits'
                key_col = ['github_id', 'repo_name', 'sha']
                data_col = list(set(data.keys()) - set(key_col))
            
            select_sql = f'SELECT * FROM {table_name} WHERE {" AND ".join([f"{x} = %s" for x in key_col])}'
            select_data = [data[x] for x in key_col]
            update_sql = f'UPDATE {table_name} SET {", ".join([f"{x} = %s" for x in data_col])} WHERE {" AND ".join([f"{x} = %s" for x in key_col])}'
            update_data = [data[x] for x in data_col + key_col]
            insert_sql = f'INSERT INTO {table_name}({", ".join(key_col + data_col)}) '
            insert_sql+= f'VALUES({", ".join(["%s"]*len(data))})'
            insert_data = [data[x] for x in key_col + data_col]
            try:
                if self.cursor.execute(select_sql, select_data) == 0:
                    self.cursor.execute(insert_sql, insert_data)
                elif len(update_data) != len(key_col):
                    self.cursor.execute(update_sql, update_data)
                self.crawlDB.commit()
            except:
                print(self.cursor.mogrify(select_sql, select_data))
                print(self.cursor.mogrify(insert_sql, insert_data))
                if len(update_data) != 0:
                    print(self.cursor.mogrify(update_sql, update_data))
                print('\n')
                sys.exit(1)
        return item
