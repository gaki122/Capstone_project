
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.db.models.functions import Lower
import secrets

from .models import (
    StudentProfile,
    Level1Result,
    Level2Result,
    Level3Result,
    Level4Result,
    TeacherProfile,
    ClassSection,
    FinalChallengeResult,
    GuestFinalChallengeResult,
)


# ==========================================================
# HOME AND LEARNING PAGES
# ==========================================================

def home(request):
    return render(request, 'home.html')


def learn(request):
    return render(request, 'learn.html')


def learn_ascii(request):
    return render(request, 'learn_ascii.html')


def learn_text(request):
    return render(request, 'learn_text.html')


def learn_images(request):
    return render(request, 'learn_images.html')


def learn_audio(request):
    return render(request, 'learn_audio.html')


# Retained for compatibility with any existing URL or template.
def learn_video(request):
    return render(request, 'learn_video.html')


def how_to_play(request):
    return render(request, 'how_to_play.html')


# ==========================================================
# STUDENT REGISTRATION
# ==========================================================

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        full_name = request.POST.get('full_name', '').strip()

        if not username or not password or not full_name:
            return render(request, 'register.html', {
                'error': 'Please fill in all required fields.'
            })

        if password != confirm_password:
            return render(request, 'register.html', {
                'error': 'Passwords do not match.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': (
                    'Username already exists. '
                    'Please choose another username.'
                )
            })

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            user.first_name = full_name
            user.save(update_fields=['first_name'])

            StudentProfile.objects.create(
                user=user,
                full_name=full_name,
            )

        login(request, user)
        return redirect('student_dashboard')

    return render(request, 'register.html')


# ==========================================================
# STUDENT LOGIN AND LOGOUT
# ==========================================================

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            if StudentProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('student_dashboard')

            return render(request, 'login.html', {
                'error': 'This is not a student account.'
            })

        return render(request, 'login.html', {
            'error': 'Invalid username or password.'
        })

    return render(request, 'login.html')


def student_logout(request):
    logout(request)
    return redirect('home')


# ==========================================================
# STUDENT DASHBOARD
# ==========================================================

@never_cache
def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('student_login')

    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return redirect('student_login')

    results = Level1Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    level2_results = Level2Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    level3_results = Level3Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    level4_results = Level4Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    final_result = FinalChallengeResult.objects.filter(
        student=student
    ).order_by('-id').first()

    return render(request, 'student_dashboard.html', {
        'student': student,
        'results': results,
        'level2_results': level2_results,
        'level3_results': level3_results,
        'level4_results': level4_results,
        'final_result': final_result,
    })


# ==========================================================
# JOIN CLASS
# ==========================================================

