from accounts.errors import LineAccountInactiveError
from accounts.models import Line
from django.conf import settings
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    AccountLinkEvent, MessageEvent, FollowEvent, UnfollowEvent, PostbackEvent,
    ImagemapSendMessage, TextMessage,
    ButtonsTemplate, ConfirmTemplate, TemplateSendMessage, TextSendMessage, StickerSendMessage, ImageSendMessage,
    VideoSendMessage, LocationSendMessage, CarouselTemplate, CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn,
    MessageAction, URIAction,
    MessageTemplateAction, PostbackTemplateAction, PostbackAction, URITemplateAction, URIImagemapAction,
    BaseSize, ImagemapArea,
)
from urllib import parse
from . import line_bot_api, handler, demo_image_url
from .models import Nonce
from .ngrok import Ngrok

import re
import requests
import socket

buttonRegex = re.compile('(ボタン|ぼたん)')
stickerRegex = re.compile('(ステッカー|すてっかー|ステッカ|すてっか|sticker)')
imageRegex = re.compile('(画像|がぞう|写真|しゃしん)')
videoRegex = re.compile('(動画|どうが|ムービー|むーびー|むーゔぃ|ムーヴぃ|movie)')
locationRegex = re.compile('(場所|ばしょ|バショ|location|ろけーしょん)')

try:
    PUBLIC_URL = Ngrok().get_public_url()
    if not PUBLIC_URL:
        if settings.DEBUG:
            PUBLIC_URL = f'http://{settings.HOSTNAME}'
        else:
            PUBLIC_URL = f'https://{settings.HOSTNAME}'
except socket.error:
    if settings.DEBUG:
        PUBLIC_URL = f'http://{settings.HOSTNAME}'
    else:
        PUBLIC_URL = f'https://{settings.HOSTNAME}'


