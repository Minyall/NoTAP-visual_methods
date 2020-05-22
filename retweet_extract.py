import pymongo

from SETTINGS import name_source_database, name_tweet_collection
connection = pymongo.MongoClient('localhost', 27017)
db = connection[name_source_database][name_tweet_collection]

pipeline = [{'$match':{'retweeted_status':{'$exists':True}}}]
cursor = db.aggregate(pipeline=pipeline)
for i, x in enumerate(cursor):
    if i % 100 == 0:
        print('Extracted {} Original Tweets'.format(i))
    # print(type(x['retweeted_status']))
    # print(x['retweeted_status'])
    connection[name_source_database][name_tweet_collection].update_one({'id': x['retweeted_status']['id']}, {'$setOnInsert':x['retweeted_status']}, upsert=True)
    connection[name_source_database][name_tweet_collection].update_one({'id': x['retweeted_status']['id']},
                                                                       {'$max':{'retweet_count':x['retweeted_status']['retweet_count']}})

