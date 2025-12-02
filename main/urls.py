from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<int:project_id>/', views.project_detail, name='project_detail'),
    path('lectures/', views.lectures, name='lectures'),
    path('lectures/<int:lecture_id>/', views.lecture_detail, name='lecture_detail'),
    path('contacts/', views.contacts, name='contacts'),
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe/success/', views.subscribe_success, name='subscribe_success'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('quick-subscribe/', views.quick_subscribe, name='quick_subscribe'),
]

