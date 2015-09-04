from flask import Flask

from flakehub import github, webhook


app = Flask(__name__)


github.oauth.init_app(app)
app.register_blueprint(github.blueprint, url_prefix='/github')

app.register_blueprint(webhook.blueprint, url_prefix='/webhook')

app.config.from_object('flakehub.config')


if __name__ == '__main__':
    app.debug = True
    app.run()
