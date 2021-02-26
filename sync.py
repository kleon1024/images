import docker
import yaml
import subprocess
import os
import sys

from utils import AUTH_CONFIG, STATUS, PREFIX
from utils import gen_tag, split_image, load_images

client = docker.from_env()

images = load_images()

for entry in images:
    image = entry['name']
    status = entry.get(STATUS, None)
    if status is not None:
        continue
    relabel = gen_tag(image)
    relabel_image = PREFIX + ":" + relabel
    image_repo, image_tag = split_image(image)

    print("Remapping {} to {}".format(image, relabel_image))
    cmd = ['sudo', 'docker', 'pull', image]
    subprocess.run(cmd)
    cmd = ['sudo', 'docker', 'tag', image, relabel_image]
    subprocess.run(cmd)
    cmd = ['sudo', 'docker', 'login', '--username=' + AUTH_CONFIG['username'], '--password=' + AUTH_CONFIG['password'], PREFIX.split('/')[0]]
    subprocess.run(cmd)
    cmd = ['sudo', 'docker', 'push', PREFIX + ":" + relabel]
    subprocess.run(cmd)
    #client.images.push(PREFIX, tag=relabel, auth_config=AUTH_CONFIG)

