from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from pymongo import MongoClient


tweet_users = ['DelhiPolice', 'MumbaiPolice',
               'wbpolice', 'hydcitypolice', 'ThaneCityPolice']


def timeit(func):
    # A Decorator to calculate how much time a func takes.
    def inner(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        time_taken = time.time() - start_time
        print 'Time taken is ', time_taken
        return result
    return inner


def scraper(police_handle):
    global driver
    print police_handle
    # Open the twitter page of specified user handle
    driver.get('https://twitter.com/' + police_handle)
    print 'link opened'
    body = driver.find_element_by_tag_name('body')

    # Clicke somewhere on the nav bar to avoid focus from login page.
    driver.find_element_by_class_name('global-nav').click()

    # end_of_page is the footer of twitter page that is shown when no more
    # feeds are available.
    end_of_page = driver.find_element_by_class_name('stream-end')

    while end_of_page.value_of_css_property('display') == 'none':
        # continue to scroll the page till end of page is not reached ie
        # display is not none.
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(.1)
        end_of_page = driver.find_element_by_class_name('stream-end')

    print 'reached down'

    # complete block of tweets and retweets on the page
    tweets_retweets = driver.find_element_by_class_name('stream')

    # find the tweets made by police_handle.
    tweets = tweets_retweets.find_elements_by_xpath(
        ".//div[@data-screen-name='" + police_handle + "']")
    print 'found tweets'
    print len(tweets)

    # Connecting to MongoDB and collection
    client = MongoClient('localhost', 27017)
    db = client['twitter_police_db']
    collection = db[police_handle]

    # Collect only the first 350 tweets
    for tweet in tweets[:350]:
        tweet_dict = {}

        # scrape the important data from each block
        tweet_dict['data-tweet-id'] = tweet.get_attribute('data-tweet-id')
        if tweet_dict['data-tweet-id']:
            tweet_dict['lang'] = tweet.\
                find_element_by_class_name(
                'tweet-text').get_attribute('lang')
            tweet_dict['data-permalink-path'] = tweet\
                .get_attribute('data-permalink-path')
            tweet_dict['content'] = tweet.\
                find_element_by_class_name('tweet-text').text
            tweet_dict['hashtags'] = [hashtag.text for hashtag in tweet.
                                      find_elements_by_class_name(
                                          'twitter-hashtag')]
            tweet_dict['retweets'] = int(tweet.find_element_by_class_name(
                'ProfileTweet-action--retweet').
                find_element_by_class_name('ProfileTweet-actionCount').
                get_attribute('data-tweet-stat-count'))
            tweet_dict['replies'] = int(tweet.find_element_by_class_name(
                'ProfileTweet-action--reply').
                find_element_by_class_name('ProfileTweet-actionCount').
                get_attribute('data-tweet-stat-count'))
            tweet_dict['like'] = int(tweet.find_element_by_class_name(
                'ProfileTweet-action--favorite').
                find_element_by_class_name('ProfileTweet-actionCount').
                get_attribute('data-tweet-stat-count'))
            tweet_dict['timestamp'] = tweet.find_element_by_class_name(
                'time').text
            try:
                tweet_dict['media'] = \
                    [img.get_attribute('src') for img in tweet.
                     find_element_by_class_name('AdaptiveMedia-container').
                     find_elements_by_tag_name('img')]
            except NoSuchElementException, e:
                tweet_dict['media'] = []

            # insert the result in DB.
            collection.insert_one(tweet_dict)


@timeit  # decorator to calculate time taken
def main():
    global driver
    # Create a instance of firefox browser
    driver = webdriver.Firefox()
    for police_handle in tweet_users:
        # scrape each handle
        scraper(police_handle)
    # exit the browser
    driver.quit()

if __name__ == '__main__':
    main()
