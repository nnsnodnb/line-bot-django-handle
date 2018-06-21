from django.http.response import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    AccountLinkEvent, MessageEvent, FollowEvent, UnfollowEvent, PostbackEvent,
    ImagemapSendMessage, TextMessage,
    ButtonsTemplate, TemplateSendMessage, TextSendMessage,
    MessageTemplateAction, PostbackTemplateAction, URITemplateAction, URIImagemapAction,
    BaseSize, ImagemapArea,
)
from urllib import parse
from . import line_bot_api, handler, demo_image_url

import re
import requests

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
            # nonceを使ってQuery後、Userの紐づけ
            user_id = event.source.user_id
            nonce = event.link.nonce
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage('Account Link success.')
            )

    @staticmethod
    @handler.add(PostbackEvent)
    def postback_event(event):
        data = dict(parse.parse_qsl(parse.urlsplit(event.postback.data).path))
        if data['action'] == 'buy':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage('Postback received.')
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
                        thumbnail_image_url=demo_image_url,
                        title='Menu',
                        text='Please select',
                        actions=[
                            PostbackTemplateAction(
                                label='postback',
                                displayText='postback text',
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

            url = f'http://10.0.1.2:8000{reverse("accounts:line_login_view")}' \
                  f'?link_token={link_token}'

            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImagemapSendMessage(
                        base_url='https://dl.nnsnodnb.moe/line_sample',
                        alt_text='ImageMap sample.',
                        base_size=BaseSize(width=1040, height=520),
                        actions=[
                            URIImagemapAction(
                                link_uri=url,
                                area=ImagemapArea(
                                    x=0, y=0, width=1040, height=520
                                )
                            )
                        ]
                    ),
                    TextSendMessage(f'連携解除機能の提供及び連携解除機能のユーザへの通知'),
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text)
            )
