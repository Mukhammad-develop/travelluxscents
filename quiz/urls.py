from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('start/', views.quiz_start, name='start'),
    path('step/<int:step>/', views.quiz_step, name='step'),
    path('results/', views.quiz_results, name='results'),
]
