from flask import Flask, request, abort
from werkzeug import exceptions
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
import wikipedia

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

wikipedia.set_lang("ja")

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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    send_message = event.message.text
    try:
        wikipedia_page = wikipedia.page(send_message)
        wikipedia_title=wikipedia_page.title
        wikipedia_url=wikipedia_page.url
        wikipedia_summary=wikipedia.summary(send_message)
        reply_message = '【' + wikipedia_title + '】\n' + wikipedia_summary + '\n\n' + '【詳しくはこちら】\n' + wikipedia_url

    except wikipedia.exceptions.PageError:
        reply_message ='【' + send_message + '】\nについての情報は見つかりませんでした。'

    except wikipedia.exceptions.DisambiguationError as e:
        disambiguation_list = e.options
        reply_message = '複数の候補が返ってきました。以下の候補から、お探しの用語に近いものを再入力してください。\n\n'
        for word in disambiguation_list:
            reply_message += '・' + word + '\n'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(reply_message)
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)