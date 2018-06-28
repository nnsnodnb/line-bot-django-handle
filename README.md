# line-bot-django-handle

LINE BOT for demonstration handled with Django.

## LINE Messaging API reference

- English: https://developers.line.me/en/docs/messaging-api/reference/
- Japanese: https://developers.line.me/ja/docs/messaging-api/reference/

## Demo

- Receive events
  - MessageEvent
  - FollowEvent
  - UnfollowEvent
  - PostbackEvent
  - AccountLinkEvent

- Send messages
  - TextSendMessage
  - StickerSendMessage
  - ImageSendMessage
  - ImagemapSendMessage
  - VideoSendMessage
  - LocationSendMessage

- Template messages
  - TemplateSendMessage
    - ButtonsTemplate
    - ConfirmTemplate
    - CarouselTemplate
    - ImageCarouselTemplate

- Actions
  - PostbackAction (ConfirmTemplate, CarouselTemplate)
  - MessageAction (CarouselTemplate)
  - URIAction (CarouselTemplate, ImageCarouselTemplate)
  - MessageTemplateAction (ButtonsTemplate)
  - PostbackTemplateAction (ButtonsTemplate)
  - URITemplateAction (ButtonsTemplate)
  - URIImagemapAction (ImagemapSendMessage)

## Preparing

```bash
$ git clone https://github.com/nnsnodnb/line-bot-django-handle.git
$ cd line-bot-django-handle
$ pip install -r requirements.txt
$ cp .env.sample .env  # Fill your secret variables
$ python manage.py migrate
$ python manage.py collectstatic --noinput
$ python manage.py createsuperuser  # If you need it
```

## Dependencies

- Python 3.6.5
- Django 2.0.6
- line-bot-sdk-python 1.7.1

### When possible

- [Ngrok](https://ngrok.com/)

## LICENSE

Copyright (c) 2018 Yuya Oka Released under the Apache License 2.0 (see LICENSE file)

## Author

Yuya Oka ([@nnsnodnb](https://github.com/nnsnodnb))
