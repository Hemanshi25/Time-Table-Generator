from django.urls import path
from . import views

urlpatterns = [
    path('teachers/', views.upload_teachers, name='teachers'),
    path('subjects/', views.upload_subjects, name='subjects'),
    path('assign-teachers/', views.assign_teachers, name='assign_teachers'),
    path('assign-lab/', views.assign_lab, name='assign_lab'),
    path('results/', views.show_results, name='results'),
]