from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from .models import StudentProfile


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        full_name = request.POST['full_name']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        StudentProfile.objects.create(
            user=user,
            full_name=full_name
        )

        login(request, user)

        return redirect('student_dashboard')

    return render(request, 'register.html')


def student_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('student_dashboard')

        return render(request, 'login.html', {
            'error': 'Invalid username or password.'
        })

    return render(request, 'login.html')


def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('student_login')

    student_profile = StudentProfile.objects.get(user=request.user)

    return render(request, 'student_dashboard.html', {
        'student': student_profile
    })

def student_logout(request):
    logout(request)
    return redirect('home')

def level1(request):
    return render(request, 'level1.html')

