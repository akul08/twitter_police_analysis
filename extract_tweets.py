import json
import tweepy
import sys
from pymongo import MongoClient

try:
    with open("credentials.json") as file:
        credentials = json.load(file)[0]
except Exception, e:
    print 'Can\'t load Credentials.\nError: ', e
    sys.exit()

CONSUMER_KEY = credentials['consumerkey']
CONSUMER_SECRET = credentials['consumersecret']
ACCESS_TOKEN = credentials['accesstoken']
ACCESS_TOKEN_SECRET = credentials['accesstokensecret']


tweet_users = ['DelhiPolice', 'MumbaiPolice',
               'Uppolice', 'wbpolice', 'BlrCityPolice']


def get_tweets(screen_name):
    ''' Function to get tweets from a user and store in the db. '''
    print screen_name
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        api = tweepy.API(auth)

        t = api.user_timeline(
            screen_name=screen_name, count=200, include_rts=False)

    except Exception, e:
        print 'Authentication Failed\nError: ', e
        sys.exit()

    tweets = []
    tweets.extend(t)
    prev_len = 0
    # Continue to collect till atleast 300 tweets are not collected.
    while len(tweets) <= 3000:
        if prev_len == len(tweets):
            break
        prev_len = len(tweets)
        print 'len of tweets = ', len(tweets)
        # last_id is the id of the earliest tweet collected.
        last_id = tweets[-1].id - 1
        # Collect the tweets before the last_id
        t = api.user_timeline(screen_name=screen_name,
                              count=200, include_rts=False, max_id=last_id)
        tweets.extend(t)
    print 'len of tweets = ', len(tweets)

    # Converting Tweepy object to list of dict.
    tweets = [tweet._json for tweet in tweets]
    # To connect and insert in MongoDB.
    client = MongoClient('localhost', 27017)
    db = client['twitter_policeDB']
    collection = db[screen_name]
    collection.insert_many(tweets)


for police_user in tweet_users:
    get_tweets(police_user)
