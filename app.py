import os
import sys
import json
from flask import Flask, request, abort, jsonify


users = []

app = Flask(__name__)

@app.route("/")
def return404():
    abort(404)
#def hello_world():
#    return "hello world!"

@app.route("/signup", methods=['POST'])
def signup():
    l = request.json

    mes = {
        "message": "Account creation failed",
        "cause": "required user_id and password"
        }

    if l == []:
        return jsonify(mes), 400
    if "user_id" not in l or "password" not in l:
        return jsonify(mes), 400
    
    for u in users:
        if u["user_id"] == l["user_id"]:
            mes = {
                "message": "Account creation failed",
                "cause": "already same user_id is used"
            }
            return jsonify(mes), 400

    users.append(l)

    mes = {
        "message": "Account successfully created",
        "user": {
            "user_id": l["user_id"],
            "nickname": l["user_id"]
        }
    }
    return jsonify(mes), 200

@app.route("/users/<userid>", methods=['GET'])
def getuser(userid):
    return userid



if __name__ == "__main__":
    app.run()