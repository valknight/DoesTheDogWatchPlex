from bs4 import BeautifulSoup
import urllib.parse
import requests

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
    print("❌ Could not find movie {} in DTDD".format(search_string))
    return None
    
def get_info_for_movie(movie_name):
    key = (search(movie_name))
    if key is not None:
        return get_info(key)
    else:
        return None
