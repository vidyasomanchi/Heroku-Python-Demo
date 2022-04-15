from flask import *
import pandas as pd
import os
import numpy as np
import string
import re
import nltk
#nltk.download('stopwords')
from nltk.corpus import stopwords
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#import snscrape.modules.twitter as sntwitter
import tweepy
import datetime

today = datetime.date.today()
yesterday= today - datetime.timedelta(days=1)

app = Flask(__name__)

# Twitter
TWITTER_API_KEY="9aoithtQMepOokNLQu1jVBe3q"
TWITTER_API_SECRET="ZBE0zYhG6d2Cx1Dmhwyid8YnFpkgTTJi94Ei4dnIagfT15GcZE"
TWITTER_ACCESS_TOKEN="617154346-biekec3f1OoGSXitALKz0SKKMg0iNVhqmyLiQ4pG"
TWITTER_ACCESS_SECRET="5zaB4q88CxqN5TcTSj0dTqOtCJGGwtWSst5QNaPH4Sev8"

# authenticate to twitter using Tweepy
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
api = tweepy.API(auth)


class Twitter_Analysis():

    # Create a function to clean the tweets
    def cleanComments(self,text):
        text = re.sub('@[A-Za-z0–9]+', '', text)  # Removing @mentions
        text = re.sub('#', '', text)  # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text)  # Removing RT
        text = re.sub('https?:\/\/\S+', '', text)  # Removing hyperlink
        return text

    def scrape(self,keyword):
        # Creating list to append tweet data
        output = []

        tweets_list = tweepy.Cursor(api.search, q="#{key} since:".format(key=keyword) , lang='en').items()

        for tweet in tweets_list:
            text = tweet._json["full_text"]
            print(text)
            favourite_count = tweet.favorite_count
            retweet_count = tweet.retweet_count
            created_at = tweet.created_at
    
            line = {'Reviews' : text, 'favourite_count' : favourite_count, 'retweet_count' : retweet_count, 'created_at' : created_at}
            output.append(line)

        # Creating a dataframe from the tweets list above
        df = pd.DataFrame(output)
        df["Reviews"] = df["Reviews"].apply(self.cleanComments)
        filename=r'Twitter_{0}.csv'.format(keyword.replace(" ","_"))
        df.to_csv(filename)
        
        return df
    
    def cleanTxt(self,df,keyword):
        
        ##Creating a list of stop words and adding custom stopwords
        stop_words = set(stopwords.words("english"))
        
        corpus = []
        for index, row in df.iterrows():
            text = row['Reviews']
    
            #Remove punctuations
            text = re.sub('[^a-zA-Z]', ' ', text)
    
            #Convert to lowercase
            text = text.lower()
    
            #remove tags
            text=re.sub("&lt;/?.*?&gt;"," &lt;&gt; ",text)
    
            # remove special characters and digits
            text=re.sub("(\\d|\\W)+"," ",text)
    
            ##Convert to list from string
            text = text.split()
    
            text = " ".join(text)

            df.loc[index,'processed_reviews'] = text
        
        filename=r'Twitter_{0}.csv'.format(keyword.replace(" ","_"))
        
        df.drop_duplicates(subset="Reviews",keep="first",inplace=True)
        df = df[df['Reviews'].notna()]
        df.to_csv(filename)
        
        return df

@app.route('/')
def my_form():
    return render_template('search.html')

@app.route('/', methods=['POST'])
def show_tables():
    twitter = Twitter_Analysis()
    keyword = request.form['keyword']
    print("Entered keyword is ----->>>>",keyword)#str(input("Enter search word-"))
    twitter_pd = pd.read_csv(r'Twitter_Analyized.csv')#twitter.scrape(keyword)#pd.read_csv(r'Twitter_Analyized.csv')
    #twitter_pd = twitter.cleanTxt(twitter_pd,keyword)
    return render_template('view.html',tables=[twitter_pd.to_html(classes='report')])

if __name__ == "__main__":
    app.run()

