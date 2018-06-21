from app.models import Nonce
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as LoginViewBase
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect


class LoginView(LoginViewBase):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'link_token': self.kwargs['link_token']
        })
        return context

    def form_valid(self, form):
        if 'link_token' not in form.data:
            return HttpResponseBadRequest(b'BadRequest.')

        link_token = form.data['link_token']
        user = form.get_user()
        login(self.request, user)

        nonce = Nonce()
        nonce.user = user
        nonce.save()
        url = f'https://access.line.me/dialog/bot/accountLink?linkToken={link_token}&nonce={nonce}'

        return HttpResponseRedirect(url)
