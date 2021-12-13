from django.contrib import admin

from analytics.models import Domain, PageView

admin.site.register(Domain)
admin.site.register(PageView)
