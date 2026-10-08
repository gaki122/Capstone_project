from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout

import secrets

from .models import (
    StudentProfile,
    Level1Result,
    GuestResult,
    TeacherProfile,
    ClassSection,
    FinalChallengeResult,
    GuestFinalChallengeResult
)


# ==========================================================
# HOME
# ==========================================================

def home(request):

    return render(
        request,
        'home.html'
    )


# ==========================================================
# LEARN
# ==========================================================

def learn(request):

    return render(
        request,
        'learn.html'
    )


# ==========================================================
# LEARN - TEXT
# ==========================================================

def learn_text(request):

    return render(
        request,
        'learn_text.html'
    )


# ==========================================================
# LEARN - IMAGES
# ==========================================================

def learn_images(request):

    return render(
        request,
        'learn_images.html'
    )


# ==========================================================
# LEARN - AUDIO
# ==========================================================

def learn_audio(request):

    return render(
        request,
        'learn_audio.html'
    )


# ==========================================================
# LEARN - VIDEO
# ==========================================================

def learn_video(request):

    return render(
        request,
        'learn_video.html'
    )


# ==========================================================
# HOW TO PLAY
# ==========================================================

def how_to_play(request):

    return render(
        request,
        'how_to_play.html'
    )


# ==========================================================
# STUDENT REGISTRATION
# ==========================================================

def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        full_name = request.POST.get('full_name')

        if not username or not password or not full_name:

            return render(
                request,
                'register.html',
                {
                    'error':
                        'Please fill in all required fields.'
                }
            )

        if password != confirm_password:

            return render(
                request,
                'register.html',
                {
                    'error':
                        'Passwords do not match.'
                }
            )

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


# ==========================================================
# STUDENT LOGIN
# ==========================================================

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


# ==========================================================
# STUDENT DASHBOARD
# ==========================================================

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

    results = Level1Result.objects.filter(
        student=student_profile
    ).order_by(
        '-completed_at'
    )

    final_result = FinalChallengeResult.objects.filter(
        student=student_profile
    ).first()

    return render(
        request,
        'student_dashboard.html',
        {
            'student': student_profile,
            'results': results,
            'final_result': final_result,
        }
    )


