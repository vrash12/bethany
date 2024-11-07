from django import forms
from .models import Schedule, Minister, Ministry, Availability


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['minister', 'day', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class MinisterForm(forms.ModelForm):
    ministry = forms.ModelChoiceField(
        queryset=Ministry.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Minister
        fields = [
            'first_name', 'last_name', 'age', 'is_youth_minister', 'position', 
            'email', 'profile_image', 'start_date', 'disciples', 'phone_number', 
            'address', 'ministry'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_youth_minister': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'disciples': forms.NumberInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ScheduleForm(forms.ModelForm):
    time_slot = forms.ChoiceField(
        choices=Schedule.TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Time Slot'
    )


    class Meta:
        model = Schedule
        fields = ['ministry', 'minister', 'location', 'duties', 'date', 'time_slot', 'attended']
        widgets = {
            'ministry': forms.Select(attrs={'class': 'form-control'}),
            'minister': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'duties': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class DateFilterForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Filter by Date'
    )

class MinistryFilterForm(forms.Form):
    ministry = forms.ModelChoiceField(
        queryset=Ministry.objects.all(),
        label="Filter by Ministry",
        required=False,
        empty_label="Choose a Ministry"
    )
