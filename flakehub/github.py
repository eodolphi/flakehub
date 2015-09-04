from flask import url_for, session, request, redirect, Blueprint, render_template
from flask_oauthlib.client import OAuth


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


blueprint = Blueprint('github', __name__)


@blueprint.route('/login')
def login():
    return github.authorize(callback=url_for('github.authorized', _external=True))


@blueprint.route('/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))


@blueprint.route('/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )

    session['github'] = {
        'token': resp['access_token'],
    }

    session['github']['user'] = github.get('/user').data

    return redirect(url_for('github.repos'))


@blueprint.route('/repos')
def repos():
    repos = github.get('/user/repos').data

    return render_template('repos.html', repos=repos, user=session['github']['user'])


@blueprint.route('/repos/<user>/<repo>')
def repo(user, repo):
    repo = github.get('/repos/{}/{}'.format(user, repo)).data
    hooks = github.get('/repos/{}/{}/hooks'.format(user, repo)).data

    try:
        active = [hook for hook in hooks if hook['config']['context'] == 'flakehub']
    except TypeError:
        active = False

    return render_template('repo.html', repo=repo, hooks=hooks, active=active, user=session['github']['user'])


@github.tokengetter
def get_github_oauth_token():
    return (session['github']['token'],)
