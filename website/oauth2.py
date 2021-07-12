from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from .models import Client, Token, User
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7009 import RevocationEndpoint
from authlib.oauth2.rfc6750 import BearerTokenValidator
from mongoengine import *
import time

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
        # q = Token.query.filter_by(client_id=client.client_id)
        if token_type_hint == 'access_token':
            return q.filter(access_token__exact = token).first()
            #return q.filter_by(access_token=token).first()
        elif token_type_hint == 'refresh_token':
            return q.filter(refresh_token__exact = token).first()
            # return q.filter_by(refresh_token=token).first()
        # without token_type_hint
        # item = q.filter_by(access_token=token).first()
        item = q.filter(access_token__exact=token).first()
        if item:
            return item
        return q.filter(refresh_token__exact=token).first()
        # return q.filter_by(refresh_token=token).first()

    def revoke_token(self, token):
        token.revoked = True
        revoke_token = Token(**token)
        revoke_token.save()
        #db.session.add(token)
        #db.session.commit()


def query_client(client_id):
    client = Client.objects.filter(client_id__exact=client_id).first()
    return client

def save_token(token_data, request):
    print(request)
    if request.user:
        user_id = request.user.get_user_id()
    else:
        # client_credentials grant_type
        user_id = request.client.user_id
        # or, depending on how you treat client_credentials
        # user_id = None
    #client_id = request.client.client_id,
    client_id = '1NvO1d5Z8bSmjz9bQXaktXYh'
    user_id = '60e8652b9ac397d1b4b19e56'
    print('the token data is', token_data)
    print('the user id is', user_id)
    print('the client id is', client_id)
    created_at = int(time.time())
    token = Token(
        #client_id=request.client.client_id,
        created_at=created_at,
        client_id=client_id,
        user_id=user_id,
        # ** significa que puede ser un numero indefinido de pares de valores
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

# define the grant we want
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
