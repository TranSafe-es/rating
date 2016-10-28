
import sys
import os
import datetime
import json
import base64
import urllib
from rauth import *
from flask_restful import Api, Resource
from flask import request, render_template, redirect, Response, url_for, Blueprint, session

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from settings import *
from db import db_session
from models import Users

authorization = Blueprint('authorization', __name__)

import logging
logging.basicConfig(stream=sys.stderr)
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger()

@authorization.route("/", methods = ['GET'])
def home():
    return render_template('home.html')

@authorization.route("/validate", methods = ['POST'])
def validate():
    if 'Access-Token' not in request.headers:
        return build_error_response("Missing authentication", \
                                    400,\
                                    "Access-Token header not present in the request")
    access_token = request.headers.get('Access-Token')
    user = Users.query.filter_by(access_token=access_token).first()
    if user == None:
        return build_error_response("Invalid authentication", \
                                    401,\
                                    "Access-Token is invalid for this service")
    if not valid_token(user):
        return build_error_response("Invalid authentication", \
                                    401,\
                                    "Access-Token is no longer valid, user logged out or token expired")
    user.creation_date = datetime.datetime.now()
    db_session.commit()
    return build_response("", \
                        200,\
                        "Request provided is valid")

@authorization.route("/logout", methods = ['GET'])
def logout():
    if 'redirect_url' in request.args:
        referrer = request.args.get('redirect_url')
    else:
        referrer = request.referrer
    if 'Access-Token' not in request.headers and 'access_token' not in request.args:
        return build_html_error_response("Missing authentication", \
                                    400,\
                                    "Access-Token header not present in the request")
    if 'Access-Token' not in request.headers:
        access_token = request.args.get('access_token')
    else:
        access_token = request.headers.get('Access-Token')
    user = Users.query.filter_by(access_token=access_token).first()
    if user == None:
        return build_html_error_response("Invalid authentication", \
                                    401,\
                                    "Access-Token is invalid for this service")
    user.token_valid = False
    db_session.commit()

    return render_template("logout.html", referrer=referrer.split('?')[0], email=user.email)

def build_response(data, status, desc):
    jd = {"status_code:" : status, "error": "", "description": desc, "data": data}
    resp = Response(response=json.dumps(jd), status=status, mimetype="application/json")
    return resp

def build_error_response(error_title, status, error_desc):
    jd = {"status_code:" : status, "error": error_title, "description": error_desc, "data": ""}
    resp = Response(response=json.dumps(jd), status=status, mimetype="application/json")
    return resp

def build_html_error_response(error_title, status, error_desc):
    jd = {"status_code:" : status, "error": error_title, "description": error_desc, "data": ""}
    resp = render_template("error.html", code=status, error_title=error_title, error_message=error_desc)
    return resp
################################################
