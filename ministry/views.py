from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import  MinisterForm, ScheduleForm, MinistryFilterForm, AvailabilityForm, DateFilterForm
from .models import Schedule,  Minister
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, TemplateView
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.views.generic.edit import UpdateView
from django.views import View
from django.views.generic.detail import DetailView
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Schedule, Minister, Ministry, Availability
import json
from schedule.models import Event
import pandas as pd


logger = logging.getLogger(__name__)




class MinisterManageView(View):
    template_name = 'ministries/add_minister.html'
    form_class = MinisterForm
    success_url = reverse_lazy('ministers_list')

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            minister = get_object_or_404(Minister, pk=pk)
            form = self.form_class(instance=minister)
        else:
            form = self.form_class()
            minister = None
        return render(request, self.template_name, {'form': form, 'minister': minister})

    def post(self, request, pk=None, *args, **kwargs):
        if pk:
            minister = get_object_or_404(Minister, pk=pk)
        else:
            minister = None

        if "delete" in request.POST and minister:
            minister.delete()
            return redirect(self.success_url)

        form = self.form_class(request.POST, request.FILES, instance=minister)
        if form.is_valid():
            form.save()
            return redirect(self.success_url)

        return render(request, self.template_name, {'form': form, 'minister': minister})
    
class ScheduleListView(ListView):
    model = Schedule
    template_name = 'schedule_calendar.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        return Schedule.objects.select_related('minister', 'ministry')


def update_schedule(request):
    data = json.loads(request.body)
    schedule_id = data.get('id')
    start = data.get('start')
    end = data.get('end')

    schedule = get_object_or_404(Schedule, id=schedule_id)
    schedule.start_time = start
    schedule.end_time = end
    schedule.save()

    return JsonResponse({'status': 'success'})
class MinisterSuccessView(TemplateView):
    template_name = 'ministries/add_minister_success.html'


class ScheduleCreateView(View):
    template_name = 'ministries/schedule_form.html'

    def get(self, request, *args, **kwargs):
        form = ScheduleForm()
        date_filter_form = DateFilterForm(request.GET)
        ministries = Ministry.objects.prefetch_related('ministers').all()
        schedules = Schedule.objects.all()

        if date_filter_form.is_valid():
            filter_date = date_filter_form.cleaned_data['date']
            schedules = schedules.filter(start_time__date=filter_date)
        
        return render(request, self.template_name, {
            'form': form,
            'date_filter_form': date_filter_form,
            'ministries': ministries,
            'schedules': schedules
        })

    def post(self, request, *args, **kwargs):
        logger.info("POST request received for ScheduleCreateView")
        form = ScheduleForm(request.POST)
        if form.is_valid():
            logger.info("Form is valid")
            form.save()
        
        else:
            logger.error("Form is not valid: %s", form.errors)
        
        date_filter_form = DateFilterForm()
        ministries = Ministry.objects.prefetch_related('ministers').all()
        schedules = Schedule.objects.all()
        
        return render(request, self.template_name, {
            'form': form,
            'date_filter_form': date_filter_form,
            'ministries': ministries,
            'schedules': schedules
        })
    
    

def load_schedules(request):
    schedules = Schedule.objects.all()
    events = []
    for schedule in schedules:
        events.append({
            'title': f"{schedule.ministry.name} - {schedule.minister.first_name}",
            'start': schedule.event.start.isoformat(),
            'end': schedule.event.end.isoformat(),
            'url': f"/schedule/{schedule.id}/"  # URL to edit or view details
        })
    return JsonResponse(events, safe=False)

class CalendarView(View):
    template_name = 'calendar.html'

    def get(self, request, *args, **kwargs):
        schedules = Schedule.objects.all()
        form = ScheduleForm()
        return render(request, self.template_name, {'schedules': schedules, 'form': form})

