from django.urls import path
from . import views


urlpatterns = [

    # =========================
    # Home
    # =========================

    path(
        '',
        views.home,
        name='home'
    ),


    # =========================
    # Student Pages
    # =========================

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.student_login,
        name='student_login'
    ),

    path(
        'logout/',
        views.student_logout,
        name='student_logout'
    ),

    path(
        'dashboard/',
        views.student_dashboard,
        name='student_dashboard'
    ),

    path(
        'join-section/',
        views.join_section,
        name='join_section'
    ),


    # =========================
    # Teacher Pages
    # =========================

    path(
        'teacher/register/',
        views.teacher_register,
        name='teacher_register'
    ),

    path(
        'teacher/login/',
        views.teacher_login,
        name='teacher_login'
    ),

    path(
        'teacher/dashboard/',
        views.teacher_dashboard,
        name='teacher_dashboard'
    ),

    path(
        'teacher/add-class/',
        views.add_class,
        name='add_class'
    ),

    # View all students in a class
    path(
        'teacher/class/<int:class_id>/students/',
        views.view_students,
        name='view_students'
    ),

    # View individual student progress
    path(
        'teacher/student/<int:student_id>/progress/',
        views.student_progress,
        name='student_progress'
    ),

    # Add student to class
    path(
        'teacher/class/<int:class_id>/add-student/',
        views.add_student,
        name='add_student'
    ),

    path(
        'teacher/logout/',
        views.teacher_logout,
        name='teacher_logout'
    ),


    # =========================
    # Level 1
    # =========================

    path(
        'level1/',
        views.level1,
        name='level1'
    ),

    path(
        'level1/game/',
        views.level1_game,
        name='level1_game'
    ),

    path(
        'level1/save-result/',
        views.save_level1_result,
        name='save_level1_result'
    ),


    # =========================
    # Guest Result
    # =========================

    path(
        'guest-result/',
        views.guest_result,
        name='guest_result'
    ),
]