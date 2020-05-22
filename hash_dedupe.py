import pymongo
from itertools import combinations
import pandas as pd
from fuzzywuzzy import process, fuzz
from SETTINGS import \
    name_source_database,\
    name_image_file_lookup

SIMILARITY_MINIMUM = 50

connection = pymongo.MongoClient()
image_file_lookup = connection[name_source_database][name_image_file_lookup]


hash_pipeline = [{'$match':{'hash':{'$exists':1}}}]

hash_cursor = image_file_lookup.aggregate(pipeline=hash_pipeline, allowDiskUse=True)

hash_dict = {record['filename']: record['hash'] for record in hash_cursor}

similar_files = []

print(len(list(combinations(hash_dict, r=2))))
for file_a, file_b in combinations(hash_dict, r=2):
    similarity = fuzz.ratio(hash_dict[file_a], hash_dict[file_b])
    if similarity >= SIMILARITY_MINIMUM:
        package = {'$addToSet':{'similar_files':{'filename':file_b, 'similarity':similarity}}}
        image_file_lookup.update_one(filter={'filename':file_a}, update=package, upsert=False)