@method_decorator(csrf_exempt, name='dispatch')
class GetSchedulesView(View):
    def get(self, request, *args, **kwargs):
        schedules = Schedule.objects.all()
        events = []
        for schedule in schedules:
            events.append({
                'id': schedule.id,
                'title': f"{schedule.ministry.name} - {schedule.minister.first_name} {schedule.minister.last_name}",
                'start': schedule.event.start.isoformat(),
                'end': schedule.event.end.isoformat(),
                'location': schedule.location,
                'duties': schedule.duties,
            })
        return JsonResponse(events, safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class UpdateScheduleView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        schedule_id = data.get('id')
        schedule = get_object_or_404(Schedule, id=schedule_id)
        schedule.event.start = data.get('start')
        schedule.event.end = data.get('end')
        schedule.event.save()
        return JsonResponse({'status': 'success'})
    
class MinistryListView(ListView):
    model = Minister
    template_name = 'ministries/ministry_list.html'
    context_object_name = 'ministers'

    def get_queryset(self):
        queryset = super().get_queryset()
        ministry_id = self.request.GET.get('ministry')
        if ministry_id:
            queryset = queryset.filter(ministry__id=ministry_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MinistryFilterForm(self.request.GET or None)
        return context

class MinisterDetailView(DetailView):
    model = Minister
    template_name = 'ministries/minister_detail.html'
    context_object_name = 'minister'

    def post(self, request, *args, **kwargs):
        if "delete" in request.POST:
            minister = self.get_object()
            minister.delete()
            return redirect('ministers_list')
        return super().get(request, *args, **kwargs)

class MinisterUpdateView(UpdateView):
    model = Minister
    fields = ['first_name', 'last_name', 'email', 'position', 'phone_number', 'address']
    template_name = 'minister_update_form.html'
    success_url = reverse_lazy('ministers_list')


def schedule_calendar(request):
    return render(request, 'ministries/schedule_calendar.html')

def minister_detail(request, pk):
    minister = get_object_or_404(Minister, pk=pk)
    data = {
        'first_name': minister.first_name,
        'last_name': minister.last_name,
        'age': minister.age,
        'is_youth_minister': minister.is_youth_minister,
        'position': minister.position,
        'email': minister.email,
        'start_date': minister.start_date,
        'disciples': minister.disciples,
        'phone_number': minister.phone_number,
        'address': minister.address,
        'profile_image': minister.profile_image.url if minister.profile_image else '',
        'ministry': {'name': minister.ministry.name}
    }
    return JsonResponse(data)


class AvailabilityView(View):
    template_name = 'availability.html'

    def get(self, request, *args, **kwargs):
        form = AvailabilityForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('availability')
        return render(request, self.template_name, {'form': form})
    
def get_schedules(request):
    schedules = Schedule.objects.select_related('minister', 'ministry').all()
    schedule_list = []
    for schedule in schedules:
        schedule_list.append({
            'id': schedule.id,
            'title': f'{schedule.minister.first_name} {schedule.minister.last_name} - {schedule.ministry.name}',
            'start': schedule.start_time.isoformat(),
            'end': schedule.end_time.isoformat(),
            'location': schedule.location,
            'duties': schedule.duties,
            'ministry': {'id': schedule.ministry.id, 'name': schedule.ministry.name},
            'minister': {'id': schedule.minister.id, 'first_name': schedule.minister.first_name, 'last_name': schedule.minister.last_name}
        })
    return JsonResponse(schedule_list, safe=False)

def update_schedule(request):
    data = json.loads(request.body)
    schedule_id = data.get('id')
    start = data.get('start')
    end = data.get('end')

    schedule = get_object_or_404(Schedule, id=schedule_id)
    schedule.start_time = start
    schedule.end_time = end
    schedule.save()

    return JsonResponse({'status': 'success'})

class ScheduleView(View):
    template_name = 'ministries/schedule_calendar.html'

    def get(self, request, *args, **kwargs):
        form = ScheduleForm()
        schedules = Schedule.objects.all()
        return render(request, self.template_name, {'form': form, 'schedules': schedules})

    def post(self, request, *args, **kwargs):
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('schedule_calendar')
        schedules = Schedule.objects.all()
        return render(request, self.template_name, {'form': form, 'schedules': schedules})

def export_attendance_to_excel(request):
    # Query the schedules from the database
    schedules = Schedule.objects.all()
    
    # Create a DataFrame
    data = []
    for schedule in schedules:
        data.append({
            "Minister": f"{schedule.minister.first_name} {schedule.minister.last_name}",
            "Ministry": schedule.ministry.name,
            "Location": schedule.location,
            "Duties": schedule.duties,
            "Start Time": schedule.start_time.replace(tzinfo=None),  # Make datetime naive
            "End Time": schedule.end_time.replace(tzinfo=None),      # Make datetime naive
            "Attended": schedule.attended,
        })

    df = pd.DataFrame(data)


    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=attendance.xlsx'

    # Use pandas to create an Excel writer
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')

    return response


class ScheduleUpdateView(UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'ministries/schedule_form.html'
    success_url = reverse_lazy('schedule_create')


class ScheduleDeleteView(View):
    def post(self, request, pk, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=pk)
        schedule.delete()
        return redirect('schedule_create')

