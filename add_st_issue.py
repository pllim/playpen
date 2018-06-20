import re
import time

try:
    from github3 import GitHub
except ImportError:
    raise ImportError('Please conda or pip install github3.py')

ISSUE_BODY = re.sub('(\S+)\n', r'\1 ', """Tyler Desjardins mentions that
we should consider moving emails from `help[at]stsci.edu` to point to the
web portal where possible and appropriate.
For HST (or any non-JWST), it is https://hsthelp.stsci.edu .
For JWST, it is https://jwsthelp.stsci.edu .
Please update info in `setup.py`, `setup.cfg`, documentation, etc
as appropriate.


Please close this issue if it is irrelevant to your repository.
This is an automated issue. *If this is opened in error, please let {0} know!*


xref spacetelescope/hstcal#317
""").strip()


def go_forth_and_multiply(owner, gh_token=''):
    """
    Open issues! Provide a valid token.
    """
    gh = GitHub(token=gh_token)
    user = gh.me()
    body = ISSUE_BODY.format(user)
    org = gh.organization(owner)

    # Hack to get remaining ones
    # with open('ztmp.txt') as fin:
    #     repositories = [s.strip() for s in fin.readlines()]
    # for reponame in repositories:

    for repo in org.repositories():
        time.sleep(0.5)  # Prevent API limit but not abuse detection
        # repo = gh.repository(owner, reponame)  # for hack only
        try:
            i = repo.create_issue('Update the help', body=body)
        except Exception as e:  # denied!
            print('Skipped {0} -- {1}'.format(repo, str(e)))
        else:
            print(i)


def one_repo_only(owner, reponame, gh_token=''):
    """
    Go back and see why this or that denied request. Provide a valid token.
    """
    gh = GitHub(token=gh_token)
    user = gh.me()
    body = ISSUE_BODY.format(user)
    repo = gh.repository(owner, reponame)
    i = repo.create_issue('Update the help', body=body)
    print(i)
