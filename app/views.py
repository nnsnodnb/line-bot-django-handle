from accounts.errors import LineAccountInactiveError
from accounts.models import Line
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    AccountLinkEvent, MessageEvent, FollowEvent, UnfollowEvent, PostbackEvent,
    ImagemapSendMessage, TextMessage,
    ButtonsTemplate, ConfirmTemplate, TemplateSendMessage, TextSendMessage,
    MessageTemplateAction, PostbackTemplateAction, PostbackAction, URITemplateAction, URIImagemapAction,
    BaseSize, ImagemapArea,
)
from urllib import parse
from . import line_bot_api, handler, demo_image_url
from .models import Nonce

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
            user_id = event.source.user_id
            profile = line_bot_api.get_profile(user_id)

            nonce = Nonce.objects.select_related('user').get(pk=event.link.nonce)
            try:
                line = Line.objects.get(pk=profile.user_id)
                line.is_active = True
                line.save()
            except Line.DoesNotExist:
                Line.objects.create(user_id=profile.user_id, display_name=profile.display_name,
                                    picture_url=profile.picture_url, status_message=profile.status_message,
                                    service_user=nonce.user)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(f'Account Link success.\nこんにちは！{nonce.user.username}さん')
            )

    @staticmethod
    @handler.add(PostbackEvent)
    def postback_event(event):
        text_send_message = None

        data = dict(parse.parse_qsl(parse.urlsplit(event.postback.data).path))

        if data['action'] == 'buy':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage('Postback received.')
            )
        elif data['action'] == 'accountLink':
            line = Line.objects.get(pk=event.source.user_id)
            if not line.is_active:
                text_send_message = TextSendMessage('アカウント連携がされていないようです')
            elif data['confirm'] == '0' or not data['confirm'] or data['confirm'] == 0:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage('アカウント連携解除をキャンセルしました')
                )
            elif data['confirm'] == '1' or data['confirm'] or data['confirm'] == 1:
                line.is_active = False
                line.save()
                text_send_message = TextSendMessage(f'{line.service_user.username}さんのアカウント連携を解除しました')

        if not text_send_message:
            text_send_message = TextSendMessage('不明な操作が行われました')

        line_bot_api.reply_message(
            event.reply_token,
            text_send_message
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
            try:
                line = Line.objects.select_related('service_user').get(pk=event.source.user_id)
                if not line.is_active:
                    raise LineAccountInactiveError()

                line_bot_api.reply_message(
                    event.reply_token,
                    TemplateSendMessage(
                        alt_text='すでに連携されています',
                        template=ConfirmTemplate(
                            text=f'{line.service_user.username}さん、アカウント連携を解除しますか？',
                            actions=[
                                PostbackAction(
                                    label='キャンセル',
                                    displayText='アカウント連携を解除しない',
                                    data='action=accountLink&confirm=0'
                                ),
                                PostbackAction(
                                    label='解除',
                                    displayText='アカウント連携を解除する',
                                    data='action=accountLink&confirm=1'
                                )
                            ]
                        )
                    )
                )

            except (Line.DoesNotExist, LineAccountInactiveError):
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
