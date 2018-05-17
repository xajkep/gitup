#!/usr/bin/python3
# coding: utf-8
#
# version: 0.2@20180517
#   [X] Python2 to Python3
#   [X] Using glob instead of os.walk
#   [X] List all available updates and ask for confirmation
#   [X] Recursivity can be disabled
#   [X] os.system to subprocess.Popen
#   [X] Add requirements.txt for easy dependances installation via pip
#   [X] Change informative output
#   [X] Checking `git status` before updating
#
HEADER = """  ___  ____  ____    __  __  ____  ____    __   ____  ____ 
 / __)(_  _)(_  _)  (  )(  )(  _ \(  _ \  /__\ (_  _)( ___)
( (_-. _)(_   )(     )(__)(  )___/ )(_) )/(__)\  )(   )__) 
 \___/(____) (__)   (______)(__)  (____/(__)(__)(__) (____)

                                      version 0.2 - @xajkep
"""
from termcolor import colored
import os, sys, argparse, time, subprocess
from glob import glob
from pathlib import Path

GIT_PATH = '/usr/bin/git'

if __name__ == '__main__':
    print(colored(HEADER, 'magenta'))

    parser = argparse.ArgumentParser(description='Recursively update git repositories')
    parser.add_argument('path', metavar='<path>', type=str, help='path to git repositories')
    parser.add_argument('--not-recursive', dest='recursivity', action='store_false', help='Disable recursivity')
    parser.add_argument('-y', dest='skip_confirmation', action='store_true', help='Skip update confirmation')
    parser.set_defaults(recursivity=True)
    parser.set_defaults(skip_confirmation=False)

    args = parser.parse_args()
    targeted_path = args.path
    recursivity = args.recursivity
    skip_confirmation = args.skip_confirmation
    confirmed = args.skip_confirmation

    if not os.path.isdir(args.path):
        print(colored("[!] %s is not a existing path" % args.path, "red"))

    targeted_dir = args.path

    # Search (recursively) all git repositories
    git_repositories = set()
    for t in glob(targeted_path + '/**/.git/HEAD', recursive=recursivity):
        current_dir = t.replace('/.git/HEAD', '')
        git_repositories.add(current_dir)

    repositories_to_update = []
    for path_to_repo in git_repositories:
        if path_to_repo.find('/') > -1:
            repository_name = path_to_repo.split('/')[-1]
        else:
            repository_name = path_to_repo
        print(colored("[-] Fetch git repository", 'green'), colored("%s" % repository_name, 'green', attrs=['bold']))

        absolute_path = str(Path(path_to_repo).resolve())

        # `git fetch` before, otherwise we will have wrong results from `git status` 
        git_process = subprocess.Popen(
                [GIT_PATH, 'fetch'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=absolute_path)
        git_process.wait()
        git_process = subprocess.Popen(
            [GIT_PATH, 'status', '-uno', '.'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=absolute_path)
        
        stdout = git_process.communicate()[0].decode()
        
        if not "Your branch is up-to-date" in stdout:
            repositories_to_update.append({
                'name': repository_name,
                'absolute_path': absolute_path
            })
    
    if len(repositories_to_update) == 0:
        print(colored("[-] All repositories (%i) are up-to-date" % len(git_repositories), 'blue'))
        exit()
    
    print("")

    if not skip_confirmation:
        print(colored("[-] The following repositories have updates:", 'blue'))
        for repo in repositories_to_update:
            print(colored("    -", 'blue'), colored("%s" % repo['name'], 'white', attrs=['bold']))
        
        print("")
        confirmed = input(colored('[?] Do you want to proceed (y/n)> ', 'blue')).lower() in ['y', 'yes', 'yeah', 'yep', 'yeap', 'ya', 'da', 'ja', 'oui', 'si']
    
    if confirmed:
        start_time = time.time()
        for repo in repositories_to_update:
            print(colored("[+] Updating repository:", 'yellow'), colored(repo['name'], 'yellow', attrs=['bold']))
            git_process = subprocess.Popen(
                [GIT_PATH, 'pull'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=repo['absolute_path'])
            stdout = git_process.communicate()[0].decode()
            print(colored(stdout, 'grey'))

        elapsed_time = float(time.time() - start_time)
        print("")
        print(colored("[-] %i/%i repositories updated in %.2f seconds" % (len(repositories_to_update), len(git_repositories), elapsed_time), 'blue'))
