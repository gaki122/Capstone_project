
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

    # Unique code students use to join a section.
    join_code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
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

    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=20)
    percentage = models.IntegerField(default=0)
    stars = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.student.full_name} "
            f"- Level 1 - "
            f"{self.score}/{self.total_questions}"
        )


# =========================
# Guest Result - Level 1
# =========================

class GuestResult(models.Model):

    session_key = models.CharField(
        max_length=100
    )

    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=20)
    percentage = models.IntegerField(default=0)
    stars = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Guest - "
            f"{self.score}/"
            f"{self.total_questions}"
        )


# =========================
# Final Challenge Result
# =========================


# =========================
# Final Challenge Result
# =========================

class FinalChallengeResult(models.Model):

    # One student can have only one Final Challenge result.
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE
    )

    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=25)
    percentage = models.IntegerField(default=0)
    stars = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)

    # Permanently stored overall result.
    # These values will not change when students
    # replay Levels 1, 2, 3, or 4.
    overall_correct = models.IntegerField(
        null=True,
        blank=True
    )

    overall_possible = models.IntegerField(
        null=True,
        blank=True
    )

    overall_percentage = models.FloatField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.student.full_name} "
            f"- Final Challenge - "
            f"{self.score}/{self.total_questions}"
        )



# =========================
# Guest Final Challenge Result
# =========================

class GuestFinalChallengeResult(models.Model):

    session_key = models.CharField(
        max_length=100,
        unique=True
    )

    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=25)
    percentage = models.IntegerField(default=0)
    stars = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Guest Final Challenge - "
            f"{self.score}/{self.total_questions}"
        )


# =========================
# Level 2 Result
# =========================

class Level2Result(models.Model):

    # Registered student results are linked to a student.
    # Guest results can be identified by their session key.
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=20)
    percentage = models.IntegerField(default=0)
    stars = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        if self.student:
            name = self.student.full_name
        else:
            name = "Guest"

        return (
            f"{name} - Level 2 - "
            f"{self.score}/{self.total_questions}"
        )


# =========================
# Level 3 Result
# =========================

class Level3Result(models.Model):

    # Registered student results
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Guest player results
    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=20)
    percentage = models.IntegerField(default=0)
    stars = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        if self.student:
            name = self.student.full_name
        else:
            name = "Guest"

        return (
            f"{name} - Level 3 - "
            f"{self.score}/{self.total_questions}"
        )




# =========================
# Level 4 Result
# =========================

class Level4Result(models.Model):

    # Registered student results
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Guest player results
    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=20)
    percentage = models.IntegerField(default=0)
    stars = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)

    completed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        if self.student:
            name = self.student.full_name
        else:
            name = "Guest"

        return (
            f"{name} - Level 4 - "
            f"{self.score}/{self.total_questions}"
        )
