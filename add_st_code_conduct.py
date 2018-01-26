# NOTE: This is adapted from https://github.com/astropy/astropy-procedures/blob/master/update-affiliated/update_astropy_helpers.py  # noqa

import os
import re
import tempfile
import subprocess

try:
    from github3 import GitHub
except ImportError:
    raise ImportError('Please conda or pip install github3.py')

BRANCH = 'add_code_of_conduct'
CODE_OF_CONDUCT_REPO = ('spacetelescope', 'stsci-package-template')
CODE_OF_CONDUCT_FILENAME = 'CODE_OF_CONDUCT.md'

GITHUB_API_HOST = 'api.github.com'
gh = GitHub(token='')  # NOTE: Insert a valid token
user = gh.me()

PR_MESSAGE_BODY = re.sub('(\S+)\n', r'\1 ', """
This is an automated addition of spacetelescope code of conduct that is
copied from https://github.com/{0}/{1}/.


*If this is opened in error, please let {2} know!*
""").strip()

# Get CoC content from template
_r = gh.repository(*CODE_OF_CONDUCT_REPO)
_c = _r.file_contents(CODE_OF_CONDUCT_FILENAME).decoded.decode('utf-8')


def run_command(command):
    print('-' * 72)
    print("Running '{0}'".format(command))
    ret = subprocess.call(command, shell=True)
    if ret != 0:
        raise Exception("Command '{0}' failed".format(command))


def ensure_fork_exists(repo):
    if repo.owner.login != user.login:
        return repo.create_fork()
    else:
        return repo


def open_pull_request(fork, repo):

    # Set up temporary directory
    tmpdir = tempfile.mkdtemp()
    os.chdir(tmpdir)

    # Clone the repository
    run_command('git clone {0} .'.format(fork.ssh_url))

    # Make sure the branch doesn't already exist
    try:
        run_command('git checkout origin/{0}'.format(BRANCH))
    except:
        pass
    else:
        print("Branch {0} already exists".format(BRANCH))
        return

    # Update to the latest upstream master
    run_command('git remote add upstream {0}'.format(repo.clone_url))
    run_command('git fetch upstream master')
    run_command('git checkout upstream/master')
    run_command('git checkout -b {0}'.format(BRANCH))

    # Check that the repo does not already have one
    if os.path.exists(CODE_OF_CONDUCT_FILENAME):
        print("Repository {0} already has {1}".format(
            repo.name, CODE_OF_CONDUCT_FILENAME))
        return

    # Write code of conduct
    with open(CODE_OF_CONDUCT_FILENAME, 'w') as fout:
        fout.write(_c)

    run_command('git add {0}'.format(CODE_OF_CONDUCT_FILENAME))
    run_command(
        'git commit -m "Added spacetelescope code of conduct. [skip ci]"')
    run_command('git push origin {0}'.format(BRANCH))

    print(tmpdir)

    report_user = '@{0}'.format(user.login)

    repo.create_pull(
        title='Add {0} to repo'.format(CODE_OF_CONDUCT_FILENAME),
        base='master',
        head='{0}:{1}'.format(fork.owner.login, BRANCH),
        body=PR_MESSAGE_BODY.format(CODE_OF_CONDUCT_REPO[0],
                                    CODE_OF_CONDUCT_REPO[1], report_user))


START_DIR = os.path.abspath(os.curdir)

owner = 'spacetelescope'
repositories = []  # NOTE: Add repository names as needed

# Remove duplicates
repositories = sorted(set(repositories))

for repository in repositories:
    repo = gh.repository(owner, repository)
    fork = ensure_fork_exists(repo)
    try:
        open_pull_request(fork, repo)
    except:
        pass
    finally:
        os.chdir(START_DIR)
