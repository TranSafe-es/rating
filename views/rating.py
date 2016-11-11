
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


@rating.route("/", methods=['POST'])
def create():
    if request.form["dest_id"] is None or request.form["source_id"] is None or request.form["rating"] is None:
        return build_error_response("Invalid Parameters", 400,
                                    "Destination ID, Source ID or Rating not present in the request")

    if int(request.form["rating"]) < 1 or int(request.form["rating"]) > 5:
        return build_error_response("Invalid Rating Values", 400,
                                    "Rating value should be between 1 and 5")

    dest_id = request.form["dest_id"]
    source_id = request.form["source_id"]
    rate_value = int(request.form["rating"])
    rate_id = uuid.uuid4()

    if UsersRating.query.filter_by(uid=dest_id).count() < 1:
        rating_received = (rate_value*100)/5
        rating_received_count = 1
        user_dest = UsersRating(uid=dest_id, rating_received=rating_received,
                                rating_received_count=rating_received_count, rating_total=rating_received)
        db_session.add(user_dest)
        db_session.commit()
    else:
        user = UsersRating.query.filter_by(uid=dest_id).first()
        rating_received = (rate_value * 100)/5
        user.rating_received = ((user.rating_received*user.rating_received_count) + rating_received) / \
                               (user.rating_received_count + 1)

        user.rating_total = (((user.rating_received*user.rating_received_count) + rating_received) +
                             (user.rating_given*user.rating_given_count)) / \
                            (user.rating_given_count + user.rating_received_count + 1)

        user.rating_received_count += 1
        db_session.commit()

    if UsersRating.query.filter_by(uid=source_id).count() < 1:
        rating_given = (rate_value * 100) / 5
        rating_given_count = 1
        user_source = UsersRating(uid=source_id, rating_given=rating_given,
                                  rating_given_count=rating_given_count, rating_total=rating_received)
        db_session.add(user_source)
        db_session.commit()
    else:
        user = UsersRating.query.filter_by(uid=source_id).first()
        rating_given = (rate_value * 100) / 5
        user.rating_given = ((user.rating_given * user.rating_given_count) + rating_given) / \
                            (user.rating_given_count + 1)

        user.rating_total = (((user.rating_given * user.rating_given_count) + rating_given) +
                             (user.rating_received * user.rating_received_count)) / \
                            (user.rating_given_count + user.rating_received_count + 1)

        user.rating_given_count += 1
        db_session.commit()

    if request.form["message"] is not None:
        message = request.form["message"]
        rate = Ratings(uid=rate_id, user_id_source=source_id, user_id_destination=dest_id, rating=rate_value,
                       message=message)
    else:
        rate = Ratings(uid=rate_id, user_id_source=source_id, user_id_destination=dest_id, rating=rate_value)

    db_session.add(rate)
    db_session.commit()

    return build_response("Rate Done", 200, "Rate has been done successfully")


@rating.route("/<uid>/", methods=['GET'])
def get_rating(uid):
    fields_available = ["uid", "user_id_source", "user_id_destination", "rating", "message", "creation_date"]
    rating_type = "received"
    size = 5
    fields = ["rating"]
    if "rating" in request.args:
        if request.args.get("rating") not in ["received", "given", "all"]:
            return build_error_response("Invalid rating parameter", 400,
                                        "Rating argument should be received, given or all")
        rating_type = request.args.get("rating")

    if "size" in request.args:
        print request.args.get("size")
        if not request.args.get("size").isdigit() and request.args.get("size") != "all":
            return build_error_response("Invalid size parameter", 400,
                                        "Size argument should be a number or all")
        try:
            size = int(request.args.get("size"))
        except:
            size = request.args.get("size")

    if "fields" in request.args:
        fields_requested = request.args.get("fields").split(",")
        if False if [x in fields_available for x in fields_requested] else True:
            return build_error_response("Invalid fields parameter", 400,
                                        "Fields argument contains an invalid field")
        fields = fields_requested

    try:
        data = UsersRating.query.filter_by(uid=uid).first().serialize(fields=fields, size=size, rating_type=rating_type)
    except:
        user_dest = UsersRating(uid=uid)
        db_session.add(user_dest)
        try:
            db_session.commit()
        except:
            db_session.rollback()
        data = UsersRating.query.filter_by(uid=uid).first().serialize(fields=fields, size=size, rating_type=rating_type)
    return build_response(data, 200, "Rating successfully retrieved.")


def build_response(data, status, desc):
    jd = {"status_code:": status, "error": "", "description": desc, "data": data}
    resp = Response(response=json.dumps(jd), status=status, mimetype="application/json")
    return resp


def build_error_response(error_title, status, error_desc):
    jd = {"status_code:": status, "error": error_title, "description": error_desc, "data": ""}
    resp = Response(response=json.dumps(jd), status=status, mimetype="application/json")
    return resp


def build_html_error_response(error_title, status, error_desc):
    jd = {"status_code:": status, "error": error_title, "description": error_desc, "data": ""}
    resp = render_template("error.html", code=status, error_title=error_title, error_message=error_desc)
    return resp
################################################
