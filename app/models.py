from django.db import models
from django.contrib.auth import get_user_model

import random
import secrets

UserModel = get_user_model()


class Nonce(models.Model):

    def __init__(self, *args, **kwargs):
        super(Nonce, self).__init__(*args, **kwargs)
        self.nonce = secrets.token_urlsafe(random.randint(50, 100))

    nonce = models.CharField(max_length=135, blank=False, null=False, default='', primary_key=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Nonce'
        verbose_name_plural = 'Nonces'

    def __str__(self):
        return self.nonce

    def __repr__(self):
        return f'{self.user.username} <ID: {self.nonce}>: "{self.__class__.__name__}"'
