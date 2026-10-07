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


class Level1Result(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    score = models.IntegerField(default=0)

    total_questions = models.IntegerField(default=20)

    percentage = models.IntegerField(default=0)

    stars = models.IntegerField(default=1)

    completed = models.BooleanField(default=False)

    attempt_number = models.IntegerField(default=1)

    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - Level 1 - {self.score}/20"