@login_required
def join_section(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return redirect('student_login')

    if student.class_section is not None:
        return render(request, 'join_section.html', {
            'student': student,
            'error': 'You have already joined a class.'
        })

    if request.method == 'POST':
        join_code = request.POST.get(
            'join_code', ''
        ).strip().upper()

        if not join_code:
            return render(request, 'join_section.html', {
                'student': student,
                'error': 'Please enter the class code.'
            })

        try:
            section = ClassSection.objects.get(join_code=join_code)
        except ClassSection.DoesNotExist:
            return render(request, 'join_section.html', {
                'student': student,
                'error': (
                    'Invalid class code. '
                    'Please check the code and try again.'
                )
            })

        student.class_section = section
        student.save(update_fields=['class_section'])

        messages.success(
            request,
            f'You have successfully joined {section.name}.'
        )

        return redirect('student_dashboard')

    return render(request, 'join_section.html', {
        'student': student,
    })


# ==========================================================
# LEAVE CLASS
# ==========================================================

@login_required
@require_POST
def leave_class(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return redirect('student_login')

    if student.class_section is None:
        messages.info(request, 'You are not currently in a class.')
        return redirect('student_dashboard')

    student.class_section = None
    student.save(update_fields=['class_section'])

    messages.success(
        request,
        'You have left the class successfully. '
        'Your account and saved game progress are preserved. '
        'You can now join another class.'
    )

    return redirect('student_dashboard')


# ==========================================================
# GAME PAGES
# ==========================================================

def _render_game_for_student_or_guest(request, template_name):
    student_profile = None

    if request.user.is_authenticated:
        try:
            student_profile = StudentProfile.objects.get(
                user=request.user
            )
        except StudentProfile.DoesNotExist:
            return redirect('home')

    return render(request, template_name, {
        'student_profile': student_profile,
    })


def level1(request):
    return _render_game_for_student_or_guest(request, 'level1.html')


def level1_game(request):
    return _render_game_for_student_or_guest(
        request, 'level1_game.html'
    )


def level2_game(request):
    return _render_game_for_student_or_guest(
        request, 'level2_game.html'
    )


def level3_game(request):
    return _render_game_for_student_or_guest(
        request, 'level3_game.html'
    )


def level4_game(request):
    return _render_game_for_student_or_guest(
        request, 'level4_game.html'
    )


# ==========================================================
# FINAL CHALLENGE HELPER
# ==========================================================

def has_saved_final_challenge(student):
    return FinalChallengeResult.objects.filter(
        student=student,
        completed=True,
    ).exists()


# ==========================================================
# SHARED RESULT VALIDATION
# ==========================================================

def get_game_result_data(request, default_total=20):
    try:
        total_questions = int(
            request.POST.get('total_questions', default_total)
        )
        score = int(request.POST.get('score', 0))
        stars = int(request.POST.get('stars', 0))
    except (TypeError, ValueError):
        return None

    if total_questions < 1 or total_questions > default_total:
        return None

    if score < 0 or score > total_questions:
        return None

    if stars < 0 or stars > 5:
        return None

    percentage = round(score * 100 / total_questions)

    return {
        'score': score,
        'total_questions': total_questions,
        'percentage': percentage,
        'stars': stars,
    }


def get_next_attempt_number(result_model, **filters):
    last_result = result_model.objects.filter(
        **filters
    ).order_by('-attempt_number', '-id').first()

    if last_result:
        return last_result.attempt_number + 1

    return 1


# ==========================================================
# SAVE STUDENT LEVEL RESULTS
# ==========================================================

@transaction.atomic
def save_student_level_result(
    request,
    result_model,
    level_number,
    data,
):
    if not request.user.is_authenticated:
        if level_number == 1:
            return redirect('level1_game')
        elif level_number == 2:
            return redirect('level2_game')
        elif level_number == 3:
            return redirect('level3_game')

        return redirect('level4_game')

    try:
        student = StudentProfile.objects.select_for_update().get(
            user=request.user
        )
    except StudentProfile.DoesNotExist:
        return redirect('home')

    attempt_number = get_next_attempt_number(
        result_model,
        student=student,
    )

    result_model.objects.create(
        student=student,
        score=data['score'],
        total_questions=data['total_questions'],
        percentage=data['percentage'],
        stars=data['stars'],
        completed=True,
        attempt_number=attempt_number,
    )

    student.total_points += data['score']
    student.total_stars += data['stars']
    student.completed_levels = max(
        student.completed_levels,
        level_number,
    )

    if (
        level_number == 1
        and data['score'] == data['total_questions']
        and data['score'] > student.best_streak
    ):
        student.best_streak = data['score']

    student.save()

    return redirect('student_dashboard')


# ==========================================================
# SAVE LEVEL 1 RESULT
# ==========================================================

@require_POST
def save_level1_result(request):
    if not request.user.is_authenticated:
        return redirect('level1_game')

    if not StudentProfile.objects.filter(user=request.user).exists():
        return redirect('home')

    data = get_game_result_data(request)

    if data is None:
        return redirect('level1_game')

    return save_student_level_result(
        request, Level1Result, 1, data
    )


# ==========================================================
# SAVE LEVEL 2 RESULT
# ==========================================================

@require_POST
def save_level2_result(request):
    if not request.user.is_authenticated:
        return redirect('level2_game')

    if not StudentProfile.objects.filter(user=request.user).exists():
        return redirect('home')

    data = get_game_result_data(request)

    if data is None:
        return redirect('level2_game')

    return save_student_level_result(
        request, Level2Result, 2, data
    )


# ==========================================================
# SAVE LEVEL 3 RESULT
# ==========================================================

@require_POST
def save_level3_result(request):
    if not request.user.is_authenticated:
        return redirect('level3_game')

    if not StudentProfile.objects.filter(user=request.user).exists():
        return redirect('home')

    data = get_game_result_data(request)

    if data is None:
        return redirect('level3_game')

    return save_student_level_result(
        request, Level3Result, 3, data
    )


# ==========================================================
# SAVE LEVEL 4 RESULT
# Guests cannot save Level 4 results.
# After Final Challenge, practice is allowed but not saved.
# ==========================================================

@require_POST
@transaction.atomic
def save_level4_result(request):
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )

    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'saved': False,
                'message': 'Guest results are not saved.',
            }, status=403)

        return redirect('level4_game')

    try:
        student = StudentProfile.objects.select_for_update().get(
            user=request.user
        )
    except StudentProfile.DoesNotExist:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'saved': False,
                'message': 'Only student accounts can save results.',
            }, status=403)

        return redirect('home')

    if has_saved_final_challenge(student):
        message = (
            'You have already completed the Final Challenge. '
            'You can continue practising Level 4, but this '
            'attempt has not been saved. Your saved scores '
            'and overall grade remain unchanged.'
        )

        if is_ajax:
            return JsonResponse({
                'success': True,
                'saved': False,
                'practice_mode': True,
                'message': message,
            })

        messages.info(request, message)
        return redirect('level4_game')

    data = get_game_result_data(request, default_total=20)

    if data is None:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'saved': False,
                'message': (
                    'The submitted result is invalid. '
                    'Please try again.'
                ),
            }, status=400)

        messages.error(
            request,
            'The submitted result is invalid. Please try again.'
        )
        return redirect('level4_game')

    attempt_number = get_next_attempt_number(
        Level4Result,
        student=student,
    )

    Level4Result.objects.create(
        student=student,
        score=data['score'],
        total_questions=data['total_questions'],
        percentage=data['percentage'],
        stars=data['stars'],
        completed=True,
        attempt_number=attempt_number,
    )

    student.total_points += data['score']
    student.total_stars += data['stars']
    student.completed_levels = max(student.completed_levels, 4)

    student.save(update_fields=[
        'total_points',
        'total_stars',
        'completed_levels',
    ])

    if is_ajax:
        return JsonResponse({
            'success': True,
            'saved': True,
            'message': (
                'Your Level 4 result has been saved. '
                'You can view your progress from your dashboard.'
            ),
            'attempt_number': attempt_number,
        })

    messages.success(request, 'Level 4 result saved successfully!')
    return redirect('student_dashboard')


