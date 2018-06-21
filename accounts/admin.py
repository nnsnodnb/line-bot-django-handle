from django.contrib import admin
from .models import Line


class LineAdmin(admin.ModelAdmin):

    list_display = ('user_id', 'display_name', 'picture_url', 'status_message', 'service_user', 'is_active',)
    list_display_links = ('user_id', 'display_name', 'picture_url',)

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.opts.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD'):
            return False
        return super(LineAdmin, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Line, LineAdmin)
