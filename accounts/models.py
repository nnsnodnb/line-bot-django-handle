from django.db import models
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class Line(models.Model):

    user_id = models.CharField(max_length=100, blank=False, null=False, default='', primary_key=True)
    display_name = models.CharField(max_length=200, blank=False, null=False, default='')
    picture_url = models.URLField(max_length=500, blank=False, null=False, default='')
    status_message = models.CharField(max_length=500, blank=False, null=False, default='')
    service_user = models.ForeignKey(UserModel, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'LINE Account'
        verbose_name_plural = 'LINE Accounts'

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f'{self.display_name} <ID: {self.user_id}>: "{self.__class__.__name__}"'

    def update(self, profile, user):
        self.service_user = user
        self.display_name = profile.display_name
        self.picture_url = profile.picture_url
        self.status_message = profile.status_message
