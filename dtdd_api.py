# This should be ran as a service if you want to make use of the web API tech without requesting the main one
from flask_api import FlaskAPI
from apis.doesthedogdie import get_info_for_movie
import re
app = FlaskAPI(__name__)

to_strip = [
    "Are( any| there)* ",
    "Does( the| a| an| someone| it)* ",
    "Is( a| there)* ",
    "\?"
]

to_replace = [
    ("die", "dying"), 
    ("dies", "dying"), 
    ("use drugs", "drug usage"), 
    ("needles/syringes used", "needles/syringes usage"),
    ("not have a happy ending", "no happy ending"),
    ("break a bone", "breaking of bones"),
    ("drown", "drowning"), 
    ("abuse alcohol", "alcohol abuse")
]

def shorten(topic):
    for filter in to_strip:
        topic = re.sub(filter, '', topic)
    for replacement in to_replace:
        topic = topic.replace(replacement[0], replacement[1])
    
    return topic

@app.route("/")
def dtdd_index():
    return {"status": "You're probably wanting to make a request to /media/[movie name]"}

@app.route("/media/<key>", methods=['GET'])
def movie_details(key):
    key = str(key)
    to_return = get_info_for_movie(key)
    
    if to_return == None:
        return {"error": "cannot find movie"}, 404
    for status in to_return:
        if status.get('topic_short', None) is None:
            status['topic_short'] = shorten(status['topic'])
    return to_return

if __name__ == "__main__":
    app.run()