from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
import json
import traceback

@csrf_exempt
def logout_view(request):
    if request.method != 'POST':  
        raise Http404
    
    logout(request)
    
    return JsonResponse({"success": True})



@csrf_exempt
def login_view(request):
    if request.method != 'POST':  
        raise Http404
    
    try:
        body = json.loads(request.body)
        username = body['username']
        password = body['password']
    except:
        traceback.print_exc()
        return JsonResponse({"error": 'User or login were not provided or were provided in an incorrect format'}, status=400)
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"error": 'Invalid credentials: could not authenticate user'}, status=403)
    
    
@csrf_exempt
def register(request):
    if request.method != 'POST':  
        raise Http404
    
    try:
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        email = body.get('email')
        last_name = body.get('last_name')
        first_name = body.get('first_name')
    except:
        traceback.print_exc()
        return JsonResponse({"error": 'Could not register user: data was provided in an incorrect format'}, status=400)
    
    query = Q(username=username)
    query.add(Q(email=email), Q.OR)
    
    if User.objects.filter(query).exists():
        return JsonResponse({"error": 'A user with a given username or email already exists'}, status=400)
    
    if not(username) or not(password) or not(email):
        return JsonResponse({"error": 'User name, password and email are required'}, status=400)
    
    user = User.objects.create_user(username, email, password)
    user.last_name = last_name or user.last_name
    user.first_name = first_name or user.first_name
    user.save()
    
    return JsonResponse({"id": user.pk})

@login_required(login_url="/users/unauthenticated") 
@csrf_exempt
def get_authenticated_user_id(request):
    if request.method != 'GET':  
        raise Http404
    
    return JsonResponse({"id": request.user.pk})


@login_required(login_url="/users/unauthenticated") 
@csrf_exempt
def user_detail(request, id):
    user = get_object_or_404(User, id=id)
    
    if (user != request.user):
        return JsonResponse({"error": 'You cannot view/edit/delete profiles of other users'}, status=401)
    
    if request.method == 'GET':  
        return JsonResponse({
            "id": user.pk,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "last_login": user.last_login,
            "date_joined": user.date_joined,
            "is_admin": user.is_superuser,
        })
    elif request.method == 'DELETE':
        user.delete()
        return JsonResponse({'success': True}, status=200)
        
    
@login_required(login_url="/users/unauthenticated") 
@csrf_exempt
def change_password(request, id):
    if request.method != 'PUT':  
        raise Http404
    
    user = get_object_or_404(User, id=id)
    
    if (user != request.user):
        return JsonResponse({"error": 'You cannot change password of other users'}, status=401)
    
    try:
        body = json.loads(request.body)
        old_password = body['old_password']
        new_password = body['new_password']
    except:
        traceback.print_exc()
        return JsonResponse({"error": 'Old or new password not provided correctly'}, status=400)
    
    authenticated_user = authenticate(request, username=user.username, password=old_password)
    if authenticated_user is not None:
        authenticated_user.set_password(new_password)
        authenticated_user.save()
        login(request, authenticated_user)
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"error": 'Invalid credentials: could not change password for user'}, status=403)


@csrf_exempt
def unauthenticated_message(request):
    return JsonResponse({"error": "You are not logged in and cannot view this page"}, status=403)
