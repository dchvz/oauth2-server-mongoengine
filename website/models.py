from mongoengine import *
import json
import datetime
connect('test')
# This class contains the basic auth models for authlib to work: User, Client, Token and Authorization Code

def to_unicode(x, charset='utf-8', errors='strict'):
    if x is None or isinstance(x, str):
        return x
    if isinstance(x, bytes):
        return x.decode(charset, errors)
    return str(x)

def list_to_scope(scope):
    """Convert a list of scopes to a space separated string."""
    if isinstance(scope, (set, tuple, list)):
        return " ".join([to_unicode(s) for s in scope])
    if scope is None:
        return scope
    return to_unicode(scope)


def scope_to_list(scope):
    """Convert a space separated string to a list of scopes."""
    if isinstance(scope, (tuple, list, set)):
        return [to_unicode(s) for s in scope]
    elif scope is None:
        return None
    return scope.strip().split()


class User(Document):
    username = StringField(required=True, max_length=200)
    password = StringField(max_length=200)

    def get_user_id(self):
        return self.id

    def get_user_by_id(self, id):
        return self.objects.get(id = id)

    def check_password(self, password):
        return password == 'valid'


class Client(Document):
    client_id = StringField(required=True, unique=True)
    client_name = StringField(required=True)
    user_id = StringField(required=True)
    user = ReferenceField(User)
    client_secret = StringField(required=True, unique=True)
    token_endpoint_auth_method = StringField(required=True)
    client_id_issued_at = IntField()
    allowed_grant_types = ListField(StringField())
    allowed_redirect_uris = ListField(StringField())
    allowed_response_types = ListField(StringField())
    scope = StringField()
    default_redirect_uri = StringField()

    def check_client_secret(self, client_secret):
        return self.client_secret == client_secret

    def check_grant_type(self, grant_type):
        return grant_type in self.allowed_grant_types

    def check_redirect_uri(self, redirect_uri):
        return redirect_uri in self.allowed_redirect_uris

    def check_response_type(self, response_type):
        return response_type in self.allowed_response_types

    def check_token_endpoint_auth_method(self, method):
        return self.token_endpoint_auth_method == method

    def get_allowed_scope(self, scope):
        if not scope:
            return ''
        allowed = set(self.scope.split())
        scopes = scope_to_list(scope)
        return list_to_scope([s for s in scopes if s in allowed])

    def get_client_id(self):
        return self.client_id

    def get_default_redirect_uri(self):
        return self.default_redirect_uri

    def has_client_secret(self):
        return bool(self.client_secret)


class Token(Document):
    # access_token: a token to authorize the http requests.
    access_token = StringField()
    # (optional) a token to exchange a new access token
    refresh_token = StringField()
    # client_id: this token is issued to which client
    client_id = StringField(required=True)
    user_id = StringField(required=True)
    user = ReferenceField(User)
    # expires_at: when will this token expired
    created_at = IntField()
    expires_in = IntField()
    expires_at = IntField()
    # scope: a limited scope of resources that this token can access
    scope = StringField()
    revoked = BooleanField()
    token_type = StringField()

    def get_redirect_uri(self):
        return self.redirect_uri

    def get_scope(self):
        return self.scope

    def get_client_id(self):
        return self.client_id

    def get_expires_at(self):
        return self.created_at + self.expires_in

    def get_expires_in(self):
        return self.expires_in

class AuthorizationCode(Document):
    user_id = StringField(required=True, unique=True)
    meta = {'allow_inheritance': True}
