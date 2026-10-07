from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout

import secrets

from .models import (
    StudentProfile,
    Level1Result,
    GuestResult,
    TeacherProfile,
    ClassSection
)


# =========================
# Home
# =========================

def home(request):

    return render(
        request,
        'home.html'
    )


# =========================
# Learn
# =========================

def learn(request):

    return render(
        request,
        'learn.html'
    )


# =========================
# Learn - Text & ASCII
# =========================

def learn_text(request):

    return render(
        request,
        'learn_text.html'
    )


# =========================
# Learn - Images & Pixels
# =========================

def learn_images(request):

    return render(
        request,
        'learn_images.html'
    )


# =========================
# Learn - Audio & Sound
# =========================

def learn_audio(request):

    return render(
        request,
        'learn_audio.html'
    )


# =========================
# Learn - Video & Digital Media
# =========================

def learn_video(request):

    return render(
        request,
        'learn_video.html'
    )


# =========================
# How to Play
# =========================

def how_to_play(request):

    return render(
        request,
        'how_to_play.html'
    )


# =========================
# Student Registration
# =========================

def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        full_name = request.POST.get('full_name')

        # =========================
        # Check required fields
        # =========================

        if not username or not password or not full_name:

            return render(
                request,
                'register.html',
                {
                    'error':
                        'Please fill in all required fields.'
                }
            )

        # =========================
        # Check password
        # =========================

        if password != confirm_password:

            return render(
                request,
                'register.html',
                {
                    'error':
                        'Passwords do not match.'
                }
            )

        # =========================
        # Check username
        # =========================

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'register.html',
                {
                    'error':
                        'Username already exists. Please choose another username.'
                }
            )

        # =========================
        # Create Student Account
        # =========================

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.first_name = full_name
        user.save()

        StudentProfile.objects.create(
            user=user,
            full_name=full_name
        )

        login(
            request,
            user
        )

        return redirect(
            'student_dashboard'
        )

    return render(
        request,
        'register.html'
    )


# =========================
# Student Login
# =========================

