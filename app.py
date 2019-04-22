import os
import sys
import json
from flask import Flask, request, abort

err1 = {"message": "Account creation failed", "cause": "required user_id and password"}

app = Flask(__name__)


@app.route("/")
def return404():
    abort(404)
#def hello_world():
#    return "hello world!"

@app.route("/signup", methods=['POST'])
def callback():
    l = request.json

    if "user_id" not in l or "" not in l:
        abort(400, err1)
    return str(l)


if __name__ == "__main__":
    app.run()