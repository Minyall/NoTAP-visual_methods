import tweepy
from credentials import *
import pymongo
connection = pymongo.MongoClient('localhost',27017)
connection.tweetlistener.authenticate('tweetwriter',tweetwriterpw,mechanism='SCRAM-SHA-1')
db = connection['tweetlistener']
tweet_catcher = db['notap_tweets']
from decorating import writing


class MyListener(tweepy.StreamListener):
    @writing
    def on_status(self,status):
        print(status.text)
        tweet_catcher.update_one({'_id':status._json['id']},{'$setOnInsert':status._json},upsert=True)

    def on_error(self,status_code):
        if status_code == 420:
            return False

auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY,ACCESS_SECRET)
api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

stream = tweepy.Stream(auth=api.auth, listener=MyListener())


stream.filter(track=['#notap'],async=True)


