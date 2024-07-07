from django.contrib import admin
from api_auth.models import Organisation, CustomUser

admin.site.register(Organisation)
admin.site.register(CustomUser)
