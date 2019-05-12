from apis.doesthedogdie import get_info_for_movie
from apis.plex import get_movies_and_format
import json
from tqdm import tqdm


def yes_or_no_formatter(topic):
    action = "Unsure"

    if topic['yes_votes'] > topic['no_votes']:
        action = "Yes"
    elif topic['no_votes'] > topic['yes_votes']:
        action = "No"

    return "{topic} : {action} (Yes: {yes_votes} | No : {no_votes})".format(topic=topic['topic'], yes_votes=topic['yes_votes'], no_votes=topic['no_votes'], action=action)


def main():
    print("⬇ Getting movies from Plex")
    movies = get_movies_and_format()

    to_write = []
    print("🐶 Getting data from DoesTheDogDie.com")
    for movie in tqdm(movies):
        movie['dtdd'] = get_info_for_movie(movie['title'])
        movie['statuses'] = []

        # we preformat all the strings for later, so we can quickly retrieve them (meaning the writer has little logic attached to DTDD)

        if movie['dtdd'] != None:
            for raw_status in movie['dtdd']:
                movie['statuses'].append(yes_or_no_formatter(raw_status))

        to_write.append(movie)

    # all we need to do now is chuck it in a big ol' json file

    print("✏ Writing to JSON file")
    with open("movies.json", "w") as f:
        f.write(json.dumps(to_write, indent=4))
    print("✅ Done!")


if __name__ == "__main__":
    main()
