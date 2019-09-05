import os
import getpass
import json
import shutil
from functools import lru_cache

import github3
from git import Repo
from git.exc import GitCommandError
import appdirs
from pressenter2exit import PressEnter2ExitGUI
from balsa import get_logger

from backupjca import __application_name__, __author__

log = get_logger(__application_name__)


def print_log(s):
    log.info(s)
    print(s)


# just instantiate once
@lru_cache()
def get_press_enter_to_exit() -> PressEnter2ExitGUI:
    return PressEnter2ExitGUI(title="github local backup")


def get_git_auth():

    username_string = 'username'
    password_string = 'password'

    credentials_dir = appdirs.user_config_dir(__application_name__, __author__)
    os.makedirs(credentials_dir, exist_ok=True)
    credentials_file_path = os.path.join(credentials_dir, "github_credentials.json")

    if os.path.exists(credentials_file_path):
        with open(credentials_file_path, 'r') as fd:
            credentials = json.load(fd)
            username = credentials[username_string]
            password = credentials[password_string]
    else:
        username = input("git username:").strip()
        password = None
        while password is None or len(password) < 1:
            password = getpass.getpass(f'Password for {username}:')
            password = password.strip()
        with open(credentials_file_path, 'w') as fd:
            credentials = {username_string: username, password_string: password}
            json.dump(credentials, fd, indent=4)

    assert(username is not None and len(username) > 0)
    assert(password is not None and len(password) > 0)
    print("Note: Using regular username/password.  Use tokens and 2FA once I can get them to work with github3.")
    gh = github3.login(username, password=password)  # , two_factor_callback=get_two_factor_code)

    return gh


def pull_branches(repo_name, branches, repo_dir):
    git_repo = Repo(repo_dir)
    for branch in branches:

        if not get_press_enter_to_exit().is_alive():
            break

        branch_name = branch.name
        print_log(f'git pull "{repo_name}" branch:"{branch_name}" to {repo_dir}')
        git_repo.git.checkout(branch_name)
        git_repo.git.pull()


def git_local_backup(backup_dir):

    gh = get_git_auth()
    for github_repo in gh.repositories():

        if not get_press_enter_to_exit().is_alive():
            break

        repo_name = str(github_repo)
        repo_dir = os.path.abspath(os.path.join(backup_dir, repo_name))
        branches = github_repo.branches()

        # if we've cloned previously, just do a pull
        pull_success = False
        if os.path.exists(repo_dir):
            try:
                pull_branches(repo_name, branches, repo_dir)
                pull_success = True
            except GitCommandError as e:
                log.info(e)
                print_log(f'could not pull "{repo_dir}" - will try to start over and do a clone of "{repo_name}"')

        # new to us - clone the repo
        if not pull_success:
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir, ignore_errors=True)

            print_log(f'git clone "{repo_name}" to "{repo_dir}"')

            Repo.clone_from(github_repo.clone_url, repo_dir)
            pull_branches(repo_name, branches, repo_dir)
