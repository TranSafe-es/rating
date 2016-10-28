
from flask import Flask
from flask_restful import Api, Resource

from settings import *
from views.authorization import authorization

app = Flask(__name__)

app.secret_key = SECRET_KEY

app.register_blueprint(authorization)

if __name__ == '__main__':
    app.run(port=PORT, host=ALLOWED_HOSTS)
