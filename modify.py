import re
import os
import sys
import json
import subprocess
from utils import STATUS, PREFIX
from utils import load_yaml, save_yaml, load_images, split_image, gen_tag

folder = sys.argv[1]

image_dict = {}
image_set = set()


for image in load_images():
    if image.get(STATUS, None) is not None:
        image_set.add(image['name'])
        image_repo, image_tag = split_image(image['name'])
        image_dict[image_repo] = {
            "full": image['name'],
            "repo": image_repo,
            "tag": image_tag,
        }

replaces = {}
current = ""

def reg(s):
    return s.replace('/', '\/')

def replace_container(c):
    if 'image' in c:
        if not isinstance(c['image'], str):
            return
        #if 'imagePullPolicy' not in c:
        #    c['imagePullPolicy'] = 'IfNotPresent'
        #if c['image'] in image_dict:
        #    c['image'] = PREFIX + ':' + gen_tag(image_dict[c['image']]['full'])
        #if c['image'] in image_set:
        #    c['image'] = PREFIX + ':' + gen_tag(c['image'])

def replace_image(c):
    if 'name' in c and 'newName' in c and 'newTag' in c:
        if c['newName'] in image_dict and c['newTag'] == image_dict[c['name']]['tag']:
            image = image_dict[c['name']]
            #c['name'] = PREFIX
            global replaces
            global current
            #print('sed -i \'\' -e \'s/newName: {}\\n\(\s+\)newTag: {}/newName: {}\\n$1newTag: {}/g\' {}'.format(reg(c['newName']), reg(c['newTag']),reg(PREFIX), reg(gen_tag(image['full'])), current))
            #print('sed -i \'\' -e \'s//g\' {}'.format(reg(c['newTag']), reg(gen_tag(image['full'])), current))
            replaces[c['newName'] + ':' + c['newTag']] = {
                'file': current,
                'old_name': reg(c['newName']),
                'old_tag': reg(c['newTag']),
                'new_name': PREFIX,
                'new_tag': gen_tag(image['full'])
            }
            c['newName'] = PREFIX
            c['newTag'] = gen_tag(image['full'])

def replace_yaml(d):
    if isinstance(d, dict):
        if 'containers' in d:
            for i, c in enumerate(d['containers']):
                replace_container(c)
        if 'images' in d:
            for i, c in enumerate(d['images']):
                replace_image(c)
        for k, v in d.items():
            replace_yaml(v)
    elif isinstance(d, list):
        for i, c in enumerate(d):
            replace_yaml(c)

def replace(folder):
    if os.path.isdir(folder):
        for d in os.listdir(folder):
            replace(os.path.join(folder, d))
    elif folder.endswith('kustomization.yaml'):
        global current
        current = folder
        ds = load_yaml(folder)
        ds = list(ds)
        ds_str = json.dumps(ds)
        for d in ds:
            replace_yaml(d)
        #if ds_str != json.dumps(ds):
        #    save_yaml(folder, ds)
    global replaces

if __name__ == '__main__':
    replace(folder)

    for k, r in replaces.items():
        filename = r['file']
        print(filename)
        before = r'newName: {}(\s+)newTag: {}'.format(r['old_name'], r['old_tag'])
        after = r'newName: {}\1newTag: {}'.format(r['new_name'], r['new_tag'])
        with open(filename) as f:
            s = f.read()
            s = re.sub(before, after, s)
        with open(filename, 'w') as f:
            f.write(s)

        before = r'newTag: {}(\s+)newName: {}'.format(r['old_tag'], r['old_name'])
        after = r'newTag: {}\1newName: {}'.format(r['new_tag'], r['new_name'])
        with open(filename) as f:
            s = f.read()
            s = re.sub(before, after, s)
        with open(filename, 'w') as f:
            f.write(s)





