from django.db import models

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
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE)
    minister = models.ForeignKey(Minister, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    duties = models.TextField(default="")
    attended = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class Availability(models.Model):
    minister = models.ForeignKey(Minister, on_delete=models.CASCADE)
    day = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
