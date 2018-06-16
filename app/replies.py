from linebot.models import MessageEvent, TextMessage, TextSendMessage
from . import line_bot_api, handler


@handler.add(MessageEvent, message=TextMessage)
def message_event(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(event.message.text)
    )
