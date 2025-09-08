from django.contrib import admin
from django.urls import path
from vizitka import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
]
