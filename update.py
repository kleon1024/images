import yaml
import subprocess
import os
import requests


def update():
    docker_hub_prefix = 'dockerkleon/k8s'

    url = 'https://registry.hub.docker.com/v2/repositories/dockerkleon/k8s/tags?page_size=1024'

    r = requests.get(url)
    if int(r.status_code) != 200:
        print('Failed connect to {}'.format(url))

    tags = set()
    for result in r.json()['results']:
        tags.add(result['name'])

    with open('images.yaml') as f:
        d = yaml.load(f.read(), Loader=yaml.BaseLoader)

    newly_synced = []
    sync_pending = []
    for i, entry in enumerate(d['images']):
        image = entry['name']
        status = entry.get('status', None)
        if status is not None:
            continue

        relabel = image.replace('/', '-').replace(':', '-')
        if relabel in tags:
            d['images'][i]['status'] = 'synced'
            d['images'][i]['image'] = docker_hub_prefix + ':' + relabel
            newly_synced.append(image)
        else:
            sync_pending.append(image)

    with open('images.yaml', 'w') as f:
        yaml.dump(d, f)

    print('Successfully synced {} images, {} images are pending'.format(len(newly_synced), len(sync_pending)))

if __name__ == '__main__':
    update()
