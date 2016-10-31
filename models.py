
import datetime
import uuid
import os
import base64
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from db import Base


class UsersRating(Base):
    __tablename__ = 'users_rating'

    uid = Column(String, primary_key=True)
    rating_total = Column(Float, default=0)
    rating_given = Column(Float, default=0)
    rating_given_count = Column(Integer, default=0)
    rating_received = Column(Float, default=0)
    rating_received_count = Column(Integer, default=0)

    def __init__(self, uid, rating_total, rating_given, rating_given_count, rating_received, rating_received_count):
        self.uid = uid
        self.rating_total = rating_total
        self.rating_given = rating_given
        self.rating_given_count = rating_given_count
        self.rating_received = rating_received
        self.rating_received_count = rating_received_count

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'uid': self.uid,
            'rating_total': self.rating_total,
            'rating_given': self.rating_given,
            'rating_given_count': self.rating_given_count,
            'rating_received': self.rating_received,
            'rating_received_count': self.rating_received_count,
        }


class Ratings(Base):
    __tablename__ = 'ratings'

    uid = Column(String, primary_key=True)
    user_id_source = Column(String, ForeignKey('users_rating.uid'))
    user_id_destination = Column(String, ForeignKey('users_rating.uid'))
    rating = Column(Integer)
    message = Column(String, default="Without Message")
    creation_date = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, uid, user_id_source, user_id_destination, rating, message, creation_date):
        self.uid = uid
        self.user_id_source = user_id_source
        self.user_id_destination = user_id_destination
        self.rating = rating
        self.message = message
        self.creation_date = creation_date

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'uid': self.uid,
            'user_id_source': self.user_id_source,
            'user_id_destination': self.user_id_destination,
            'rating': self.rating,
            'message': self.message,
            'creation_date': self.creation_date
        }
