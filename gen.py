import sys
import yaml

from utils import PREFIX, STATUS
from utils import gen_tag, load_images

synced_images = set()
pending_images = set()

images = load_images()

for image in images:
    if image.get(STATUS, None) == 'synced':
        synced_images.add(image['name'])
    else:
        pending_images.add(image['name'])

images = sys.argv[1:] if len(sys.argv) > 1 else [image['name'] for image in images]

out_str = ''
for image in images:
    if image not in synced_images:
        print('Unsynced image: {}'.format(image))
        exit(0)
    relabel = gen_tag(image)
    relabeled_image = PREFIX + ":" + relabel
    out_str += 'sudo docker pull {}\n'.format(relabeled_image)
    out_str += 'sudo docker tag {} {}\n'.format(relabeled_image, image)

print(out_str)


