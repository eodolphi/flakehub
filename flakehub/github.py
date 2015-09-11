import os
import re
import json

from flask import url_for, session, request, redirect, Blueprint

from flask_restful import Resource, Api

from flask_oauthlib.client import OAuth

from Crypto.PublicKey import RSA
from jwkest.jwk import RSAKey
from jwkest.jwe import JWE


blueprint = Blueprint('github', __name__)
api = Api(blueprint)


oauth = OAuth()

github = oauth.remote_app(
    'github',
    app_key='GITHUB',
    request_token_params={'scope': 'user:email,repo,write:repo_hook'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

with open(os.path.join(os.path.dirname(__file__), 'jwe.key')) as f:
    key = RSA.importKey(f.read())
    jwk_rsa = RSAKey(key=key)


def get_bearer_token():
    match = re.match('^Bearer (?P<token>.+)$', request.headers['authorization'])
    return match.groupdict()['token']


@github.tokengetter
def get_github_oauth_token():
    jwe = get_bearer_token()
    return JWE().decrypt(jwe, keys=[jwk_rsa]),


class Token(Resource):
    def get(self):
        resp = github.authorized_response()

        if 'error' in resp:
            return resp, 401

        jwe = JWE(resp['access_token'], alg="RSA-OAEP", enc="A256GCM")

        return {'token': jwe.encrypt([jwk_rsa])}


class User(Resource):
    def get(self):
        response = github.get('/user')
        return response.data, response.status


class Repos(Resource):
    def get(self):
        response = github.get('/user/repos')
        return response.data, response.status


class Repo(Resource):
    def get(self, user, repo):
        repo_response = github.get('/repos/{}/{}'.format(user, repo))
        if repo_response.status != 200:
            return repo_response.data, repo_response.status

        repo = repo_response.data
        hooks = github.get(repo['hooks_url']).data

        try:
            repo['active'] = any(
                [hook['config'].get('context') == 'flakehub' for hook in hooks]
            )
        except TypeError:
            repo['active'] = False

        return repo

    def post(self, user, repo):
        response = github.post(
            '/repos/{}/{}/hooks'.format(user, repo),
            content_type='json',
            data=json.dumps({
                'name': 'web',
                'events': ['pull_request'],
                'active': True,
                'config': {
                    'url': url_for('webhook.hook', _external=True),
                    'content_type': 'json',
                    'context': 'flakehub',
                    'token': get_bearer_token()
                }
            })
        )

        return response.data, response.status


api.add_resource(Token, '/token/')
api.add_resource(User, '/user/')
api.add_resource(Repos, '/repos/')
api.add_resource(Repo, '/repos/<user>/<repo>/')