# ==========================================================
# GUEST RESULT PAGE
# ==========================================================

def guest_result(request):
    return redirect('level1_game')


# ==========================================================
# GAME LEVEL SELECTION
# ==========================================================

def quest_levels(request):
    return render(request, 'quest_levels.html')


# ==========================================================
# FINAL CHALLENGE
# ==========================================================

def final_challenge(request):
    if request.user.is_authenticated:
        try:
            student = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return redirect('home')

        if student.completed_levels < 4:
            return redirect('student_dashboard')

        result = FinalChallengeResult.objects.filter(
            student=student
        ).order_by('-id').first()

        if result:
            return render(
                request,
                'final_challenge_completed.html',
                {
                    'student': student,
                    'result': result,
                    'guest': False,
                }
            )

        return render(request, 'final_challenge.html', {
            'student': student,
            'guest': False,
        })

    if not request.session.session_key:
        request.session.create()

    if request.session.get('completed_levels', 0) < 4:
        return redirect('home')

    result = GuestFinalChallengeResult.objects.filter(
        session_key=request.session.session_key
    ).order_by('-id').first()

    if result:
        return render(
            request,
            'final_challenge_completed.html',
            {
                'result': result,
                'guest': True,
            }
        )

    return render(request, 'final_challenge.html', {
        'guest': True,
    })


