from bs4 import BeautifulSoup
import urllib.parse
import requests
import time
import json
try:
    from config import use_memcache
    if  use_memcache:
        try:
            from config import memcache_address, memcache_port, invalidation_time
        except ImportError:
            print("⚠ Please set memcache_address, memcache_port and invalidation_time in config.py")
            use_memcache = False
except ImportError:
    print("⚠ Please set use_memcache in config.py")
    use_memcache = False

if use_memcache:
    from pymemcache.client import base
    client = base.Client((memcache_address, memcache_port))
    print("✅ Established memcache client")
else:
    print("⚠ memcache is disabled - we recommend you enable it to improve performance")

base_string = "https://www.doesthedogdie.com/{media_id}"

def get_topics(media_id):
    resp = requests.get(base_string.format(media_id=media_id))
    soup = BeautifulSoup(resp.text, 'lxml')
    try:
        return(soup.find("div", {"id": "topics"}).select('.topicRow'))
    except AttributeError:
        print("❌ Could not find topics for {}".format(media_id))
        return []

def get_info(media_id):
    topics = get_topics(media_id)
    to_return = []
    for topic in topics:
        
        name = topic.select('.name>a')[0].text

        # the yesNo container is the little box which highlights red or green for a specific topic

        yesNo = topic.select('.yesNo')[0]

        # extract votes from the yesNo container
        yes_votes = int(yesNo.select('.yes')[0].select('.count')[0].text)
        no_votes = int(yesNo.select('.no')[0].select('.count')[0].text)
        to_return.append(dict(topic=name, yes_votes=yes_votes, no_votes=no_votes))
    return to_return
    
def search(search_string):
    search_string = search_string.lower()
    search_string = urllib.parse.quote_plus(search_string)
    url = 'https://www.doesthedogdie.com/search?q={}'.format(search_string)
    search_request = requests.get(url, headers={"X-Requested-With":"XMLHttpRequest", "PoliteRequest":"Hey, could you make an API? That would be real sweet, as it means I don't have to do this wacky hack"})
    soup = BeautifulSoup(search_request.text, 'lxml')
    names = soup.select('.name')
    counter = 0
    while counter < len(names):
        if "media/" in names[counter]['href']:
            return names[counter]['href']
        counter += 1
    return None
    
def get_info_for_movie(movie_name, use_cache=True):
    movie_name = movie_name.lower()
    movie_name = urllib.parse.quote_plus(movie_name)
    data = client.get(movie_name)
    if use_cache and use_memcache: # use_memcache is the global config, use_cache is if we don't want to hit the cache on this occasion
        invalid = False
        if data is None:
            invalid = True
        else:
            try:
                data =  json.loads(data)
                if int(data['time_retrieved']) - time.time() > invalidation_time:
                    invalid = True
                else:
                    data = data['data']
            except:
                invalid = True
        
    if invalid or not(use_cache):
        key = search(movie_name)
        if key is not None:
            data = get_info(key)
            if use_memcache: # this allows us to force refresh data if we want
                client.set(movie_name, json.dumps(dict(data=data, time_retrieved=int(time.time()))))
        else:
            data = None
    return data