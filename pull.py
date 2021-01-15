import docker
import yaml
import sys

from update import update

update()

def pull()
    images_to_pull = sys.argv[1:]

    docker_hub_prefix = 'dockerhubkleon/k8s'

    client = docker.from_env()

    with open('images.yaml') as f:
        images = yaml.load(f.read(), Loader=yaml.BaseLoader)['images']

    synced_images = set()
    pending_images = set()

    for image in images:
        if image.get('status', None) == 'synced':
            synced_images.add(image['name'])
        else:
            pending_images.add(image['name'])

    for image in images_to_pull:
        if image in synced_images:
        relabeled_image = docker_hub_prefix + ":" + image.replace('/', '-').replace(':', '-')

        image_frags = image.split(':')
        image_repo = image_frags[0]
        image_tag = None
        if len(image_frags) == 2:
            image_tag = image_frags[1]

        image = client.images.pull(docker_hub_prefix, tag=relabel)
        image.tag(image_repo, tag=image_tag)

