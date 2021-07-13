# OAuth 2.0 Provider with Flask & MongoDB

This is an example of OAuth 2.0 server in [Authlib](https://authlib.org/) that uses mongoengine as the database

- Documentation: <https://docs.authlib.org/en/latest/flask/2/>
- Authlib Repo: <https://github.com/lepture/authlib>

## Take a quick look

This is a ready to run example, let's take a quick experience at first. To
run the example, we need to install all the dependencies:

```bash
$ pip install -r requirements.txt
```

Set Flask and Authlib environment variables:

```bash
# disable check https (DO NOT SET THIS IN PRODUCTION)
$ export AUTHLIB_INSECURE_TRANSPORT=1
```

Now, you can open your browser with `http://127.0.0.1:5000/`, login with any
name you want.

Before testing, we need to create a client:

![create a client](https://user-images.githubusercontent.com/290496/38811988-081814d4-41c6-11e8-88e1-cb6c25a6f82e.png)

### Password flow example

Get your `client_id` and `client_secret` for testing. In this example, we
have enabled `password` grant types, let's try:

```
$ curl -u ${client_id}:${client_secret} -XPOST http://127.0.0.1:5000/oauth/token -F grant_type=password -F username=${username} -F password=valid -F scope=profile
```

Because this is an example, every user's password is `valid`. Now you can access `/api/me`:

```bash
$ curl -H "Authorization: Bearer ${access_token}" http://127.0.0.1:5000/api/me
```

### Authorization code flow example

To test the authorization code flow, you can just open this URL in your browser.
```bash
$ open http://127.0.0.1:5000/oauth/authorize?response_type=code&client_id=${client_id}&scope=profile
```

After granting the authorization, you should be redirected to `${redirect_uri}/?code=${code}`

Then your app can send the code to the authorization server to get an access token:

```bash
$ curl -u ${client_id}:${client_secret} -XPOST http://127.0.0.1:5000/oauth/token -F grant_type=authorization_code -F scope=profile -F code=${code}
```

Now you can access `/api/me`:

```bash
$ curl -H "Authorization: Bearer ${access_token}" http://127.0.0.1:5000/api/me
```

## POSTMAN's requests

You may import the postman's request from request_examples folder to make use of this project. You can do so like this https://kb.datamotion.com/?ht_kb=postman-instructions-for-exporting-and-importing

For now, you can read the source in example or follow the long boring tutorial below.

**IMPORTANT**: To test implicit grant, you need to `token_endpoint_auth_method` to `none`.