# ==========================================================
# SAVE FINAL CHALLENGE RESULT
# ==========================================================

@require_POST
@transaction.atomic
def save_final_challenge_result(request):
    data = get_game_result_data(request, default_total=25)

    if data is None:
        messages.error(
            request,
            'We could not validate your result. Please try again.'
        )
        return redirect('final_challenge')

    # REGISTERED STUDENT
    if request.user.is_authenticated:
        try:
            student = StudentProfile.objects.select_for_update().get(
                user=request.user
            )
        except StudentProfile.DoesNotExist:
            messages.error(
                request,
                'Student account not found. Please log in again.'
            )
            return redirect('home')

        if student.completed_levels < 4:
            messages.warning(
                request,
                'Please complete Levels 1–4 before taking '
                'the Final Challenge.'
            )
            return redirect('student_dashboard')

        existing_result = FinalChallengeResult.objects.filter(
            student=student
        ).first()

        if existing_result:
            messages.info(
                request,
                'You have already completed the Final Challenge. '
                'Your saved result is displayed below.'
            )
            return redirect('final_challenge_result')

        FinalChallengeResult.objects.create(
            student=student,
            score=data['score'],
            total_questions=data['total_questions'],
            percentage=data['percentage'],
            stars=data['stars'],
            completed=True,
        )

        student.total_points += data['score']
        student.total_stars += data['stars']
        student.save(update_fields=['total_points', 'total_stars'])

        messages.success(
            request,
            'Your Final Challenge result has been saved successfully!'
        )
        return redirect('final_challenge_result')

    # GUEST PLAYER
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.session.get('completed_levels', 0) < 4:
        messages.warning(
            request,
            'Please complete the previous levels before taking '
            'the Final Challenge.'
        )
        return redirect('home')

    existing_result = GuestFinalChallengeResult.objects.filter(
        session_key=session_key
    ).first()

    if existing_result:
        messages.info(
            request,
            'You have already completed the Final Challenge. '
            'Your saved result is displayed below.'
        )
        return redirect('final_challenge_result')

    GuestFinalChallengeResult.objects.create(
        session_key=session_key,
        score=data['score'],
        total_questions=data['total_questions'],
        percentage=data['percentage'],
        stars=data['stars'],
        completed=True,
    )

    messages.success(
        request,
        'Your Final Challenge result has been saved successfully!'
    )
    return redirect('final_challenge_result')


# ==========================================================
# FINAL CHALLENGE RESULT PAGE
# ==========================================================

@never_cache
def final_challenge_result(request):
    if request.user.is_authenticated:
        try:
            student = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return redirect('home')

        result = FinalChallengeResult.objects.filter(
            student=student
        ).order_by('-id').first()

        if result is None:
            return redirect('final_challenge')

        return render(
            request,
            'final_challenge_completed.html',
            {
                'student': student,
                'result': result,
                'guest': False,
            }
        )

    if not request.session.session_key:
        return redirect('home')

    result = GuestFinalChallengeResult.objects.filter(
        session_key=request.session.session_key
    ).order_by('-id').first()

    if result is None:
        return redirect('final_challenge')

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
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not full_name or not username or not password:
            return render(request, 'teacher_register.html', {
                'error': 'Please fill in all required fields.'
            })

        if password != confirm_password:
            return render(request, 'teacher_register.html', {
                'error': 'Passwords do not match.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'teacher_register.html', {
                'error': (
                    'Username already exists. '
                    'Please choose another username.'
                )
            })

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            user.first_name = full_name
            user.save(update_fields=['first_name'])

            TeacherProfile.objects.create(
                user=user,
                full_name=full_name,
            )

        login(request, user)
        return redirect('teacher_dashboard')

    return render(request, 'teacher_register.html')


