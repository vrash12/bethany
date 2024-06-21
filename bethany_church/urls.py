from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from attendance import views as attendance_views
from ministry.views import (
    schedule_calendar, load_schedules,
    MinisterManageView, MinisterDetailView,
    MinisterUpdateView, MinisterSuccessView, MinistryListView,
    minister_detail, get_schedules, update_schedule,
    CalendarView, AvailabilityView, ScheduleCreateView, ScheduleView, export_attendance_to_excel, ScheduleUpdateView, ScheduleDeleteView
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('schedule/', include('schedule.urls')),
    path('add_member/', attendance_views.add_member, name='add_member'),
    path('member_list/', attendance_views.member_list, name='member_list'),
    path('download-excel/', attendance_views.download_excel, name='download_excel'),
    path('mark_attendance/', attendance_views.mark_attendance, name='mark_attendance'),
    path('download-attendance/', attendance_views.download_attendance, name='download_attendance'),
    path('member_added_success/', attendance_views.add_member_success, name='success_url'),
    path('ministry_list/', MinistryListView.as_view(), name='ministry_list'),
    path('attendance_success/', attendance_views.home, name='attendance_success'),
    path('members/<int:member_id>/details/', attendance_views.get_member_details, name='member-details'),
    path('minister/', MinisterManageView.as_view(), name='minister_add'),
    path('minister_detail/<int:pk>/', minister_detail, name='minister_detail'),
    path('minister/<int:pk>/', MinisterManageView.as_view(), name='minister_manage'),
    path('ministers/', MinistryListView.as_view(), name='ministers_list'),
    path('minister/<int:pk>/update/', MinisterUpdateView.as_view(), name='minister_update'),
    path('', attendance_views.home, name='home'),  
    path('login/', auth_views.LoginView.as_view(template_name='attendance/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('minister/success/', MinisterSuccessView.as_view(), name='minister_success'),
    path('get_attendance_records/', attendance_views.get_attendance_records, name='get_attendance_records'),
    path('get_member_details/', attendance_views.get_member_details, name='get_member_details'),
    path('attendance_data/', attendance_views.get_attendance_records, name='attendance_data'),
    path('last-sunday-attendance/', attendance_views.last_sunday_attendance_data, name='last_sunday_attendance'),
    path('schedule/', schedule_calendar, name='schedule_calendar'),
    path('load_schedules/', load_schedules, name='load_schedules'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('availability/', AvailabilityView.as_view(), name='availability'),
    path('get_schedules/', get_schedules, name='get_schedules'),
    path('update_schedule/', update_schedule, name='update_schedule'),
    path('schedule/create/', ScheduleCreateView.as_view(), name='schedule_create'),
     path('schedule/<int:pk>/edit/', ScheduleUpdateView.as_view(), name='edit_schedule'),
    path('schedule/<int:pk>/delete/', ScheduleDeleteView.as_view(), name='delete_schedule'),
    path('schedule_calendar/', ScheduleView.as_view(), name='schedule_calendar'),
    path('create-schedule/', ScheduleCreateView.as_view(), name='create_schedule'),
    path('export-attendance/', export_attendance_to_excel, name='export_attendance'),
    path('small-groups/', attendance_views.small_group_list_create, name='small_group_list_create'),
    path('small-groups/<int:pk>/', attendance_views.small_group_list_create, name='small_group_list_create_with_pk'),
    path('small-groups/delete/<int:pk>/', attendance_views.small_group_delete, name='small_group_delete'),
    path('record-attendance/', attendance_views.record_attendance, name='record_attendance'),
      path('manage-giving/', attendance_views.manage_giving, name='manage_giving'),
    path('download-member-giving-excel/', attendance_views.download_member_giving_excel, name='download_member_giving_excel'),
    path('download-minister-giving-excel/', attendance_views.download_minister_giving_excel, name='download_minister_giving_excel'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
