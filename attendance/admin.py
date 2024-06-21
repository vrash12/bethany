from django.contrib import admin
from .models import Member, Attendance, Service, SmallGroup, SmallGroupMembership, SmallGroupAttendance

admin.site.register(Member)
admin.site.register(Attendance)
admin.site.register(Service)
admin.site.register(SmallGroup)
admin.site.register(SmallGroupMembership)
admin.site.register(SmallGroupAttendance)