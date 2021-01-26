# coding: utf-8
import requests
import urllib.parse
from flask import Flask, jsonify, request, render_template
import base64
import json

app = Flask(__name__)


client_id = "0oa45gsxiVSEYyHUl5d6"
client_secret = "bQoef25j8ohIjcnLusY05kZY3e9HYNzWCgfLj3cj"

okta_domain = "dev-4633786.okta.com"
base_auth_link = f"https://{okta_domain}/oauth2/default/v1"


def get_login_redirect_url(app_host):
	return f"http://{app_host}/authorization-code/callback"


def get_logout_redirect_url(app_host):
	return f"http://{app_host}/"


def get_login_url(app_host):
	return f"{base_auth_link}/authorize?" + urllib.parse.urlencode({
		"client_id": client_id,
		"response_type": "code",
		"scope": ",".join(["openid"]),
		"redirect_uri": get_login_redirect_url(app_host),
		"state": "12345",
	})


def get_logout_url(app_host, id_token):
	return f"{base_auth_link}/logout?" + urllib.parse.urlencode({
		"client_id": client_id,
		"id_token_hint": id_token,
		"post_logout_redirect_uri": get_logout_redirect_url(app_host),
	})


# Hooks docs
# https://developer.okta.com/docs/reference/token-hook/


@app.template_filter('jsonify')
def jsonify_filter(s):
	return json.dumps(s, indent=4)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def _default(path):
	return render_template("login.jinja2", **{
		"login_url": get_login_url(request.host)
	})


def request_token_by_code_and_client_id_and_client_secret(code, redirect_uri):
	client_id_with_secret = client_id + ':' + client_secret
	basic_auth = base64.b64encode(client_id_with_secret.encode("utf8")).decode("utf8")
	response = requests.post(
		f"{base_auth_link}/token",
		headers={
			"authorization": f"Basic {basic_auth}",
		},
		data={
			"grant_type": "authorization_code",
			"redirect_uri": redirect_uri,
			"code": code,
		}
	)
	return response.json()


def get_claims_from_token(access_token):
	header, payload, signature = access_token.split(".")
	dat = payload + '=' * (-len(payload) % 4)
	claims = base64.b64decode(dat.encode("utf8")).decode("utf8")
	return json.loads(claims)


@app.route('/authorization-code/callback')
def authorization_code_callback():
	code = request.args.get('code')
	if code is None:
		return "Please use this route only for redirect from OKTA."

	token_response = request_token_by_code_and_client_id_and_client_secret(code, get_login_redirect_url(request.host))
	if "access_token" in token_response:
		decoded_id_token = get_claims_from_token(token_response["id_token"])
		decoded_access_token = get_claims_from_token(token_response["access_token"])
		return render_template(
			"authorized.jinja2",
			logout_url=get_logout_url(request.host, token_response["id_token"]),
			token_response=token_response,
			decoded_id_token=decoded_id_token,
			decoded_access_token=decoded_access_token,
		)
	return jsonify(token_response)


if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=8080)