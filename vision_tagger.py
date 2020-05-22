import os
import io
import json
import pymongo
from google.cloud import vision
from google.protobuf.json_format import MessageToJson
from SETTINGS import name_image_file_lookup, name_media_dir_path, name_source_database
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vision_secret.json"


def response_to_dict(response):
    return json.loads(MessageToJson(response))


connection = pymongo.MongoClient()
file_lookup = connection[name_source_database][name_image_file_lookup]
client = vision.ImageAnnotatorClient()




image_list_pipeline = [{'$match': {'labelAnnotations': {'$exists': 0}, 'image_tagged':{'$exists':0}}}]
# image_list_pipeline.append({'$limit': 10})

image_list_cursor = file_lookup.aggregate(pipeline=image_list_pipeline, allowDiskUse=True)
to_tag_count = len(list(image_list_cursor))

image_list_cursor = file_lookup.aggregate(pipeline=image_list_pipeline, allowDiskUse=True)
for i, record in enumerate(image_list_cursor):
    if i % 10 == 0:
        print(f'{i} of {to_tag_count} complete. {to_tag_count - i} remaining.')
    filepath = os.path.join(name_media_dir_path, record['filename'])
    if os.path.exists(filepath):
        with io.open(filepath, 'rb') as image_file:
            content = image_file.read()
        image = vision.types.Image(content=content)
        label_response = client.label_detection(image)
        # text_response = client.text_detection(image)

        #         package = {**response_to_dict(label_response), **response_to_dict(text_response)}
        package = response_to_dict(label_response)
        package['image_tagged'] = True

        file_lookup.update_one(filter={'_id': record['_id']}, update={'$set':package}, upsert=False)
