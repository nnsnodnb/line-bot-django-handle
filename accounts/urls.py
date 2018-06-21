from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import LoginView

app_name = 'accounts'

urlpatterns = [
    path('line/<str:link_token>/login/', LoginView.as_view(), name='line_login_view'),
    path('line/logout/', LogoutView.as_view(), name='line_logout_view'),
]
