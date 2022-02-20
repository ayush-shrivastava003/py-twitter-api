"""
Sample usage of the API wrapper.

Used for debugging purposes.
"""
from main import Twitter
from flask import Flask, request
import json
import webbrowser

server = Flask(__name__)

with open("credentials.json") as f:
    CREDIENTIALS = json.loads(f.read())

twitter = Twitter(
    oauth_client_id=CREDIENTIALS["client_id"],
    oauth_client_secret=CREDIENTIALS["client_secret"],
    scopes=["tweet.read", "tweet.write", "users.read", "offline.access"],
    redirect_uri="http://localhost:3000/"
)

webbrowser.open(twitter.get_auth_url())

@server.route("/")
def index():
    twitter.get_access_token(request.url)
    print(twitter.access_token, twitter.refresh_token)
    # twitter.get_refresh_token()

    # tweet = twitter.Tweet()
    # tweet.text("Testing some more things...")
    # tweet.for_super_followers(False)
    # tweet.poll(120, ["yes", "no"])
    # tweet.quote_tweet("1494878189574922244")
    # tweet.reply("1494878820880560128")
    # tweet.send()
    return "<h1/>Authorized!"

server.run(host="0.0.0.0", port=3000, debug=True)