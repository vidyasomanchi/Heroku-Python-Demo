#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
import snscrape.modules.twitter as sntwitter
app = Flask(__name__)


# In[ ]:


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
        tweets_list = []

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(keyword).get_items()):
            if i > 10:
                break
            tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.username])

        # Creating a dataframe from the tweets list above
        #df = pd.read_csv(r'Twitter_omnicron.csv')
        df = pd.DataFrame(tweets_list, columns=['Date', 'Tweet Id', 'Reviews', 'Username'])
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


# In[ ]:


@app.route('/')
def my_form():
    return render_template('search.html')

@app.route('/', methods=['POST'])
def show_tables():
    #data = pd.read_csv(r'Twitter_Analyized.csv')
    twitter = Twitter_Analysis()
    keyword = request.form['keyword']
    print("Entered keyword is ----->>>>",keyword)#str(input("Enter search word-"))
    twitter_pd = twitter.scrape(keyword)#pd.read_csv(r'Twitter_Analyized.csv')
    twitter_pd = twitter.cleanTxt(twitter_pd,keyword)
    return render_template('view.html',tables=[twitter_pd.to_html(classes='report')])

if __name__ == "__main__":
    app.run()

