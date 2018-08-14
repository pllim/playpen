import math
import re
import time

try:
    from github3 import GitHub
except ImportError:
    raise ImportError('Please conda or pip install github3.py')

ISSUE_TITLE = 'Retire Python 2'

# Two endlines here = one endline on GitHub
ISSUE_BODY = re.sub('(\S+)\n', r'\1 ', """Python 2 will not be maintained
past Jan 1, 2020 (see https://pythonclock.org/). Please remove all Python 2
compatibility and move this package to Python 3 only.


For conda recipe (including `astroconda-contrib`), please include the
following to prevent packaging it for Python 2
(https://conda.io/docs/user-guide/tasks/build-packages/define-metadata.html?preprocessing-selectors#skipping-builds):


```

build:

  skip: true  # [py2k]

```


Please close this issue if it is irrelevant to your repository.
This is an automated issue. *If this is opened in error, please let {0} know!*
""").strip()


def go_forth_and_multiply(owner, listfile, gh_token=''):
    """
    Open issues! Provide a valid token.
    """
    gh = GitHub(token=gh_token)
    user = gh.me()
    body = ISSUE_BODY.format(user)

    # Only allowed to spam pre-approved list now.
    with open(listfile) as fin:
        repositories = [s.strip() for s in fin.readlines()
                        if not s.startswith('#')]

    tot_n = len(repositories)

    if tot_n == 0:
        print('No repository to process!')
        return

    max_n_per_chunk = 30
    n_chunks = math.ceil(tot_n / max_n_per_chunk)
    i_chunk = 0

    while i_chunk < n_chunks:
        i_start = i_chunk * max_n_per_chunk
        i_end = min(i_start + max_n_per_chunk, tot_n)

        for reponame in repositories[i_start:i_end]:
            time.sleep(0.5)  # Prevent API limit but not abuse detection
            repo = gh.repository(owner, reponame)
            if repo.archived:
                print('Skipped {0} -- archived'.format(repo.name))
                continue
            try:
                i = repo.create_issue('Update the help', body=body)
            except Exception as e:  # denied!
                print('Skipped {0} -- {1}'.format(repo.name, str(e)))
            else:
                print(i)

        i_chunk += 1
        if i_chunk < n_chunks:
            time.sleep(10)  # Prevent abuse detection, maybe


def one_repo_only(owner, reponame, gh_token=''):
    """
    Go back and see why this or that denied request. Provide a valid token.
    """
    gh = GitHub(token=gh_token)
    user = gh.me()
    body = ISSUE_BODY.format(user)
    repo = gh.repository(owner, reponame)
    i = repo.create_issue(ISSUE_TITLE, body=body)
    print(i)
