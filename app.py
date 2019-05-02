import os
import sys
import random

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

from search_dict import SearchDict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    line_id = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class RepSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry = db.Column(db.String(80), nullable=False)
    flag = db.Column(db.Boolean)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref=db.backref('rep_settings', lazy=True))

    def __repr__(self):
        return '<RepSetting %r>' % (str(self.user_id) + ':' + self.entry)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(120), nullable=False)
    meaning = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref=db.backref('words', lazy=True))
    
    def __repr__(self):
        return '<Word %r>' % self.word

# 環境変数からchannel_secret・channel_access_tokenを取得
channel_secret = os.environ['CHANNEL_SECRET']
channel_access_token = os.environ['CHANNEL_ACCESS_TOKEN']


if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

search_dict = SearchDict(
    search_url='http://public.dejizo.jp/NetDicV09.asmx/SearchDicItemLite',
    get_url='http://public.dejizo.jp/NetDicV09.asmx/GetDicItemLite')

@app.route('/')
def hello_world():
    #reg = User(name, email)
    #db.session.add(reg)
    #db.session.commit()
    return 'Hello World!'

@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    line_id = event.source.user_id
    profile = line_bot_api.get_profile(line_id)

    u = User.query.filter_by(line_id=line_id).first()
    if u == None:
        u = User(username=profile.display_name, line_id=line_id)
        db.session.add(u)
        db.session.commit()

    #settings = RepSetting.query.filter_by(user=u).all()
    q_r = RepSetting.query.filter_by(entry='word_registration', user=u).first()
    q_d = RepSetting.query.filter_by(entry='word_delete', user=u).first()
    q_da = RepSetting.query.filter_by(entry='word_delete_all', user=u).first()
    voc = Word.query.filter_by(user=u).all()
    voc_size = len(voc)

    if text == '単語登録':
        if q_d: 
            db.session.delete(q_d)
            db.session.commit()
        if not q_r:
            word_registration = RepSetting(entry='word_registration', user=u)
            db.session.add(word_registration)
            db.session.commit()

        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text='登録したい単語を教えてね\n（『キャンセル』と入力すると登録をキャンセルできます）'))
    
    elif text == '単語削除':

        if voc_size < 1:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='単語が登録されてないよ\nまずは『単語登録』と入力して単語を登録してね'))
        else:
            if q_r: 
                db.session.delete(q_r)
                db.session.commit()
            if not q_d:
                word_delete = RepSetting(entry='word_delete', user=u)
                db.session.add(word_delete)
                db.session.commit()

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='削除したい単語を教えてね\n（『キャンセル』と入力すると削除をキャンセルできます）'))
    
    elif text == '単語全削除':

        if voc_size < 1:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='単語が登録されてないよ\nまずは『単語登録』と入力して単語を登録してね'))
        else:
            if q_r: 
                db.session.delete(q_r)
                db.session.commit()
            if q_d:
                db.session.delete(q_d)
                db.session.commit()
            if not q_da:
                word_delete_all = RepSetting(entry='word_delete_all', user=u)
                db.session.add(word_delete_all)
                db.session.commit()

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='一旦すべての単語を削除すると元に戻せないよ\n本当に削除しますか？[はい/いいえ]'))
    
    elif text == 'テスト':
        word_list = Word.query.filter_by(user=u).all()
        size = len(word_list)
        if size == 0:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='単語が登録されてないよ\nまずは『単語登録』と入力して単語を登録してね'))
        else:
            question_number = min(size, 10)
            questions = random.sample(word_list, question_number)

            question_text = ''
            for i, question in enumerate(questions):
                if i > 0: question_text += '\n'
                question_text += 'Q %02d   %s' % (i+1, question.word)
        
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=question_text))


    else:
        w = Word.query.filter_by(word=text, user=u).first()

        if q_r != None:
            if text == 'キャンセル':
                db.session.delete(q_r)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='単語帳への登録をキャンセルしました'))

            elif w == None:
                db.session.delete(q_r)

                result = search_dict.search_and_get(text)
                if result == '':
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=text + 'の意味を英和辞書から見つけられませんでした'))
                else:
                    lines = result.split('\t')
                    lines = lines[:min(3, len(result))]
                    result=''
                    for i, line in enumerate(lines):
                        if i > 0: result += '\n'
                        result += line

                    w = Word(word=text, user=u, meaning=result)
                    db.session.add(w)
                    db.session.commit()

                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text='単語名\n%s\n\n意味\n%s\n\nを単語帳に追加しました！' % (text, result)))
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text + 'はすでに単語帳に登録されています'))

        elif q_d != None:
            if text == 'キャンセル':
                db.session.delete(q_d)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='単語帳からの削除をキャンセルしました'))
            elif w != None:
                db.session.delete(q_d)
                db.session.delete(w)
                db.session.commit()

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text + 'を単語帳から削除しました'))
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text + 'は単語帳に登録されていません'))

        elif q_da != None:
            db.session.delete(q_da)
            db.session.commit()
            if text=='はい':
                for v in voc:
                    db.session.delete(v)
                db.session.commit()

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='すべての単語を単語帳から削除しました'))
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='全削除をキャンセルしました'))

        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text))
    
    

if __name__ == "__main__":
    app.run()