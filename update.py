import subprocess
import os

from utils import PREFIX, STATUS
from utils import get_remote_tags, gen_tag, load_images, save_images

def update():
    tags = get_remote_tags()
    d = load_images('images.yaml')

    images_set = set()
    newly_synced = []
    sync_pending = []
    for i, entry in enumerate(d):
        image = entry['name']
        status = entry.get(STATUS, None)
        if image in images_set:
            del d[i]
        images_set.add(image)
        if status is not None:
            continue

        relabel = gen_tag(image)
        if relabel in tags:
            d[i][STATUS] = 'synced'
            d[i][STATUS + '_image'] = PREFIX + ':' + relabel
            newly_synced.append(image)
        else:
            sync_pending.append(image)

    save_images(d)

    print('Successfully synced {} images, {} images are pending, {} by total'.format(len(newly_synced), len(sync_pending), len(images_set)))

if __name__ == '__main__':
    update()
