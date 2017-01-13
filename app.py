from flask import Flask, render_template
from pymongo import MongoClient
import datetime
from collections import defaultdict, Counter
import os
from textblob import TextBlob

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


@app.route('/sentiment')
def sentiment_analysis():
    sentiment_dict = {}
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        sent = defaultdict(float)
        sent['polarity'] = []
        sent['polarity_division'] = defaultdict(int)
        for i in collection.find({'lang': 'en'}):
            tweet = TextBlob(i['content'])

            if tweet.sentiment.polarity < 0:
                sent["negative"] += 1
            elif tweet.sentiment.polarity == 0:
                sent["neutral"] += 1
            else:
                sent["positive"] += 1
            sent['polarity'].append(tweet.sentiment.polarity)
            sent['polarity_division'][str(tweet.sentiment.polarity * 10)] += 1

        sent['avg_polarity'] = sum(
            sent['polarity']) / (sent['positive'] + sent['negative'] +
                                 sent['neutral'])
        sentiment_dict[police_handle] = sent
    return render_template('sentiment.html', sentiment_dict=sentiment_dict)


@app.route('/likes')
def like_on_tweets():
    like_dict = {}
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        likes = {'500': 0, '300': 0, '100': 0,
                 '50': 0, '20': 0, '10': 0, '0': 0}
        for i in collection.find():
            like = i['like']
            if like >= 500:
                likes['500'] += 1
            if like >= 300:
                likes['300'] += 1
            if like >= 100:
                likes['100'] += 1
            if like >= 50:
                likes['50'] += 1
            if like >= 20:
                likes['20'] += 1
            if like >= 10:
                likes['10'] += 1
            likes['0'] += 1

        like_dict[police_handle] = likes
    return render_template('like.html', like_dict=like_dict)


@app.route('/retweets')
def retweet_on_tweets():
    retweet_dict = {}
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        retweets = {'500': 0, '300': 0, '100': 0,
                    '50': 0, '20': 0, '10': 0, '0': 0}
        for i in collection.find():
            retweet = i['retweets']
            if retweet >= 500:
                retweets['500'] += 1
            if retweet >= 300:
                retweets['300'] += 1
            if retweet >= 100:
                retweets['100'] += 1
            if retweet >= 50:
                retweets['50'] += 1
            if retweet >= 20:
                retweets['20'] += 1
            if retweet >= 10:
                retweets['10'] += 1
            retweets['0'] += 1

        retweet_dict[police_handle] = retweets
    return render_template('retweet.html', retweet_dict=retweet_dict)


@app.route('/reply')
def reply_on_tweets():
    reply_dict = {}
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        replies = {'500': 0, '300': 0, '100': 0,
                   '50': 0, '20': 0, '10': 0, '0': 0}
        for i in collection.find():
            reply = i['replies']
            if reply >= 500:
                replies['500'] += 1
            if reply >= 300:
                replies['300'] += 1
            if reply >= 100:
                replies['100'] += 1
            if reply >= 50:
                replies['50'] += 1
            if reply >= 20:
                replies['20'] += 1
            if reply >= 10:
                replies['10'] += 1
            replies['0'] += 1

        reply_dict[police_handle] = replies
    return render_template('reply.html', reply_dict=reply_dict)


# in production Heroku will set the PORT environment variable.
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    print url
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
