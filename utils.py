import os
import yaml
import requests
import json

from enum import Enum

from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcr.request.v20160607 import GetRepoTagsRequest

AK = os.getenv('AK')
AS = os.getenv('AS')
REGION = os.getenv('DOCKER_REGION')
PREFIX = os.getenv('DOCKER_PREFIX')
STATUS = os.getenv('IMAGE_STATUS')
AUTH_CONFIG = {
    'username': os.getenv('DOCKER_USERNAME'),
    'password': os.getenv('DOCKER_PASSWORD'),
}

def gen_tag(image):
    relabel = image.replace('/', '-').replace(':', '-')
    if '@sha256:' in image:
        relabel = image.split(':')[0].replace('@sha256', '').replace('/', '-')
    return relabel

def split_image(image):
    image_frags = image.split(':')
    image_repo = image_frags[0]
    image_tag = 'latest'
    if len(image_frags) == 2:
        image_tag = image_frags[1]
    return image_repo, image_tag

def get_aliyun_tags():
    client = AcsClient(AK, AS, REGION)

    request = GetRepoTagsRequest.GetRepoTagsRequest()
    request.set_RepoNamespace("pai_product")
    request.set_RepoName("k8s")
    request.set_endpoint("cr."+REGION+".aliyuncs.com")

    try:
        i = 0
        tags = set()
        while(True):
            i += 1
            request.set_Page(i)
            request.set_PageSize(100)
            response = client.do_action_with_exception(request)
            response = json.loads(response)
            if len(response['data']['tags']) == 0:
                break
            for tag in response['data']['tags']:
                tags.add(tag['tag'])
        return tags
    except ServerException as e:
        print(e)
    except ClientException as e:
        print(e)

def load_yaml(filename):
    with open(filename) as f:
        return yaml.load_all(f.read(), Loader=yaml.BaseLoader)

def save_yaml(filename, ds):
    with open(filename, 'w') as f:
        yaml.dump_all(ds, f, default_flow_style=False)

def load_images(filename='images.yaml'):
    return list(load_yaml(filename))[0]['images']

def save_images(d, filename='images.yaml'):
    save_yaml(filename, [{'images' : d}])

def get_dockerhub_tags():
    url = 'https://registry.hub.docker.com/v2/repositories/dockerkleon/k8s/tags?page_size=1024'

    r = requests.get(url)
    if int(r.status_code) != 200:
        print('Failed connect to {}'.format(url))

    tags = set()
    for result in r.json()['results']:
        tags.add(result['name'])

    return tags


def get_remote_tags():
    return {
        'dockerhub': get_dockerhub_tags,
        'aliyun': get_aliyun_tags,
    }[STATUS]()


