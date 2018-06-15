import re

import requests


# This is from https://github.com/astropy/astropy-bot
def paged_github_json_request(url, headers=None):

    response = requests.get(url, headers=headers)
    assert response.ok, response.content
    results = response.json()

    if 'Link' in response.headers:

        links = response.headers['Link']

        # There are likely better ways to parse/extract the link information
        # but here we just find the last page number mentioned in the header
        # 'Link' section and then loop over all pages to get the comments
        last_match = list(re.finditer('page=[0-9]+', links))[-1]
        last_page = int(
            links[last_match.start():last_match.end()].split('=')[1])

        # If there are other pages, just loop over them and get all the
        # comments
        if last_page > 1:
            for page in range(2, last_page + 1):
                response = requests.get(
                    url + '?page={0}'.format(page), headers=headers)
                assert response.ok, response.content
                results += response.json()

    return results


def user_activity(username, public_only=True, token=None, to_table=False):
    """GitHub activity for given user."""
    headers = {'Accept': 'application/vnd.github.machine-man-preview+json'}

    if token is not None:
        headers['Authorization'] = f'token {token}'

    url = f'https://api.github.com/users/{username}/events'

    if public_only:
        url += '/public'

    results = paged_github_json_request(url, headers=headers)

    if to_table:
        results = _json_to_table(results)

    return results


def _json_to_table(results):
    """Parse select JSON results into Astropy table."""
    from astropy.table import Table

    colnames = ('created_at', 'type', 'public', 'repo_name', 'description')
    coltypes = ('S11', 'S50', 'S6', 'S50', 'S255')
    tab = Table(names=colnames, dtype=coltypes)

    for r in results:
        r_type = r['type']
        payload = r['payload']

        # TODO: What payload info is useful to display?
        if r_type == 'PushEvent':
            r_descrip = payload['commits'][0]['message']
        elif r_type == 'PullRequestEvent':
            r_descrip = f"{payload['action']} {payload['number']}"
        elif r_type == 'IssuesEvent':
            r_descrip = f"{payload['action']} {payload['issue']['number']}"
        # TODO: Implement CreateEvent, IssueCommentEvent,
        #       PullRequestReviewCommentEvent, ReleaseEvent
        else:
            r_descrip = f'unknown for {r_type}'

        tab.add_row((r['created_at'], r_type, r['public'],
                     r['repo']['name'], r_descrip))

    return tab
