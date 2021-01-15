import sys
import yaml
from update import update

update()

docker_hub_prefix = 'dockerhubkleon/k8s'

with open('images.yaml') as f:
    images = yaml.load(f.read(), Loader=yaml.BaseLoader)['images']

synced_images = set()
pending_images = set()

for image in images:
    if image.get('status', None) == 'synced':
        synced_images.add(image['name'])
    else:
        pending_images.add(image['name'])

    image = image['name']
    relabeled_image = docker_hub_prefix + ":" + image.replace('/', '-').replace(':', '-')

    image_frags = image.split(':')
    image_repo = image_frags[0]
    image_tag = None
    if len(image_frags) == 2:
        image_tag = image_frags[1]

images = sys.argv[1:]

for image in images:
    if image not in synced_images:
        print('Unsynced image: {}'.format(image))
        exit(0)
    relabeled_image = docker_hub_prefix + ":" + image.replace('/', '-').replace(':', '-')
    print('sudo docker pull {}'.format(relabeled_image))
    print('sudo docker tag {} {}'.format(relabeled_image, image))



