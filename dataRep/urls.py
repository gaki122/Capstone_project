
from django.urls import path
from . import views


urlpatterns = [

    # =========================
    # HOME
    # =========================

    path(
        '',
        views.home,
        name='home'
    ),

    # =========================
    # LEARNING PAGES
    # =========================

    path(
        'learn/',
        views.learn,
        name='learn'
    ),

    path(
        'learn/ascii/',
        views.learn_ascii,
        name='learn_ascii'
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
    # STUDENT PAGES
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
        'my-progress/',
        views.student_my_progress,
        name='student_my_progress'
    ),

    # JOIN AND LEAVE CLASS

    path(
        'join-section/',
        views.join_section,
        name='join_section'
    ),

    path(
        'student/leave-class/',
        views.leave_class,
        name='leave_class'
    ),

    # =========================
    # TEACHER PAGES
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
        'teacher/class/<int:class_id>/add-student/',
        views.add_student,
        name='add_student'
    ),

    path(
        'teacher/classes/<int:class_id>/delete/',
        views.delete_class,
        name='delete_class'
    ),

    path(
        'teacher/students/',
        views.teacher_all_students,
        name='teacher_all_students'
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
    # LEVEL SELECTION
    # =========================

    path(
        'quest-levels/',
        views.quest_levels,
        name='quest_levels'
    ),

    # =========================
    # LEVEL 1 — ASCII GAME
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
    # LEVEL 2 — TEXT GAME
    # =========================

    path(
        'level2/game/',
        views.level2_game,
        name='level2_game'
    ),

    path(
        'level2/save-result/',
        views.save_level2_result,
        name='save_level2_result'
    ),

    # =========================
    # LEVEL 3 — IMAGE GAME
    # =========================

    path(
        'level3/game/',
        views.level3_game,
        name='level3_game'
    ),

    path(
        'level3/save-result/',
        views.save_level3_result,
        name='save_level3_result'
    ),

    # =========================
    # LEVEL 4 — AUDIO / SOUND GAME
    # =========================

    path(
        'level4/game/',
        views.level4_game,
        name='level4_game'
    ),

    path(
        'level4/save-result/',
        views.save_level4_result,
        name='save_level4_result'
    ),

    # =========================
    # GUEST RESULT
    # =========================

    path(
        'guest-result/',
        views.guest_result,
        name='guest_result'
    ),

    # =========================
    # FINAL CHALLENGE
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
