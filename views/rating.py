
import sys
import os
import datetime
import json
import uuid
import urllib
from rauth import *
from flask_restful import Api, Resource
from flask import request, render_template, redirect, Response, url_for, Blueprint, session

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from settings import *
from db import db_session
from models import UsersRating, Ratings

rating = Blueprint('rating', __name__)

import logging
logging.basicConfig(stream=sys.stderr)
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger()


@rating.route("/", methods = ['POST'])
def create():
    if request.form["dest_id"] is None or request.form["source_id"] is None or request.form["rating"] is None:
        return build_error_response("Invalid Parameters", 400,
                                    "Destination ID, Source ID or Rating not present in the request")

    if request.form["rating"] < 1 or request.form["rating"] > 5:
        return build_error_response("Invalid Rating Values", 400,
                                    "Rating value should be between 1 and 5")

    dest_id = request.form["dest_id"]
    source_id = request.form["source_id"]
    rating = request.form["rating"]
    rate_id = uuid.uuid4()

    if request.form["message"] is not None:
        message = request.form["message"]
        rate = Ratings(uid=rate_id, user_id_source=source_id, user_id_destination=dest_id, rating=rating,
                       message=message)
    else:
        rate = Ratings(uid=rate_id, user_id_source=source_id, user_id_destination=dest_id, rating=rating)

    db_session.add(rate)
    if UsersRating.query.filter_by(uid=dest_id).count() < 1:
        rating_received = (rating*100)/5
        rating_received_count = 1
        user_dest = UsersRating(uid=dest_id, rating_received=rating_received,
                                rating_received_count=rating_received_count, rating_total=rating_received)
        db_session.add(user_dest)
        db_session.commit()
    else:
        user = UsersRating.query.filter_by(uid=dest_id).first()
        rating_received = (rating * 100)/5
        user.rating_received = ((user.rating_received*user.rating_received_count) + rating_received) / \
                               (user.rating_received_count + 1)

        user.rating_total = (((user.rating_received*user.rating_received_count) + rating_received) +
                             (user.rating_given*user.rating_given_count)) / \
                            (user.rating_given_count + user.rating_received_count + 1)

        user.rating_received_count += 1
        db_session.commit()

    if UsersRating.query.filter_by(uid=source_id).count() < 1:
        rating_given = (rating * 100) / 5
        rating_given_count = 1
        user_source = UsersRating(uid=dest_id, rating_given=rating_given,
                                  rating_given_count=rating_given_count, rating_total=rating_received)
        db_session.add(user_source)
        db_session.commit()
    else:
        user = UsersRating.query.filter_by(uid=source_id).first()
        rating_given = (rating * 100) / 5
        user.rating_given = ((user.rating_given * user.rating_given_count) + rating_given) / \
                               (user.rating_given_count + 1)

        user.rating_total = (((user.rating_given * user.rating_given_count) + rating_given) +
                             (user.rating_received * user.rating_received_count)) / \
                            (user.rating_given_count + user.rating_received_count + 1)

        user.rating_given_count += 1
        db_session.commit()

    return build_response("Rate Done", 200, "Rate has been done successfully")


@rating.route("/rate", methods = ['POST'])
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
