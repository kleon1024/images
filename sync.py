import docker
import yaml
import subprocess
import os

auth_config = {
    'username': os.getenv('DOCKER_USERNAME'),
    'password': os.getenv('DOCKER_PASSWORD'),
}

docker_hub_prefix = 'dockerkleon/k8s'

client = docker.from_env()

with open('images.yaml') as f:
    images = yaml.load(f.read(), Loader=yaml.BaseLoader)['images']

for entry in images:
    image = entry['name']
    status = entry.get('status', None)
    if status is not None:
        continue
    relabel = image.replace('/', '-').replace(':', '-')
    print("Remapping {} to {}".format(image, docker_hub_prefix + ":" + relabel))
    image_frags = image.split(':')
    image_repo = image_frags[0]
    image_tag = None
    if len(image_frags) == 2:
        image_tag = image_frags[1]

    image = client.images.pull(image_repo, tag=image_tag)
    image.tag(docker_hub_prefix, tag=relabel)
    status = client.images.push(docker_hub_prefix, tag=relabel, auth_config=auth_config)
    print(status)

