#attendace/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import MemberForm, LoginForm, SmallGroupForm, SmallGroupAttendanceForm, GivingForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
from ministry.models import Ministry, Minister
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.db.models.functions import Cast, ExtractWeekDay, TruncMonth, TruncYear
from .models import Attendance, Service, Attendance, MinisterAttendance, SmallGroup, Member,  SmallGroupMembership, SmallGroupAttendance, Giving
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
import io
import base64
from django.db.models.functions import ExtractWeek
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.views.generic import ListView
from django.db.models import Q, F, Func, Value, Case, When, CharField, IntegerField, Count
from django.core.serializers import serialize
import json
import io
import matplotlib.pyplot as plt
import logging
from datetime import datetime, timedelta
from django.db.models import Avg
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.generic import View
from django.db.models import Avg
import pandas as pd
from django.forms import modelformset_factory
from .forms import SmallGroupMembershipForm
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Count

logger = logging.getLogger(__name__)
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI rendering

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') 
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'attendance/login.html', {'form': form})



def home(request):
    today = timezone.now().date()
    days_to_last_sunday = (today.weekday() + 1) % 7
    if days_to_last_sunday == 0:
        days_to_last_sunday = 7
    last_sunday = today - timedelta(days=days_to_last_sunday)

    # Aggregate data
    total_attendance = Attendance.objects.filter(status=True).count()
    average_attendance = Attendance.objects.annotate(
        status_int=Case(When(status=True, then=1), default=0, output_field=IntegerField())
    ).aggregate(average=Avg('status_int'))['average']

    small_group_stats = SmallGroupAttendance.objects.values('small_group__name').annotate(
        total_attendance=Count('id'),
        average_attendance=Avg('attended')
    ).order_by('-total_attendance')

    # Monthly Attendance Trends
    monthly_trends = Attendance.objects.filter(status=True).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(count=Count('id')).order_by('month')

    # Yearly Attendance Trends
    yearly_trends = Attendance.objects.filter(status=True).annotate(
        year=TruncYear('date')
    ).values('year').annotate(count=Count('id')).order_by('year')

    # Weekday vs Weekend Attendance
    weekday_vs_weekend = Attendance.objects.filter(status=True).annotate(
        weekday=ExtractWeekDay('date')
    ).annotate(
        is_weekend=Case(
            When(weekday__in=[6, 7], then=Value(True)),
            default=Value(False),
            output_field=IntegerField()
        )
    ).values('is_weekend').annotate(count=Count('id')).order_by('is_weekend')

    # Demographics Analysis
    age_group_distribution = Member.objects.annotate(
        age_group=Case(
            When(age__lte=12, then=Value('0-12')),
            When(age__gt=12, age__lte=18, then=Value('13-18')),
            When(age__gt=18, age__lte=35, then=Value('19-35')),
            When(age__gt=35, age__lte=50, then=Value('36-50')),
            When(age__gt=50, then=Value('51+')),
            default=Value('Unknown'),
            output_field=CharField()
        )
    ).values('age_group').annotate(count=Count('id')).order_by('age_group')

    gender_ratio = Member.objects.values('gender').annotate(count=Count('id')).order_by('gender')

    # Generate Graphs using Matplotlib
    def plot_to_img(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_str

    # Monthly Trends Graph
    if monthly_trends.exists():
        fig, ax = plt.subplots(figsize=(8, 4))
        months = [x['month'].strftime('%Y-%m') for x in monthly_trends]
        monthly_counts = [x['count'] for x in monthly_trends]
        ax.plot(months, monthly_counts, marker='o')
        ax.set_title('Monthly Attendance Trends')
        ax.set_xlabel('Month')
        ax.set_ylabel('Attendance Count')
        ax.set_xticks(range(len(months)))  # Set explicit tick positions
        ax.set_xticklabels(months, rotation=45)
        monthly_trends_img = plot_to_img(fig)
    else:
        monthly_trends_img = None  # Or use a placeholder image

    # Yearly Trends Graph
    if yearly_trends.exists():
        fig, ax = plt.subplots(figsize=(8, 4))
        years = [x['year'].year for x in yearly_trends]
        yearly_counts = [x['count'] for x in yearly_trends]
        ax.plot(years, yearly_counts, marker='o', color='g')
        ax.set_title('Yearly Attendance Trends')
        ax.set_xlabel('Year')
        ax.set_ylabel('Attendance Count')
        ax.set_xticks(range(len(years)))
        ax.set_xticklabels(years)
        yearly_trends_img = plot_to_img(fig)
    else:
        yearly_trends_img = None

    # Weekday vs Weekend Graph
    if weekday_vs_weekend.exists():
        fig, ax = plt.subplots(figsize=(8, 4))
        labels = ['Weekday', 'Weekend']
        counts = [x['count'] for x in weekday_vs_weekend]
        # Ensure counts have both Weekday and Weekend
        while len(counts) < 2:
            counts.append(0)
        ax.bar(labels, counts, color=['blue', 'orange'])
        ax.set_title('Weekday vs. Weekend Attendance')
        ax.set_ylabel('Attendance Count')
        weekday_vs_weekend_img = plot_to_img(fig)
    else:
        weekday_vs_weekend_img = None

    # Age Group Distribution Graph
    if age_group_distribution.exists():
        fig, ax = plt.subplots(figsize=(8, 4))
        age_groups = [x['age_group'] for x in age_group_distribution]
        age_group_counts = [x['count'] for x in age_group_distribution]
        ax.pie(age_group_counts, labels=age_groups, autopct='%1.1f%%', startangle=140)
        ax.set_title('Age Group Distribution')
        age_group_distribution_img = plot_to_img(fig)
    else:
        age_group_distribution_img = None

    # Gender Ratio Graph
    if gender_ratio.exists():
        fig, ax = plt.subplots(figsize=(8, 4))
        genders = ['Male' if g['gender'] == 'M' else 'Female' if g['gender'] == 'F' else 'Other' for g in gender_ratio]
        gender_counts = [x['count'] for x in gender_ratio]
        ax.pie(gender_counts, labels=genders, autopct='%1.1f%%', startangle=140)
        ax.set_title('Gender Ratio')
        gender_ratio_img = plot_to_img(fig)
    else:
        gender_ratio_img = None

    context = {
        'total_attendance': total_attendance,
        'average_attendance': average_attendance,
        'last_sunday': last_sunday,
        'small_group_stats': small_group_stats,
        'monthly_trends_img': monthly_trends_img,
        'yearly_trends_img': yearly_trends_img,
        'weekday_vs_weekend_img': weekday_vs_weekend_img,
        'age_group_distribution_img': age_group_distribution_img,
        'gender_ratio_img': gender_ratio_img,
    }

    return render(request, 'attendance/home.html', context)

def load_attendance_data(request):
    if request.method == 'GET':
        attendance_date = request.GET.get('attendance_date')
        service_id = request.GET.get('service')
        # Fetch members and their attendance status
        members = []
        ministers = []

        try:
            service = Service.objects.get(id=service_id)
            all_members = Member.objects.all()
            all_ministers = Minister.objects.all()

            for member in all_members:
                attendance = Attendance.objects.filter(
                    member=member,
                    date=attendance_date,
                    service=service
                ).first()
                members.append({
                    'id': member.id,
                    'first_name': member.first_name,
                    'last_name': member.last_name,
                    'status': attendance.status if attendance else False
                })

            for minister in all_ministers:
                attendance = MinisterAttendance.objects.filter(
                    minister=minister,
                    date=attendance_date,
                    service=service
                ).first()
                ministers.append({
                    'id': minister.id,
                    'first_name': minister.first_name,
                    'last_name': minister.last_name,
                    'status': attendance.status if attendance else False
                })

            return JsonResponse({'members': members, 'ministers': ministers})

        except Service.DoesNotExist:
            return JsonResponse({'error': 'Selected service does not exist.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def add_member(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url') 
    else:
        form = MemberForm()
    return render(request, 'attendance/add_member.html', {'form': form})

def download_excel(request):

    members = Member.objects.all().values()
 
    df = pd.DataFrame(members)
  
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="members.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return response

def member_list(request):
    members = Member.objects.all()
    return render(request, 'attendance/member_list.html', {'members': members})

def mark_attendance(request):
    if request.method == 'POST':
        # Handle AJAX submission
        attendance_date = request.POST.get('attendance_date', timezone.now().date().isoformat())
        service_id = request.POST.get('service')
        present_ids = request.POST.getlist('present_members[]')  # Note the '[]' for multiple values

        try:
            service = Service.objects.get(id=service_id)
            all_members = Member.objects.all()
            all_ministers = Minister.objects.all()

            with transaction.atomic():
                # Update member attendance
                for member in all_members:
                    status = f"member_{member.id}" in present_ids
                    Attendance.objects.update_or_create(
                        member=member,
                        date=attendance_date,
                        service=service,
                        defaults={'status': status}
                    )

                # Update minister attendance
                for minister in all_ministers:
                    status = f"minister_{minister.id}" in present_ids
                    MinisterAttendance.objects.update_or_create(
                        minister=minister,
                        date=attendance_date,
                        service=service,
                        defaults={'status': status}
                    )

            return JsonResponse({'message': 'Attendance successfully updated.'})

        except Service.DoesNotExist:
            return JsonResponse({'error': 'Selected service does not exist.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    else:
        # Handle GET request to render the page
        services = Service.objects.all()
        members = Member.objects.all()
        ministers = Minister.objects.all()
        return render(request, 'attendance/attendance.html', {
            'services': services,
            'members': members,
            'ministers': ministers,
            'today': timezone.now().date(),
        })
    

def download_attendance(request):

    attendance_records = Attendance.objects.all().values('member__first_name', 'member__last_name', 'date', 'service__name', 'status')
    df = pd.DataFrame(list(attendance_records))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="attendance_{timezone.now().strftime("%Y-%m-%d")}.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    return response


def generate_attendance_graph(request):

    services = Service.objects.all()
    service_names = [service.name for service in services]
    attendance_counts = [Attendance.objects.filter(service=service, status=True).count() for service in services]

    plt.figure(figsize=(10, 5))
    plt.bar(service_names, attendance_counts, color='skyblue')
    plt.xlabel('Services')
    plt.ylabel('Number of Attendees')
    plt.title('Attendance per Service')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()

 
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type='image/png')

def custom_serialize(queryset):
    list_results = []
    for attendance in queryset:
        member = attendance.member
        service = attendance.service
        result = {
            "id": attendance.id,
            "date": attendance.date.strftime('%Y-%m-%d'),
            "status": attendance.status,
            "member": {
                "first_name": member.first_name,
                "last_name": member.last_name
            },
            "service": {
                "name": service.name,
                "time": service.get_time_display() if service else None
            }
        }
        list_results.append(result)
    return json.dumps(list_results)


def get_attendance_records(request):
    if request.method == 'GET':
        attendance_date = request.GET.get('attendance_date')
        service_id = request.GET.get('service')

        try:
            attendance_records = Attendance.objects.all()
            minister_attendance_records = MinisterAttendance.objects.all()

            if attendance_date:
                attendance_records = attendance_records.filter(date=attendance_date)
                minister_attendance_records = minister_attendance_records.filter(date=attendance_date)

            if service_id:
                service = Service.objects.get(id=service_id)
                attendance_records = attendance_records.filter(service=service)
                minister_attendance_records = minister_attendance_records.filter(service=service)

            attendance_records = attendance_records.select_related('member')
            minister_attendance_records = minister_attendance_records.select_related('minister')

            records = []

            for attendance in attendance_records:
                records.append({
                    'name': f"{attendance.member.first_name} {attendance.member.last_name}",
                    'type': 'Member',
                    'status': attendance.status
                })

            for attendance in minister_attendance_records:
                records.append({
                    'name': f"{attendance.minister.first_name} {attendance.minister.last_name}",
                    'type': 'Minister',
                    'status': attendance.status
                })

            return JsonResponse({'records': records})

        except Service.DoesNotExist:
            return JsonResponse({'error': 'Selected service does not exist.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)


def add_member_success(request):
    return render(request, 'attendance/add_member_success.html')

def attendance_success(request):
    return render(request, 'attendance/attendance_success.html')

def ministry_list(request):
    ministries = Ministry.objects.all()  
    return render(request, 'ministries/ministry_list.html', {'ministries': ministries})


def get_attendance_data(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        today = timezone.now().date()
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = today - timedelta(days=today.weekday() + 1)

    services = Service.objects.all()
    data = {
        'labels': [service.name for service in services],
        'attendance': [Attendance.objects.filter(service=service, date__range=[start_date, end_date], status=True).count() for service in services],
        'title': f'Attendance from {start_date} to {end_date}'
    }
    return JsonResponse(data)



logger = logging.getLogger(__name__)

def get_member_details(request):
    member_id = request.GET.get('member_id')
    if not member_id:
        return JsonResponse({'status': 'error', 'message': 'Member ID is required'}, status=400)

    logger.info(f"Received member ID: {member_id}")  

    try:
 
        member_id = int(member_id)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': f'Invalid Member ID format: {member_id}'}, status=400)

    try:
        member = Member.objects.get(id=member_id)
        data = {
            "first_name": member.first_name,
            "middle_name": member.middle_name or "",
            "last_name": member.last_name,
            "birthday": member.birthday.strftime('%Y-%m-%d') if member.birthday else "Not Available",
            "age": member.age,
            "fb_name": member.fb_name or "N/A"
        }
        return JsonResponse({'status': 'ok', 'member': data})
    except Member.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Member not found'}, status=404)
    except Exception as e:
        logger.error(f"Error retrieving member details: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
    
class MinisterListView(ListView):
    model = Minister
    template_name = 'ministries/ministry_list.html'
    context_object_name = 'ministers'

class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/user_dashboard.html'  # Path to the template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch ministry schedules (you can adjust this to fit your data model)
        schedules = Schedule.objects.all().order_by('start_time')

        # Fetch small group attendance records for the logged-in user
        small_group_attendance = SmallGroupAttendance.objects.filter(members__user=self.request.user).distinct()

        # Add data to context
        context['schedules'] = schedules
        context['small_group_attendance'] = small_group_attendance
        return context
    
    
def last_sunday_attendance_data(request):
    today = timezone.now().date()
    days_to_last_sunday = (today.weekday() + 1) % 7
    if days_to_last_sunday == 0:
        days_to_last_sunday = 7
    last_sunday = today - timedelta(days=days_to_last_sunday)

    services = Service.objects.all()
    data = {
        'labels': [service.name for service in services],
        'attendance': [Attendance.objects.filter(service=service, date=last_sunday, status=True).count() for service in services],
        'lastSunday': last_sunday.isoformat()
    }
    return JsonResponse(data)


def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def small_group_list_create(request):
    query = request.GET.get('q')
    page_number = request.GET.get('page')

    if query:
        small_groups = SmallGroup.objects.filter(name__icontains=query)
    else:
        small_groups = SmallGroup.objects.all()

    paginator = Paginator(small_groups, 5) 
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        if group_id:
            group = get_object_or_404(SmallGroup, pk=group_id)
        else:
            group = None

        group_form = SmallGroupForm(request.POST, instance=group)
        
        if group_form.is_valid():
            group = group_form.save()
            group.memberships.all().delete() 

            for member in group_form.cleaned_data['members']:
                SmallGroupMembership.objects.create(small_group=group, member=member)

            for minister in group_form.cleaned_data['ministers']:
                SmallGroupMembership.objects.create(small_group=group, minister=minister)

            if is_ajax(request):
                return JsonResponse({'message': 'Group saved successfully'})
            else:
                return redirect('small_group_list_create')
        else:
            if is_ajax(request):
                return JsonResponse({'errors': group_form.errors}, status=400)
    else:
        group_form = SmallGroupForm()

    attendance_form = SmallGroupAttendanceForm()
    attendance_list = SmallGroupAttendance.objects.all()

    return render(request, 'attendance/small_group_crud.html', {
        'group_form': group_form,
        'attendance_form': attendance_form,
        'page_obj': page_obj,
        'attendance_list': attendance_list,
    })

def small_group_detail(request):
    group_id = request.GET.get('group_id')
    if group_id:
        group = get_object_or_404(SmallGroup, pk=group_id)
        data = {
            'id': group.id,
            'name': group.name,
            'leader_id': group.leader.id if group.leader else None,
            'members': list(group.memberships.filter(member__isnull=False).values_list('member__id', flat=True)),
            'ministers': list(group.memberships.filter(minister__isnull=False).values_list('minister__id', flat=True)),
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No group ID provided'}, status=400)

def small_group_delete(request, pk):
    group = get_object_or_404(SmallGroup, pk=pk)
    group.delete()
    return redirect('small_group_list_create')

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@require_POST
def record_attendance(request):
    form = SmallGroupAttendanceForm(request.POST)
    
    if form.is_valid():
        small_group_id = request.POST.get('small_group_id')
        small_group = get_object_or_404(SmallGroup, pk=small_group_id)
        date = form.cleaned_data['date']
        attended = form.cleaned_data['attended']

        # Check if attendance for this small group and date already exists
        attendance, created = SmallGroupAttendance.objects.get_or_create(
            small_group=small_group,
            date=date,
            defaults={'attended': attended}
        )

        if not created:
            # Update the 'attended' status if the record already exists
            attendance.attended = attended
            attendance.save()
        
        if attended:
            # Automatically associate all members and ministers of the small group
            members = small_group.memberships.filter(member__isnull=False).values_list('member', flat=True)
            ministers = small_group.memberships.filter(minister__isnull=False).values_list('minister', flat=True)
            attendance.members.set(members)
            attendance.ministers.set(ministers)
        else:
            # If not attended, clear any existing associations
            attendance.members.clear()
            attendance.ministers.clear()

        if is_ajax(request):
            return JsonResponse({'message': 'Attendance recorded successfully'})
        else:
            return redirect('small_group_list_create')
    else:
        if is_ajax(request):
            return JsonResponse({'errors': form.errors}, status=400)
        else:
            # Handle non-AJAX form submissions if necessary
            return redirect('small_group_list_create')

@login_required
def manage_giving(request):
    if request.method == "POST":
        if 'update_giving' in request.POST:
            pk = request.POST.get('giving_id')
            giving = get_object_or_404(Giving, pk=pk)
            form = GivingForm(request.POST, instance=giving)
            if form.is_valid():
                giver_type = form.cleaned_data['giver_type']
                updated_giving = form.save(commit=False)
                if giver_type == 'member':
                    updated_giving.minister = None
                elif giver_type == 'minister':
                    updated_giving.member = None
                updated_giving.save()
                messages.success(request, 'Giving record updated successfully.')
                return redirect('manage_giving')
        elif 'delete_giving' in request.POST:
            pk = request.POST.get('giving_id')
            giving = get_object_or_404(Giving, pk=pk)
            giving.delete()
            messages.success(request, 'Giving record deleted successfully.')
            return redirect('manage_giving')
        else:
            form = GivingForm(request.POST)
            if form.is_valid():
                giver_type = form.cleaned_data['giver_type']
                giving = form.save(commit=False)
                if giver_type == 'member':
                    giving.minister = None
                elif giver_type == 'minister':
                    giving.member = None
                giving.save()
                return redirect('manage_giving')
    else:
        form = GivingForm()

    member_givings = Giving.objects.filter(member__isnull=False)
    minister_givings = Giving.objects.filter(minister__isnull=False)

    top_members = (Giving.objects.filter(member__isnull=False)
                   .values('member__first_name', 'member__last_name')
                   .annotate(total_giving=Sum('amount'))
                   .order_by('-total_giving')[:10])

    top_ministers = (Giving.objects.filter(minister__isnull=False)
                     .values('minister__first_name', 'minister__last_name')
                     .annotate(total_giving=Sum('amount'))
                     .order_by('-total_giving')[:10])

    context = {
        'form': form,
        'member_givings': member_givings,
        'minister_givings': minister_givings,
        'top_members': top_members,
        'top_ministers': top_ministers,
    }

    return render(request, 'attendance/manage_giving.html', context)

@login_required
def download_member_giving_excel(request):
    date_filter = request.GET.get('date', None)
    if date_filter:
        member_givings = Giving.objects.filter(member__isnull=False, date=date_filter).values('member__first_name', 'member__last_name', 'date', 'amount', 'purpose', 'notes')
    else:
        member_givings = Giving.objects.filter(member__isnull=False).values('member__first_name', 'member__last_name', 'date', 'amount', 'purpose', 'notes')
    
    df = pd.DataFrame(list(member_givings))
    df.rename(columns={'member__first_name': 'First Name', 'member__last_name': 'Last Name'}, inplace=True)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="member_givings_{date_filter}.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Member Givings')
    return response

@login_required
def download_minister_giving_excel(request):
    date_filter = request.GET.get('date', None)
    if date_filter:
        minister_givings = Giving.objects.filter(minister__isnull=False, date=date_filter).values('minister__first_name', 'minister__last_name', 'date', 'amount', 'purpose', 'notes')
    else:
        minister_givings = Giving.objects.filter(minister__isnull=False).values('minister__first_name', 'minister__last_name', 'date', 'amount', 'purpose', 'notes')
    
    df = pd.DataFrame(list(minister_givings))
    df.rename(columns={'minister__first_name': 'First Name', 'minister__last_name': 'Last Name'}, inplace=True)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="minister_givings_{date_filter}.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Minister Givings')
    return response

def prepare_attendance_data():
    # Query attendance data from the database, assuming status=True means present
    attendance_data = Attendance.objects.filter(status=True).values('date').annotate(count=Count('id'))
    
    # Create a DataFrame from the query
    df = pd.DataFrame(attendance_data)
    
    # Convert 'date' to datetime format and set it as the index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Ensure data is sorted by date
    df.sort_index(inplace=True)
    
    return df
def export_giving_pdf(request, giver_type):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="giving_{giver_type}_{timezone.now().strftime("%Y-%m-%d")}.pdf"'

    # Create the PDF object using ReportLab
    pdf_canvas = canvas.Canvas(response, pagesize=letter)

    # Set up the PDF document
    pdf_canvas.setTitle(f"{giver_type.capitalize()} Giving Report")
    width, height = letter
    pdf_canvas.setFont("Helvetica", 12)

    # Retrieve all givers with givings
    if giver_type == 'member':
        givers = Member.objects.filter(giving__isnull=False).distinct().prefetch_related('giving_set')
    else:
        givers = Minister.objects.filter(giving__isnull=False).distinct().prefetch_related('giving_set')

    # Iterate over each giver
    for idx, giver in enumerate(givers):
        # Start a new page for each giver except the first one
        if idx > 0:
            pdf_canvas.showPage()
            pdf_canvas.setFont("Helvetica", 12)

        # Header for the giver
        pdf_canvas.drawString(1 * inch, height - 1 * inch, f"{giver_type.capitalize()} Giving Report")
        pdf_canvas.drawString(1 * inch, height - 1.2 * inch, f"Date: {timezone.now().strftime('%B %d, %Y')}")
        pdf_canvas.drawString(1 * inch, height - 1.4 * inch, "Thank you for your generosity!")

        # Giver's name
        giver_name = f"{giver.first_name} {giver.last_name}"
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(1 * inch, height - 1.8 * inch, f"Giver: {giver_name}")
        pdf_canvas.setFont("Helvetica", 12)

        y_position = height - 2.2 * inch

        # Retrieve the giver's givings (using prefetch_related data)
        if giver_type == 'member':
            givings = giver.giving_set.all()
        else:
            givings = giver.giving_set.all()

        # Iterate over the giver's givings
        for giving in givings:
            pdf_canvas.drawString(1 * inch, y_position, f"Date: {giving.date.strftime('%B %d, %Y')}")
            pdf_canvas.drawString(1 * inch, y_position - 0.2 * inch, f"Amount Given: ${giving.amount:.2f}")
            pdf_canvas.drawString(1 * inch, y_position - 0.4 * inch, f"Purpose: {giving.get_purpose_display()}")
            pdf_canvas.drawString(1 * inch, y_position - 0.6 * inch, f"Notes: {giving.notes or 'N/A'}")
            pdf_canvas.drawString(1 * inch, y_position - 0.8 * inch, "Thank you for your generous contribution!")

            y_position -= 1.2 * inch

            # Check if we need a new page
            if y_position < inch:
                pdf_canvas.showPage()
                pdf_canvas.setFont("Helvetica", 12)
                y_position = height - 1 * inch

    # Finalize the PDF and close it
    pdf_canvas.save()

    return response

@login_required
def download_individual_giving_pdf(request, giver_type, giver_id):
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year
    month_name = current_date.strftime('%B')

    # Retrieve the giver
    if giver_type == 'member':
        giver = get_object_or_404(Member, pk=giver_id)
        givings = Giving.objects.filter(
            member=giver, date__month=current_month, date__year=current_year
        )
        giver_name = f"{giver.first_name} {giver.last_name}"
    elif giver_type == 'minister':
        giver = get_object_or_404(Minister, pk=giver_id)
        givings = Giving.objects.filter(
            minister=giver, date__month=current_month, date__year=current_year
        )
        giver_name = f"{giver.first_name} {giver.last_name}"
    else:
        return HttpResponseBadRequest("Invalid giver type.")

    # Organize givings per week
    givings_per_week = (
        givings.annotate(week=ExtractWeek('date'))
        .values('week')
        .annotate(total_amount=Sum('amount'))
        .order_by('week')
    )

    # Prepare PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{giver_name}_giving_{month_name}_{current_year}.pdf"'
    )

    # Create the PDF object
    pdf_canvas = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Set up the PDF document
    pdf_canvas.setTitle(f"{giver_name}'s Giving Report for {month_name} {current_year}")
    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(
        inch, height - inch, f"{giver_name}'s Giving Report for {month_name} {current_year}"
    )
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(inch, height - 1.2 * inch, "Thank you for your generosity!")

    y_position = height - 1.8 * inch

    # Add the weekly donations
    if givings_per_week:
        pdf_canvas.setFont("Helvetica-Bold", 12)
        pdf_canvas.drawString(inch, y_position, "Weekly Donations:")
        y_position -= 0.3 * inch
        pdf_canvas.setFont("Helvetica", 12)

        for giving_week in givings_per_week:
            week_number = giving_week['week']
            total_amount = giving_week['total_amount']
            week_start = timezone.datetime.strptime(
                f'{current_year} {week_number} 1', '%Y %W %w'
            )
            week_end = week_start + timedelta(days=6)
            week_range = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"

            pdf_canvas.drawString(
                inch, y_position, f"Week {week_number} ({week_range}): ${total_amount:.2f}"
            )
            y_position -= 0.2 * inch

            # Check if we need a new page
            if y_position < inch:
                pdf_canvas.showPage()
                pdf_canvas.setFont("Helvetica", 12)
                y_position = height - inch

    else:
        pdf_canvas.drawString(
            inch, y_position, "No donations recorded for this month."
        )

    # Finalize the PDF
    pdf_canvas.save()
    return response