# ==========================================================
# TEACHER LOGIN AND LOGOUT
# ==========================================================

def teacher_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            if TeacherProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('teacher_dashboard')

            return render(request, 'teacher_login.html', {
                'error': 'This account is not a teacher account.'
            })

        return render(request, 'teacher_login.html', {
            'error': 'Invalid username or password.'
        })

    return render(request, 'teacher_login.html')


def teacher_logout(request):
    logout(request)
    return redirect('teacher_login')


# ==========================================================
# TEACHER DASHBOARD
# ==========================================================

@never_cache
def teacher_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('teacher_login')

    try:
        teacher = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        return redirect('teacher_login')

    classes = ClassSection.objects.filter(
        teacher=request.user
    ).order_by('name')

    for section in classes:
        section.total_students = StudentProfile.objects.filter(
            class_section=section
        ).count()

    return render(request, 'teacher_dashboard.html', {
        'teacher': teacher,
        'classes': classes,
    })


# ==========================================================
# TEACHER: VIEW ALL STUDENTS
# ==========================================================

@never_cache
def teacher_all_students(request):
    if not request.user.is_authenticated:
        return redirect('teacher_login')

    if not TeacherProfile.objects.filter(user=request.user).exists():
        return redirect('teacher_login')

    students = StudentProfile.objects.filter(
        class_section__teacher=request.user
    ).select_related(
        'user',
        'class_section',
    ).order_by(
        'class_section__name',
        Lower('full_name'),
        'id',
    )

    return render(request, 'teacher_all_students.html', {
        'students': students,
        'total_students': students.count(),
    })


# ==========================================================
# TEACHER: ADD CLASS
# ==========================================================

def add_class(request):
    if not request.user.is_authenticated:
        return redirect('teacher_login')

    if not TeacherProfile.objects.filter(user=request.user).exists():
        return redirect('teacher_login')

    if request.method == 'POST':
        class_name = request.POST.get('class_name', '').strip()

        if not class_name:
            return render(request, 'add_class.html', {
                'error': 'Please enter a class or section name.'
            })

        while True:
            join_code = secrets.token_hex(4).upper()

            if not ClassSection.objects.filter(
                join_code=join_code
            ).exists():
                break

        ClassSection.objects.create(
            name=class_name,
            join_code=join_code,
            teacher=request.user,
        )

        return redirect('teacher_dashboard')

    return render(request, 'add_class.html')


# ==========================================================
# TEACHER: VIEW STUDENTS IN ONE CLASS
# ==========================================================

@never_cache
def view_students(request, class_id):
    if not request.user.is_authenticated:
        return redirect('teacher_login')

    if not TeacherProfile.objects.filter(user=request.user).exists():
        return redirect('teacher_login')

    try:
        section = ClassSection.objects.get(
            id=class_id,
            teacher=request.user,
        )
    except ClassSection.DoesNotExist:
        return redirect('teacher_dashboard')

    students = StudentProfile.objects.filter(
        class_section=section
    ).select_related(
        'user',
    ).order_by(
        Lower('full_name'),
        'id',
    )

    return render(request, 'view_students.html', {
        'class_section': section,
        'students': students,
    })


# ==========================================================
# TEACHER: ADD STUDENT TO CLASS
# ==========================================================

