import requests

def tika(url):
    rsp = requests.get('http://localhost:9998/', params={'doc': url})
    if 'retval' not in rsp.json():
        return None
    return rsp.json()['retval']
