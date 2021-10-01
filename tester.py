from configure import OAUTH_TOKEN
from api import GitHub_API

if __name__ == '__main__' :
    api = GitHub_API(OAUTH_TOKEN)
    print(api.check_quota())
    result = api.get_repo('tsfo1489', 'GitHub_Crawl')

    print('{')
    for key in result :
        print(f'\t{key}: {result[key]}')
    print('}')
    print(api.check_quota())