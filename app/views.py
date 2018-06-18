from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    AccountLinkEvent, MessageEvent, FollowEvent, UnfollowEvent,
    TextMessage,
    ButtonsTemplate, TemplateSendMessage, TextSendMessage,
    MessageTemplateAction, PostbackTemplateAction, URITemplateAction,
)
from . import line_bot_api, handler

import re
import requests
import uuid

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
    @handler.add(AccountLinkEvent)
    def account_link_event(event):
        if event.link.result == 'ok':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage('Account Link success.')
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
        elif event.message.text == 'アカウント連携':
            response = requests.post(f'https://api.line.me/v2/bot/user/{event.source.user_id}/linkToken',
                                     headers=line_bot_api.headers).json()
            if 'linkToken' not in response:
                return

            link_token = response['linkToken']
            nonce = str(uuid.uuid4())
            success_link = f'https://access.line.me/dialog/bot/accountLink?linkToken={link_token}&nonce={nonce}'

            # デモ用なので連携できたとします
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=f'こちらにアクセスしてログインしてください\n'
                                         f'https://example.com/link?linkToken={link_token}'),
                    TextSendMessage(f'連携成功時のリンク\n{success_link}')
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text)
            )
