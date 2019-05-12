# DoesTheDogWatchPlex

> An integration of DoesTheDogDie.com and Plex Media Server

![Demonstration of DoesTheDogWatchPlex using Marvel's Infinity War](/screenshots/1.png)
## What does this do?

This modifies the summaries of movies to contain content warnings from DoesTheDogDie.com.

## Why?

Some of the people using my Plex server (myself included) sometimes go through rough patches, and don't want to stumble into a movie that happens to contain something like, a pet dying, sexual assault, or other things. However, alt-tabbing to DoesTheDogDie.com can get tiresome, so this exists, meaning you can see brief previews of the data from DoesTheDogDie.com without ever leaving the Plex interface.

## How to get started

0. Install python 3.4+ and create a virtual environment for this
1. Execute `pip install -r requirements.txt`
2. Copy config.py.example to config.py, and fill out the data with what is relevant to your setup
3. Execute `python build_json.py`, and sit back and wait for the movies.json file to be generated 
4. Once this file is generated, check over it, and **make a Plex Media Server database backup** (from this point on, all metadata changes will be permanent to your server)
5. Run `python write_to_plex.py`

To update the content warnings, run build_json.py again, and then write_to_plex.py - anything below the line reading `doesthedogdie: ` will simply be removed, and replaced with the new updated content warnings (anything above shouldn't be touched)

## Plans

- TV series support
- Moving to an agent instead of this hacky setup
- Customizing splitter between the actual summary and content warnings
- Performance improvements in the processing of results from doesthedogdie.com

## LICENSE

This project is licensed under the MIT license.