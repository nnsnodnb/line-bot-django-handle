from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, FollowEvent, UnfollowEvent, TextMessage,
    ButtonsTemplate, TemplateSendMessage, TextSendMessage,
    MessageTemplateAction, PostbackTemplateAction, URITemplateAction,
)
from . import line_bot_api, handler

import re

buttonRegex = re.compile('(ボタン|ぼたん)')


class CallbackView(View):

    def post(self, request, *args, **kwargs):
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseBadRequest()

        return HttpResponse('OK')

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CallbackView, self).dispatch(*args, **kwargs)

    @staticmethod
    @handler.add(FollowEvent)
    # https://developers.line.me/en/docs/messaging-api/reference/#follow-event
    def follow_event(event):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage('Follow Event')
        )

    @staticmethod
    @handler.add(UnfollowEvent)
    # https://developers.line.me/en/docs/messaging-api/reference/#unfollow-event
    def unfollow_event(event):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage('Unfollow Event')
        )

    @staticmethod
    @handler.add(MessageEvent, message=TextMessage)
    def message_event(event):
        if buttonRegex.search(event.message.text):
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        thumbnail_image_url='https://example.com/image.jpg',
                        title='Menu',
                        text='Please select',
                        actions=[
                            PostbackTemplateAction(
                                label='postback',
                                text='postback text',
                                data='action=buy&itemid=1'
                            ),
                            MessageTemplateAction(
                                label='message',
                                text='message text'
                            ),
                            URITemplateAction(
                                label='uri',
                                uri='http://example.com/'
                            )
                        ]
                    )
                )
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text)
            )
