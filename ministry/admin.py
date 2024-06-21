from django.contrib import admin
from .models import Minister, Ministry, Schedule, Availability

admin.site.register(Minister)
admin.site.register(Ministry)
admin.site.register(Schedule)
admin.site.register(Availability)