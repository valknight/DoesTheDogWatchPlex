# This should be ran as a service if you want to make use of the web API tech without requesting the main one
from flask_api import FlaskAPI
from apis.doesthedogdie import get_info_for_movie

app = FlaskAPI(__name__)

@app.route("/")
def dtdd_index():
    return {"status": "You're probably wanting to make a request to /media/[movie name]"}

@app.route("/media/<key>", methods=['GET'])
def notes_detail(key):
    key = str(key)
    to_return = get_info_for_movie(key)
    if to_return == None:
        return {"error": "cannot find movie"}, 404
    return to_return

if __name__ == "__main__":
    app.run()