# ==========================================================
# JOIN CLASS
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

    if request.method == 'POST':

        join_code = request.POST.get(
            'join_code'
        )

        if join_code:

            join_code = join_code.strip().upper()

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

        try:

            section = ClassSection.objects.get(
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

        student_profile.class_section = section

        student_profile.save()

        return redirect(
            'student_dashboard'
        )

    return render(
        request,
        'join_section.html',
        {
            'student': student_profile
        }
    )


# ==========================================================
# STUDENT LOGOUT
# ==========================================================

def student_logout(request):

    logout(request)

    return redirect(
        'home'
    )


# ==========================================================
# LEVEL 1
# ==========================================================

def level1(request):

    if not request.user.is_authenticated:

        return render(
            request,
            'level1.html'
        )

    try:

        StudentProfile.objects.get(
            user=request.user
        )

    except StudentProfile.DoesNotExist:

        return redirect(
            'student_login'
        )

    return render(
        request,
        'level1.html'
    )


# ==========================================================
# LEVEL 1 GAME
# ==========================================================

def level1_game(request):

    if not request.user.is_authenticated:

        return render(
            request,
            'level1_game.html'
        )

    try:

        StudentProfile.objects.get(
            user=request.user
        )

    except StudentProfile.DoesNotExist:

        return redirect(
            'student_login'
        )

    return render(
        request,
        'level1_game.html'
    )


# ==========================================================
# SAVE LEVEL 1 RESULT
# ==========================================================

def save_level1_result(request):

    if request.method != 'POST':

        return redirect(
            'level1_game'
        )

    try:

        score = int(
            request.POST.get(
                'score',
                0
            )
        )

    except (TypeError, ValueError):

        score = 0

    try:

        total_questions = int(
            request.POST.get(
                'total_questions',
                20
            )
        )

    except (TypeError, ValueError):

        total_questions = 20

    try:

        percentage = int(
            request.POST.get(
                'percentage',
                0
            )
        )

    except (TypeError, ValueError):

        percentage = 0

    try:

        stars = int(
            request.POST.get(
                'stars',
                1
            )
        )

    except (TypeError, ValueError):

        stars = 1


    # ======================================================
    # REGISTERED STUDENT RESULT
    # ======================================================

    if request.user.is_authenticated:

        try:

            student_profile = StudentProfile.objects.get(
                user=request.user
            )

        except StudentProfile.DoesNotExist:

            return redirect(
                'student_login'
            )

        last_attempt = Level1Result.objects.filter(
            student=student_profile
        ).order_by(
            '-attempt_number'
        ).first()

        if last_attempt:

            attempt_number = (
                last_attempt.attempt_number + 1
            )

        else:

            attempt_number = 1

        Level1Result.objects.create(
            student=student_profile,
            score=score,
            total_questions=total_questions,
            percentage=percentage,
            stars=stars,
            completed=True,
            attempt_number=attempt_number
        )

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


    # ======================================================
    # GUEST RESULT
    # ======================================================

    if not request.session.session_key:

        request.session.create()

    session_key = request.session.session_key

    GuestResult.objects.create(
        session_key=session_key,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        stars=stars,
        completed=True
    )

    # Remember that the guest completed Level 1.
    request.session['completed_levels'] = 1
    request.session.modified = True

    return redirect(
        'guest_result'
    )


# ==========================================================
# GUEST RESULT
# ==========================================================

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
# FINAL CHALLENGE
# ==========================================================

def final_challenge(request):

    # ======================================================
    # REGISTERED STUDENT
    # ======================================================

    if request.user.is_authenticated:

        try:

            student_profile = StudentProfile.objects.get(
                user=request.user
            )

        except StudentProfile.DoesNotExist:

            # Teachers cannot take the Final Challenge.
            return redirect(
                'home'
            )

        # --------------------------------------------------
        # LEVEL 4 MUST BE COMPLETED
        # --------------------------------------------------

        if student_profile.completed_levels < 4:

            return redirect(
                'student_dashboard'
            )

        # --------------------------------------------------
        # CHECK STUDENT FINAL RESULT
        # --------------------------------------------------

        final_result = FinalChallengeResult.objects.filter(
            student=student_profile
        ).first()

        if final_result:

            return render(
                request,
                'final_challenge_completed.html',
                {
                    'student': student_profile,
                    'result': final_result,
                }
            )

        # --------------------------------------------------
        # START FINAL CHALLENGE
        # --------------------------------------------------

        return render(
            request,
            'final_challenge.html',
            {
                'student': student_profile,
                'guest': False,
            }
        )


    # ======================================================
    # GUEST
    # ======================================================

    if not request.session.session_key:

        request.session.create()

    session_key = request.session.session_key

    # ------------------------------------------------------
    # LEVEL 4 MUST BE COMPLETED
    # ------------------------------------------------------

    completed_levels = request.session.get(
        'completed_levels',
        0
    )

    if completed_levels < 4:

        return redirect(
            'home'
        )

    # ------------------------------------------------------
    # CHECK GUEST FINAL RESULT
    # ------------------------------------------------------

    final_result = GuestFinalChallengeResult.objects.filter(
        session_key=session_key
    ).first()

    if final_result:

        return render(
            request,
            'final_challenge_completed.html',
            {
                'result': final_result,
                'guest': True,
            }
        )

    # ------------------------------------------------------
    # START FINAL CHALLENGE
    # ------------------------------------------------------

    return render(
        request,
        'final_challenge.html',
        {
            'guest': True,
        }
    )


# ==========================================================
# SAVE FINAL CHALLENGE RESULT
# ==========================================================

def save_final_challenge_result(request):

    if request.method != 'POST':

        return redirect(
            'final_challenge'
        )


    # ======================================================
    # GET RESULT DATA
    # ======================================================

    try:

        score = int(
            request.POST.get(
                'score',
                0
            )
        )

    except (TypeError, ValueError):

        score = 0


    try:

        total_questions = int(
            request.POST.get(
                'total_questions',
                25
            )
        )

    except (TypeError, ValueError):

        total_questions = 25


    try:

        percentage = int(
            request.POST.get(
                'percentage',
                0
            )
        )

    except (TypeError, ValueError):

        percentage = 0


    try:

        stars = int(
            request.POST.get(
                'stars',
                1
            )
        )

    except (TypeError, ValueError):

        stars = 1


    # ======================================================
    # REGISTERED STUDENT
    # ======================================================

    if request.user.is_authenticated:

        try:

            student_profile = StudentProfile.objects.get(
                user=request.user
            )

        except StudentProfile.DoesNotExist:

            return redirect(
                'home'
            )

        # --------------------------------------------------
        # LEVEL 4 CHECK
        # --------------------------------------------------

        if student_profile.completed_levels < 4:

            return redirect(
                'student_dashboard'
            )

        # --------------------------------------------------
        # ONE ATTEMPT ONLY
        # --------------------------------------------------

        existing_result = FinalChallengeResult.objects.filter(
            student=student_profile
        ).first()

        if existing_result:

            return redirect(
                'final_challenge'
            )

        # --------------------------------------------------
        # SAVE STUDENT RESULT
        # --------------------------------------------------

        FinalChallengeResult.objects.create(
            student=student_profile,
            score=score,
            total_questions=total_questions,
            percentage=percentage,
            stars=stars,
            completed=True
        )

        # --------------------------------------------------
        # UPDATE STUDENT TOTALS
        # --------------------------------------------------

        student_profile.total_points += score

        student_profile.total_stars += stars

        student_profile.save()

        return redirect(
            'final_challenge_result'
        )


    # ======================================================
    # GUEST
    # ======================================================

    if not request.session.session_key:

        request.session.create()

    session_key = request.session.session_key

    # ------------------------------------------------------
    # LEVEL 4 CHECK
    # ------------------------------------------------------

    completed_levels = request.session.get(
        'completed_levels',
        0
    )

    if completed_levels < 4:

        return redirect(
            'home'
        )

    # ------------------------------------------------------
    # ONE ATTEMPT ONLY
    # ------------------------------------------------------

    existing_result = GuestFinalChallengeResult.objects.filter(
        session_key=session_key
    ).first()

    if existing_result:

        return redirect(
            'final_challenge_result'
        )

    # ------------------------------------------------------
    # SAVE GUEST RESULT
    # ------------------------------------------------------

    GuestFinalChallengeResult.objects.create(
        session_key=session_key,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        stars=stars,
        completed=True
    )

    return redirect(
        'final_challenge_result'
    )


# ==========================================================
# FINAL CHALLENGE RESULT
# ==========================================================

def final_challenge_result(request):

    # ======================================================
    # REGISTERED STUDENT RESULT
    # ======================================================

    if request.user.is_authenticated:

        try:

            student_profile = StudentProfile.objects.get(
                user=request.user
            )

        except StudentProfile.DoesNotExist:

            return redirect(
                'home'
            )

        result = FinalChallengeResult.objects.filter(
            student=student_profile
        ).first()

        if result is None:

            return redirect(
                'final_challenge'
            )

        return render(
            request,
            'final_challenge_completed.html',
            {
                'student': student_profile,
                'result': result,
                'guest': False,
            }
        )


    # ======================================================
    # GUEST RESULT
    # ======================================================

    if not request.session.session_key:

        return redirect(
            'home'
        )

    session_key = request.session.session_key

    result = GuestFinalChallengeResult.objects.filter(
        session_key=session_key
    ).first()

    if result is None:

        return redirect(
            'final_challenge'
        )

    return render(
        request,
        'final_challenge_completed.html',
        {
            'result': result,
            'guest': True,
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

        if not full_name or not username or not password:

            return render(
                request,
                'teacher_register.html',
                {
                    'error':
                        'Please fill in all required fields.'
                }
            )

        if password != confirm_password:

            return render(
                request,
                'teacher_register.html',
                {
                    'error':
                        'Passwords do not match.'
                }
            )

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

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.first_name = full_name
        user.save()

        TeacherProfile.objects.create(
            user=user,
            full_name=full_name
        )

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
# ADD CLASS
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

        if not class_name:

            return render(
                request,
                'add_class.html',
                {
                    'error':
                        'Please enter a class or section name.'
                }
            )

        while True:

            join_code = secrets.token_hex(
                4
            ).upper()

            if not ClassSection.objects.filter(
                join_code=join_code
            ).exists():

                break

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
# VIEW STUDENTS
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
# ADD STUDENT
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
# STUDENT PROGRESS FOR TEACHER
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

    final_result = FinalChallengeResult.objects.filter(
        student=student
    ).first()

    return render(
        request,
        'student_progress.html',
        {
            'student': student,
            'results': results,
            'final_result': final_result,
        }
    )