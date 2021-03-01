import sys
import yaml
import argparse
import os
import subprocess

from utils import PREFIX, STATUS
from utils import gen_tag, load_images

def pull(args):
    synced_images = set()
    pending_images = set()

    hosts = []
    if args.cluster_hosts is not None:
        with open(args.cluster_hosts) as f:
            for l in f.readlines():
                hosts.append(l.strip())

    images = load_images()

    for image in images:
        if image.get(STATUS, None) == 'synced':
            synced_images.add(image['name'])
        else:
            pending_images.add(image['name'])

    cmds = []
    shells = []
    tars = []
    if not args.dry_run and not os.path.exists(args.folder):
        os.makedirs(args.folder)
    for image in args.images:
        save_file = os.path.join(args.folder, gen_tag(image) + ".tar.gz")
        tars.append(save_file)
        if image not in synced_images:
            cmds.append('docker pull {}'.format(image))
        else:
            relabel = PREFIX + ":" + gen_tag(image)
            cmds.append('docker pull {}'.format(relabel))
            cmds.append('docker tag {} {}'.format(relabel, image))
        cmds.append('docker save {} -o {}'.format(image, save_file))
        for host in hosts:
            shells.append('rsync -avP {} {}:~ && docker load -i {} &\n'.format(args.folder, host, save_file))
    cmds.append('rsync -avP {} {}:{}'.format(args.folder, args.remote_host, args.remote_folder))
    cmds.append('ssh {} -C \"bash -s\" < {}'.format(args.remote_host, args.script))

    if args.dry_run:
        print('---CMDS---')
        for cmd in cmds:
            print(cmd)
        print('---SHELLS---')
        for shell in shells:
            print(shell)
        print('---TARS---')
        for tar in tars:
            print(tar)
        print('---HOSTS---')
        for host in hosts:
            print(host)
        return

    with open(args.script, 'w') as f:
        f.writelines(shells)
    for cmd in cmds:
        subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sync Docker Images')
    parser.add_argument('--dry-run', action='store_true', help='dry run')
    parser.add_argument('--remote-host', default='master', help='remote host, copy-ssh-id first')
    parser.add_argument('--remote-folder', default='~', help='remote folder to cache docker image tar')
    parser.add_argument('--cluster-hosts', default='hosts.txt', help='cluster hosts file')
    parser.add_argument('--folder', default='images', help='local folder save docekr image tar')
    parser.add_argument('--script', default='pull.sh', help='temp script')
    parser.add_argument('images', metavar='N', nargs='+', help='images')
    args = parser.parse_args()

    pull(args)









