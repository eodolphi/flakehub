import re
import json

import rethinkdb as r

from flask import url_for, current_app, request, Blueprint

from flask_restful import Resource, Api

from flask_oauthlib.client import OAuth

import jwt

from flakehub.db import db


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


class InvalidSession(Exception):
    status_code = 401


def get_session():
    try:
        match = re.match(
            '^Bearer (?P<token>.+)$', request.headers['authorization']
        ).groupdict()

        token = jwt.decode(match['token'], current_app.secret_key, algorithm='HS256')
    except (KeyError, jwt.DecodeError):
        raise InvalidSession()

    return r.table('sessions').get(token['id']).run(db.conn)


@github.tokengetter
def get_oauth_token():
    return (get_session()['access_token'], )


class Session(Resource):
    def get(self):
        response = github.authorized_response()

        if 'error' in response:
            return response, 401

        user = github.get('/user', token=(response['access_token'], ))
        session = {
            'access_token': response['access_token'],
            'login': user.data['login'],
            'user_id': user.data['id'],
            'avatar': user.data['avatar_url'],
            'url': user.data['url']
        }

        result = r.table('sessions').insert(session).run(db.conn)
        session['access_token'] = jwt.encode(
            {'id': result['generated_keys'][0]},
            current_app.secret_key, algorithm='HS256'
        )

        return session


class User(Resource):
    def get(self):
        user = github.get('/user')
        return {
            'login': user.data['login'],
            'user_id': user.data['id'],
            'avatar': user.data['avatar_url'],
            'url': user.data['url']
        }, user.status


class Repos(Resource):
    def get(self):
        response = github.get('/user/repos')
        repos = [{
            'id': repo['full_name'],
            'name': repo['name'],
            'owner': repo['owner']['login'],
            'url': repo['html_url'],
            'description': repo['description']
        } for repo in response.data]

        return {'repos': repos}, response.status


class Repo(Resource):
    def get(self, full_name):
        response = github.get('/repos/{}'.format(full_name))
        if response.status != 200:
            return response.data, response.status

        return {'repo': {
            'id': response.data['full_name'],
            'owner': response.data['owner']['login'],
            'url': response.data['html_url'],
            'description': response.data['description'],
        }}


class Hook(Resource):
    def _save_hook(self, hook):
        hook = dict(hook)
        session = get_session()
        hook['access_token'] = session['access_token']
        hook = r.table('hooks').insert([hook]).run(db.conn)

    def get(self, full_name):
        response = github.get('/repos/{}/hooks'.format(full_name))

        hook = {'id': full_name}
        try:
            match = [match for match in response.data
                     if match['config'].get('context') == 'flakehub'][0]

            hook['active'] = True
            hook['hook_url'] = match['url']
        except:
            hook['active'] = False

        return {'hook': hook}

    def put(self, full_name):
        hook = json.loads(request.data)['hook']
        hook['id'] = full_name

        if hook.get('active'):
            url = '/repos/{}/hooks'.format(full_name)
            response = github.post(
                url,
                content_type='json',
                data=json.dumps({
                    'name': 'web',
                    'events': ['pull_request'],
                    'active': True,
                    'config': {
                        'url': url_for('webhook.hook', _external=True),
                        'content_type': 'json',
                    }
                })
            )
            hook['hook_url'] = response.data['url']
            self._save_hook(hook)

        else:
            response = github.delete(hook['hook_url'])
            del hook['hook_url']

        return hook, response.status


api.add_resource(Session, '/session')
api.add_resource(User, '/user')
api.add_resource(Repos, '/repos')
api.add_resource(Repo, '/repos/<path:full_name>')
api.add_resource(Hook, '/hooks/<path:full_name>')
