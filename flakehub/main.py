from flask import Flask

from flakehub import github, webhook, db


app = Flask(__name__)
app.config.from_object('flakehub.config')

github.oauth.init_app(app)
db.db.init_app(app)


app.register_blueprint(github.blueprint, url_prefix='/api')
app.register_blueprint(webhook.blueprint, url_prefix='/webhook')


if __name__ == '__main__':
    app.debug = True
    app.run()
