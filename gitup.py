#!/usr/bin/python
# coding: utf-8
HEADER = """
  ___  ____  ____    __  __  ____  ____    __   ____  ____ 
 / __)(_  _)(_  _)  (  )(  )(  _ \(  _ \  /__\ (_  _)( ___)
( (_-. _)(_   )(     )(__)(  )___/ )(_) )/(__)\  )(   )__) 
 \___/(____) (__)   (______)(__)  (____/(__)(__)(__) (____)
"""
from termcolor import colored
import os
import sys
import argparse
import time

if __name__ == '__main__':
    start_time = time.time()
    print colored(HEADER, 'magenta')
    print ""

    parser = argparse.ArgumentParser(description='Recursively update git repositories')
    parser.add_argument('path', metavar='<path>', type=str, help='path to git repositories')

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print colored("[!] %s is not a existing path" % args.path, "red")

    targeted_dir = args.path

    dirs_to_update = set()
    for root, dirs, files in os.walk(targeted_dir):
        for name in dirs:
            dirs_to_update.add(os.path.join(root, name))

    counter = 0
    for d in dirs_to_update:
        if os.path.isfile(d + '/.git/HEAD'):
            print colored("\n[+] %s is a git repository" % d, 'green')
            os.system("cd %s && git pull" % d)
            counter += 1

    elapsed_time = int(time.time() - start_time)
    print ""
    print ""
    print colored("[+] %i repositories updated in %s seconds" % (counter, elapsed_time), 'blue')
