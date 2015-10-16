from datetime import datetime, timedelta
import time
import hashlib
import random
import string
from bson import ObjectId
from ming import schema as s
from ming.odm import FieldProperty, RelationProperty, ForeignIdProperty
from ming.odm.declarative import MappedClass
from tg import url
from tg.caching import cached_property
from tgext.pluggable import app_model
from tgext.pluggable.utils import mount_point
from googleplusauth.model import DBSession
from pymongo.errors import DuplicateKeyError


class GoogleAuth(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'googleplusauth_info'
        indexes = [(('activated', ), ('code', ))]

    _id = FieldProperty(s.ObjectId)
    registered = FieldProperty(s.Bool, if_missing=False)
    just_connected = FieldProperty(s.Bool, if_missing=False)
    profile_picture = FieldProperty(s.String)

    _user_id = ForeignIdProperty(s.ObjectId)
    user = RelationProperty('User')

    google_id = FieldProperty(s.String, required=True)
    access_token = FieldProperty(s.String, required=True)
    access_token_expiry = FieldProperty(s.DateTime, required=True)

    @classmethod
    def user_by_google_id(cls, google_id):
        google_auth = DBSession.query(cls).filter_by(google_id=google_id).first()
        if not google_auth:
            return None
        return google_auth.user
