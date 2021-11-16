import requests
from tqdm import tqdm

for _ in tqdm(range(300)):
    res = requests.get(
        'http://api.github.com', 
        headers={'Authorization': 'token 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'}
        )

print(res.headers)