def add_student(request, class_id):
    if not request.user.is_authenticated:
        return redirect('teacher_login')

    if not TeacherProfile.objects.filter(user=request.user).exists():
        return redirect('teacher_login')

    try:
        section = ClassSection.objects.get(
            id=class_id,
            teacher=request.user,
        )
    except ClassSection.DoesNotExist:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not full_name or not username or not password:
            return render(request, 'add_student.html', {
                'class_section': section,
                'error': 'Please fill in all required fields.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'add_student.html', {
                'class_section': section,
                'error': 'Username already exists.'
            })

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password,
            )

            user.first_name = full_name
            user.save(update_fields=['first_name'])

            StudentProfile.objects.create(
                user=user,
                full_name=full_name,
                class_section=section,
            )

        return redirect('view_students', class_id=section.id)

    return render(request, 'add_student.html', {
        'class_section': section,
    })


# ==========================================================
# TEACHER: VIEW STUDENT PROGRESS
# ==========================================================

@never_cache
def student_progress(request, student_id):
    if not request.user.is_authenticated:
        return redirect('teacher_login')

    if not TeacherProfile.objects.filter(user=request.user).exists():
        return redirect('teacher_login')

    try:
        student = StudentProfile.objects.select_related(
            'user',
            'class_section',
        ).get(
            id=student_id,
            class_section__teacher=request.user,
        )
    except StudentProfile.DoesNotExist:
        return redirect('teacher_dashboard')

    results = Level1Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    level2_results = Level2Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    level3_results = Level3Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    level4_results = Level4Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    level1_is_completed = results.filter(completed=True).exists()
    level2_is_completed = level2_results.filter(completed=True).exists()
    level3_is_completed = level3_results.filter(completed=True).exists()
    level4_is_completed = level4_results.filter(completed=True).exists()

    final_result = FinalChallengeResult.objects.filter(
        student=student,
        completed=True,
    ).order_by('-id').first()

    final_challenge_is_completed = (
        final_result is not None
        and final_result.total_questions > 0
    )

    level1_attempts = results.count()
    level2_attempts = level2_results.count()
    level3_attempts = level3_results.count()
    level4_attempts = level4_results.count()

    total_attempts = (
        level1_attempts
        + level2_attempts
        + level3_attempts
        + level4_attempts
    )

    def get_best_result(level_results):
        completed_results = [
            result for result in level_results
            if result.completed and result.total_questions > 0
        ]

        if not completed_results:
            return None

        return max(
            completed_results,
            key=lambda result: (
                result.score / result.total_questions,
                result.score,
                result.id,
            ),
        )

    best_level1 = get_best_result(results)
    best_level2 = get_best_result(level2_results)
    best_level3 = get_best_result(level3_results)
    best_level4 = get_best_result(level4_results)

    activity_results = [
        best_level1,
        best_level2,
        best_level3,
        best_level4,
        final_result,
    ]

    completed_results = [
        result for result in activity_results
        if (
            result is not None
            and result.completed
            and result.total_questions > 0
        )
    ]

    overall_correct = sum(
        result.score for result in completed_results
    )
    overall_possible = sum(
        result.total_questions for result in completed_results
    )

    completed_activity_count = len(completed_results)
    total_activities = 5

    overall_percentage = (
        round(overall_correct * 100 / overall_possible, 1)
        if overall_possible > 0
        else None
    )

    overall_grade_finalized = (
        completed_activity_count == total_activities
    )

    return render(request, 'student_progress.html', {
        'student': student,

        'results': results,
        'level2_results': level2_results,
        'level3_results': level3_results,
        'level4_results': level4_results,
        'final_result': final_result,

        'level1_attempts': level1_attempts,
        'level2_attempts': level2_attempts,
        'level3_attempts': level3_attempts,
        'level4_attempts': level4_attempts,
        'total_attempts': total_attempts,

        'best_level1': best_level1,
        'best_level2': best_level2,
        'best_level3': best_level3,
        'best_level4': best_level4,

        'level1_is_completed': level1_is_completed,
        'level2_is_completed': level2_is_completed,
        'level3_is_completed': level3_is_completed,
        'level4_is_completed': level4_is_completed,
        'final_challenge_is_completed': final_challenge_is_completed,

        'overall_percentage': overall_percentage,
        'overall_correct': overall_correct,
        'overall_possible': overall_possible,
        'completed_activity_count': completed_activity_count,
        'total_activities': total_activities,
        'overall_grade_finalized': overall_grade_finalized,
    })


