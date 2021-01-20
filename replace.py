import os
import yaml
import subprocess
import sys

from utils import PREFIX, STATUS
from utils import gen_tag, load_images

images = load_images()

synced_images = set()
pending_images = set()

for image in images:
    if image.get(STATUS, None) == 'synced':
        synced_images.add(image['name'])
    else:
        pending_images.add(image['name'])

images = sys.argv[1:] if len(sys.argv) > 1 else [image['name'] for image in images]

for image in images:
    if image not in synced_images:
        print('Unsynced image: {}'.format(image))
        exit(0)

    relabel = gen_tag(image)
    relabeled_image = PREFIX + ":" + relabel
    image = image.replace('/', '\/')
    relabeled_image = relabeled_image.replace('/', '\/')
    print('find . -name "*.yaml" | xargs sed -i -e \'s/{}/{}/g\''.format(image, relabeled_image))
    print('echo "replacing {} with {}"'.format(image, relabeled_image))

