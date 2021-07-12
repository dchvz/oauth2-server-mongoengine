import time
from flask import Blueprint, request, session, url_for
from flask import render_template, redirect, jsonify
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from .models import User, Client
from .oauth2 import server, require_oauth
import bson

bp = Blueprint('home', __name__)

def split_by_crlf(s):
    return [v for v in s.splitlines() if v]

def current_user():
    """ if 'id' in session:
        uid = session['id']
        return User.objects.get(username =='marcus')
    return None """
    return User.objects.get(username = 'marcus')

@bp.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.objects.filter(username__exact=username).first()
        print('no user seems to have been found')
        if not user:
            user = User(username=username)
            user.save()
        print('we are here')
        print('we are past the register')
        # if user is not just to log in, but need to head back to the auth page, then go for it
        next_page = request.args.get('next')
        print('about to go to next page')
        if next_page:
            return redirect(next_page)
        return redirect('/')
    user = current_user()
    print('the current user is', user)
    if user:
        print('the cient info')
        clients = Client.objects.filter(user_id__exact='60e8652b9ac397d1b4b19e56')
    else:
        clients = []
    print('about to make a return statement')
    return render_template('home.html', user=user, clients=clients)

# this example is only used for the code authorization grant
@bp.route('oauth/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    # if user log status is not true (Auth server), then to log it in
    if not user:
        return redirect(url_for('website.routes.home', next=request.url))
    if request.method == 'GET':
        try:
            grant = server.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.objects.filter(username__exact=username).first()
    if request.form['confirm']:
        grant_user = user
    else:
        grant_user = None
    return server.create_authorization_response(grant_user=grant_user)

@bp.route('/logout')
def logout():
    del session['id']
    return redirect('/')

@bp.route('/create-client', methods=['GET','POST'])
def create_client():
    print('about to create client')
    print('the form values are', request.form)
    print('after create client')
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')

    form = request.form
    print('the form values are', form)
    client_id_issued_at = int(time.time())
    client_id = gen_salt(24)
    client = Client(
        user_id = '60e8652b9ac397d1b4b19e56',
        client_id = client_id,
        client_id_issued_at = client_id_issued_at,
        client_name = form['client_name'],
        default_redirect_uri = form['redirect_uri'],
        scope = form['scope'],
        allowed_grant_types = split_by_crlf(form["grant_type"]),
        allowed_redirect_uris =split_by_crlf(form["redirect_uri"]),
        allowed_response_types = split_by_crlf(form["response_type"]),
        token_endpoint_auth_method = form['token_endpoint_auth_method'],
    )
    print('we are here after getting client data')
    if form['token_endpoint_auth_method'] == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)
    # TODO CHECK if scope is a list or what, it should be a lsit
    client.save()
    return redirect('/')

@bp.route('/create-user', methods=['GET','POST'])
def create_user():
    form = request.json
    user = User(
        name = form["username"]
    )
    user.save()
    return jsonify('user was successfully saved')


@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    return server.create_token_response()


@bp.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return server.create_endpoint_response('revocation')


@bp.route('/api/me')
@require_oauth('profile')
def api_me():
    # TODO think of a method to obtain the current token for the current user
    #user = current_token.user
    user_id = '60e8652b9ac397d1b4b19e56'
    user_username = 'marcus'
    #return jsonify(id=user.id, username=user.username)
    return jsonify(id=user_id, username=user_username)

@bp.route('hello')
def hello():
    return jsonify('hello')