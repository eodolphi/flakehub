import json

from flask import Flask, request
from flask_restful import Resource, Api

import requests

from flakehub import repo


ACCESS_TOKEN = '966fbb0b406357ad8eaf24ce0654459a01eb2e5a'

app = Flask(__name__)
api = Api(app)


class Repo(Resource):
    def get(self, user, repo):
        import ipdb;ipdb.set_trace()



class WebHook(Resource):
    def post(self):
        payload = request.get_json()

        if payload.get('action') == 'opened':
            pull_request = payload['pull_request']

            repository = repo.Repo(pull_request['base']['repo']['full_name'])
            repository.checkout(pull_request['head']['sha'])

            if repository.errors:
                description = 'Found {} style errors'.format(len(repository.errors))
                state = 'error'
            else:
                description = 'No problems'
                state = 'success'

            url = 'https://api.github.com/repos/{full_name}/statuses/{sha}'.format(
                full_name=repository.full_name,
                sha=pull_request['head']['sha']
            )
            headers = {
                'Authorization': 'token {}'.format(ACCESS_TOKEN),
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


api.add_resource(WebHook, '/webhook/')

if __name__ == "__main__":
    app.debug = True
    app.run()
