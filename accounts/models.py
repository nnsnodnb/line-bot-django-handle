from django.db import models


class Line(models.Model):

    user_id = models.CharField(max_length=100, blank=False, null=False, default='', primary_key=True)
    display_name = models.CharField(max_length=200, blank=False, null=False, default='')
    picture_url = models.URLField(max_length=500, blank=False, null=False, default='')
    status_message = models.CharField(max_length=500, blank=False, null=False, default='')

    class Meta:
        verbose_name = 'LINE Account'
        verbose_name_plural = 'LINE Accounts'

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f'{self.display_name} <ID: {self.user_id}>: "{self.__class__.__name__}"'
