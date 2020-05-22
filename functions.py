import os
import requests
from urllib.error import HTTPError
from shutil import copyfileobj
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from SETTINGS import media_filter


def get_video_url(entity, _id, medium):
    data_dict = {'tweet_id': _id, 'media_url': '', 'bitrate': -1, 'type': '', 'medium': medium}

    for variant in entity['video_info']['variants']:
        if 'bitrate' in variant:
            if variant['bitrate'] > data_dict['bitrate']:
                data_dict['media_url'] = variant['url']
                data_dict['bitrate'] = variant['bitrate']
                data_dict['type'] = variant['content_type'][-3:]
    return data_dict


def get_photo_url(entity, _id, medium):
    data_dict = {'tweet_id': _id, 'media_url': '', 'type': '', 'medium': medium}
    data_dict['media_url'] = entity['media_url']
    data_dict['type'] = entity['media_url'][-3:]
    return data_dict


def get_entities(data, _id):
    if 'extended_entities' in data:
        target = data['extended_entities']
    elif 'entities' in data:
        target = data['entities']
    else:
        return {'message': 'No Media Found', 'tweet_id': _id}

    media_items = []
    if 'media' in target:
        for ent in target['media']:
            if (ent['type'] == 'video') and (media_filter['video']):
                data_dict = get_video_url(ent, _id, medium='video')
            elif (ent['type'] == 'photo') and (media_filter['photo']):
                data_dict = get_photo_url(ent, _id, medium='photo')
            elif (ent['type'] == 'animated_gif') and (media_filter['animated_gif']):
                data_dict = get_video_url(ent, _id, medium='animated_gif')
            else:
                data_dict =  {'tweet_id': _id, 'media_url': 'N/A', 'type': '', 'medium': ent['type']}
            media_items.append(data_dict)
    return media_items



def item_retrieve(url, idx, zfill_val=5, media_dir=None):
    try:
        media_dir = media_dir if not None else ''
        file_type = url[-4:]
        filename = str(idx).zfill(zfill_val) + file_type
        save_to = os.path.join(media_dir,filename)
        # save_to = 'test.jpg'
        if os.path.exists(save_to):
            raise OSError(f'File {save_to} already exists.')
        r = requests_retry_session().get(url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(save_to, 'wb') as f:
                copyfileobj(r.raw, f)

        return {'status': r.status_code,
                'filename':filename}

    except HTTPError as e:
        print(e.reason)
        return {'status':e.reason}

def if_no_dir_make(path):
    import os
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
    finally:
    	return path

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
if __name__ == '__main__':
    pass
