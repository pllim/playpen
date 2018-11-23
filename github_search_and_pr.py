import os
import subprocess
import time

import github3


# pattern = '"from astropy.tests.runner import TestRunner" language:python'
# filename = '_astropy_init.py'
def search_and_pr(pattern, filename, token=None, login=''):
    gh = github3.GitHub(token=token)
    # user = gh.me()  # https://github.com/sigmavirus24/github3.py/issues/797
    count = 0
    start_dir = os.path.abspath(os.curdir)
    search_result = gh.search_code('filename:{} {}'.format(filename, pattern))

    # NOTE: Modify as needed.
    code_fix = 'test.__test__ = False'

    for res in search_result:
        time.sleep(2)  # Prevent GitHub killing stuff
        found = False
        count += 1
        repo = res.repository

        # Skip forks.
        if repo.fork:
            print('Skipping fork {}'.format(repo.full_name))
            continue

        print('Checking {}'.format(repo.full_name))

        # Check if file is affected.
        targfile = res.path
        contents = repo.file_contents(targfile)
        lines = contents.decoded.decode('utf-8').split('\n')

        for i, row in enumerate(lines):
            # NOTE: Modify as needed.
            if 'test = TestRunner.make_test_runner_in' in row:
                if code_fix in lines[i + 1]:  # Already fixed: no-op
                    print('Already fixed, skipping {}'.format(repo.full_name))
                    found = False
                else:
                    found = True
                break

        if not found:
            continue

        print('*** Fixing {}'.format(repo.full_name))

        # NOTE: Modify as needed.
        x = row.split('test =')  # x[0] = indentation
        the_fix = x[0] + code_fix
        lines.insert(i + 1, the_fix)
        new_content = '\n'.join(lines)

        # Make a fork if needed.
        if repo.owner.login != login:  # user.login
            fork_repo = repo.create_fork()
        else:
            fork_repo = repo

        try:
            # NOTE: Modify as needed.
            open_pull_request(
                fork_repo, gh.repository(repo.owner, repo.name),
                'test_false', targfile, new_content)
            print('***** SUCCESS')
        except Exception as e:
            print('***** FAILED: {}'.format(str(e)))
        finally:
            os.chdir(start_dir)


def run_command(command):
    print('-' * 72)
    print("Running '{0}'".format(command))
    ret = subprocess.call(command, shell=True)
    if ret != 0:
        raise Exception("Command '{0}' failed".format(command))


def open_pull_request(fork, repo, branch, filename, content):

    # Set up temporary directory
    tmpdir = 'pr_for_{}'.format(repo.name)
    os.mkdir(tmpdir)
    os.chdir(tmpdir)

    # Clone the repository
    run_command('git clone {0} .'.format(fork.ssh_url))

    # Update to the latest upstream master
    master = repo.default_branch
    run_command('git remote add upstream {0}'.format(repo.clone_url))
    run_command('git fetch upstream {}'.format(master))
    run_command('git checkout upstream/{}'.format(master))
    run_command('git checkout -b {0}'.format(branch))

    # NOTE: Modify as needed.
    # Fix the affected file.
    report_user = '@{0}'.format(fork.owner.login)
    commit_msg = 'Prevent pytest from picking up test function as a test'
    pr_body = ('This one-line change prevents pytest from picking up the '
               'test function as a test. See astropy/package-template#373.\n\n'
               '*This is an automated fix by {}. If this is opened in error, '
               'please close without merge.*'.format(report_user))
    with open(filename, 'w+') as fout:
        fout.write(content)

    run_command('git add {0}'.format(filename))
    run_command('git commit -m "{}"'.format(commit_msg))
    run_command('git push origin {0}'.format(branch))

    repo.create_pull(title=commit_msg, base=master, body=pr_body,
                     head='{0}:{1}'.format(fork.owner.login, branch))
