import os
import sys
from flask import Flask, request, abort

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

# 環境変数からchannel_secret・channel_access_tokenを取得
channel_secret = 'f0c75eb6d5f5d8775ac3a4c4c1e5d1b5'
channel_access_token = 'PEtbobZiK/ek6VlUsdkhYdbvEDWgx6VZmkDJUS8oaszqOPm0MbFYVz6uCvbD8U8A3FBK7fx73Zqx3xbWKPR71cIUb/aIcPbzZDT3TxnYf2AR3gDryB36Oza47XzwrTwRzoSfbVSjiP3WSvXf+jT38AdB04t89/1O/w1cDnyilFU='
#os.environ['LINE_CHANNEL_ACCESS_TOKEN']

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
    return "hello world!"

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
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run()