import os
import sys
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, word, user_id):
        self.word = word
        self.user_id = user_id
    
    def __repr__(self):
        return '<Word %r>' % self.word

# 環境変数からchannel_secret・channel_access_tokenを取得
channel_secret = 'f0c75eb6d5f5d8775ac3a4c4c1e5d1b5'
channel_access_token = 'PEtbobZiK/ek6VlUsdkhYdbvEDWgx6VZmkDJUS8oaszqOPm0MbFYVz6uCvbD8U8A3FBK7fx73Zqx3xbWKPR71cIUb/aIcPbzZDT3TxnYf2AR3gDryB36Oza47XzwrTwRzoSfbVSjiP3WSvXf+jT38AdB04t89/1O/w1cDnyilFU='
#os.environ['CHANNEL_ACCESS_TOKEN']


if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/")
def hello_world():
    name = 'Abe Harukasu'
    email = 'hoge@hoge.com'
    reg = User(name, email)
    db.session.add(reg)
    db.session.commit()
    return User.query.all()

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == "単語登録":
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text="登録したい単語を教えて！"))
    else:
#        if voc_add:
#            voc_add = False
#            voc_list.append(text)
#            line_bot_api.reply_message(
#                event.reply_token,
#                TextSendMessage(text=text + "を追加しました！"))
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run()