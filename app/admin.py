from django.contrib import admin
from .models import Nonce


class NonceAdmin(admin.ModelAdmin):

    list_display = ('nonce', 'user',)

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.opts.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD'):
            return False
        return super(NonceAdmin, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Nonce, NonceAdmin)
