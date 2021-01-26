# coding: utf-8
import requests
import urllib.parse
from flask import Flask, jsonify, request, render_template
import base64
import json

app = Flask(__name__)


users = {
	"admin@admin.com": "ADMIN CLAIM",
	"admin1@admin.com": "ADMIN 1 CLAIM",
	"admin2@admin.com": "ADMIN 2 CLAIM",
}


@app.route('/hook-test', methods=["POST"])
def hook_test():
	data = request.get_json()
	user_email = data["data"]["context"]["session"]["login"]
	user_data = users.get(user_email)
	return jsonify({
		"commands": [
			{
				"type": "com.okta.access.patch",
				"value": [
					{
						"op": "add",
						"path": "/claims/HOOK_CUSTOM_ACCESS_1",
						"value": user_data
					}
				]
			},
			{
				"type": "com.okta.identity.patch",
				"value": [
					{
						"op": "add",
						"path": "/claims/HOOK_CUSTOM_ID_1",
						"value": user_data
					}
				]
			},
		]
	})


if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=8081)
