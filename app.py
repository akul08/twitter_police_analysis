from flask import Flask, render_template
from pymongo import MongoClient
import datetime
from collections import defaultdict, Counter
import os
from textblob import TextBlob

app = Flask(__name__)

# list of police twitter accounts
tweet_users = ['DelhiPolice', 'MumbaiPolice',
               'wbpolice', 'hydcitypolice', 'ThaneCityPolice']

# open the given Mongolab Uri if available or open localhost
url = os.getenv('MONGOLAB_URI', 'mongodb://localhost:27017')

@app.route('/')
def welcome():
    ''' welcome page '''
    return render_template('index.html')


@app.route('/frequency')
def frequency_of_tweets_in_week():
    ''' frequency Tweets that are generated on a day '''
    avg_tweets = {}
    # Connect to DB
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]
        week = defaultdict(int)

        for i in collection.find({}):
            # convert the given timestamp to weekday
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
    # send the data to create bar graph
    return render_template('frequency.html', avg_tweets=avg_tweets)


@app.route('/most_used')
def most_used_hashtags():
    ''' most used hashtags by the police twitter accounts '''
    most_used_hashtags_dict = {}
    # Connect to DB
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        hashtags_list = []
        for i in collection.find({}):
            hashtags_list.extend(i['hashtags'])

        top_ten_hashtags = Counter(hashtags_list).most_common(10)
        most_used_hashtags_dict[police_handle] = top_ten_hashtags
    # send the data to create table of hashtages
    return render_template('most_used.html',
                           most_used_hashtags_dict=most_used_hashtags_dict)


@app.route('/most_engagement')
def most_engagement():
    ''' most engaged tweets and what type '''
    top_liked_tweets_dict = {}
    highest_tweet_type = {}
    # Connect to DB
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        top_liked_tweets = {'image+text': 0, 'image': 0, 'text': 0}
        tweets = list(collection.find())
        tw = sorted(
            tweets, key=lambda x: x['like'] + x['retweets'], reverse=True)

        # check for image, text, or both
        for i in tw[:len(tw) / 10]:
            if i['media']:
                if i['content']:
                    top_liked_tweets['image+text'] += 1
                else:
                    top_liked_tweets['image'] += 1
            else:
                top_liked_tweets['text'] += 1

        # most engaged tweet type
        if tw[0]['media']:
            if tw[0]['content']:
                highest_tweet_type[police_handle] = 'image+text'
            else:
                highest_tweet_type[police_handle] = 'image'
        else:
            highest_tweet_type[police_handle] = 'text'

        top_liked_tweets_dict[police_handle] = top_liked_tweets
    # send data to create pie charts
    return render_template('most_engagement.html',
                           top_liked_tweets_dict=top_liked_tweets_dict,
                           highest_tweet_type=highest_tweet_type)



@app.route('/type')
def type():
    ''' types of tweets '''
    liked_tweets_dict = {}
    # Connect to DB
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        liked_tweets = {'image+text': 0, 'image': 0, 'text': 0}
        tweets = list(collection.find())

        # check for image, text, or both
        for i in tweets:
            if i['media']:
                if i['content']:
                    liked_tweets['image+text'] += 1
                else:
                    liked_tweets['image'] += 1
            else:
                liked_tweets['text'] += 1

        liked_tweets_dict[police_handle] = liked_tweets

    # send data to create pie charts
    return render_template('type.html',
                           liked_tweets_dict=liked_tweets_dict)


@app.route('/sentiment')
def sentiment_analysis():
    sentiment_dict = {}
    # Connect to DB
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        sent = defaultdict(float)
        sent['polarity'] = []
        sent['polarity_division'] = defaultdict(int)

        # check polarity of english tweets using TextBlob
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

    # send data to create pice chart and scatter plot chart
    return render_template('sentiment.html', sentiment_dict=sentiment_dict)


@app.route('/likes')
def like_on_tweets():
    like_dict = {}
    # Connect to DB
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        # calculate likes
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
    # send the data to create table
    return render_template('like.html', like_dict=like_dict)


@app.route('/retweets')
def retweet_on_tweets():
    retweet_dict = {}
    # Connect to DB
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        # calculate retweets
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
    # send the data to create table  
    return render_template('retweet.html', retweet_dict=retweet_dict)


@app.route('/reply')
def reply_on_tweets():
    reply_dict = {}
    # Connect to DB
    client = MongoClient(url)
    db = client['twitter_police_db']

    for police_handle in tweet_users:
        collection = db[police_handle]

        # calculate replies
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
    # send the data to create table
    return render_template('reply.html', reply_dict=reply_dict)


# in production Heroku will set the PORT environment variable.
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
