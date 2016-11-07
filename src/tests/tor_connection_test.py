import requests

proxies = {'http': 'socks5://localhost:9050',
           'https': 'socks5://localhost:9050'}

assert requests.get('http://nzxj65x32vh2fkhk.onion/all', proxies=proxies, timeout=24).status_code == 200