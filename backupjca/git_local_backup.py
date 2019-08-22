import os
import getpass
import json

import github3
import appdirs
from sundry import is_main

from backupjca import __application_name__, __author__


def get_two_factor_code():
    code = None
    while code is None or len(code) < 1:
        code = input('Enter 2FA code:')
        print(code)
    return code


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
    print("Note: Using regular username/password.  Use tokens and 2FA once I can get them to work with github2.")
    gh = github3.login(username, password=password)  # , two_factor_callback=get_two_factor_code)

    return gh


def git_local_backup():

    gh = get_git_auth()
    for repo in gh.repositories():
        # todo: STOPPED HERE - CLONE REPOS DOWN TO A DIR
        print(repo.url)


if is_main():
    get_git_auth()
