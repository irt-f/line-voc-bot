import os
import sys
from flask import Flask, request, abort



app = Flask(__name__)


@app.route("/")
def return404():
    abort(404)
#def hello_world():
#    return "hello world!"

@app.route("/signup", methods=['POST'])
def callback():
    l = request.json

    return 'OK'


if __name__ == "__main__":
    app.run()