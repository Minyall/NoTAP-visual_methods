import pymongo
import time
from pymongo.errors import BulkWriteError
from functions import get_entities, item_retrieve, if_no_dir_make
from SETTINGS import \
    name_tweet_collection,\
    name_source_database,\
    name_image_file_lookup,\
    name_tweet_image_lookup,\
    name_media_dir_path

if_no_dir_make(name_media_dir_path)

connection = pymongo.MongoClient()
collection_names = connection[name_source_database].list_collection_names()
tweet_db = connection[name_source_database][name_tweet_collection]

tweet_image_lookup = connection[name_source_database][name_tweet_image_lookup]
image_file_lookup = connection[name_source_database][name_image_file_lookup]

if not name_tweet_image_lookup in collection_names:
    media_pipeline = [{'$match':{
        '$or':[{'extended_entities':{'$exists':1}}, {'entities':{'$exists':1}}]
    }}]

    media_cursor = tweet_db.aggregate(pipeline=media_pipeline, allowDiskUse=True)

    media_data = []
    for tweet in media_cursor:
        tweet_id = tweet['id']
        if 'extended_tweet' in tweet:
            tweet = tweet['extended_tweet']
        entities = (get_entities(tweet, tweet_id))
        media_data.extend(entities)
    # media_data = list(filter(lambda x: x['media_url'] != 'N/A', media_data))
    media_data = [x for x in media_data if x['media_url'] !='N/A']
    try:
        tweet_image_lookup.insert_many(documents=media_data, ordered=False)
    except BulkWriteError as e:
        code_check = list(filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
        if len(code_check) > 0:
            raise

if not name_image_file_lookup in collection_names:
    dedupe_by_file_pipeline = [{'$group':{'_id':'$media_url',
                                          'tweet_ids':{'$addToSet':'$tweet_id'},
                                          'count':{'$sum':1}
                                          }
                                },
                               {'$out':name_image_file_lookup}
                               ]

    tweet_image_lookup.aggregate(pipeline=dedupe_by_file_pipeline, allowDiskUse=True)
#
# to_download_pipeline = [{'$match':{'_id':{'$exists':1}}}]
# # to_download_pipeline.append({'$limit':10})
# to_download_cursor = image_file_lookup.aggregate(pipeline=to_download_pipeline, allowDiskUse=True)
#
# for idx, record in enumerate(to_download_cursor):
#     time.sleep(0.2)
#     if 'status' not in record:
#         url = record['_id']
#         update = item_retrieve(url, idx, zfill_val=5, media_dir=name_media_dir_path)
#         image_file_lookup.update_one(filter={'_id': record['_id']},
#                                          update={'$set': update},
#                                          upsert=False)








