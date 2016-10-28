
import datetime
import uuid
import os
import base64
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from db import Base


class Users(Base):
    __tablename__ = 'users'

    # Oauth fields
    uid = Column(String, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    picture_url = Column(String)
    platform = Column(String)

    def __init__(self, uid, email, name, picture, platform):
        self.uid = uid
        self.email = email
        self.name = name
        self.picture_url = picture
        self.platform = platform

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'uid': self.uid,
            'name': self.name,
            'email': self.email,
            'picture_url': self.picture_url,
            'platform': self.platform,
        }
