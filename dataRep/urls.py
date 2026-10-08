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
    # Learning Pages
    # =========================

    path(
        'learn/',
        views.learn,
        name='learn'
    ),

    path(
        'learn/text/',
        views.learn_text,
        name='learn_text'
    ),

    path(
        'learn/images/',
        views.learn_images,
        name='learn_images'
    ),

    path(
        'learn/audio/',
        views.learn_audio,
        name='learn_audio'
    ),

    path(
        'learn/video/',
        views.learn_video,
        name='learn_video'
    ),

    path(
        'how-to-play/',
        views.how_to_play,
        name='how_to_play'
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

    path(
        'teacher/class/<int:class_id>/students/',
        views.view_students,
        name='view_students'
    ),

    path(
        'teacher/student/<int:student_id>/progress/',
        views.student_progress,
        name='student_progress'
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


    # =========================
    # Final Challenge
    # =========================

    path(
        'final-challenge/',
        views.final_challenge,
        name='final_challenge'
    ),

    path(
        'final-challenge/save-result/',
        views.save_final_challenge_result,
        name='save_final_challenge_result'
    ),

    path(
        'final-challenge/result/',
        views.final_challenge_result,
        name='final_challenge_result'
    ),

]