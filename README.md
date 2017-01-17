# Task A solution for PrecogSummer2017

### Problem: Collect tweets (not retweets/replies) of 5 verified Indian police accounts, and do Data Analysis, Data Visualization and Sentiment Analysis and show the results and graphs in a web app.

### Solution: Web App = Flask + Heroku + MongoDB/MongoLab + Selenium + Google Charts.

### Link to Web App: [https://akul-precog.herokuapp.com/](https://akul-precog.herokuapp.com/)

#### Step 0: Initial Environment Setup

- Clone the repo

- Setup virtualenv: `virtualenv venv`

- Activate virtualenv: `source venv/bin/activate`

- Install required libraries: `pip install -r requirements.txt`

#### Step 1: Get Tweets from twitter by using api/scraping.

- **Didn't worked with Twitter API** due to tweets limit and replies and retweets included in the result json. Out of **3200 max tweets, approx 150 original tweets** can be populated in MongoDB. can be run by: python extract_tweets.py.

- Done by **Web Scraping using Selenium**, recieved minimum 300 tweets for each account and populated MongoDB, Time Taken: approx. 25min, to run: `python twitter_scraper.py`

#### Step 2: Create a web app.

- Create a **Flask web app** for data Visualization and analysis, to run web app: `python app.py`

- Create various **routes and templates** for specific functions and data analysis.

- Sentiment Analysis done using python library: **TextBlob**

- Stylize the Templates by css from **static**

- Data Visualization done with the help of **Google charts** and the data query done from **MongoDB**.

#### Step 3: Create DB backup.

- Create MongoDB backup by using: `mongodump -d twitter_police_db -o backup` and saving the JSON files.

- Export the MongoDB to MongoLab by running: `mongorestore -h MONGOLAB_URI -d twitter_police_db -u USERNAME -p PASSWORD backup/twitter_police_db`

#### Step 4: Create Heroku app.

- Login in the git repo using heroku: `heroku login`

- Create Heroku app: `heroku create akul-precog`

- Set the MongoLab URI for Heroku app: `heroku config:set MONGOLAB_URI="mongodb://USERNAME:PASSWORD@MONGOLAB_URI/twitter_police_db"`

- Create the Procfile with the required info on how to run flask app: `web: python app.py`

- Push the code to Heroku Server: `git push heroku master`, This will also install the specific libraries defined in `requirements.txt`

- Open the Web app Url: `heroku open`

### Web App created and deployed successfully on Heroku.
