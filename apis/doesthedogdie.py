from bs4 import BeautifulSoup
import urllib.parse
import requests
import time
import json


try:
    from config import dtdd_api_enabled
    try:
        from config import dtdd_api_key
        api_headers = {'Accept' :'application/json', 'X-API-KEY': dtdd_api_key}
        check_request = requests.get('https://www.doesthedogdie.com/search?q=old%20yeller', headers=api_headers)
        try:
            json.loads(check_request.text)
        except json.decoder.JSONDecodeError:
            dtdd_api_enabled = False
            print("Failed to connect to DTDD's official api. Please check your API key, or disable the DTDD official API module.")
            exit(1)
    except ImportError:
        print("Disabled DTDD's official API due to api key not being set.")
        dtdd_api_enabled = False
except ImportError:
    dtdd_api_enabled = False

if not (dtdd_api_enabled):
    print("⚠ DTDD's api is recommended for performance reasons")
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

def get_topics_api(media_id):
    resp = requests.get(base_string.format(media_id=media_id), headers=api_headers)
    resp = json.loads(resp.text)
    return resp.get('topicItemStats')

def get_info(media_id):
    to_return = []
    if dtdd_api_enabled:
        topics = get_topics_api(media_id)
        print(topics)
        for topic in topics:
            print(topic)
            name = topic.get('topic').get('doesName') + "?"
            short_name = topic.get('topic').get('smmwDescription')
            yes_votes = topic.get('yesSum')
            no_votes = topic.get('noSum')
            to_return.append(dict(topic=name, topic_short=short_name, yes_votes=yes_votes, no_votes=no_votes))
    else:
        topics = get_topics(media_id)
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
    if dtdd_api_enabled:
        search_request = requests.get(url, headers=api_headers)
        resp = json.loads(search_request.text).get('items', [])
        
        if len(resp) == 0:
            return None
        return "media/{}".format(resp[0].get('id', None))
    else:
        search_request = requests.get(url, headers={"X-Requested-With":"XMLHttpRequest", 'X-Note': 'I am using DoesTheDogWatchPlex without using the official API.'})
        soup = BeautifulSoup(search_request.text, 'lxml')
        names = soup.select('.name')
        counter = 0
        while counter < len(names):
            if "media/" in names[counter]['href']:
                print(names[counter]['href'])
                return names[counter]['href']
            counter += 1
    
    return None
    
def get_info_for_movie(movie_name, use_cache=True):
    movie_name = movie_name.lower()
    movie_name = urllib.parse.quote_plus(movie_name)
    if use_cache and use_memcache: # use_memcache is the global config, use_cache is if we don't want to hit the cache on this occasion
        data = client.get(movie_name)
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
    else:
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