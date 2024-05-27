from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import login_view, logout_view, register, unauthenticated_message, get_authenticated_user_id, user_detail, change_password

urlpatterns = [
    path('login', login_view, name='user-login'),
    path('register', register, name='user-register'),
    path('logout', logout_view, name='user-logout'),
    path('authenticated-user-id', get_authenticated_user_id, name='get-authenticated-user-id'),
    path('<int:id>/change-password', change_password, name='change-password-user'),
    path('<int:id>', user_detail, name='user-detail'),
    path('unauthenticated', unauthenticated_message, name='unauthenticated-message')
]

urlpatterns = format_suffix_patterns(urlpatterns)