# ==========================================================
# STUDENT: MY PROGRESS
# ==========================================================

@never_cache
def student_my_progress(request):
    if not request.user.is_authenticated:
        return redirect('student_login')

    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return redirect('student_login')

    level1_results = Level1Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    level2_results = Level2Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    level3_results = Level3Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    level4_results = Level4Result.objects.filter(
        student=student
    ).order_by('-completed_at', '-id')

    final_result = FinalChallengeResult.objects.filter(
        student=student,
        completed=True,
    ).order_by('-id').first()

    total_level_attempts = (
        level1_results.count()
        + level2_results.count()
        + level3_results.count()
        + level4_results.count()
    )

    def get_best_result(results):
        completed_results = [
            result for result in results
            if result.completed and result.total_questions > 0
        ]

        if not completed_results:
            return None

        return max(
            completed_results,
            key=lambda result: (
                result.score / result.total_questions,
                result.score,
                result.id,
            ),
        )

    best_level1 = get_best_result(level1_results)
    best_level2 = get_best_result(level2_results)
    best_level3 = get_best_result(level3_results)
    best_level4 = get_best_result(level4_results)

    best_results = [
        best_level1,
        best_level2,
        best_level3,
        best_level4,
        final_result,
    ]

    completed_activity_results = [
        result for result in best_results
        if (
            result is not None
            and result.completed
            and result.total_questions > 0
        )
    ]

    overall_correct = sum(
        result.score for result in completed_activity_results
    )
    overall_possible = sum(
        result.total_questions
        for result in completed_activity_results
    )

    completed_activity_count = len(completed_activity_results)
    total_activities = 5

    overall_percentage = (
        round(overall_correct * 100 / overall_possible, 1)
        if overall_possible > 0
        else None
    )

    overall_grade_finalized = (
        completed_activity_count == total_activities
    )

    return render(request, 'student_my_progress.html', {
        'student': student,

        'level1_results': level1_results,
        'level2_results': level2_results,
        'level3_results': level3_results,
        'level4_results': level4_results,
        'final_result': final_result,

        'total_level_attempts': total_level_attempts,

        'best_level1': best_level1,
        'best_level2': best_level2,
        'best_level3': best_level3,
        'best_level4': best_level4,

        'overall_percentage': overall_percentage,
        'overall_correct': overall_correct,
        'overall_possible': overall_possible,
        'completed_activity_count': completed_activity_count,
        'total_activities': total_activities,
        'overall_grade_finalized': overall_grade_finalized,
    })


# ==========================================================
# TEACHER: DELETE CLASS
# Only the owning teacher can delete a class.
# ==========================================================

@login_required
@require_http_methods(["GET", "POST"])
def delete_class(request, class_id):
    if not TeacherProfile.objects.filter(user=request.user).exists():
        messages.error(
            request,
            'You are not authorized to delete classes.'
        )
        return redirect('teacher_login')

    section = get_object_or_404(
        ClassSection,
        id=class_id,
        teacher=request.user,
    )

    if request.method == 'GET':
        return render(
            request,
            'delete_class_confirm.html',
            {'class_section': section},
        )

    if request.POST.get('confirm_delete') != 'yes':
        messages.error(
            request,
            'Please confirm before deleting a class.'
        )
        return redirect('teacher_dashboard')

    section.delete()

    messages.success(
        request,
        'Class deleted successfully. Student accounts and saved '
        'game results have been preserved.'
    )

    return redirect('teacher_dashboard')
