from django.contrib import admin
from django.urls import path, include
from sso import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sso/', include('sso.urls')),  # Include URLs from the sso app
    path('', views.home, name='home'),  # Root URL pattern
]
