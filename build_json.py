from apis.doesthedogdie import get_info_for_movie
from apis.plex import get_movies_and_format
import json
import requests
import urllib.parse

from tqdm import tqdm
try:
    from config import only_show_yes
except:
    print("⚠ Please set only_show_yes in your config.py")
    only_show_yes = False
try:
    from config import use_memcache
except:
    use_memcache = False
try:
    from config import use_dtdd_web_api
    if use_dtdd_web_api:
        try:
            from config import dtdd_web_api_address
        except ImportError:
            print("⚠ Please set dtdd_web_api_address in your config.py")
            use_dtdd_web_api = False
except:
    print("⚠ Please set use_dtdd_web_api in your config.py")
    use_dtdd_web_api = False

try:
    from config import use_short_names
except:
    print("⚠ Please set use_short_names in your config.py")
    use_short_names = False


def yes_or_no_formatter(topic):
    action = "Unsure"
    
    if topic['yes_votes'] > topic['no_votes']:
        action = "Yes"
    elif topic['no_votes'] > topic['yes_votes']:
        action = "No"
    return "{topic} : {action} (Yes: {yes_votes} | No : {no_votes})\n".format(topic=topic['topic'], yes_votes=topic['yes_votes'], no_votes=topic['no_votes'], action=action), action, topic['topic_short']

def main():
    print("⬇ Getting movies from Plex")
    movies = get_movies_and_format()

    to_write = []
    if use_dtdd_web_api:
        print("⏩ Getting data from faster web API")
    else:
        print("🐶 Getting data from DoesTheDogDie.com")
        if not use_memcache:
            print("⚠ You aren't using a memcache or an external API for DTDD - this will take a while")
    for movie in tqdm(movies):
        if use_dtdd_web_api:
            resp = requests.get("{}/media/{}".format(dtdd_web_api_address, movie['title']))
            if resp.status_code == 200:
                movie['dtdd'] = json.loads(resp.text)
            else:
                movie['dtdd'] = None
        else:
            movie['dtdd'] = get_info_for_movie(movie['title'])
        movie['statuses'] = []

        # we preformat all the strings for later, so we can quickly retrieve them (meaning the writer has little logic attached to DTDD)

        if movie['dtdd'] != None:
            for raw_status in movie['dtdd']:
                yes_or_no = yes_or_no_formatter(raw_status)
                if (not only_show_yes) or (yes_or_no[1] == "Yes"):
                    movie['statuses'].append(yes_or_no)
        to_write.append(movie)

    # all we need to do now is chuck it in a big ol' json file

    print("✏ Writing to JSON file")
    with open("movies.json", "w") as f:
        f.write(json.dumps(to_write, indent=4))
    print("✅ Done!")


if __name__ == "__main__":
    main()
