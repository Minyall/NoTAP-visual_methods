from SETTINGS import name_tweet_collection, name_source_database
import pymongo
from datetime import datetime as dt
import pytz

#  To be run on server with a local mongo db.

connection = pymongo.MongoClient()
db = connection[name_source_database][name_tweet_collection]


counter = 0

for x in db.find():
    if counter % 1000 == 0:
        print('[*] Dated {} records so far...'.format(counter))
    db.update_one({'_id': x['_id']},{'$set':
        {
        'new_created_at': dt.strptime(x['created_at'],'%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC),
        'user.new_created_at': dt.strptime(x['user']['created_at'],'%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC)
        }
    }

    )
    counter += 1