class CallbackView(View):

    def post(self, request, *args, **kwargs):
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseBadRequest()
        except LineBotApiError as e:
            print(e)
            return HttpResponseServerError()

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
    # https://developers.line.me/en/docs/messaging-api/reference/#account-link-event
    def account_link_event(event):
        if event.link.result == 'ok':
            user_id = event.source.user_id
            profile = line_bot_api.get_profile(user_id)

            nonce = Nonce.objects.select_related('user').get(pk=event.link.nonce)
            try:
                line = Line.objects.get(pk=profile.user_id)
                line.update(profile=profile, user=nonce.user)
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
    # https://developers.line.me/en/docs/messaging-api/reference/#postback-event
    def postback_event(event):
        text_send_message = None

        data = dict(parse.parse_qsl(parse.urlsplit(event.postback.data).path))

        if data['action'] == 'buy':
            text_send_message = TextSendMessage('Postback received.')
        elif data['action'] == 'like':
            text_send_message = TextSendMessage('いいねしました！')
        elif data['action'] == 'accountLink':
            line = Line.objects.get(pk=event.source.user_id)
            if not line.is_active:
                text_send_message = TextSendMessage('アカウント連携がされていないようです')
            elif data['confirm'] == '0' or not data['confirm'] or data['confirm'] == 0:
                text_send_message = TextSendMessage('アカウント連携解除をキャンセルしました')
            elif data['confirm'] == '1' or data['confirm'] or data['confirm'] == 1:
                username = line.service_user.username
                line.service_user = None
                line.is_active = False
                line.save()
                text_send_message = TextSendMessage(f'{username}さんのアカウント連携を解除しました')

        if not text_send_message:
            image_url = f'{PUBLIC_URL}/static/images/wrong_postback_response.jpg'
            text_send_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)

        line_bot_api.reply_message(
            event.reply_token,
            text_send_message
        )

    @staticmethod
    @handler.add(MessageEvent, message=TextMessage)
    # https://developers.line.me/en/docs/messaging-api/reference/#message-event
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
        elif stickerRegex.search(event.message.text.lower()):
            # https://developers.line.me/en/docs/messaging-api/reference/#sticker-message
            # https://developers.line.me/media/messaging-api/sticker_list.pdf
            line_bot_api.reply_message(
                event.reply_token,
                StickerSendMessage(package_id='1', sticker_id='116')
            )
        elif imageRegex.search(event.message.text.lower()):
            # https://developers.line.me/en/docs/messaging-api/reference/#image-message
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(original_content_url=f'{PUBLIC_URL}/static/images/spring.jpg',
                                 preview_image_url=f'{PUBLIC_URL}/static/images/spring.jpg')
            )
        elif videoRegex.search(event.message.text.lower()):
            # https://developers.line.me/en/docs/messaging-api/reference/#video-message
            line_bot_api.reply_message(
                event.reply_token,
                VideoSendMessage(original_content_url=f'{PUBLIC_URL}/static/videos/linebot_video_sample.mp4', 
                                 preview_image_url=f'{PUBLIC_URL}/static/images/video_preview.jpg')
            )
        elif locationRegex.search(event.message.text.lower()):
            # https://developers.line.me/en/docs/messaging-api/reference/#location-message
            line_bot_api.reply_message(
                event.reply_token,
                LocationSendMessage(title='京都アスニー', address='京都市中京区聚楽廻松下町9-2',
                                    latitude=35.0190007, longitude=135.7362375)
            )
        elif event.message.text == 'カルーセル':
            # https://developers.line.me/en/docs/messaging-api/reference/#carousel
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                thumbnail_image_url=f'{PUBLIC_URL}/static/images/image_carousel_1.jpg',
                                title='マンホール',
                                text='函館、十字街電停周辺で見つけた',
                                actions=[
                                    PostbackAction(
                                        label='いいね',
                                        displayText='いいね！',
                                        data='action=like&item_id=1'
                                    ),
                                    MessageAction(
                                        label='何かしらのラベル',
                                        text='何かしらのメッセージ'
                                    ),
                                    URIAction(
                                        label='詳細を見る',
                                        uri='http://example.com/1'
                                    )
                                ]
                            ),
                            CarouselColumn(
                                thumbnail_image_url=f'{PUBLIC_URL}/static/images/image_carousel_2.jpg',
                                title='白鷺',
                                text='平安神宮で撮った白鷺',
                                actions=[
                                    PostbackAction(
                                        label='いいね',
                                        displayText='いいね！',
                                        data='action=like&item_id=2'
                                    ),
                                    MessageAction(
                                        label='何かしらのラベル',
                                        text='何かしらのメッセージ'
                                    ),
                                    URIAction(
                                        label='詳細を見る',
                                        uri='http://example.com/2'
                                    )
                                ]
                            )
                        ]
                    )
                )
            )
        elif event.message.text == 'イメージカルーセル':
            # https://developers.line.me/en/docs/messaging-api/reference/#image-carousel
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='ImageCarousel template',
                    template=ImageCarouselTemplate(
                        columns=[
                            ImageCarouselColumn(
                                image_url=f'{PUBLIC_URL}/static/images/image_carousel_1.jpg',
                                action=PostbackAction(
                                    label='函館のマンホール',
                                    displayText='いいね',
                                    data='action=like&item_id=1'
                                )
                            ),
                            ImageCarouselColumn(
                                image_url=f'{PUBLIC_URL}/static/images/image_carousel_2.jpg',
                                action=URIAction(
                                    label='白鷺について',
                                    uri='https://ja.wikipedia.org/wiki/%E7%99%BD%E9%B7%BA'
                                )
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

                url = f'{PUBLIC_URL}{reverse("accounts:line_login_view", kwargs={"link_token": link_token})}'

                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        ImagemapSendMessage(
                            base_url=f'{PUBLIC_URL}/static/images',
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
        elif event.message.text == '終わり':
            image_url = f'{PUBLIC_URL}/static/images/finish_response.jpg'
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text)
            )


class URLSchemeView(TemplateView):

    template_name = 'app/url_scheme.html'

    def get(self, request, *args, **kwargs):
        return super(URLSchemeView, self).get(request, *args, **kwargs)
