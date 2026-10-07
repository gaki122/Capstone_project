from django.db import models
from django.contrib.auth.models import User


# =========================
# Teacher Profile
# =========================

class TeacherProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.full_name


# =========================
# Class Section
# =========================

class ClassSection(models.Model):

    name = models.CharField(
        max_length=100
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='classes_taught'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


# =========================
# Student Profile
# =========================

class StudentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=100
    )

    # Student can belong to only ONE section.
    # It stays empty until the student joins
    # a section after logging in.
    class_section = models.ForeignKey(
        'ClassSection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    total_points = models.IntegerField(
        default=0
    )

    total_stars = models.IntegerField(
        default=0
    )

    best_streak = models.IntegerField(
        default=0
    )

    completed_levels = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.full_name


# =========================
# Level 1 Result
# =========================

class Level1Result(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    score = models.IntegerField(
        default=0
    )

    total_questions = models.IntegerField(
        default=20
    )

    percentage = models.IntegerField(
        default=0
    )

    stars = models.IntegerField(
        default=1
    )

    completed = models.BooleanField(
        default=False
    )

    attempt_number = models.IntegerField(
        default=1
    )

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.student.full_name} "
            f"- Level 1 - "
            f"{self.score}/20"
        )


# =========================
# Guest Result
# =========================

class GuestResult(models.Model):

    # Used to identify the guest's browser session.
    # Guest results are NOT connected to any student
    # or teacher account.
    session_key = models.CharField(
        max_length=100
    )

    score = models.IntegerField(
        default=0
    )

    total_questions = models.IntegerField(
        default=20
    )

    percentage = models.IntegerField(
        default=0
    )

    stars = models.IntegerField(
        default=1
    )

    completed = models.BooleanField(
        default=False
    )

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Guest - "
            f"{self.score}/"
            f"{self.total_questions}"
        )