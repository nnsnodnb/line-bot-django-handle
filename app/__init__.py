from django.conf import settings
from linebot import LineBotApi, WebhookHandler


line_bot_api = LineBotApi(settings.LINE_BOT_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_BOT_ACCESS_SECRET)

demo_image_url = 'https://pbs.twimg.com/profile_images/912149878431563776/JbLZR5nP_400x400.jpg'
connect_image_url = 'https://cdn-ak.f.st-hatena.com/images/fotolife/n/nanashinodonbee/20180620/20180620004737.png'
