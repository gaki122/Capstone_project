from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    total_points = models.IntegerField(default=0)
    total_stars = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    completed_levels = models.IntegerField(default=0)

    def __str__(self):
        return self.full_name