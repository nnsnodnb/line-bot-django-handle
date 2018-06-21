from django.contrib import admin
from .models import Nonce


class NonceAdmin(admin.ModelAdmin):

    list_display = ('nonce', 'user',)
    list_display_links = ('nonce', 'user')


admin.site.register(Nonce, NonceAdmin)
