from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.sso_login, name='sso_login'),
    path('callback/', views.microsoft_sso_callback, name='microsoft_sso_callback'),
    path('login-successful/', views.login_successful, name='login_successful'),
    path('logout/', views.logout, name='logout'),  # Add this line
]
