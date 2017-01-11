from flask import Flask, render_template
from pymongo import MongoClient
import datetime
from collections import defaultdict, Counter
import os

app = Flask(__name__)

tweet_users = ['DelhiPolice', 'MumbaiPolice',
               'wbpolice', 'hydcitypolice', 'ThaneCityPolice']

url = os.getenv('MONGOLAB_URI', 'mongodb://localhost:27017')


@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/frequency')
def frequency_of_tweets_in_week():
    avg_tweets = {}
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:

        collection = db[police_handle]

        week = defaultdict(int)

        for i in collection.find({}):
            # print i['timestamp']
            try:
                day = datetime.datetime.strptime(
                    i['timestamp'], '%d %b %Y').strftime('%A')
            except:
                try:
                    day = datetime.datetime.strptime(
                        i['timestamp'], '%b %d').strftime('%A')
                except:
                    day = datetime.datetime.today().strftime('%A')
            week[day] += 1
        avg_tweets[police_handle] = week
    return render_template('frequency.html', avg_tweets=avg_tweets)


@app.route('/most_used')
def most_used_hashtags():

    most_used_hashtags_dict = {}
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:

        collection = db[police_handle]

        hashtags_list = []
        for i in collection.find({}):
            hashtags_list.extend(i['hashtags'])
        print len(hashtags_list)

        top_ten_hashtags = Counter(hashtags_list).most_common(10)
        # print top_ten_hashtags
        most_used_hashtags_dict[police_handle] = top_ten_hashtags

    return render_template('most_used.html',
                           most_used_hashtags_dict=most_used_hashtags_dict)


@app.route('/most_engagement')
def most_engagement():
    top_liked_tweets_dict = {}
    highest_tweet_type = {}
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:

        collection = db[police_handle]

        print police_handle
        top_liked_tweets = {'image_text': 0, 'image': 0, 'text': 0}
        tweets = list(collection.find())
        tw = sorted(
            tweets, key=lambda x: x['like'] + x['retweets'], reverse=True)

        for i in tw[:len(tw) / 10]:
            if i['media']:
                if i['content']:
                    top_liked_tweets['image_text'] += 1
                else:
                    top_liked_tweets['image'] += 1
            else:
                top_liked_tweets['text'] += 1

        if tw[0]['media']:
            if tw[0]['content']:
                highest_tweet_type[police_handle] = 'image_text'
            else:
                highest_tweet_type[police_handle] = 'image'
        else:
            highest_tweet_type[police_handle] = 'text'

        top_liked_tweets_dict[police_handle] = top_liked_tweets

    return render_template('most_engagement.html',
                           top_liked_tweets_dict=top_liked_tweets_dict,
                           highest_tweet_type=highest_tweet_type)


# in production Heroku will set the PORT environment variable.
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    print url
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
