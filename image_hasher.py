import pymongo
import os
from PIL import Image
import imagehash
from SETTINGS import \
    name_source_database,\
    name_image_file_lookup,\
    name_media_dir_path

connection = pymongo.MongoClient()
image_file_lookup = connection[name_source_database][name_image_file_lookup]


image_pipeline = [{'$match':{'filename':{'$exists':1},
                             'status':200,
                             'hash':{'$exists':0}}}]

image_file_cursor = image_file_lookup.aggregate(pipeline=image_pipeline, allowDiskUse=True)

for image in image_file_cursor:
    filename = image['filename']
    file_path = os.path.join(name_media_dir_path, filename)
    img = Image.open(file_path)
    img_hash = imagehash.dhash(img)
    image_file_lookup.update_one(filter={'_id':image['_id']}, update={'$set':{'hash':str(img_hash)}})