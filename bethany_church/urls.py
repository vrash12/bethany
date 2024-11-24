from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from attendance import views as attendance_views
from attendance.views import UserDashboardView

from ministry.views import (
    schedule_calendar, load_schedules,
    MinisterManageView, MinisterDetailView,
    MinisterUpdateView, MinisterSuccessView, MinistryListView,
    minister_detail, get_schedules, update_schedule, schedule_detail,
    CalendarView, AvailabilityView, ScheduleCreateView, ScheduleView, export_attendance_to_excel, ScheduleUpdateView, ScheduleDeleteView,  GeneralDashboardView, minister_list_ajax, get_schedules_by_date, ScheduleDeleteView
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_home/', attendance_views.home, name='admin_home'),
    path('dashboard/', UserDashboardView.as_view(), name='user_dashboard'),

   # Ensure 'schedule.urls' doesn't contain conflicting patterns
    path('schedule_calendar/', ScheduleView.as_view(), name='schedule_calendar'),
    path('schedule/create/', ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedule/<int:pk>/edit/', ScheduleUpdateView.as_view(), name='edit_schedule'),
    path('schedule/<int:pk>/delete/', ScheduleDeleteView.as_view(), name='delete_schedule'),
    
    # Attendance URLs
    path('add_member/', attendance_views.add_member, name='add_member'),
    path('member_list/', attendance_views.member_list, name='member_list'),
    path('download-excel/', attendance_views.download_excel, name='download_excel'),
    path('mark_attendance/', attendance_views.mark_attendance, name='mark_attendance'),
    path('download-attendance/', attendance_views.download_attendance, name='download_attendance'),
    path('member_added_success/', attendance_views.add_member_success, name='success_url'),
    path('load_attendance_data/', attendance_views.load_attendance_data, name='load_attendance_data'),
    path('small_group_detail/', attendance_views.small_group_detail, name='small_group_detail'),
    
    # Ministry URLs
    path('ministry_list/', MinistryListView.as_view(), name='ministry_list'),
    path('attendance_success/', attendance_views.home, name='attendance_success'),
    path('members/<int:member_id>/details/', attendance_views.get_member_details, name='member-details'),
    path('minister/', MinisterManageView.as_view(), name='minister_add'),
    path('minister_detail/<int:pk>/', minister_detail, name='minister_detail'),
    path('minister/<int:pk>/', MinisterManageView.as_view(), name='minister_manage'),
    path('ministers/', MinistryListView.as_view(), name='ministers_list'),
    path('minister/<int:pk>/update/', MinisterUpdateView.as_view(), name='minister_update'),
    path('minister/success/', MinisterSuccessView.as_view(), name='minister_success'),
    
    # General Dashboard
    path('', GeneralDashboardView.as_view(), name='home'),
    
    # Authentication URLs
    path('login/', attendance_views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', attendance_views.register, name='register'),  # Added trailing slash for consistency
    
    # AJAX and API URLs
    path('get_attendance_records/', attendance_views.get_attendance_records, name='get_attendance_records'),
    path('get_member_details/', attendance_views.get_member_details, name='get_member_details'),
    path('attendance_data/', attendance_views.get_attendance_records, name='attendance_data'),
    path('last-sunday-attendance/', attendance_views.last_sunday_attendance_data, name='last_sunday_attendance'),
    path('load_schedules/', load_schedules, name='load_schedules'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('availability/', AvailabilityView.as_view(), name='availability'),
    path('get_schedules/', get_schedules, name='get_schedules'),
    path('update_schedule/', update_schedule, name='update_schedule'),
    path('export-attendance/', export_attendance_to_excel, name='export_attendance'),
    
    # Small Groups URLs
    path('small-groups/', attendance_views.small_group_list_create, name='small_group_list_create'),
    path('small-groups/<int:pk>/', attendance_views.small_group_list_create, name='small_group_list_create_with_pk'),
    path('small-groups/delete/<int:pk>/', attendance_views.small_group_delete, name='small_group_delete'),
    path('record-attendance/', attendance_views.record_attendance, name='record_attendance'),
    
    # Giving URLs
    path('manage-giving/', attendance_views.manage_giving, name='manage_giving'),
    path('download-member-giving-excel/', attendance_views.download_member_giving_excel, name='download_member_giving_excel'),
    path('download-minister-giving-excel/', attendance_views.download_minister_giving_excel, name='download_minister_giving_excel'),
    path('small_group/detail/<int:pk>/', attendance_views.small_group_detail, name='small_group_detail'),
    path('export/giving/<str:giver_type>/pdf/', attendance_views.export_giving_pdf, name='export_giving_pdf'),
    path('export/giving/<str:giver_type>/<int:giver_id>/individual_pdf/', attendance_views.download_individual_giving_pdf, name='download_individual_giving_pdf'),
    
    # Additional AJAX URLs
    path('minister_list_ajax/', minister_list_ajax, name='minister_list_ajax'),
    path('ajax/get_schedule/', get_schedules_by_date, name='get_schedules_by_date'),
    path('schedule_detail/<int:pk>/', schedule_detail, name='schedule_detail'),
    path('schedule/delete/', ScheduleDeleteView.as_view(), name='schedule_delete'),
    
    # User-specific URLs
    path('user/profile/', attendance_views.user_profile, name='user_profile'),
    path('user/mark_attendance/', attendance_views.user_mark_attendance, name='user_mark_attendance'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