def student_login(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # =========================
            # Make sure this is a student
            # =========================

            if StudentProfile.objects.filter(
                user=user
            ).exists():

                login(
                    request,
                    user
                )

                return redirect(
                    'student_dashboard'
                )

            return render(
                request,
                'login.html',
                {
                    'error':
                        'This is not a student account.'
                }
            )

        return render(
            request,
            'login.html',
            {
                'error':
                    'Invalid username or password.'
            }
        )

    return render(
        request,
        'login.html'
    )


# =========================
# Student Dashboard
# =========================

def student_dashboard(request):

    if not request.user.is_authenticated:

        return redirect(
            'student_login'
        )

    try:

        student_profile = StudentProfile.objects.get(
            user=request.user
        )

    except StudentProfile.DoesNotExist:

        return redirect(
            'student_login'
        )

    return render(
        request,
        'student_dashboard.html',
        {
            'student': student_profile
        }
    )


# ==========================================================
# STUDENT JOIN CLASS USING JOIN CODE
# ==========================================================

def join_section(request):

    if not request.user.is_authenticated:

        return redirect(
            'student_login'
        )

    try:

        student_profile = StudentProfile.objects.get(
            user=request.user
        )

    except StudentProfile.DoesNotExist:

        return redirect(
            'student_login'
        )

    # ======================================================
    # Student can join only ONE class
    # ======================================================

    if student_profile.class_section is not None:

        return render(
            request,
            'join_section.html',
            {
                'student': student_profile,
                'error':
                    'You have already joined a class.'
            }
        )

    # ======================================================
    # Process Join Code
    # ======================================================

    if request.method == 'POST':

        join_code = request.POST.get(
            'join_code'
        )

        # Remove unnecessary spaces
        # and convert code to uppercase

        if join_code:

            join_code = join_code.strip().upper()

        # ==================================================
        # Check whether code was entered
        # ==================================================

        if not join_code:

            return render(
                request,
                'join_section.html',
                {
                    'student': student_profile,
                    'error':
                        'Please enter the class code.'
                }
            )

        # ==================================================
        # Find class using join code
        # ==================================================

        try:

            section = ClassSection.objects.select_related(
                'teacher'
            ).get(
                join_code=join_code
            )

        except ClassSection.DoesNotExist:

            return render(
                request,
                'join_section.html',
                {
                    'student': student_profile,
                    'error':
                        'Invalid class code. Please check the code and try again.'
                }
            )

        # ==================================================
        # Final security check
        # ==================================================

        if student_profile.class_section is not None:

            return render(
                request,
                'join_section.html',
                {
                    'student': student_profile,
                    'error':
                        'You have already joined a class.'
                }
            )

        # ==================================================
        # Join Class
        # ==================================================

        student_profile.class_section = section

        student_profile.save()

        return redirect(
            'student_dashboard'
        )

    # ======================================================
    # Show Join Class Page
    # ======================================================

    return render(
        request,
        'join_section.html',
        {
            'student': student_profile
        }
    )


# =========================
# Student Logout
# =========================

def student_logout(request):

    logout(request)

    return redirect(
        'home'
    )


# =========================
# Level 1
# =========================

def level1(request):

    # =========================
    # Guest
    # =========================

    if not request.user.is_authenticated:

        return render(
            request,
            'level1.html'
        )

    # =========================
    # Registered Student
    # =========================

    try:

        student_profile = StudentProfile.objects.get(
            user=request.user
        )

    except StudentProfile.DoesNotExist:

        return redirect(
            'student_login'
        )

    # =========================
    # Student must join a class
    # =========================

    if student_profile.class_section is None:

        return redirect(
            'student_dashboard'
        )

    return render(
        request,
        'level1.html'
    )


# =========================
# Level 1 Game
# =========================

def level1_game(request):

    # =========================
    # Guest
    # =========================

    if not request.user.is_authenticated:

        return render(
            request,
            'level1_game.html'
        )

    # =========================
    # Registered Student
    # =========================

    try:

        student_profile = StudentProfile.objects.get(
            user=request.user
        )

    except StudentProfile.DoesNotExist:

        return redirect(
            'student_login'
        )

    # =========================
    # Student must join class
    # =========================

    if student_profile.class_section is None:

        return redirect(
            'student_dashboard'
        )

    return render(
        request,
        'level1_game.html'
    )


# =========================
# Save Level 1 Result
# =========================

def save_level1_result(request):

    if request.method != 'POST':

        return redirect(
            'level1_game'
        )

    # =========================
    # Get Result Information
    # =========================

    score = int(
        request.POST.get(
            'score',
            0
        )
    )

    total_questions = int(
        request.POST.get(
            'total_questions',
            20
        )
    )

    percentage = int(
        request.POST.get(
            'percentage',
            0
        )
    )

    stars = int(
        request.POST.get(
            'stars',
            1
        )
    )

    # =========================
    # Registered Student
    # =========================

    if request.user.is_authenticated:

        try:

            student_profile = StudentProfile.objects.get(
                user=request.user
            )

        except StudentProfile.DoesNotExist:

            return redirect(
                'student_login'
            )

        # =========================
        # Security Check
        # =========================

        if student_profile.class_section is None:

            return redirect(
                'student_dashboard'
            )

        # =========================
        # Count Previous Attempts
        # =========================

        previous_attempts = Level1Result.objects.filter(
            student=student_profile
        ).count()

        attempt_number = previous_attempts + 1

        # =========================
        # Save Result
        # =========================

        Level1Result.objects.create(
            student=student_profile,
            score=score,
            total_questions=total_questions,
            percentage=percentage,
            stars=stars,
            completed=True,
            attempt_number=attempt_number
        )

        # =========================
        # Update Statistics
        # =========================

        student_profile.total_points += score

        student_profile.total_stars += stars

        if student_profile.completed_levels < 1:

            student_profile.completed_levels = 1

        if score == total_questions:

            if score > student_profile.best_streak:

                student_profile.best_streak = score

        student_profile.save()

        return redirect(
            'student_dashboard'
        )

    # =========================
    # Guest Player
    # =========================

    if not request.session.session_key:

        request.session.create()

    session_key = request.session.session_key

    # =========================
    # Save Guest Result
    # =========================

    GuestResult.objects.create(
        session_key=session_key,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        stars=stars,
        completed=True
    )

    return redirect(
        'guest_result'
    )


# =========================
# Guest Result
# =========================

def guest_result(request):

    if not request.session.session_key:

        return redirect(
            'level1_game'
        )

    session_key = request.session.session_key

    result = GuestResult.objects.filter(
        session_key=session_key
    ).order_by(
        '-completed_at'
    ).first()

    if result is None:

        return redirect(
            'level1_game'
        )

    return render(
        request,
        'guest_result.html',
        {
            'result': result
        }
    )


# ==========================================================
# TEACHER REGISTRATION
# ==========================================================

def teacher_register(request):

    if request.method == 'POST':

        full_name = request.POST.get(
            'full_name'
        )

        username = request.POST.get(
            'username'
        )

        email = request.POST.get(
            'email'
        )

        password = request.POST.get(
            'password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        # =========================
        # Required Fields
        # =========================

        if not full_name or not username or not password:

            return render(
                request,
                'teacher_register.html',
                {
                    'error':
                        'Please fill in all required fields.'
                }
            )

        # =========================
        # Password Check
        # =========================

        if password != confirm_password:

            return render(
                request,
                'teacher_register.html',
                {
                    'error':
                        'Passwords do not match.'
                }
            )

        # =========================
        # Username Check
        # =========================

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'teacher_register.html',
                {
                    'error':
                        'Username already exists. Please choose another username.'
                }
            )

        # =========================
        # Create Teacher User
        # =========================

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.first_name = full_name

        user.save()

        # =========================
        # Create Teacher Profile
        # =========================

        TeacherProfile.objects.create(
            user=user,
            full_name=full_name
        )

        # =========================
        # Automatically Login
        # =========================

        login(
            request,
            user
        )

        return redirect(
            'teacher_dashboard'
        )

    return render(
        request,
        'teacher_register.html'
    )


# ==========================================================
# TEACHER LOGIN
# ==========================================================

def teacher_login(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # =========================
            # Check Teacher Account
            # =========================

            if TeacherProfile.objects.filter(
                user=user
            ).exists():

                login(
                    request,
                    user
                )

                return redirect(
                    'teacher_dashboard'
                )

            return render(
                request,
                'teacher_login.html',
                {
                    'error':
                        'This account is not a teacher account.'
                }
            )

        return render(
            request,
            'teacher_login.html',
            {
                'error':
                    'Invalid username or password.'
            }
        )

    return render(
        request,
        'teacher_login.html'
    )


# ==========================================================
# TEACHER DASHBOARD
# ==========================================================

def teacher_dashboard(request):

    if not request.user.is_authenticated:

        return redirect(
            'teacher_login'
        )

    try:

        teacher_profile = TeacherProfile.objects.get(
            user=request.user
        )

    except TeacherProfile.DoesNotExist:

        return redirect(
            'teacher_login'
        )

    # =========================
    # Only this teacher's classes
    # =========================

    classes = ClassSection.objects.filter(
        teacher=request.user
    ).order_by(
        'name'
    )

    return render(
        request,
        'teacher_dashboard.html',
        {
            'teacher': teacher_profile,
            'classes': classes,
        }
    )


# ==========================================================
# ADD NEW CLASS / SECTION
# ==========================================================

def add_class(request):

    if not request.user.is_authenticated:

        return redirect(
            'teacher_login'
        )

    try:

        TeacherProfile.objects.get(
            user=request.user
        )

    except TeacherProfile.DoesNotExist:

        return redirect(
            'teacher_login'
        )

    if request.method == 'POST':

        class_name = request.POST.get(
            'class_name'
        )

        if class_name:

            class_name = class_name.strip()

        # ==================================================
        # Check class name
        # ==================================================

        if not class_name:

            return render(
                request,
                'add_class.html',
                {
                    'error':
                        'Please enter a class or section name.'
                }
            )

        # ==================================================
        # Generate UNIQUE join code
        # ==================================================

        while True:

            join_code = secrets.token_hex(
                4
            ).upper()

            if not ClassSection.objects.filter(
                join_code=join_code
            ).exists():

                break

        # ==================================================
        # Create class
        # ==================================================

        ClassSection.objects.create(
            name=class_name,
            join_code=join_code,
            teacher=request.user
        )

        return redirect(
            'teacher_dashboard'
        )

    return render(
        request,
        'add_class.html'
    )


# ==========================================================
# VIEW STUDENTS IN CLASS
# ==========================================================

def view_students(request, class_id):

    if not request.user.is_authenticated:

        return redirect(
            'teacher_login'
        )

    try:

        TeacherProfile.objects.get(
            user=request.user
        )

    except TeacherProfile.DoesNotExist:

        return redirect(
            'teacher_login'
        )

    try:

        class_section = ClassSection.objects.get(
            id=class_id,
            teacher=request.user
        )

    except ClassSection.DoesNotExist:

        return redirect(
            'teacher_dashboard'
        )

    students = StudentProfile.objects.filter(
        class_section=class_section
    ).order_by(
        'full_name'
    )

    return render(
        request,
        'view_students.html',
        {
            'class_section': class_section,
            'students': students,
        }
    )


# ==========================================================
# ADD STUDENT TO CLASS
# ==========================================================

def add_student(request, class_id):

    if not request.user.is_authenticated:

        return redirect(
            'teacher_login'
        )

    try:

        TeacherProfile.objects.get(
            user=request.user
        )

    except TeacherProfile.DoesNotExist:

        return redirect(
            'teacher_login'
        )

    try:

        class_section = ClassSection.objects.get(
            id=class_id,
            teacher=request.user
        )

    except ClassSection.DoesNotExist:

        return redirect(
            'teacher_dashboard'
        )

    if request.method == 'POST':

        full_name = request.POST.get(
            'full_name'
        )

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        if full_name and username and password:

            # =========================
            # Prevent duplicate username
            # =========================

            if User.objects.filter(
                username=username
            ).exists():

                return render(
                    request,
                    'add_student.html',
                    {
                        'class_section':
                            class_section,
                        'error':
                            'Username already exists.'
                    }
                )

            user = User.objects.create_user(
                username=username,
                password=password
            )

            user.first_name = full_name

            user.save()

            StudentProfile.objects.create(
                user=user,
                full_name=full_name,
                class_section=class_section
            )

            return redirect(
                'view_students',
                class_id=class_section.id
            )

    return render(
        request,
        'add_student.html',
        {
            'class_section': class_section
        }
    )


# ==========================================================
# TEACHER LOGOUT
# ==========================================================

def teacher_logout(request):

    logout(request)

    return redirect(
        'teacher_login'
    )


# ==========================================================
# VIEW INDIVIDUAL STUDENT PROGRESS
# ==========================================================

def student_progress(request, student_id):

    if not request.user.is_authenticated:

        return redirect(
            'teacher_login'
        )

    try:

        TeacherProfile.objects.get(
            user=request.user
        )

    except TeacherProfile.DoesNotExist:

        return redirect(
            'teacher_login'
        )

    # =========================
    # Security:
    # Teacher can only view
    # students belonging to
    # their own sections.
    # =========================

    try:

        student = StudentProfile.objects.get(
            id=student_id,
            class_section__teacher=request.user
        )

    except StudentProfile.DoesNotExist:

        return redirect(
            'teacher_dashboard'
        )

    results = Level1Result.objects.filter(
        student=student
    ).order_by(
        '-completed_at'
    )

    return render(
        request,
        'student_progress.html',
        {
            'student': student,
            'results': results,
        }
    )