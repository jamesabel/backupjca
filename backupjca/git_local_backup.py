import os
import getpass
import json

import github3
from git import Repo
import appdirs
from pressenter2exit import PressEnter2ExitGUI

from backupjca import __application_name__, __author__


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


def git_local_backup(backup_dir):

    print("note: pulls are to default branch - other branches are not backed up")

    press_enter_to_exit = PressEnter2ExitGUI()

    gh = get_git_auth()
    for repo in gh.repositories():

        if not press_enter_to_exit.is_alive():
            break

        repo_string = str(repo)
        repo_dir = os.path.abspath(os.path.join(backup_dir, repo_string))
        if os.path.exists(repo_dir):
            print(f'git pull "{repo_dir}"')
            Repo(repo_dir).remote().pull()
        else:
            print(f'git clone "{repo_string}" to "{repo_dir}"')
            Repo.clone_from(repo.clone_url, repo_dir)
