from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Devices)
admin.site.register(Passwords)
admin.site.register(History)
admin.site.register(Screenshot)
admin.site.register(CustomUser)