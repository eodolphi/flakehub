import json

from flask import Blueprint, request, current_app

import requests

from flakehub.repo import Repo
from flakehub.github import github


ACCESS_TOKEN = '966fbb0b406357ad8eaf24ce0654459a01eb2e5a'

blueprint = Blueprint('webhook', __name__)


@blueprint.route('/', methods=['POST'])
def hook():
    payload = request.get_json()

    if 'pull_request' in payload and payload.get('action') in ['opened', 'synchronized']:
        pull_request = payload['pull_request']

        repo = Repo(pull_request['base']['repo']['full_name'])
        repo.checkout(pull_request['head']['sha'])

        if repo.errors:
            description = 'Found {} style errors'.format(len(repo.errors))
            state = 'error'
        else:
            description = 'No problems'
            state = 'success'

        url = 'https://api.github.com/repos/{full_name}/statuses/{sha}'.format(
            full_name=repo.full_name,
            sha=pull_request['head']['sha']
        )
        import ipdb;ipdb.set_trace() # FIXME: decrypt token
        headers = {
            'Authorization': 'token {}'.format(token),
            'Content-Type': 'application/json'
        }
        data = {
            'state': state,
            'description': description,
            'contect': 'flake8',
            'target': 'http://www.example.com'
        }

        requests.post(url, headers=headers, data=json.dumps(data))

    return 'OK'
