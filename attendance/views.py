from django.shortcuts import render, redirect, get_object_or_404
from .forms import MemberForm, LoginForm, SmallGroupForm, SmallGroupAttendanceForm, GivingForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator

from ministry.models import Ministry, Minister
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponseNotAllowed, JsonResponse
from django.db.models.functions import Cast

from .models import Attendance, Service, Attendance, MinisterAttendance, SmallGroup, Member,  SmallGroupMembership, SmallGroupAttendance, Giving
from django.utils import timezone
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.db.models import IntegerField
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.views.generic import ListView
from django.db.models import Q
from django.core.serializers import serialize
import json
import io
import matplotlib.pyplot as plt
import logging
from datetime import datetime, timedelta
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.generic import View
from django.db.models import Avg
import pandas as pd
from django.forms import modelformset_factory
from .forms import SmallGroupMembershipForm
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

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



@login_required
def home(request):
    today = timezone.now().date()
    days_to_last_sunday = (today.weekday() + 1) % 7
    if days_to_last_sunday == 0:
        days_to_last_sunday = 7
    last_sunday = today - timedelta(days=days_to_last_sunday)

    total_attendance = Attendance.objects.filter(status=True).count()
    average_attendance = Attendance.objects.annotate(
        status_int=Cast('status', IntegerField())
    ).aggregate(average=Avg('status_int'))['average']

    small_group_stats = SmallGroupAttendance.objects.values('small_group__name').annotate(
        total_attendance=Count('id'),
        average_attendance=Avg('attended')
    ).order_by('-total_attendance')

    context = {
        'total_attendance': total_attendance,
        'average_attendance': average_attendance,
        'last_sunday': last_sunday,
        'small_group_stats': small_group_stats
    }

    return render(request, 'attendance/home.html', context)



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
    # Fetch all members from the database
    members = Member.objects.all().values()
    # Create a DataFrame
    df = pd.DataFrame(members)
    # Create a Pandas Excel writer using openpyxl as the engine
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
        attendance_date = request.POST.get('attendance_date', timezone.now().date().isoformat())
        service_id = request.POST.get('service')
        present_ids = request.POST.getlist('present_members')  # This will now include both members and ministers

        try:
            service = Service.objects.get(id=service_id)
            all_members = Member.objects.all()
            all_ministers = Minister.objects.all()

            with transaction.atomic():
                existing_attendances = Attendance.objects.filter(date=attendance_date, service=service)
                existing_members_ids = set(existing_attendances.values_list('member_id', flat=True))

                for member in all_members:
                    status = f"member_{member.id}" in present_ids

                    if member.id in existing_members_ids:
                        Attendance.objects.filter(member=member, date=attendance_date, service=service).update(status=status)
                    else:
                        Attendance.objects.create(member=member, date=attendance_date, service=service, status=status)

                existing_minister_attendances = MinisterAttendance.objects.filter(date=attendance_date, service=service)
                existing_ministers_ids = set(existing_minister_attendances.values_list('minister_id', flat=True))

                for minister in all_ministers:
                    status = f"minister_{minister.id}" in present_ids

                    if minister.id in existing_ministers_ids:
                        MinisterAttendance.objects.filter(minister=minister, date=attendance_date, service=service).update(status=status)
                    else:
                        MinisterAttendance.objects.create(minister=minister, date=attendance_date, service=service, status=status)

            messages.success(request, 'Attendance successfully updated.')
            return redirect('attendance_success')

        except Service.DoesNotExist:
            messages.error(request, 'Selected service does not exist.')
        except Exception as e:
            messages.error(request, f'An error occurred while processing attendance: {str(e)}')

    else:
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
    # Sample data: Count of present members per service
    services = Service.objects.all()
    service_names = [service.name for service in services]
    attendance_counts = [Attendance.objects.filter(service=service, status=True).count() for service in services]

    plt.figure(figsize=(10, 5))
    plt.bar(service_names, attendance_counts, color='skyblue')
    plt.xlabel('Services')
    plt.ylabel('Number of Attendees')
    plt.title('Attendance per Service')

    # Save it to a bytes buffer rather than a file
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()

    # Rewind the buffer
    buf.seek(0)

    # Construct a server response
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
    filter_date = request.GET.get('filter_date')
    if not filter_date:
        logger.error("Date parameter is missing")
        return JsonResponse({'status': 'error', 'message': 'Date parameter is missing'}, status=400)
    
    try:
        member_attendance_records = Attendance.objects.filter(date=filter_date).select_related('member', 'service')
        minister_attendance_records = MinisterAttendance.objects.filter(date=filter_date).select_related('minister', 'service')

        records = []

        for record in member_attendance_records:
            if record.member:
                member_name = f"{record.member.first_name} {record.member.last_name}"
                member_id = record.member.id
            else:
                member_name = 'Unknown'
                member_id = 'undefined'
                logger.warning(f"Member is undefined for record with date {record.date}")

            service_name = record.service.name if record.service else 'N/A'
            if not record.service:
                logger.warning(f"Service is undefined for member {member_name} on date {record.date}")

            status = 'Present' if record.status else 'Absent'
            records.append({
                'id': f"member_{member_id}",
                'name': member_name,
                'date': record.date.strftime('%Y-%m-%d'),
                'service': service_name,
                'status': status,
                'type': 'Member'
            })

        for record in minister_attendance_records:
            if record.minister:
                minister_name = f"{record.minister.first_name} {record.minister.last_name}"
                minister_id = record.minister.id
            else:
                minister_name = 'Unknown'
                minister_id = 'undefined'
                logger.warning(f"Minister is undefined for record with date {record.date}")

            service_name = record.service.name if record.service else 'N/A'
            if not record.service:
                logger.warning(f"Service is undefined for minister {minister_name} on date {record.date}")

            status = 'Present' if record.status else 'Absent'
            records.append({
                'id': f"minister_{minister_id}",
                'name': minister_name,
                'date': record.date.strftime('%Y-%m-%d'),
                'service': service_name,
                'status': status,
                'type': 'Minister'
            })

        logger.debug(f"Records fetched: {records}")
        return JsonResponse({'status': 'ok', 'data': records})
    
    except Exception as e:
        logger.error(f"Error fetching attendance records: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    

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

    logger.info(f"Received member ID: {member_id}")  # Log the received ID for debugging

    try:
        # Validate if member_id is an integer
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
def small_group_list_create(request, pk=None):
    query = request.GET.get('q')
    page_number = request.GET.get('page')

    if query:
        small_groups = SmallGroup.objects.filter(name__icontains=query)
    else:
        small_groups = SmallGroup.objects.all()

    paginator = Paginator(small_groups, 5)  # 5 items per page
    page_obj = paginator.get_page(page_number)

    if pk:
        group = get_object_or_404(SmallGroup, pk=pk)
    else:
        group = None

    if request.method == 'POST':
        group_form = SmallGroupForm(request.POST, instance=group)
        
        if group_form.is_valid():
            group = group_form.save()
            group.memberships.all().delete()  # Clear existing memberships

            for member in group_form.cleaned_data['members']:
                SmallGroupMembership.objects.create(small_group=group, member=member)

            for minister in group_form.cleaned_data['ministers']:
                SmallGroupMembership.objects.create(small_group=group, minister=minister)

            return redirect('small_group_list_create')
    else:
        group_form = SmallGroupForm(instance=group)
        if group:
            group_form.fields['members'].initial = group.memberships.filter(member__isnull=False).values_list('member', flat=True)
            group_form.fields['ministers'].initial = group.memberships.filter(minister__isnull=False).values_list('minister', flat=True)
    
    attendance_form = SmallGroupAttendanceForm()
    attendance_list = SmallGroupAttendance.objects.all()

    return render(request, 'attendance/small_group_crud.html', {
        'group_form': group_form,
        'attendance_form': attendance_form,
        'page_obj': page_obj,
        'edit_group': group,
        'attendance_list': attendance_list,
    })

def small_group_delete(request, pk):
    group = get_object_or_404(SmallGroup, pk=pk)
    group.delete()
    return redirect('small_group_list_create')

def record_attendance(request):
    if request.method == 'POST':
        form = SmallGroupAttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)  # Don't save to database yet
            small_group_id = request.POST.get('small_group_id')
            if small_group_id:
                small_group = get_object_or_404(SmallGroup, pk=small_group_id)
                attendance.small_group = small_group  # Set the small group
                attendance.save()  # Save the attendance to the database
                # Add members and ministers to the many-to-many fields
                for member in form.cleaned_data['members']:
                    attendance.members.add(member)
                for minister in form.cleaned_data['ministers']:
                    attendance.ministers.add(minister)
                return redirect('small_group_list_create')
            else:
                return render(request, 'attendance/small_group_crud.html', {
                    'attendance_form': form,
                    'error': 'Small group ID not found'
                })
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