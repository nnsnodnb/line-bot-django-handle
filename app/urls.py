from django.urls import path
from .views import CallbackView, URLSchemeView

app_name = 'app'

urlpatterns = [
    path('callback', CallbackView.as_view(), name='callback_view'),
    path('url_scheme', URLSchemeView.as_view(), name='url_scheme_view'),
]
