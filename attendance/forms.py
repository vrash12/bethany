#attendance/forms.py
from django import forms
from .models import Member, Attendance, Service, SmallGroup, SmallGroupMembership, SmallGroupAttendance, Giving
from ministry.models import Minister
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'middle_name', 'birthday', 'fb_name', 'invited_by', 'address', 'contact_number', 'is_youth', 'school', 'course', 'is_newcomer', 'gender']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fb_name': forms.TextInput(attrs={'class': 'form-control'}),
            'invited_by': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_youth': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'is_newcomer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gender' : forms.Select(attrs={'class': 'form-control'}),
        }
        def __init__(self, *args, **kwargs):
            super(MemberForm, self).__init__(*args, **kwargs)
            if self.instance and self.instance.user:
                self.fields['first_name'].initial = self.instance.user.first_name
                self.fields['last_name'].initial = self.instance.user.last_name

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['service', 'member', 'status', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'service': forms.Select(),
            'member': forms.CheckboxSelectMultiple(),
            'status': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AttendanceForm, self).__init__(*args, **kwargs)
        members = Member.objects.all()
        ministers = Minister.objects.all()
        
        # Combine members and ministers into a single queryset-like structure
        combined_choices = [
            (f"member_{member.id}", f"{member.first_name} {member.last_name} (Member)")
            for member in members
        ] + [
            (f"minister_{minister.id}", f"{minister.first_name} {minister.last_name} (Minister)")
            for minister in ministers
        ]
        
        self.fields['member'].choices = combined_choices
        self.fields['service'].queryset = Service.objects.all()
        self.fields['status'].initial = True  # Assuming marking presence


class DateFilterForm(forms.Form):
    filter_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class AttendanceGraphFilterForm(forms.Form):
    start_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)



class SmallGroupForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=Member.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    ministers = forms.ModelMultipleChoiceField(
        queryset=Minister.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = SmallGroup
        fields = ['name', 'leader', 'members', 'ministers']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'leader': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SmallGroupForm, self).__init__(*args, **kwargs)
        self.fields['members'].queryset = Member.objects.all()
        self.fields['ministers'].queryset = Minister.objects.all()

        # Debugging: Print minister queryset in form
        print("Ministers queryset in form: ", self.fields['ministers'].queryset)


class SmallGroupMembershipForm(forms.ModelForm):
    class Meta:
        model = SmallGroupMembership
        fields = ['member', 'minister']

        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'minister': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SmallGroupMembershipForm, self).__init__(*args, **kwargs)
        self.fields['member'].queryset = Member.objects.all()
        self.fields['minister'].queryset = Minister.objects.all()


class SmallGroupAttendanceForm(forms.ModelForm):
    class Meta:
        model = SmallGroupAttendance
        fields = ['date', 'attended', 'image']  # Include the image field
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'attended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),  # New widget
        }


class GivingForm(forms.ModelForm):
    GIVER_CHOICES = [
        ('member', 'Member'),
        ('minister', 'Minister'),
    ]

    giver_type = forms.ChoiceField(choices=GIVER_CHOICES, required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        model = Giving
        fields = ['giver_type', 'member', 'minister', 'date', 'amount', 'purpose', 'notes']

    def __init__(self, *args, **kwargs):
        super(GivingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'giver_type',
            'member',
            'minister',
            'date',
            'amount',
            'purpose',
            'notes',
        )



class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')