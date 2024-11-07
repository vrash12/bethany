#ministry/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from datetime import date, time

class Minister(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    is_youth_minister = models.BooleanField(default=False)
    position = models.CharField(max_length=50)
    email = models.EmailField()
    profile_image = models.ImageField(upload_to='ministers/', null=True)
    start_date = models.DateField(null=True)
    disciples = models.IntegerField(default=0)
    phone_number = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=100, blank=True)
    ministry = models.ForeignKey('Ministry', on_delete=models.CASCADE, related_name='ministers', default=1)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='minister_profile', null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {'Youth' if self.is_youth_minister else 'Adult'}"

class Ministry(models.Model):
    MINISTRY_CHOICES = [
        ('Worship', 'Worship'),
        ('Production', 'Production'),
        ('Real Life', 'Real Life'),
        ('Campus', 'Campus'),
        ('Multimedia', 'Multimedia'),
        ('OPS', 'OPS'),
    ]
    
    name = models.CharField(max_length=50, choices=MINISTRY_CHOICES, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Schedule(models.Model):
    TIME_SLOT_CHOICES = [
        ('7am-9am', '7am-9am'),
        ('9am-11am', '9am-11am'),
        ('1pm-3pm', '1pm-3pm'),
    ]

    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE)
    minister = models.ForeignKey(Minister, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=100)
    duties = models.TextField(default="")
    attended = models.BooleanField(default=False)
    date = models.DateField(default=date.today)
    time_slot = models.CharField(
        max_length=10,
        choices=TIME_SLOT_CHOICES,
        default='7am-9am'
    )
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.time_slot:
            time_mapping = {
                '7am-9am': (time(7, 0), time(9, 0)),
                '9am-11am': (time(9, 0), time(11, 0)),
                '1pm-3pm': (time(13, 0), time(15, 0)),
            }
            times = time_mapping.get(self.time_slot)
            if times:
                self.start_time, self.end_time = times
        super(Schedule, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.minister} - {self.ministry} on {self.date} from {self.start_time} to {self.end_time}"
class Availability(models.Model):
    minister = models.ForeignKey(Minister, on_delete=models.CASCADE)
    day = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
