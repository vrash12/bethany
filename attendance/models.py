#attendance/models.py
from django.db import models
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ValidationError
from ministry.models import Minister
from django.contrib.auth.models import User


class Service(models.Model):
    name = models.CharField(max_length=100)
    time = models.IntegerField(choices=(
        (7, '7 AM - General Service'),
        (9, '9 AM - General Service'),
        (13, '1 PM - Youth Service'),
        (1, 'Others - Campus Service'),
    ))


    def __str__(self):
        return f"{self.name} at {self.get_time_display()}"


class Member(models.Model):
    GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ]

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField()
    age = models.IntegerField()
    fb_name = models.CharField(max_length=255, blank=True, null=True)
    invited_by = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=255, blank=True, null=True)
    is_youth = models.BooleanField(default=False)
    school = models.CharField(max_length=255, blank=True, null=True)
    course = models.CharField(max_length=255, blank=True, null=True)
    is_newcomer = models.BooleanField(default=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"


class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)  # Allow null temporarily
    status = models.BooleanField(default=False)

    def __str__(self):
        service_str = self.service.name if self.service else "No Service"
        return f"{self.member} - {service_str} - {self.date} - {'Present' if self.status else 'Absent'}"


class MinisterAttendance(models.Model):
    minister = models.ForeignKey('ministry.Minister', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        service_str = self.service.name if self.service else "No Service"
        return f"{self.minister} - {service_str} - {self.date} - {'Present' if self.status else 'Absent'}"


class SmallGroup(models.Model):
    name = models.CharField(max_length=100)
    leader = models.ForeignKey('ministry.Minister', on_delete=models.CASCADE, related_name='leading_groups')

    def __str__(self):
        return self.name


class SmallGroupMembership(models.Model):
    small_group = models.ForeignKey(SmallGroup, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    minister = models.ForeignKey('ministry.Minister', on_delete=models.CASCADE, null=True, blank=True)
    joined_at = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('small_group', 'member', 'minister')

    def __str__(self):
        if self.member:
            return f"{self.member} - {self.small_group.name}"
        elif self.minister:
            return f"{self.minister} - {self.small_group.name}"


class SmallGroupAttendance(models.Model):
    small_group = models.ForeignKey(SmallGroup, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    members = models.ManyToManyField(Member, blank=True)
    ministers = models.ManyToManyField(Minister, blank=True)
    attended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.small_group.name} - {self.date} - {'Attended' if self.attended else 'Absent'}"



class Giving(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    minister = models.ForeignKey(Minister, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    purpose = models.CharField(max_length=255, choices=(
        ('tithe', 'Tithe'),
        ('offering', 'Offering'),
        ('donation', 'Donation'),
        ('other', 'Other'),
    ))
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.member or self.minister} - {self.amount} - {self.purpose} on {self.date}"