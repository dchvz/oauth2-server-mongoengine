from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from .models import Client, Token, User
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7009 import RevocationEndpoint
from authlib.oauth2.rfc6750 import BearerTokenValidator
from mongoengine import *
import time
from pprint import pprint

connect('test')

class MyBearerTokenValidator(BearerTokenValidator):
    def authenticate_token(self, token_string):
        return Token.objects.filter(access_token__exact=token_string).first()

    def request_invalid(self, request):
        return False

    def token_revoked(self, token):
        return token.revoked

class MyRevocationEndpoint(RevocationEndpoint):
    def query_token(self, token, token_type_hint, client):
        q = Token.objects.filter(client_id__exact=client.client_id)
        if token_type_hint == 'access_token':
            return q.filter(access_token__exact = token).first()
        elif token_type_hint == 'refresh_token':
            return q.filter(refresh_token__exact = token).first()
        item = q.filter(access_token__exact=token).first()
        if item:
            return item
        return q.filter(refresh_token__exact=token).first()

    def revoke_token(self, token):
        token.revoked = True
        revoke_token = Token(**token.asdict())
        revoke_token.save()

def query_client(client_id):
    client = Client.objects.filter(client_id__exact=client_id).first()
    return client

def save_token(token_data, request):
    if request.user:
        user_id = request.user.get_user_id()
    else:
        # client_credentials grant_type
        user_id = request.client.user_id
        # or, depending on how you treat client_credentials
        # user_id = None
    client_id = request.client.client_id,
    # TODO review why the client_id is giving back a tuple and not an string
    created_at = int(time.time())
    token = Token(
        created_at=created_at,
        client_id=client_id[0],
        user_id=user_id,
        **token_data
    )
    token.save()

server = AuthorizationServer(
    query_client=query_client,
    save_token=save_token,
)

class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        user = User.objects.filter(username__exact=username).first()
        if user is not None and user.check_password(password):
            return user

class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic', 'client_secret_post'
    ]

require_oauth = ResourceProtector()

def config_oauth(app):
    server.init_app(app)
    # register grants
    server.register_grant(ClientCredentialsGrant)
    server.register_grant(PasswordGrant)
    # register revocation endpoint
    server.register_endpoint(MyRevocationEndpoint)
    # only bearer token is supported currently
    require_oauth.register_token_validator(MyBearerTokenValidator())
