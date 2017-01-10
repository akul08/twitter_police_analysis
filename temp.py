from pymongo import MongoClient
import datetime
from collections import defaultdict, Counter

tweet_users = ['DelhiPolice', 'MumbaiPolice',
               'wbpolice', 'hydcitypolice', 'ThaneCityPolice']

police_handle = 'DelhiPolice'

# avg_tweets = {}
# for police_handle in tweet_users:

#     client = MongoClient('localhost', 27017)
#     db = client['twitter_policeDB']
#     collection = db[police_handle]

#     week = defaultdict(int)

#     for i in collection.find({}):
#         # print i['timestamp']
#         try:
#             day = datetime.datetime.strptime(
#                 i['timestamp'], '%d %b %Y').strftime('%A')
#         except:
#             try:
#                 day = datetime.datetime.strptime(
#                     i['timestamp'], '%b %d').strftime('%A')
#             except:
#                 day = datetime.datetime.today().strftime('%A')
#         week[day] += 1
#     avg_tweets[police_handle] = week
# print avg_tweets

client = MongoClient('localhost', 27017)
db = client['twitter_policeDB']
collection = db[police_handle]


# most_used_hashtags_dict = {}
# for police_handle in tweet_users:

#     client = MongoClient('localhost', 27017)
#     db = client['twitter_policeDB']
#     collection = db[police_handle]

#     hashtags_list = []
#     for i in collection.find():
#         # if i['hashtags']:
#         hashtags_list.extend(i['hashtags'])
#     # print hashtags_list
#     print len(hashtags_list)

#     # print Counter(hashtags_list)
#     top_ten_hashtags = Counter(hashtags_list).most_common(10)
#     print top_ten_hashtags
#     most_used_hashtags_dict[police_handle] = top_ten_hashtags

# print most_used_hashtags_dict
top_liked_tweets_dict = {}
for police_handle in tweet_users:

    client = MongoClient('localhost', 27017)
    db = client['twitter_policeDB']
    collection = db[police_handle]

    print police_handle
    top_liked_tweets = defaultdict(int)
    tweets = list(collection.find())
    tw = sorted(tweets, key=lambda x: x['like'] + x['retweets'], reverse=True)

    for i in tw[:len(tw) / 10]:
        # print i['data-tweet-id'], i['like'], i['retweets']
        if i['media']:
            if i['content']:
                top_liked_tweets['image_text'] += 1
            else:
                top_liked_tweets['image'] += 1
        else:
            top_liked_tweets['text'] += 1

    if tw[0]['media']:
        if tw[0]['content']:
            top_liked_tweets['highest_tweet_type'] = 'image_text'
        else:
            top_liked_tweets['highest_tweet_type'] = 'image'
    else:
        top_liked_tweets['highest_tweet_type'] = 'text'

    top_liked_tweets_dict[police_handle] = top_liked_tweets

print top_liked_tweets_dict
