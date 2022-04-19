from flask import *
import pandas as pd
import os
import numpy as np
import string
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#import snscrape.modules.twitter as sntwitter
import tweepy
import datetime

today = datetime.date.today()
yesterday= today - datetime.timedelta(days=1)

app = Flask(__name__)

# Twitter
TWITTER_API_KEY="3iTMZx5ZmEW5KLoQCr7CXat6R"
TWITTER_API_SECRET="1XHzxw8rhPnPJz4DybRK8H34U7gmwOg7ChMf8i48bjVuduFmZf"
TWITTER_ACCESS_TOKEN="617154346-ESiFKJXeqS7FP2LHraEd0W0MaM7pNdR32TJXRPWE"
TWITTER_ACCESS_SECRET="wv9D4fxYdUZlA1LbJcoDOFebDG3F53OECEeqlEuoM3qGp"

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

        tweets_list = api.search_tweets( q="{key}".format(key=keyword) , lang='en')

        for tweet in tweets_list:
            text = tweet.text
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

    def analyze_tweets(self,df):
        analyzer = SentimentIntensityAnalyzer()

        df.dropna(subset=['processed_reviews'], inplace=True)

        df['compound'] = [analyzer.polarity_scores(x)['compound'] for x in df['processed_reviews']]
        df['neg'] = [analyzer.polarity_scores(x)['neg'] for x in df['processed_reviews']]
        df['neu'] = [analyzer.polarity_scores(x)['neu'] for x in df['processed_reviews']]
        df['pos'] = [analyzer.polarity_scores(x)['pos'] for x in df['processed_reviews']]

        V_score=[]

        df = df.reset_index()

        for t in range(len(df)):
            if df['compound'][t] >= 0.05 :
                V_score.append("Positive")
            elif df['compound'][t] <= - 0.05 :
                V_score.append("Negative")
            else :
                V_score.append("Neutral")

        df['Sentiment']=V_score

        filename=r'Twitter_{0}.csv'.format('Analyized')

        df.to_csv(filename)

        return df

@app.route('/sentiment', methods=['POST'])
def my_form():
    return render_template('search.html')

@app.route('/sentiment', methods=['POST'])
def show_tables():
    twitter = Twitter_Analysis()
    keyword = request.form['keyword']
    print("Entered keyword is ----->>>>",keyword)#str(input("Enter search word-"))
    twitter_pd = twitter.scrape(keyword)#pd.read_csv(r'Twitter_Analyized.csv')
    twitter_pd = twitter.cleanTxt(twitter_pd,keyword)
    twitter_pd = twitter.analyze_tweets(twitter_pd)
    return render_template('view.html',data=twitter_pd.to_html(table_id="example"))

if __name__ == "__main__":
    app.run(debug='True',port='1234')

